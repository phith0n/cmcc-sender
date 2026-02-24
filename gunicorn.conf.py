import os
import yaml

config_path = os.environ.get("CONFIG_PATH", "config.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    server_conf = config.get("server", {})
    host = server_conf.get("host", "0.0.0.0")
    port = server_conf.get("port", 5000)
except Exception:
    host = "0.0.0.0"
    port = 5000

bind = f"{host}:{port}"
