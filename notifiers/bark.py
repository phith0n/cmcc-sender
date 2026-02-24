import requests
from urllib.parse import quote


def send(sms_data, config):
    """通过 Bark API 发送短信通知。"""
    server_url = config["server_url"].rstrip("/")

    title = f"📱 来自 {sms_data['sender']} 的短信"
    body = (
        f"时间: {sms_data['timestamp']}\n"
        f"内容: {sms_data['message']}"
    )

    url = f"{server_url}/{quote(title)}/{quote(body)}"

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return {"platform": "bark", "success": True}
