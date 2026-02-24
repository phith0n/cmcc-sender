from notifiers import telegram, bark

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
            continue
        try:
            result = module.send(sms_data, notifier_conf)
            results.append(result)
        except Exception as e:
            results.append({
                "platform": name,
                "success": False,
                "error": str(e),
            })

    return results
