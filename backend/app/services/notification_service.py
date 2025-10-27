"""
通知服务 - 支持邮件和Telegram通知
"""
import logging
import smtplib
import aiohttp
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        self.is_initialized = False
        self.email_enabled = False
        self.telegram_enabled = False
        
        # 配置从环境变量读取
        self.smtp_config = {
            "host": os.getenv("SMTP_HOST", "smtp.qq.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("FROM_EMAIL", "")
        }
        
        self.telegram_config = {
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
        }
    
    async def initialize(self):
        """初始化通知服务"""
        try:
            logger.info("🔄 初始化通知服务...")
            
            # 检查邮件配置
            if (self.smtp_config["username"] and self.smtp_config["password"]):
                self.email_enabled = True
                logger.info("✅ 邮件通知已启用")
            else:
                logger.warning("⚠️ 邮件通知未配置")
            
            # 检查Telegram配置
            if (self.telegram_config["bot_token"] and self.telegram_config["chat_id"]):
                self.telegram_enabled = True
                logger.info("✅ Telegram通知已启用")
            else:
                logger.warning("⚠️ Telegram通知未配置")
            
            self.is_initialized = True
            logger.info("✅ 通知服务初始化完成")
            
        except Exception as e:
            logger.error(f"通知服务初始化失败: {e}")
    
    async def send_email(self, to_email: str, subject: str, content: str, is_html: bool = False) -> Dict:
        """发送邮件通知"""
        if not self.email_enabled:
            return {"success": False, "message": "邮件通知未启用"}
        
        try:
            # 创建邮件消息
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config["from_email"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加邮件内容
            if is_html:
                msg.attach(MIMEText(content, 'html'))
            else:
                msg.attach(MIMEText(content, 'plain'))
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"]) as server:
                server.starttls()  # 启用安全连接
                server.login(self.smtp_config["username"], self.smtp_config["password"])
                server.send_message(msg)
            
            logger.info(f"📧 邮件发送成功: {to_email} - {subject}")
            return {"success": True, "message": "邮件发送成功"}
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return {"success": False, "message": f"邮件发送失败: {str(e)}"}
    
    async def send_telegram(self, message: str, parse_mode: str = "HTML") -> Dict:
        """发送Telegram通知"""
        if not self.telegram_enabled:
            return {"success": False, "message": "Telegram通知未启用"}
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            
            payload = {
                "chat_id": self.telegram_config["chat_id"],
                "text": message,
                "parse_mode": parse_mode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        logger.info("📱 Telegram消息发送成功")
                        return {"success": True, "message": "Telegram消息发送成功"}
                    else:
                        error_msg = result.get("description", "未知错误")
                        logger.error(f"Telegram发送失败: {error_msg}")
                        return {"success": False, "message": f"Telegram发送失败: {error_msg}"}
                        
        except Exception as e:
            logger.error(f"Telegram发送异常: {e}")
            return {"success": False, "message": f"Telegram发送异常: {str(e)}"}
    
    async def send_market_alert(self, symbol: str, price: float, change_percent: float, alert_type: str = "price_alert") -> Dict:
        """发送市场警报"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建消息内容
        if alert_type == "price_alert":
            direction = "上涨" if change_percent > 0 else "下跌"
            email_subject = f"🚨 股价警报 - {symbol}"
            email_content = f"""
            <h2>🚨 股价波动警报</h2>
            <p><strong>股票代码:</strong> {symbol}</p>
            <p><strong>当前价格:</strong> {price} 元</p>
            <p><strong>涨跌幅:</strong> {change_percent}%</p>
            <p><strong>方向:</strong> {direction}</p>
            <p><strong>时间:</strong> {timestamp}</p>
            <hr>
            <p><em>来自 OmniMarket 金融监控系统</em></p>
            """
            
            telegram_message = f"""
🚨 <b>股价波动警报</b>

📈 <b>股票代码:</b> {symbol}
💰 <b>当前价格:</b> {price} 元
📊 <b>涨跌幅:</b> {change_percent}%
🎯 <b>方向:</b> {direction}
⏰ <b>时间:</b> {timestamp}

<em>来自 OmniMarket 金融监控系统</em>
            """
        
        # 发送通知
        results = {}
        
        if self.email_enabled:
            # 这里可以配置接收警报的邮箱
            admin_email = os.getenv("ADMIN_EMAIL", self.smtp_config["from_email"])
            results["email"] = await self.send_email(admin_email, email_subject, email_content, is_html=True)
        
        if self.telegram_enabled:
            results["telegram"] = await self.send_telegram(telegram_message)
        
        return results
    
    async def send_system_alert(self, title: str, message: str, level: str = "info") -> Dict:
        """发送系统警报"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        level_icons = {
            "info": "ℹ️",
            "warning": "⚠️", 
            "error": "❌",
            "success": "✅"
        }
        
        icon = level_icons.get(level, "📢")
        
        email_subject = f"{icon} 系统通知 - {title}"
        email_content = f"""
        <h2>{icon} 系统通知</h2>
        <p><strong>标题:</strong> {title}</p>
        <p><strong>级别:</strong> {level}</p>
        <p><strong>内容:</strong> {message}</p>
        <p><strong>时间:</strong> {timestamp}</p>
        <hr>
        <p><em>来自 OmniMarket 金融监控系统</em></p>
        """
        
        telegram_message = f"""
{icon} <b>系统通知</b>

📢 <b>标题:</b> {title}
🎚️ <b>级别:</b> {level}
📝 <b>内容:</b> {message}
⏰ <b>时间:</b> {timestamp}

<em>来自 OmniMarket 金融监控系统</em>
        """
        
        # 发送通知
        results = {}
        
        if self.email_enabled:
            admin_email = os.getenv("ADMIN_EMAIL", self.smtp_config["from_email"])
            results["email"] = await self.send_email(admin_email, email_subject, email_content, is_html=True)
        
        if self.telegram_enabled:
            results["telegram"] = await self.send_telegram(telegram_message)
        
        return results
    
    def get_status(self) -> Dict:
        """获取通知服务状态"""
        return {
            "initialized": self.is_initialized,
            "email_enabled": self.email_enabled,
            "telegram_enabled": self.telegram_enabled,
            "smtp_config": {
                "host": self.smtp_config["host"],
                "port": self.smtp_config["port"],
                "username_set": bool(self.smtp_config["username"]),
                "from_email": self.smtp_config["from_email"]
            },
            "telegram_config": {
                "bot_token_set": bool(self.telegram_config["bot_token"]),
                "chat_id_set": bool(self.telegram_config["chat_id"])
            }
        }

# 创建全局通知服务实例
notification_service = NotificationService()
