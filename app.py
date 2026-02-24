import os
from datetime import datetime, timezone, timedelta
import yaml
from flask import Flask, request, jsonify
from notifiers import dispatch

app = Flask(__name__)

config_path = os.environ.get("CONFIG_PATH", "config.yaml")
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
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid JSON"}), 400

    missing = [f for f in ("sender", "message", "timestamp") if f not in data]
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400

    ts = data["timestamp"]
    try:
        ts_val = int(ts)
        if ts_val > 1e12:
            ts_val = ts_val / 1000
        time_conf = config.get("time", {})
        utc_offset = time_conf.get("utc_offset", 8)
        time_format = time_conf.get("format", "%d/%m/%Y %H:%M:%S")
        tz = timezone(timedelta(hours=utc_offset))
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
