import logging
from typing import List
from datetime import datetime

from sftp_client import SFTPClient
from ruxit.api.base_plugin import RemoteBasePlugin
from dynatrace import Dynatrace
from dynatrace.environment_v1.synthetic_third_party import SYNTHETIC_EVENT_TYPE_OUTAGE, SyntheticTestStep, SyntheticMonitorStepResult


log = logging.getLogger(__name__)
ENGINE_NAME = "SFTP"


class SFTPExtension(RemoteBasePlugin):
    def initialize(self, **kwargs):
        self.dt_client = Dynatrace(self.config.get("api_url"), self.config.get("api_token"), log=log, proxies=self.build_proxy_url())
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
        key = self.config.get("ssh_key_file") if self.config.get("ssh_key_file") else None
        passphrase = self.config.get("ssh_key_passphrase") if self.config.get("ssh_key_passphrase") else None
        test_read = self.config.get("test_read", False)
        test_put = self.config.get("test_put", False)
        local_file = self.config.get("local_file") if self.config.get("local_file") else None
        remote_dir = self.config.get("remote_dir") if self.config.get("remote_dir") else None

        test_title = self.config.get("test_name") if self.config.get("test_name") else f"{hostname}:{port}"
        location = self.config.get("location") if self.config.get("location") else "ActiveGate"
        location_id = location.replace(" ", "_").lower()
        frequency = int(self.config.get("frequency")) if self.config.get("frequency") else 15
        failure_count = self.config.get("failure_count", 1)

        if self.executions % frequency == 0:
            steps: List[SyntheticTestStep] = []
            results: List[SyntheticMonitorStepResult] = []
            test_response_time = 0

            with SFTPClient(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                key=key,
                passphrase=passphrase,
                log=log
            ) as client:
                conn_success, reason, conn_time = client.test_connect()
                log.info(f"Test: {test_title}, Step: Connect, success: {conn_success}, time: {conn_time}")
                
                success = conn_success
                test_response_time += conn_time
                steps.append(self.dt_client.third_part_synthetic_tests.create_synthetic_test_step(1, "SFTP Connect"))
                results.append(self.dt_client.third_part_synthetic_tests.create_synthetic_test_step_result(1, datetime.now(), conn_time))

                if conn_success and test_read:
                    read_success, reason, read_time = client.test_read(remote_dir)
                    log.info(f"Test: {test_title}, Step: Read, success: {read_success}, time: {read_time}")
                    
                    success = success and read_success
                    test_response_time += read_time
                    steps.append(self.dt_client.third_part_synthetic_tests.create_synthetic_test_step(2, "SFTP Read"))
                    results.append(self.dt_client.third_part_synthetic_tests.create_synthetic_test_step_result(2, datetime.now(), read_time))
                
                if conn_success and test_put:
                    put_success, reason, put_time = client.test_put(local_file, remote_dir)
                    log.info(f"Test: {test_title}, Step: Put, success: {put_success}, time: {put_time}")
                    
                    success = success and put_success
                    test_response_time += put_time
                    steps.append(self.dt_client.third_part_synthetic_tests.create_synthetic_test_step(3, "SFTP Put"))
                    results.append(self.dt_client.third_part_synthetic_tests.create_synthetic_test_step_result(3, datetime.now(), put_time))

            if not success:
                self.failures_detected += 1
                if self.failures_detected < failure_count:
                    log.info(f"Success: {success}. Attempt {self.failures_detected}/{failure_count}. Not reporting yet")
                    success = True
            else:
                self.failures_detected = 0

            self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test(
                engine_name=ENGINE_NAME,
                timestamp=datetime.now(),
                location_id=location_id,
                location_name=location,
                test_id=self.activation.entity_id,
                test_title=test_title,
                schedule_interval=frequency * 60,
                success=success,
                response_time=test_response_time,
                edit_link=f"#settings/customextension;id={self.plugin_info.name}",
                icon_url="https://raw.githubusercontent.com/Dynatrace/dynatrace-api/master/third-party-synthetic/active-gate-extensions/extension-third-party-sftp/sftp.png",
                detailed_steps=steps,
                detailed_step_results=results
            )

            self.dt_client.third_part_synthetic_tests.report_simple_thirdparty_synthetic_test_event(
                test_id=self.activation.entity_id,
                name=f"SFTP Test failed for {test_title}",
                location_id=location_id,
                timestamp=datetime.now(),
                state="open" if not success else "resolved",
                event_type=SYNTHETIC_EVENT_TYPE_OUTAGE,
                reason=reason,
                engine_name=ENGINE_NAME
            )
        
        self.executions += 1