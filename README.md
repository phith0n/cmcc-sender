# cmcc-sender

接收手机短信并转发到 Telegram / Bark 等通知平台的服务端程序。

配合 Android 端短信转发应用（如 SmsForwarder）使用，将收到的短信通过 HTTP 接口推送到本服务，再由本服务分发到各通知渠道。

## 快速开始

### Docker 部署（推荐）

```bash
# 准备配置文件
cp config.example.yaml config.yaml
# 编辑 config.yaml，填入你的 token 和 key（见下方配置说明）

# 运行
docker run -d \
  -v ./config.yaml:/app/config.yaml \
  -p 5000:5000 \
  ghcr.io/your-username/cmcc-sender:latest
```

### 本地运行

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml
# 编辑 config.yaml

python app.py
```

## 配置说明

配置文件默认读取当前目录下的 `config.yaml`，可通过环境变量 `CONFIG_PATH` 指定路径：

```bash
CONFIG_PATH=/etc/cmcc-sender/config.yaml python app.py
```

完整配置示例见 `config.example.yaml`：

```yaml
server:
  host: "0.0.0.0"
  port: 5000
  # 可选：接口鉴权 token，为空则不校验
  auth_token: ""

notifiers:
  telegram:
    enabled: true
    bot_token: "your-bot-token"
    chat_id: "your-chat-id"

  bark:
    enabled: true
    server_url: "https://api.day.app/your-key"
```

### Telegram 配置

需要两个参数：`bot_token` 和 `chat_id`。

**获取 bot_token：**

1. 在 Telegram 中搜索 [@BotFather](https://t.me/BotFather) 并打开对话
2. 发送 `/newbot`，按提示设置 bot 名称和用户名
3. 创建完成后 BotFather 会返回一个 token，格式类似 `123456789:ABCdefGhIJKlmNoPQRsTUVwxyz`

**获取 chat_id：**

1. 在 Telegram 中搜索你刚创建的 bot 并点击 **Start**
2. 随便给 bot 发一条消息
3. 在浏览器中访问以下地址（将 `<BOT_TOKEN>` 替换为你的 token）：
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   ```
4. 在返回的 JSON 中找到 `result[0].message.chat.id`，这就是你的 `chat_id`

> 如果需要发送到群组：将 bot 拉入群组，在群里发一条消息，然后同样访问 `getUpdates` 接口获取群组的 `chat_id`（群组 ID 通常为负数）。

### Bark 配置

[Bark](https://github.com/Finb/Bark) 是一个 iOS 推送通知工具。

1. 在 App Store 下载 Bark 应用
2. 打开 Bark，复制应用内显示的推送 URL
3. 将 URL 填入 `server_url`，格式为 `https://api.day.app/your-key`

### 鉴权配置

设置 `auth_token` 后，所有请求必须携带 token 才能通过验证：

```bash
# 通过 query 参数
curl -X POST "http://host:5000/sms?token=your-token" ...

# 或通过 Header
curl -X POST http://host:5000/sms -H "Authorization: your-token" ...
```

## API

### POST /sms

接收短信数据并转发到已启用的通知平台。

**请求体：**

```json
{
  "sender": "10086",
  "message": "您的验证码是 123456",
  "timestamp": "2025-01-01 12:00:00"
}
```

**响应：**

```json
{
  "results": [
    { "platform": "telegram", "success": true },
    { "platform": "bark", "success": true }
  ]
}
```
