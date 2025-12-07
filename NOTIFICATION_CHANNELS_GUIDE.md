# 通知渠道配置指南

OmniMarket 金融监控系统支持 **5种通知渠道**: 邮件、Telegram、钉钉、飞书、自定义Webhook

---

## 📧 邮件通知 (SMTP)

### 配置步骤

1. **获取邮箱配置**:
   - **Gmail**: 需要开启"应用专用密码" (不是账户密码)
   - **QQ邮箱**: 需要开启SMTP服务并获取授权码
   - **163邮箱**: 需要开启SMTP服务并设置客户端授权密码

2. **Gmail示例配置**:
   ```bash
   # .env文件
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-specific-password  # 16位应用专用密码
   EMAIL_FROM=your-email@gmail.com
   ```

3. **QQ邮箱示例配置**:
   ```bash
   SMTP_SERVER=smtp.qq.com
   SMTP_PORT=587
   SMTP_USERNAME=your-qq-number@qq.com
   SMTP_PASSWORD=授权码  # 不是QQ密码,是邮箱授权码
   EMAIL_FROM=your-qq-number@qq.com
   ```

### Gmail应用专用密码获取

1. 访问 https://myaccount.google.com/security
2. 启用"两步验证"
3. 搜索"应用专用密码" → 生成密码 → 选择"邮件"和"Windows计算机"
4. 复制16位密码到 `SMTP_PASSWORD`

---

## 📱 Telegram通知

### 配置步骤

1. **创建Telegram机器人**:
   - 搜索 `@BotFather` 并发送 `/newbot`
   - 设置机器人名称和用户名
   - 获取 `BOT_TOKEN` (格式: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

2. **获取Chat ID**:
   - 搜索 `@userinfobot` 并发送任意消息
   - 机器人会返回你的 `Chat ID` (数字格式,如 `123456789`)
   
   或者:
   - 先启动机器人,给你的机器人发送一条消息
   - 访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - 在返回的JSON中找到 `"chat":{"id": 123456789}`

3. **配置环境变量**:
   ```bash
   # .env文件
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   TELEGRAM_CHAT_ID=123456789
   ```

### 群组通知配置

如果要发送到群组:
1. 将机器人添加到群组
2. 获取群组Chat ID (通常是负数,如 `-1001234567890`)
3. 设置 `TELEGRAM_CHAT_ID=-1001234567890`

---

## 💬 钉钉通知

### 配置步骤

1. **创建自定义机器人**:
   - 打开钉钉群 → 群设置 → 智能群助手 → 添加机器人 → 自定义
   - 选择"自定义关键词"或"加签"安全方式
   - 复制 Webhook 地址

2. **配置环境变量**:
   
   **方式1: 仅Webhook (使用关键词验证)**:
   ```bash
   # .env文件
   DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxxxx
   ```
   
   **方式2: Webhook + 签名 (更安全)**:
   ```bash
   # .env文件
   DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxxxx
   DINGTALK_SECRET=SECxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 安全设置说明

钉钉机器人提供3种安全设置:

1. **自定义关键词**: 消息必须包含设置的关键词(如"预警")
   - 优点: 配置简单
   - 缺点: 安全性较低
   
2. **加签验证** (推荐):
   - 优点: 安全性高,防止恶意调用
   - 需要配置: `DINGTALK_SECRET`
   
3. **IP白名单**: 限制请求来源IP
   - 适用于固定IP服务器

### 测试消息

配置后可通过以下方式测试:

```bash
curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "markdown",
    "markdown": {
      "title": "测试消息",
      "text": "### 🚨 测试消息\n这是一条测试消息"
    }
  }'
```

---

## 🚀 飞书通知

### 配置步骤

1. **创建自定义机器人**:
   - 打开飞书群 → 设置 → 群机器人 → 添加机器人 → 自定义机器人
   - 设置机器人名称和描述
   - 选择"签名校验"安全设置(可选)
   - 复制 Webhook 地址

2. **配置环境变量**:
   
   **方式1: 仅Webhook**:
   ```bash
   # .env文件
   FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
   ```
   
   **方式2: Webhook + 签名 (推荐)**:
   ```bash
   # .env文件
   FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
   FEISHU_SECRET=your-secret-key
   ```

### 消息格式

飞书通知支持富文本卡片消息,包含:
- 🚨 红色标题栏
- Markdown格式内容
- 时间戳和系统版本信息

### 测试消息

```bash
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "测试消息 - OmniMarket"
    }
  }'
```

---

## 🔗 自定义Webhook

### 配置步骤

如果你有自己的webhook服务(如企业微信、Slack、Discord等):

```bash
# .env文件
WEBHOOK_URL=https://your-webhook-service.com/api/notifications
```

### Webhook请求格式

系统会发送POST请求到你的webhook地址,JSON格式:

```json
{
  "title": "价格预警触发",
  "message": "BTC/USDT 突破 50000 USDT",
  "timestamp": "2024-12-07T12:34:56",
  "system": "OmniMarket Financial Monitor",
  "version": "1.0.0",
  "additional_data": {
    "symbol": "BTC/USDT",
    "price": 50000,
    "alert_type": "price_above"
  }
}
```

---

## 🎯 使用示例

### API调用发送通知

```python
from backend.services.notification_service import notification_service

# 单渠道通知
await notification_service.send_notification(
    notification_type="dingtalk",
    title="价格预警",
    message="BTC/USDT 价格突破 50000 USDT"
)

# 多渠道通知
await notification_service.send_notification(
    notification_type="all",  # 发送到所有已配置渠道
    title="重要预警",
    message="多个品种同时触发预警",
    additional_data={
        "symbols": ["BTC/USDT", "ETH/USDT"],
        "alert_count": 5
    }
)
```

### REST API调用

```bash
# 发送测试通知
curl -X POST "http://localhost:8000/api/v1/alerts/test-notification" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "dingtalk",
    "title": "测试通知",
    "message": "这是一条测试消息"
  }'
```

---

## 📊 通知渠道对比

| 渠道 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **邮件** | 正式、可保存、支持HTML | 延迟较高(1-5分钟) | 日报、周报、重要通知 |
| **Telegram** | 实时、支持群组、免费 | 需要科学上网 | 个人用户、国际团队 |
| **钉钉** | 企业级、免费、集成好 | 仅限国内 | 国内企业团队 |
| **飞书** | 现代化、功能丰富、免费 | 仅限国内 | 国内现代团队 |
| **Webhook** | 灵活、可定制 | 需要自己搭建服务 | 企业内部系统集成 |

---

## 🔧 故障排查

### 邮件通知失败

**问题**: `SMTPAuthenticationError`
- **原因**: 密码错误或未开启应用专用密码
- **解决**: 检查是否使用应用专用密码(不是账户密码)

**问题**: 连接超时
- **原因**: 防火墙阻止SMTP端口(587或465)
- **解决**: 检查防火墙设置或使用SSL端口(465)

### Telegram通知失败

**问题**: `Forbidden: bot was blocked by the user`
- **原因**: 机器人被用户屏蔽
- **解决**: 在Telegram中搜索机器人并发送 `/start`

**问题**: `Chat not found`
- **原因**: Chat ID错误
- **解决**: 重新获取Chat ID (使用 `@userinfobot`)

### 钉钉通知失败

**问题**: `errcode: 310000` (关键词不匹配)
- **原因**: 消息中未包含设置的关键词
- **解决**: 
  1. 检查机器人安全设置的关键词
  2. 系统默认包含"预警"、"通知"等关键词
  3. 或改用"加签"验证方式

**问题**: `errcode: 310001` (签名验证失败)
- **原因**: `DINGTALK_SECRET` 配置错误
- **解决**: 检查secret是否正确(以"SEC"开头)

### 飞书通知失败

**问题**: `code: 19021` (签名验证失败)
- **原因**: 签名计算错误或时间戳偏差过大
- **解决**: 检查系统时间是否准确

**问题**: Webhook地址失效
- **原因**: 机器人被删除或重新生成
- **解决**: 重新创建机器人并更新Webhook地址

---

## ⚙️ 高级配置

### 条件通知

根据预警级别选择不同渠道:

```python
# 在 alert_service.py 中
if alert.severity == "critical":
    # 紧急预警: 发送所有渠道
    await notification_service.send_notification(
        notification_type="all",
        title="🚨 紧急预警",
        message=alert.message
    )
elif alert.severity == "high":
    # 高级预警: 钉钉/飞书
    await notification_service.send_notification(
        notification_type="dingtalk",
        title="⚠️ 重要预警",
        message=alert.message
    )
else:
    # 普通预警: 应用内通知
    await notification_service.send_notification(
        notification_type="in_app",
        title="ℹ️ 提醒",
        message=alert.message
    )
```

### 通知限流

避免频繁通知:

```python
from datetime import datetime, timedelta

class NotificationService:
    def __init__(self):
        self.last_notification_time = {}
        self.notification_interval = 300  # 5分钟
    
    async def send_notification(self, ...):
        # 检查是否需要限流
        key = f"{notification_type}:{title}"
        last_time = self.last_notification_time.get(key)
        
        if last_time and (datetime.now() - last_time).seconds < self.notification_interval:
            logger.warning(f"通知限流: {key}")
            return {"throttled": True}
        
        # 发送通知
        result = await self._do_send(...)
        
        # 记录发送时间
        self.last_notification_time[key] = datetime.now()
        
        return result
```

---

## 📚 参考文档

- [钉钉机器人开发文档](https://open.dingtalk.com/document/robots/custom-robot-access)
- [飞书机器人开发文档](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Gmail SMTP配置](https://support.google.com/mail/answer/7126229)

---

## ✅ 完整配置示例

```bash
# .env 完整配置示例

# 邮件通知
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Telegram通知
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl
TELEGRAM_CHAT_ID=123456789

# 钉钉通知
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxxxx
DINGTALK_SECRET=SECxxxxxxxxxxxxx

# 飞书通知
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
FEISHU_SECRET=your-secret

# 自定义Webhook
WEBHOOK_URL=https://your-service.com/webhook
```

配置完成后重启服务即可生效!
