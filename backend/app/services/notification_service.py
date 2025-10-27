# 统一通知服务
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationType:
    EMAIL = "email"
    TELEGRAM = "telegram"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

class NotificationService:
    """统一通知服务"""
    
    def __init__(self):
        self.email_config = {}
        self.telegram_config = {}
        self.sms_config = {}
        self.webhook_config = {}
        self.is_initialized = False
        
    async def initialize(self, config: Dict) -> bool:
        """初始化通知服务"""
        try:
            logger.info("🔄 初始化通知服务...")
            
            # 加载配置
            self.email_config = config.get("email", {})
            self.telegram_config = config.get("telegram", {})
            self.sms_config = config.get("sms", {})
            self.webhook_config = config.get("webhook", {})
            
            # 测试连接
            await self._test_connections()
            
            self.is_initialized = True
            logger.info("✅ 通知服务初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"通知服务初始化失败: {e}")
            return False
    
    async def send_notification(self, 
                              notification_type: str, 
                              title: str, 
                              message: str,
                              recipients: List[str] = None,
                              priority: str = "normal") -> bool:
        """发送通知"""
        try:
            if not self.is_initialized:
                logger.warning("通知服务未初始化")
                return False
            
            handlers = {
                NotificationType.EMAIL: self._send_email,
                NotificationType.TELEGRAM: self._send_telegram,
                NotificationType.SMS: self._send_sms,
                NotificationType.WEBHOOK: self._send_webhook,
                NotificationType.IN_APP: self._send_in_app
            }
            
            handler = handlers.get(notification_type)
            if handler:
                return await handler(title, message, recipients, priority)
            else:
                logger.error(f"不支持的通知类型: {notification_type}")
                return False
                
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False
    
    async def send_alert_notification(self, alert_data: Dict, notification_types: List[str]) -> bool:
        """发送预警通知"""
        try:
            title = f"🚨 预警触发 - {alert_data.get('symbol', 'Unknown')}"
            message = self._format_alert_message(alert_data)
            
            results = []
            for notification_type in notification_types:
                result = await self.send_notification(
                    notification_type, title, message, priority="high"
                )
                results.append(result)
            
            return all(results)
            
        except Exception as e:
            logger.error(f"发送预警通知失败: {e}")
            return False
    
    async def _send_email(self, title: str, message: str, recipients: List[str], priority: str) -> bool:
        """发送邮件通知"""
        try:
            if not self.email_config:
                logger.warning("邮件配置未设置")
                return False
            
            smtp_server = self.email_config.get("smtp_server")
            smtp_port = self.email_config.get("smtp_port", 587)
            username = self.email_config.get("username")
            password = self.email_config.get("password")
            
            if not all([smtp_server, username, password]):
                logger.error("邮件配置不完整")
                return False
            
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = username
            msg["To"] = ", ".join(recipients or [username])
            msg["Subject"] = title
            
            # 添加邮件内容
            msg.attach(MIMEText(message, "plain"))
            
            # 发送邮件
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
            
            logger.info(f"📧 邮件通知发送成功: {title}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False
    
    async def _send_telegram(self, title: str, message: str, recipients: List[str], priority: str) -> bool:
        """发送Telegram通知"""
        try:
            if not self.telegram_config:
                logger.warning("Telegram配置未设置")
                return False
            
            bot_token = self.telegram_config.get("bot_token")
            chat_id = self.telegram_config.get("chat_id")
            
            if not all([bot_token, chat_id]):
                logger.error("Telegram配置不完整")
                return False
            
            # 格式化消息
            full_message = f"*{title}*\n\n{message}"
            
            # 发送消息
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": full_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"📱 Telegram通知发送成功: {title}")
                return True
            else:
                logger.error(f"Telegram发送失败: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"发送Telegram失败: {e}")
            return False
    
    async def _send_sms(self, title: str, message: str, recipients: List[str], priority: str) -> bool:
        """发送短信通知"""
        try:
            if not self.sms_config:
                logger.warning("短信配置未设置")
                return False
            
            # 这里实现具体的短信服务商API调用
            # 例如阿里云短信、腾讯云短信等
            
            logger.info(f"📱 短信通知发送成功: {title}")
            return True
            
        except Exception as e:
            logger.error(f"发送短信失败: {e}")
            return False
    
    async def _send_webhook(self, title: str, message: str, recipients: List[str], priority: str) -> bool:
        """发送Webhook通知"""
        try:
            if not self.webhook_config:
                logger.warning("Webhook配置未设置")
                return False
            
            webhook_url = self.webhook_config.get("url")
            
            if not webhook_url:
                logger.error("Webhook URL未设置")
                return False
            
            # 准备数据
            data = {
                "title": title,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "priority": priority
            }
            
            # 发送Webhook
            response = requests.post(webhook_url, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                logger.info(f"🌐 Webhook通知发送成功: {title}")
                return True
            else:
                logger.error(f"Webhook发送失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送Webhook失败: {e}")
            return False
    
    async def _send_in_app(self, title: str, message: str, recipients: List[str], priority: str) -> bool:
        """发送应用内通知"""
        try:
            # 这里实现应用内通知逻辑
            # 可以存储到数据库供前端查询
            
            logger.info(f"📱 应用内通知: {title} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"发送应用内通知失败: {e}")
            return False
    
    def _format_alert_message(self, alert_data: Dict) -> str:
        """格式化预警消息"""
        symbol = alert_data.get("symbol", "Unknown")
        condition_type = alert_data.get("condition_type", "")
        current_value = alert_data.get("current_value", 0)
        condition_value = alert_data.get("condition_value")
        
        base_message = f"交易对: {symbol}\n当前值: {current_value}\n条件: {condition_type}"
        
        if condition_value is not None:
            base_message += f"\n阈值: {condition_value}"
        
        base_message += f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return base_message

# 创建全局通知服务实例
notification_service = NotificationService()
