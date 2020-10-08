from ruxit.api.base_plugin import RemoteBasePlugin
from datetime import datetime
import logging
import socket

from dynatrace import Dynatrace
from dynatrace.synthetic_third_party import SYNTHETIC_EVENT_TYPE_OUTAGE


log = logging.getLogger(__name__)


class PortExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        # The Dynatrace API client
        self.dt_client = Dynatrace(
            self.config.get("api_url"), self.config.get("api_token"), log=log, proxies=self.build_proxy_url()
        )
        self.executions = 0

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

        if self.executions % frequency == 0:
            for port in target_ports:
                if port:
                    success, response_time = test_port(target_ip, int(port))
                    log.info(f"{target_ip}:{port} = {success}, {response_time}")

                    step_title = f"{target_ip}:{port}"
                    test_title = f"self.config.get('test_name') port {port}" if self.config.get("test_name") else step_title

                    self.dt_client.report_simple_thirdparty_synthetic_test(
                        engine_name="Port",
                        timestamp=datetime.now(),
                        location_id=location_id,
                        location_name=location,
                        test_id=f"{self.activation.entity_id}{port}",
                        test_title=test_title,
                        step_title=step_title,
                        schedule_interval=frequency * 60,
                        success=success,
                        response_time=response_time,
                        edit_link=f"#settings/customextension;id={self.plugin_info.name}",
                    )

                    self.dt_client.report_simple_thirdparty_synthetic_test_event(
                        test_id=f"{self.activation.entity_id}{port}",
                        name=f"Port check failed for {step_title}",
                        location_id=location_id,
                        timestamp=datetime.now(),
                        state="open" if not success else "resolved",
                        event_type=SYNTHETIC_EVENT_TYPE_OUTAGE,
                        reason=f"Port check failed for {step_title}",
                        engine_name="Port",
                    )

        self.executions += 1


def test_port(ip: str, port: int) -> (bool, int):
    start = datetime.now()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((ip, port))
    sock.close()

    return result == 0, int((datetime.now() - start).total_seconds() * 1000)
