import logging
from notifiers import telegram, bark

logger = logging.getLogger("cmcc-sender.dispatch")

_NOTIFIERS = {
    "telegram": telegram,
    "bark": bark,
}


def dispatch(sms_data, config):
    """根据配置将短信分发到各已启用的通知平台。

    返回各平台推送结果列表。
    """
    results = []
    notifiers_config = config.get("notifiers", {})

    for name, module in _NOTIFIERS.items():
        notifier_conf = notifiers_config.get(name, {})
        if not notifier_conf.get("enabled", False):
            logger.debug("%s is disabled, skipping", name)
            continue
        try:
            logger.info("Sending to %s ...", name)
            result = module.send(sms_data, notifier_conf)
            logger.info("%s: success", name)
            results.append(result)
        except Exception as e:
            logger.error("%s: failed - %s", name, e)
            results.append({
                "platform": name,
                "success": False,
                "error": str(e),
            })

    return results
