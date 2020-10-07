from datetime import datetime
import logging

from dns import resolver

from ruxit.api.base_plugin import RemoteBasePlugin
from dynatrace_api import DynatraceAPI

log = logging.getLogger(__name__)


class DNSExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        # The Dynatrace API client
        self.client = DynatraceAPI(
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

        name = self.config.get("test_name")
        dns_server = self.config.get("dns_server")
        host = self.config.get("host")
        location = self.config.get("test_location") if self.config.get("test_location") else "ActiveGate"
        frequency = int(self.config.get("frequency")) if self.config.get("frequency") else 15

        if self.executions % frequency == 0:
            success, response_time = test_dns(dns_server, host)
            log.info(f"DNS test, DNS server: {dns_server}, host: {host}, success: {success}, time: {response_time} ")

            self.client.report_simple_test(
                name,
                location,
                success,
                response_time,
                test_type="DNS",
                interval=frequency * 60,
                edit_link=f"#settings/customextension;id={self.plugin_info.name}",
            )

            if not success:
                self.client.report_simple_event(
                    name, f"DNS lookup failed for {name}, server: {dns_server}, host: {host}", location, test_type="DNS"
                )
            else:
                self.client.report_simple_event(
                    name,
                    f"DNS lookup failed for {name}, server: {dns_server}, host: {host}",
                    location,
                    state="resolved",
                    test_type="DNS",
                )

        self.executions += 1


def test_dns(dns_server: str, host: str) -> (bool, int):
    res = resolver.Resolver(configure=False)
    res.nameservers = [dns_server]
    res.lifetime = res.timeout = 2

    start = datetime.now()
    try:
        res.query(host, "A")
    except Exception as e:
        log.error(f"Failed executing the DNS test: {e}")
        return False, int((datetime.now() - start).total_seconds() * 1000)

    return True, int((datetime.now() - start).total_seconds() * 1000)
