import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """多渠道通知服务"""
    
    def __init__(self):
        self.smtp_enabled = bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        self.telegram_enabled = bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
        self.webhook_enabled = bool(settings.WEBHOOK_URL)
        self.dingtalk_enabled = bool(getattr(settings, 'DINGTALK_WEBHOOK', None))
        self.feishu_enabled = bool(getattr(settings, 'FEISHU_WEBHOOK', None))
        
        logger.info(f"通知服务初始化: SMTP={self.smtp_enabled}, Telegram={self.telegram_enabled}, "
                   f"Webhook={self.webhook_enabled}, DingTalk={self.dingtalk_enabled}, Feishu={self.feishu_enabled}")
    
    async def send_notification(self, 
                                notification_type: str, 
                                title: str, 
                                message: str,
                                recipients: Optional[List[str]] = None,
                                additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        发送通知
        
        Args:
            notification_type: 通知类型 (email, telegram, webhook, all)
            title: 通知标题
            message: 通知内容
            recipients: 收件人列表（仅邮件通知使用）
            additional_data: 附加数据
            
        Returns:
            字典，键为通知方式，值为是否成功
        """
        results = {}
        
        if notification_type == "email" or notification_type == "all":
            if self.smtp_enabled:
                try:
                    await self._send_email(title, message, recipients)
                    results["email"] = True
                    logger.info(f"邮件通知发送成功: {title}")
                except Exception as e:
                    results["email"] = False
                    logger.error(f"邮件通知发送失败: {e}")
            else:
                results["email"] = False
                logger.warning("邮件通知未配置，跳过发送")
        
        if notification_type == "telegram" or notification_type == "all":
            if self.telegram_enabled:
                try:
                    await self._send_telegram(message)
                    results["telegram"] = True
                    logger.info(f"Telegram通知发送成功: {title}")
                except Exception as e:
                    results["telegram"] = False
                    logger.error(f"Telegram通知发送失败: {e}")
            else:
                results["telegram"] = False
                logger.warning("Telegram通知未配置，跳过发送")
        
        if notification_type == "webhook" or notification_type == "all":
            if self.webhook_enabled:
                try:
                    await self._send_webhook(title, message, additional_data)
                    results["webhook"] = True
                    logger.info(f"Webhook通知发送成功: {title}")
                except Exception as e:
                    results["webhook"] = False
                    logger.error(f"Webhook通知发送失败: {e}")
            else:
                results["webhook"] = False
                logger.warning("Webhook通知未配置，跳过发送")
        
        if notification_type == "dingtalk" or notification_type == "all":
            if self.dingtalk_enabled:
                try:
                    await self._send_dingtalk(title, message)
                    results["dingtalk"] = True
                    logger.info(f"钉钉通知发送成功: {title}")
                except Exception as e:
                    results["dingtalk"] = False
                    logger.error(f"钉钉通知发送失败: {e}")
            else:
                results["dingtalk"] = False
                logger.warning("钉钉通知未配置，跳过发送")
        
        if notification_type == "feishu" or notification_type == "all":
            if self.feishu_enabled:
                try:
                    await self._send_feishu(title, message)
                    results["feishu"] = True
                    logger.info(f"飞书通知发送成功: {title}")
                except Exception as e:
                    results["feishu"] = False
                    logger.error(f"飞书通知发送失败: {e}")
            else:
                results["feishu"] = False
                logger.warning("飞书通知未配置，跳过发送")
        
        if notification_type == "in_app":
            # 应用内通知 - 记录日志即可
            logger.info(f"应用内通知: {title} - {message}")
            results["in_app"] = True
        
        return results
    
    async def _send_email(self, subject: str, body: str, recipients: Optional[List[str]] = None):
        """发送邮件通知"""
        if not recipients:
            recipients = [settings.EMAIL_FROM]  # 如果没有指定收件人，发送给自己
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"[OmniMarket预警] {subject}"
        
        # 邮件正文
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .header {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                .title {{ color: #2c3e50; font-size: 18px; font-weight: bold; }}
                .content {{ padding: 10px; }}
                .footer {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #eee; font-size: 12px; color: #7f8c8d; }}
                .timestamp {{ color: #95a5a6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">🚨 金融监控预警通知</div>
                </div>
                <div class="content">
                    <p><strong>{subject}</strong></p>
                    <p>{body.replace(chr(10), '<br>')}</p>
                </div>
                <div class="footer">
                    <p>发送时间: <span class="timestamp">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span></p>
                    <p>系统: OmniMarket Financial Monitor v{settings.VERSION}</p>
                    <p>此邮件由系统自动发送，请勿直接回复。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # 发送邮件
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    
    async def _send_telegram(self, message: str):
        """发送Telegram通知"""
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": f"🚨 OmniMarket预警通知\n\n{message}",
            "parse_mode": "HTML",
            "disable_notification": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    
    async def _send_webhook(self, title: str, message: str, additional_data: Optional[Dict[str, Any]] = None):
        """发送Webhook通知"""
        payload = {
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "system": "OmniMarket Financial Monitor",
            "version": settings.VERSION
        }
        
        if additional_data:
            payload.update(additional_data)
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"OmniMarket-Financial-Monitor/{settings.VERSION}"
        }
        
        response = requests.post(settings.WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    
    async def _send_dingtalk(self, title: str, message: str):
        """
        发送钉钉群机器人通知
        
        文档: https://open.dingtalk.com/document/robots/custom-robot-access
        """
        webhook_url = getattr(settings, 'DINGTALK_WEBHOOK', None)
        if not webhook_url:
            raise ValueError("钉钉Webhook URL未配置")
        
        # 构造Markdown格式消息
        markdown_text = f"""### 🚨 {title}
        
{message}

---

**发送时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**系统**: OmniMarket Financial Monitor v{settings.VERSION}
"""
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": markdown_text
            },
            "at": {
                "isAtAll": False  # 是否@所有人
            }
        }
        
        # 如果配置了签名密钥,计算签名
        secret = getattr(settings, 'DINGTALK_SECRET', None)
        if secret:
            import time
            import hmac
            import hashlib
            import base64
            import urllib.parse
            
            timestamp = str(round(time.time() * 1000))
            secret_enc = secret.encode('utf-8')
            string_to_sign = f'{timestamp}\n{secret}'.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("errcode") != 0:
            raise Exception(f"钉钉通知发送失败: {result.get('errmsg')}")
    
    async def _send_feishu(self, title: str, message: str):
        """
        发送飞书群机器人通知
        
        文档: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
        """
        webhook_url = getattr(settings, 'FEISHU_WEBHOOK', None)
        if not webhook_url:
            raise ValueError("飞书Webhook URL未配置")
        
        # 构造富文本消息
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🚨 {title}"
                    },
                    "template": "red"  # 红色模板
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": message
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**发送时间**\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**系统版本**\nv{settings.VERSION}"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        # 如果配置了签名密钥,计算签名
        secret = getattr(settings, 'FEISHU_SECRET', None)
        if secret:
            import time
            import hmac
            import hashlib
            import base64
            
            timestamp = str(int(time.time()))
            string_to_sign = f"{timestamp}\n{secret}"
            hmac_code = hmac.new(
                string_to_sign.encode("utf-8"), 
                digestmod=hashlib.sha256
            ).digest()
            sign = base64.b64encode(hmac_code).decode('utf-8')
            
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != 0:
            raise Exception(f"飞书通知发送失败: {result.get('msg')}")
    
    def get_notification_status(self) -> Dict[str, bool]:
        """获取通知服务状态"""
        return {
            "smtp": self.smtp_enabled,
            "telegram": self.telegram_enabled,
            "webhook": self.webhook_enabled,
            "dingtalk": self.dingtalk_enabled,
            "feishu": self.feishu_enabled
        }


# 全局通知服务实例
notification_service = NotificationService()
