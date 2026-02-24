import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import yaml
from flask import Flask, request, jsonify
from notifiers import dispatch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("cmcc-sender")

app = Flask(__name__)

config_path = os.environ.get("CONFIG_PATH", "config.yaml")
logger.info("Loading config from %s", config_path)
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


def check_auth():
    """校验请求鉴权 token，若未配置则跳过。"""
    token = config.get("server", {}).get("auth_token", "")
    if not token:
        return True
    req_token = request.args.get("token") or request.headers.get("Authorization")
    return req_token == token


@app.route("/sms", methods=["POST"])
def receive_sms():
    if not check_auth():
        logger.warning("Unauthorized request from %s", request.remote_addr)
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        logger.warning("Received invalid JSON from %s", request.remote_addr)
        return jsonify({"error": "invalid JSON"}), 400

    missing = [f for f in ("sender", "message", "timestamp") if f not in data]
    if missing:
        logger.warning("Missing fields: %s", ", ".join(missing))
        return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400

    logger.info("Received SMS from %s, message: %s", data.get("sender"), data.get("message"))

    ts = data["timestamp"]
    try:
        ts_val = int(ts)
        if ts_val > 1e12:
            ts_val = ts_val / 1000
        time_conf = config.get("time", {})
        tz_name = time_conf.get("timezone", "Asia/Singapore")
        time_format = time_conf.get("format", "%d/%m/%Y %I:%M:%S %p")
        tz = ZoneInfo(tz_name)
        data["timestamp"] = datetime.fromtimestamp(ts_val, tz=tz).strftime(time_format)
    except (ValueError, TypeError, OSError):
        pass

    results = dispatch(data, config)
    return jsonify({"results": results})


if __name__ == "__main__":
    server_conf = config.get("server", {})
    app.run(
        host=server_conf.get("host", "0.0.0.0"),
        port=server_conf.get("port", 5000),
    )
