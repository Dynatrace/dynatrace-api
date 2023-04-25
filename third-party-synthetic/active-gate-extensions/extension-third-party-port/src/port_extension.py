from collections import defaultdict
from typing import Dict
import logging
import socket
import re

from ruxit.api.base_plugin import RemoteBasePlugin
from datetime import datetime

from dynatrace import Dynatrace
from dynatrace.environment_v1.synthetic_third_party import SYNTHETIC_EVENT_TYPE_OUTAGE
from ruxit.api.exceptions import ConfigException

from port_imports.environment import get_api_url

DT_TIMEOUT_SECONDS = 10

log = logging.getLogger(__name__)

class PortExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        self.api_url = get_api_url()
        self.dt_client = Dynatrace(self.api_url,
                                   self.config.get("api_token"),
                                   log=self.logger,
                                   proxies=self.build_proxy_url(), 
                                   timeout=DT_TIMEOUT_SECONDS)
        self.executions = 0
        self.failures: Dict[str, int] = defaultdict(int)

        valid_ip = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        valid_hostname = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

        target = self.config.get("test_target_ip")
        if not re.match(valid_ip, target) and not re.match(valid_hostname, target):
            raise ConfigException(f"Invalid test_target: {target}, must be a valid IP or hostname")

    def build_proxy_url(self):
        proxy_address = self.config.get("proxy_address")
        proxy_username = self.config.get("proxy_username")
        proxy_password = self.config.get("proxy_password")

        if proxy_address:
            protocol, address = proxy_address.split("://")
            proxy_url = f"{protocol}://"
            if proxy_username:
                proxy_url += proxy_username
            if proxy_password:
                proxy_url += f":{proxy_password}"
            proxy_url += f"@{address}"
            return {"https": proxy_url}

        return {}

    def query(self, **kwargs) -> None:

        self.logger.setLevel(self.config.get("log_level"))

        target_ip = self.config.get("test_target_ip")

        target_ports = self.config.get("test_target_ports", "").split(",")
        location = self.config.get("test_location", "") if self.config.get("test_location") else "ActiveGate"
        location_id = location.replace(" ", "_").lower()
        frequency = int(self.config.get("frequency")) if self.config.get("frequency") else 15
        failure_count = self.config.get("failure_count", 1)

        if self.executions % frequency == 0:
            # This test has multiple steps, these variables will be modified as the steps are created
            test_success = True
            test_response_time = 0
            test_steps = []
            test_step_results = []
            test_title = f"{self.config.get('test_name')}" if self.config.get("test_name") else f"Port checks for {target_ip}"

            for i, port in enumerate(target_ports):
                if port:
                    timeout = int(self.config.get("test_timeout", 2)) or 2
                    step_success, step_response_time = test_port(target_ip,
                                                                 int(port),
                                                                 protocol=self.config.get("test_protocol", "TCP"),
                                                                 timeout=timeout)
                    test_response_time += step_response_time

                    self.logger.info(f"{target_ip}:{port} = {step_success}, {step_response_time}")
                    step_title = f"{target_ip}:{port}"

                    if not step_success:
                        test_success = False
                        self.failures[step_title] += 1

                        if self.failures[step_title] < failure_count:
                            self.logger.info(f"The result for {step_title} was: {step_success}. Attempt {self.failures[step_title]}/{failure_count}, not reporting yet")
                            step_success = True
                    else:
                        self.failures[step_title] = 0

                    test_steps.append(
                        {"step": self.dt_client.third_part_synthetic_tests.create_synthetic_test_step(i + 1, step_title), "success": step_success}
                    )
                    test_step_results.append(
                        self.dt_client.third_part_synthetic_tests.create_synthetic_test_step_result(i + 1, datetime.now(), step_response_time)
                    )

            try:
                self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test(
                    engine_name="Port",
                    timestamp=datetime.now(),
                    location_id=location_id,
                    location_name=location,
                    test_id=f"{self.activation.entity_id}",
                    test_title=test_title,
                    schedule_interval=frequency * 60,
                    success=test_success,
                    response_time=test_response_time,
                    edit_link=f"#settings/customextension;id={self.plugin_info.name}",
                    detailed_steps=[test_step["step"] for test_step in test_steps],
                    detailed_step_results=test_step_results,
                    icon_url="https://raw.githubusercontent.com/Dynatrace/dynatrace-api/master/third-party-synthetic/active-gate-extensions/extension-third-party-port/port.png",
                )

                for step in test_steps:
                    event_name = f"Port check failed for {test_title} ({step['step'].title})"
                    self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test_event(
                        test_id=f"{self.activation.entity_id}",
                        name=event_name,
                        location_id=location_id,
                        timestamp=datetime.now(),
                        state="open" if not step["success"] else "resolved",
                        event_type=SYNTHETIC_EVENT_TYPE_OUTAGE,
                        reason=event_name,
                        engine_name="Port",
                    )
            except Exception as e:
                self.logger.error(f"Error reporting third party test results to {self.api_url}: '{e}'")

        self.executions += 1


def udp_check(ip: str, port: int, timeout: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_recv_bufsize = 8192
    udp_send_payload = b""

    try:
        sock.connect((ip, port))
        sock.send(udp_send_payload)
        sock.settimeout(timeout)

        try:
            sock.recv(udp_recv_bufsize)
        except socket.timeout:
            pass
        finally:
            sock.settimeout(0)
        local = sock.getsockname()
        log.info(f"Connected to {ip}:{port} from {local[0]}:{local[1]}")
        return True
    except (OSError, socket.error) as error:
        log.warning(f"Could not connect to {ip}:{port} - {error}")
        return False
    finally:
        sock.close()


def tcp_check(ip: str, port: int, timeout: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.connect((ip, port))

    except socket.timeout:
        return False
    except Exception as ex:
        log.error(f"Could not connect to {ip}:{port} - {ex}")
        return False
    finally:
        sock.close()
    return True


def test_port(ip: str, port: int, protocol: str = "TCP", timeout: int = 2) -> (bool, int):
    log.debug(f"Testing {ip}:{port} using protocol {protocol}")
    start = datetime.now()
    if protocol == "UDP":
        result = udp_check(ip, port, timeout)
    else:
        result = tcp_check(ip, port, timeout)

    return result, int((datetime.now() - start).total_seconds() * 1000)


def main():
    print(test_port("192.168.15.101", 123, "UDP"))
    print(test_port("192.168.15.101", 124, "UDP"))
    print(test_port("192.168.15.25", 333, "UDP"))
    print(test_port("192.168.15.101", 1521, "TCP"))
    print(test_port("192.168.15.101", 1522, "TCP"))


if __name__ == "__main__":
    main()
