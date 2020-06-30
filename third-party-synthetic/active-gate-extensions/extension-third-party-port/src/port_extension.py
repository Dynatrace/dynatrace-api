from ruxit.api.base_plugin import RemoteBasePlugin
from datetime import datetime
import logging
import socket

from dynatrace_api import DynatraceAPI

log = logging.getLogger(__name__)


class PortExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        # The Dynatrace API client
        self.client = DynatraceAPI(self.config.get("api_url"), self.config.get("api_token"), log=log)
        self.executions = 0

    def query(self, **kwargs) -> None:

        log.setLevel(self.config.get("log_level"))

        name = self.config.get("test_name")
        target_ip = self.config.get("test_target_ip")
        target_ports = self.config.get("test_target_ports", "").split(",")
        location = self.config.get("test_location", "") if self.config.get("test_location") else "ActiveGate"
        frequency = int(self.config.get("frequency")) if self.config.get("frequency") else 1

        if self.executions % frequency == 0:
            for port in target_ports:
                if port:
                    success, response_time = test_port(target_ip, int(port))
                    test_name = f"{name} {target_ip}:{port}"
                    log.info(f"{target_ip}:{port} = {success}, {response_time}")

                    self.client.report_simple_test(
                        test_name, location, success, response_time, test_type="Port", interval=frequency * 60
                    )

                    if not success:
                        self.client.report_simple_event(
                            test_name,
                            f"Port check failed for {name}, target: {target_ip}:{port}",
                            location,
                            state="open",
                            test_type="Port",
                        )
                    else:
                        self.client.report_simple_event(
                            test_name,
                            f"Port check failed for {name}, target: {target_ip}:{port}",
                            location,
                            state="resolved",
                            test_type="Port",
                        )

        self.executions += 1


def test_port(ip: str, port: int) -> (bool, int):
    start = datetime.now()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((ip, port))
    sock.close()

    return result == 0, int((datetime.now() - start).total_seconds() * 1000)
