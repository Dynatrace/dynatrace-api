from collections import defaultdict
from typing import Dict

from ruxit.api.base_plugin import RemoteBasePlugin
from datetime import datetime
import logging
import socket

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

        target_protocol = self.config.get("test_target_protocol", "TCP")
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
            test_title = f"{self.config.get('test_name')}" if self.config.get("test_name") else f"{target_protocol} port checks for {target_ip}"

            for i, port in enumerate(target_ports):
                if port:
                    step_success, step_response_time = test_port(target_ip, int(port), target_protocol == "TCP")
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

def test_port(ip: str, port: int, tcp: bool) -> (bool, int):
    result = 1
    duration = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM if tcp else socket.SOCK_DGRAM)
    sock.settimeout(2)
    if tcp:
        start = datetime.now()
        try:
            result = sock.connect_ex((ip, port))
        except Exception as ex:
            log.error(f"Could not connect to {ip}:{port} over TCP - {ex}")
        duration = int((datetime.now() - start).total_seconds() * 1000)
    else:
        try:
            sock.sendto(bytes(0), (ip, port))
            sock.recvfrom(1024)
        except socket.timeout:
            result = 0
        except Exception as ex:
            log.error(f"Could not connect to {ip}:{port} over UDP - {ex}")
    sock.close()
    
    return result == 0, duration