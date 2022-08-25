import re
import time
import logging
import paramiko
from typing import Union, Optional


class RemoteClient:
    def __init__(self,
        hostname: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        key: Optional[str] = None,
        passphrase: Optional[str] = None,
        log: Optional[logging.Logger] = None
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key = key
        self.passphrase = passphrase
        self.log = log if log is not None else logging.getLogger(__name__)
        self.connected = False

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.client = client

    def __enter__(self) -> "RemoteClient":
        try:
            if self.key is not None:
                self.log.debug("Connecting using key")
                self.client.connect(self.hostname, port=self.port, username=self.username, key_filename=self.key, passphrase=self.passphrase)
            else:
                self.log.debug("Connecting using password")
                self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password, timeout=20)
        except Exception as e:
            self.log.exception(e)
            self.connected = False
        else:
            self.connected = True
        
        return self

    def __exit__(self, e_type, e_value, e_trace) -> bool:
        self.connected = False
        if self.client:
            self.client.close()

        if e_type is not None:
            self.log.exception(e_type, e_value, e_trace)

        return True
    
    def _run_command(self, command: str) -> list:
        self.log.debug(f"Executing command: {command}")
        _, stdout, stderr = self.client.exec_command(command, timeout=30)
        err = stderr.read().decode("utf-8")
        out = stdout.read().decode("utf-8")
        
        exit_status = stdout.channel.recv_exit_status()
        self.log.debug(f"Exit status: {exit_status}")
        stdout_lines = [l.strip() for l in out.split("\n") if l.strip()]
        self.log.debug(f"Lines from stdout: {stdout_lines}")
        stderr_lines = [l.strip() for l in err.split("\n") if l.strip()]
        self.log.debug(f"Lines from stderr: {stderr_lines}")

        return stdout_lines + stderr_lines

    def _run_command_as_user(self, command: str, second_user: str, second_pass: str) -> list:
        self.log.debug(f"Executing command: {command} as user {second_user}")
        session = self.client.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command(f'su {second_user} -c "{command}"')
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        time.sleep(1) # needed to wait for remote host to be ready for
        stdin.write(second_pass + '\n')
        stdin.flush()
        out = stdout.read().decode("utf-8")
        
        lines = [l.strip() for l in out.split("\n") if l.strip()]
        self.log.debug(f"Lines from stdout: {lines}")

        return lines

    def _evaluate_output(
        self,
        output: list,
        evaluation: str,
        operator: Optional[str] = None,
        value: Optional[int] = None,
        pattern: Optional[str] = None
    ) -> Union[bool, str]:
        output_len= len(output)
        for index, line in enumerate(output):
            if line != "Password:":
                if evaluation == "NUMERIC_VALUE_COMPARISON":
                    output_number = float(line)
                    expression = f"{output_number} {operator} {value}"
                    self.log.debug(f"Evaluating expression: {expression}")
                    if eval(expression):
                        return True, ""
                    return False, f"Numeric evaluation of expression {expression} failed"
                elif evaluation == "TEXT_PATTERN_MATCH":
                    self.log.debug(f"Evaluating pattern: {pattern} on line '{line}'")
                    if re.search(pattern, line):
                        return True, ""
                    elif index == output_len - 1:
                        return False, f"Pattern {pattern} did not match the output"

    def test_command(
        self,
        command: str,
        evaluation: str,
        second_username: Optional[str] = None,
        second_password: Optional[str] = None,
        comparison_operator: Optional[str] = None,
        comparison_value: Optional[str] = None,
        text_pattern: Optional[str] = None
    ) -> Union[bool, str, int]:
        start = time.time()
        output = []
        try:
            if second_username is not None and second_password is not None:
                output = self._run_command_as_user(command, second_username, second_password)
            else:
                output = self._run_command(command)
            
            status, reason = self._evaluate_output(output, evaluation, comparison_operator, comparison_value, text_pattern)
        except Exception as e:
            self.log.exception(e)
            status, reason = False, f"Failed executing the test: {e}"
        finally:
            return status, reason, int((time.time() - start) * 1000)