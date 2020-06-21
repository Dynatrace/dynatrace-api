import logging

from ruxit.api.base_plugin import RemoteBasePlugin
from dynatrace_api import DynatraceAPI

import pingparsing

log = logging.getLogger(__name__)


class PingExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        # The Dynatrace API client
        self.client = DynatraceAPI(self.config.get("api_url"), self.config.get("api_token"), log=log)
        self.executions = 0

    def query(self, **kwargs) -> None:

        log.setLevel(self.config.get("log_level"))

        name = self.config.get("test_name")
        target = self.config.get("test_target")
        location = self.config.get("test_location", "") if self.config.get("test_location") else "ActiveGate"
        frequency = self.config.get("frequency") if self.config.get("frequency") else 1

        if self.executions % frequency == 0:
            ping_result = ping(target)
            log.info(ping_result.as_dict())

            self.client.report_simple_test(
                name=name, location_name=location, success=ping_result.packet_loss_rate == 0, response_time=ping_result.rtt_avg or 0,
            )

            if ping_result.packet_loss_rate > 0:
                self.client.report_simple_event(name, f"Ping failed for {name}, target: {target}", location)
            else:
                self.client.report_simple_event(name, f"Ping failed for {name}, target: {target}", location, state="resolved")

        self.executions += 1


def ping(host: str) -> pingparsing.PingStats:
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = host
    transmitter.count = 2
    transmitter.timeout = 2000
    return ping_parser.parse(transmitter.ping())
