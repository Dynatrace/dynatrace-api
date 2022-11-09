import os
import re
from pathlib import Path
import logging

log = logging.getLogger(__name__)

tenant_regex = re.compile(r"\[(.*)\]")


def get_api_url() -> str:
    endpoint = ""
    environment = ""

    base_path = Path(__file__)

    # Only true if running from simulator
    if "remotepluginmodule" not in str(base_path):
        base_path = "/opt" if os.name != "nt" else "C:/Program Files"
        base_path = Path(base_path) / "dynatrace" / "remotepluginmodule" / "agent"

    # Go up one level until the directory name is remotepluginmodule
    while True:
        base_path = base_path.parent
        if base_path.name == "remotepluginmodule":
            extensions_conf = base_path / "agent" / "conf" / "extensions.conf"
            with open(extensions_conf, "r", errors="replace") as f:
                for line in f:
                    if line.startswith("Server "):
                        endpoint = line.split(" ")[1].strip()
                        endpoint = endpoint.replace("/communication", "")
                    if line.startswith("Tenant "):
                        environment = line.split(" ")[1].strip()
            if endpoint and environment:
                api_url = f"{endpoint}/e/{environment}"
                log.info(f"Found API URL: '{api_url}' in '{extensions_conf}'")
                return api_url
            else:
                raise Exception(f"Could not find API URL after reading {extensions_conf}")
        # End of the line
        if base_path.parent == base_path:
            raise Exception("Could not find config directory")
