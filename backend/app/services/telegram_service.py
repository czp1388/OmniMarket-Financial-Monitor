# 寰宇多市场金融监控系统 - Telegram机器人服务
import logging
import requests
import asyncio
from typing import List, Dict, Optional
import os
import json

logger = logging.getLogger(__name__)

class TelegramBotService:
    """Telegram机器人通知服务"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_ids = os.getenv('TELEGRAM_CHAT_IDS', '').split(',') if os.getenv('TELEGRAM_CHAT_IDS') else []
        self.is_enabled = bool(self.bot_token and self.chat_ids)
        
        if self.is_enabled:
            logger.info("✅ Telegram机器人服务已启用")
            logger.info(f"📱 配置了 {len(self.chat_ids)} 个聊天ID")
        else:
            logger.warning("⚠️ Telegram机器人服务未配置，请设置环境变量")
    
    async def send_alert_notification(self, alert_data: Dict, chat_ids: Optional[List[str]] = None) -> bool:
        """发送预警通知到Telegram"""
        if not self.is_enabled:
            logger.warning("Telegram服务未配置，跳过发送")
            return False
        
        try:
            message = self._format_alert_message(alert_data)
            target_chat_ids = chat_ids or self.chat_ids
            
            success_count = 0
            for chat_id in target_chat_ids:
                if await self._send_message(chat_id.strip(), message):
                    success_count += 1
            
            logger.info(f"✅ Telegram预警消息发送成功: {success_count}/{len(target_chat_ids)}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"发送Telegram预警消息失败: {e}")
            return False
    
    async def send_system_notification(self, message: str, chat_ids: Optional[List[str]] = None) -> bool:
        """发送系统通知到Telegram"""
        if not self.is_enabled:
            return False
        
        try:
            formatted_message = f"🔔 系统通知:\n{message}"
            target_chat_ids = chat_ids or self.chat_ids
            
            success_count = 0
            for chat_id in target_chat_ids:
                if await self._send_message(chat_id.strip(), formatted_message):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"发送Telegram系统消息失败: {e}")
            return False
    
    async def _send_message(self, chat_id: str, message: str) -> bool:
        """发送单个消息到Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Telegram消息发送成功: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"发送消息到Telegram聊天 {chat_id} 失败: {e}")
            return False
    
    def _format_alert_message(self, alert_data: Dict) -> str:
        """格式化预警消息为Telegram HTML格式"""
        symbol = alert_data.get('symbol', 'Unknown')
        condition = alert_data.get('condition', 'Unknown')
        current_price = alert_data.get('current_price', 0)
        threshold = alert_data.get('threshold', 0)
        message = alert_data.get('message', '')
        triggered_time = alert_data.get('triggered_time', '')
        
        condition_text = {
            'above': '🟢 价格高于',
            'below': '🔴 价格低于', 
            'change_up': '📈 涨幅超过',
            'change_down': '📉 跌幅超过'
        }.get(condition, condition)
        
        # 使用HTML格式，Telegram支持
        return f"""
🚨 <b>金融预警触发</b>

<b>交易对:</b> <code>{symbol}</code>
<b>预警条件:</b> {condition_text} <code>{threshold}{'%' if 'change' in condition else ''}</code>
<b>当前价格:</b> <code>${current_price:,.2f}</code>
<b>触发时间:</b> <code>{triggered_time}</code>
<b>预警信息:</b> {message}

<i>请及时关注市场变化并采取相应措施。</i>

<pre>寰宇多市场金融监控系统 v2.7.0</pre>
        """.strip()
    
    async def get_bot_info(self) -> Dict:
        """获取机器人信息"""
        if not self.is_enabled:
            return {'enabled': False}
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            bot_info = response.json()
            return {
                'enabled': True,
                'bot_username': bot_info['result']['username'],
                'bot_name': f"{bot_info['result']['first_name']} {bot_info['result'].get('last_name', '')}",
                'chat_ids_count': len(self.chat_ids),
                'configured': True
            }
        except Exception as e:
            logger.error(f"获取Telegram机器人信息失败: {e}")
            return {
                'enabled': True,
                'configured': False,
                'error': str(e)
            }
    
    def get_config_status(self) -> Dict:
        """获取配置状态"""
        return {
            'enabled': self.is_enabled,
            'bot_token_configured': bool(self.bot_token),
            'chat_ids_configured': bool(self.chat_ids),
            'chat_ids_count': len(self.chat_ids)
        }

# 创建全局Telegram服务实例
telegram_service = TelegramBotService()
