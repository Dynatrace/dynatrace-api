from datetime import datetime
import re

from ruxit.api.base_plugin import RemoteBasePlugin
from ruxit.api.exceptions import ConfigException
from dynatrace import Dynatrace
from dynatrace.environment_v1.synthetic_third_party import SYNTHETIC_EVENT_TYPE_OUTAGE

import pingparsing

from ping_imports.environment import get_api_url

DT_TIMEOUT_SECONDS = 10

class PingExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):

        self.api_url = get_api_url()
        self.dt_client = Dynatrace(self.api_url, self.config.get("api_token"), log=self.logger, proxies=self.build_proxy_url(), timeout=DT_TIMEOUT_SECONDS)
        self.executions = 0
        self.failures_detected = 0

        valid_ip = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        valid_hostname = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"

        target = self.config.get("test_target")
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

        target = self.config.get("test_target")

        failure_count = self.config.get("failure_count", 1)

        step_title = f"{target}"
        test_title = self.config.get("test_name") if self.config.get("test_name") else step_title
        location = self.config.get("test_location", "") if self.config.get("test_location") else "ActiveGate"
        location_id = location.replace(" ", "_").lower()
        frequency = int(self.config.get("frequency")) if self.config.get("frequency") else 15

        if self.executions % frequency == 0:
            timeout = int(self.config.get("test_timeout", 2)) or 2
            ping_result = ping(target, timeout)
            self.logger.info(ping_result.as_dict())

            success = ping_result.packet_loss_rate is not None and ping_result.packet_loss_rate == 0

            if not success:
                self.failures_detected += 1
                if self.failures_detected < failure_count:
                    self.logger.info(f"The result was: {success}. Attempt {self.failures_detected}/{failure_count}, not reporting yet")
                    success = True
            else:
                self.failures_detected = 0

            response_time = ping_result.rtt_avg or 0

            try:
                self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test(
                    engine_name="Ping",
                    timestamp=datetime.now(),
                    location_id=location_id,
                    location_name=location,
                    test_id=self.activation.entity_id,
                    test_title=test_title,
                    step_title=step_title,
                    schedule_interval=frequency * 60,
                    success=success,
                    response_time=response_time,
                    edit_link=f"#settings/customextension;id={self.plugin_info.name}",
                    icon_url="https://raw.githubusercontent.com/Dynatrace/dynatrace-api/master/third-party-synthetic/active-gate-extensions/extension-third-party-ping/ping.png",
                )

                self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test_event(
                    test_id=self.activation.entity_id,
                    name=f"Ping failed for {step_title}",
                    location_id=location_id,
                    timestamp=datetime.now(),
                    state="open" if not success else "resolved",
                    event_type=SYNTHETIC_EVENT_TYPE_OUTAGE,
                    reason=f"Ping failed for {step_title}. Result: {str(ping_result.as_dict())}",
                    engine_name="Ping",
                )
            except Exception as e:
                self.logger.error(f"Error reporting third party test results to {self.api_url}: '{e}'")

        self.executions += 1


def ping(host: str, timeout: int) -> pingparsing.PingStats:
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = host
    transmitter.count = 2
    transmitter.timeout = timeout * 1000
    return ping_parser.parse(transmitter.ping())
