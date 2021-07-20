from collections import defaultdict
from typing import Dict
import logging
import socket

from pingparsing import PingStats, PingParsing, PingTransmitter
from ruxit.api.base_plugin import RemoteBasePlugin
from datetime import datetime

from dynatrace import Dynatrace
from dynatrace.environment_v1.synthetic_third_party import SYNTHETIC_EVENT_TYPE_OUTAGE


log = logging.getLogger(__name__)


class PortExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        # The Dynatrace API client
        self.dt_client = Dynatrace(self.config.get("api_url"), self.config.get("api_token"), log=log, proxies=self.build_proxy_url())
        self.executions = 0
        self.failures: Dict[str, int] = defaultdict(int)

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

        log.setLevel(self.config.get("log_level"))

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
                    step_success, step_response_time = test_port(target_ip, int(port), protocol=self.config.get("test_protocol", "TCP"))
                    test_response_time += step_response_time

                    log.info(f"{target_ip}:{port} = {step_success}, {step_response_time}")
                    step_title = f"{target_ip}:{port}"

                    if not step_success:
                        test_success = False
                        self.failures[step_title] += 1

                        if self.failures[step_title] < failure_count:
                            log.info(f"The result for {step_title} was: {step_success}. Attempt {self.failures[step_title]}/{failure_count}, not reporting yet")
                            step_success = True
                    else:
                        self.failures[step_title] = 0

                    test_steps.append(
                        {"step": self.dt_client.third_part_synthetic_tests.create_synthetic_test_step(i + 1, step_title), "success": step_success}
                    )
                    test_step_results.append(
                        self.dt_client.third_part_synthetic_tests.create_synthetic_test_step_result(i + 1, datetime.now(), step_response_time)
                    )

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

        self.executions += 1


def test_port(ip: str, port: int, protocol: str = "TCP") -> (bool, int):
    log.debug(f"Testing {ip}:{port} using protocol {protocol}")
    start = datetime.now()
    result = True
    try:
        socket_type = socket.SOCK_STREAM if protocol == "TCP" else socket.SOCK_DGRAM
        sock = socket.socket(socket.AF_INET, socket_type)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(2)
        sock.connect((ip, port))

        if protocol == "UDP":
            sock.sendall(b"")
            data = sock.recv(1024)
            log.debug(f"Received data: {data}")
        sock.close()

    except socket.timeout:
        if protocol == "UDP":
            log.warning(f"The UDP test for {ip}:{port} timed out, checking if the host can be pinged before reporting")
            ping_result = ping(ip)
            log.info(f"Ping result to double check UDP: {ping_result.as_dict()}")
            result = ping_result.packet_loss_rate is not None and ping_result.packet_loss_rate == 0
        else:
            result = False
    except Exception as ex:
        log.error(f"Could not connect to {ip}:{port} with protocol {protocol} - {ex}")
        result = False

    return result, int((datetime.now() - start).total_seconds() * 1000)


def ping(host: str) -> PingStats:
    ping_parser = PingParsing()
    transmitter = PingTransmitter()
    transmitter.destination = host
    transmitter.count = 1
    transmitter.timeout = 2000
    return ping_parser.parse(transmitter.ping())


def main():
    print(test_port("192.168.15.101", 123, "UDP"))
    print(test_port("192.168.15.101", 124, "UDP"))
    print(test_port("192.168.15.25", 333, "UDP"))
    print(test_port("192.168.15.101", 1521, "TCP"))
    print(test_port("192.168.15.101", 1522, "TCP"))


if __name__ == "__main__":
    main()
