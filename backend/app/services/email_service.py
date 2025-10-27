# 寰宇多市场金融监控系统 - 邮件通知服务
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import os
import json

logger = logging.getLogger(__name__)

class EmailConfig:
    """邮件配置类"""
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.use_tls = os.getenv('USE_TLS', 'True').lower() == 'true'
        
    def is_configured(self) -> bool:
        """检查邮件配置是否完整"""
        return all([
            self.smtp_server,
            self.sender_email,
            self.sender_password
        ])

class EmailNotificationService:
    """邮件通知服务"""
    
    def __init__(self):
        self.config = EmailConfig()
        self.is_enabled = self.config.is_configured()
        
        if self.is_enabled:
            logger.info("✅ 邮件通知服务已启用")
        else:
            logger.warning("⚠️ 邮件通知服务未配置，请设置环境变量")
    
    async def send_alert_notification(self, alert_data: Dict, recipients: List[str]) -> bool:
        """发送预警通知邮件"""
        if not self.is_enabled:
            logger.warning("邮件服务未配置，跳过发送")
            return False
        
        try:
            subject = f"🚨 金融预警触发 - {alert_data.get('symbol', 'Unknown')}"
            
            # 创建HTML邮件内容
            html_content = self._create_alert_html(alert_data)
            text_content = self._create_alert_text(alert_data)
            
            # 发送邮件
            success_count = 0
            for recipient in recipients:
                if await self._send_email(recipient, subject, text_content, html_content):
                    success_count += 1
            
            logger.info(f"✅ 预警邮件发送成功: {success_count}/{len(recipients)}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"发送预警邮件失败: {e}")
            return False
    
    async def send_system_notification(self, subject: str, message: str, recipients: List[str]) -> bool:
        """发送系统通知邮件"""
        if not self.is_enabled:
            return False
        
        try:
            html_content = f"""
            <html>
                <body>
                    <h2>系统通知</h2>
                    <p>{message}</p>
                    <hr>
                    <p><small>来自寰宇多市场金融监控系统</small></p>
                </body>
            </html>
            """
            
            success_count = 0
            for recipient in recipients:
                if await self._send_email(recipient, subject, message, html_content):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"发送系统邮件失败: {e}")
            return False
    
    async def _send_email(self, recipient: str, subject: str, text_content: str, html_content: str) -> bool:
        """发送单个邮件"""
        try:
            # 创建邮件消息
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.sender_email
            msg['To'] = recipient
            
            # 添加文本和HTML版本
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.sender_email, self.config.sender_password)
                server.send_message(msg)
            
            logger.info(f"✅ 邮件发送成功: {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件到 {recipient} 失败: {e}")
            return False
    
    def _create_alert_html(self, alert_data: Dict) -> str:
        """创建预警HTML邮件内容"""
        symbol = alert_data.get('symbol', 'Unknown')
        condition = alert_data.get('condition', 'Unknown')
        current_price = alert_data.get('current_price', 0)
        threshold = alert_data.get('threshold', 0)
        message = alert_data.get('message', '')
        triggered_time = alert_data.get('triggered_time', '')
        
        condition_text = {
            'above': '价格高于',
            'below': '价格低于', 
            'change_up': '涨幅超过',
            'change_down': '跌幅超过'
        }.get(condition, condition)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .alert-header {{ background: #ff4444; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .alert-details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .price {{ font-size: 24px; font-weight: bold; color: #ff4444; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="alert-header">
                <h1>🚨 金融预警触发</h1>
            </div>
            <div class="content">
                <h2>{symbol} 预警通知</h2>
                <div class="alert-details">
                    <p><strong>预警条件:</strong> {condition_text} {threshold}{'%' if 'change' in condition else ''}</p>
                    <p><strong>当前价格:</strong> <span class="price">${current_price:,.2f}</span></p>
                    <p><strong>触发时间:</strong> {triggered_time}</p>
                    <p><strong>预警信息:</strong> {message}</p>
                </div>
                <p>请及时关注市场变化并采取相应措施。</p>
            </div>
            <div class="footer">
                <p>此邮件由寰宇多市场金融监控系统自动发送</p>
                <p>系统版本: 专业版 v2.6.0 | 邮件通知服务</p>
            </div>
        </body>
        </html>
        """
    
    def _create_alert_text(self, alert_data: Dict) -> str:
        """创建预警文本邮件内容"""
        symbol = alert_data.get('symbol', 'Unknown')
        condition = alert_data.get('condition', 'Unknown')
        current_price = alert_data.get('current_price', 0)
        threshold = alert_data.get('threshold', 0)
        message = alert_data.get('message', '')
        triggered_time = alert_data.get('triggered_time', '')
        
        condition_text = {
            'above': '价格高于',
            'below': '价格低于',
            'change_up': '涨幅超过', 
            'change_down': '跌幅超过'
        }.get(condition, condition)
        
        return f"""
🚨 金融预警触发通知

交易对: {symbol}
预警条件: {condition_text} {threshold}{'%' if 'change' in condition else ''}
当前价格: ${current_price:,.2f}
触发时间: {triggered_time}
预警信息: {message}

请及时关注市场变化并采取相应措施。

--
寰宇多市场金融监控系统 专业版 v2.6.0
邮件通知服务
        """
    
    def get_config_status(self) -> Dict:
        """获取邮件配置状态"""
        return {
            'enabled': self.is_enabled,
            'smtp_server': self.config.smtp_server,
            'sender_email': self.config.sender_email,
            'configured': self.config.is_configured()
        }

# 创建全局邮件服务实例
email_service = EmailNotificationService()
