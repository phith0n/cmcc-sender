import logging
import requests
from urllib.parse import quote

logger = logging.getLogger("cmcc-sender.bark")


def send(sms_data, config):
    """通过 Bark API 发送短信通知。"""
    server_url = config["server_url"].rstrip("/")

    title = f"📱 来自 {sms_data['sender']} 的短信"
    body = (
        f"时间: {sms_data['timestamp']}\n"
        f"内容: {sms_data['message']}"
    )

    url = f"{server_url}/{quote(title)}/{quote(body)}"

    logger.info("POST %s", server_url + "/...")
    resp = requests.get(url, timeout=10)
    if not resp.ok:
        logger.error("Bark responded %s: %s", resp.status_code, resp.text)
    resp.raise_for_status()
    return {"platform": "bark", "success": True}
