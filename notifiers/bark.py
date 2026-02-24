import logging
import requests

logger = logging.getLogger("cmcc-sender.bark")


def send(sms_data, config):
    """通过 Bark API 发送短信通知。"""
    server_url = config["server_url"].rstrip("/")

    title = f"📱 来自 {sms_data['sender']} 的短信"
    body = (
        f"时间: {sms_data['timestamp']}\n"
        f"内容: {sms_data['message']}"
    )

    logger.info("POST %s", server_url)
    resp = requests.post(server_url, json={
        "title": title,
        "body": body,
    }, timeout=10)
    if not resp.ok:
        logger.error("Bark responded %s: %s", resp.status_code, resp.text)
    resp.raise_for_status()
    return {"platform": "bark", "success": True}
