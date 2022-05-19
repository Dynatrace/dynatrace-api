import os
import time
import logging
import paramiko
from typing import Optional, Union


class SFTPClient:
    def __init__(
        self,
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
        self.client: Optional[paramiko.SFTPClient] = None
        self.transport: Optional[paramiko.Transport] = None
        self.connect_time = time.time()

    def __enter__(self) -> "SFTPClient":
        try:
            self.transport = paramiko.Transport((self.hostname, self.port))
            if self.key is not None:
                with open(file=self.key, mode="r") as f:
                    self.key = paramiko.RSAKey.from_private_key(f, self.passphrase)
            self.transport.connect(None, self.username, self.password, self.key)
            self.client = paramiko.SFTPClient.from_transport(self.transport)
        except Exception as e:
            self.log.exception(e)
            self.connected = False
        else:
            self.connected = True
        finally:
            self.connect_time = int((time.time() - self.connect_time)*1000)

        return self

    def __exit__(self, e_type, e_value, e_trace) -> bool:
        self.connected = False
        if self.client is not None:
            self.client.close()
        if self.transport is not None:
            self.transport.close()

        if e_type is not None:
            self.log.exception(e_type, e_value, e_trace)
        
        return True
    
    def test_connect(self) -> Union[bool, str, int]:
        if self.connected:
            return True, "", self.connect_time
        return False, f"Error connecting to host {self.hostname}", 0

    def test_read(self, remote_dir: str) -> Union[bool, str, int]:
        start = time.time()
        try:
            self.client.chdir(remote_dir)
            self.client.listdir()
        except Exception as e:
            self.log.exception(e)
            return False, f"Could not read directory {remote_dir}", 0
        else:
            return True, "", int((time.time() - start)*1000)

    def test_put(self, local_file: str, remote_dir: str) -> Union[bool, str, int]:
        start = time.time()
        if os.path.getsize(local_file) > 100_000:
            return False, "File size too large. Must be under 100KBs", 0
        
        try:
            filename = local_file.split(os.path.sep)[-1]
            dest = f"{remote_dir}/{filename}"
            self.log.info(f'Uploading local file "{local_file}" to remote destination "{dest}"')
            self.client.put(local_file, dest)
        except Exception as e:
            self.log.exception(e)
            return False, f"Error uploading file {local_file} to {dest}", 0
        else:
            return True, "", int((time.time()-start)*1000)