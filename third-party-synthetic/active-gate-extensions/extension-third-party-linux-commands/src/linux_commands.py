import logging
from datetime import datetime

from remote_client import RemoteClient
from ruxit.api.base_plugin import RemoteBasePlugin
from dynatrace import Dynatrace
from dynatrace.environment_v1.synthetic_third_party import SYNTHETIC_EVENT_TYPE_OUTAGE

from commands_imports.environment import get_api_url

DT_TIMEOUT_SECONDS = 10
ENGINE_NAME = "SSH"

log = logging.getLogger(__name__)

class LinuxCommandsExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        self.api_url = get_api_url()
        self.dt_client = Dynatrace(self.api_url, self.config.get("api_token"), log=log, proxies=self.build_proxy_url(), timeout=DT_TIMEOUT_SECONDS)
        self.executions = 0
        self.failures_detected = 0

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

    def query(self, **kwargs):
        log.setLevel(self.config.get("log_level"))
        hostname = self.config.get("hostname").strip()
        username = self.config.get("username")
        port = int(self.config.get("port", 22))
        password = self.config.get("password") if self.config.get("password") else None
        second_username = self.config.get("second_username") if self.config.get("second_username") else None
        second_password = self.config.get("second_password") if self.config.get("second_password") else None
        key = self.config.get("ssh_key_file") if self.config.get("ssh_key_file") else None
        passphrase = self.config.get("ssh_key_passphrase") if self.config.get("ssh_key_passphrase") else None
        command = self.config.get("command").strip()
        evaluation = self.config.get("output_evaluation", "TEXT_PATTERN_MATCH")
        comparison_operator = self.config.get("validation_numeric_operator") if self.config.get("validation_numeric_operator") else None
        comparison_value = float(self.config.get("validation_numeric_value")) if self.config.get("validation_numeric_value") else None
        text_pattern = self.config.get("validation_pattern") if self.config.get("validation_pattern") else None

        step_title = f"{hostname} ({command})"
        test_title = self.config.get("test_name") if self.config.get("test_name") else step_title
        location = self.config.get("location") if self.config.get("location") else "ActiveGate"
        location_id = location.replace(" ", "_").lower()
        frequency = int(self.config.get("frequency")) if self.config.get("frequency") else 15
        failure_count = self.config.get("failure_count", 1)

        if self.executions % frequency == 0:
            with RemoteClient(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                key=key,
                passphrase=passphrase,
                log=log
            ) as client:
                if not client.connected:
                    success, reason, response_time = False, "Failed to connect to host", 0
                else:
                    success, reason, response_time = client.test_command(
                        command=command,
                        second_username=second_username,
                        second_password=second_password,
                        evaluation=evaluation,
                        comparison_operator=comparison_operator,
                        comparison_value=comparison_value,
                        text_pattern=text_pattern
                    )
            log.info(f"Test: {step_title}, success: {success}, time: {response_time}")

            if not success:
                self.failures_detected += 1
                if self.failures_detected < failure_count:
                    log.info(f"Success: {success}. Attempt {self.failures_detected}/{failure_count}. Not reporting yet")
                    success = True
            else:
                self.failures_detected = 0

            try:
                self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test(
                    engine_name=ENGINE_NAME,
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
                    icon_url="https://raw.githubusercontent.com/Dynatrace/dynatrace-api/master/third-party-synthetic/active-gate-extensions/extension-third-party-linux-commands/linux_commands.png"
                )

                self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test_event(
                    test_id=self.activation.entity_id,
                    name=f"Command execution failed for {step_title}",
                    location_id=location_id,
                    timestamp=datetime.now(),
                    state="open" if not success else "resolved",
                    event_type=SYNTHETIC_EVENT_TYPE_OUTAGE,
                    reason=reason,
                    engine_name=ENGINE_NAME,
                )
            except Exception as e:
                self.logger.error(f"Error reporting third party test results to {self.api_url}: '{e}'")

        self.executions += 1