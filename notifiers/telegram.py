import requests


def send(sms_data, config):
    """通过 Telegram Bot API 发送短信通知。"""
    bot_token = config["bot_token"]
    chat_id = config["chat_id"]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    text = (
        f"📱 收到新短信\n"
        f"发送者: {sms_data['sender']}\n"
        f"时间: {sms_data['timestamp']}\n"
        f"内容: {sms_data['message']}"
    )

    resp = requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
    }, timeout=10)
    resp.raise_for_status()
    return {"platform": "telegram", "success": True}
