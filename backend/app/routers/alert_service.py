import asyncio
import smtplib
from email.mime.text import MimeText
from datetime import datetime

class AlertService:
    def __init__(self):
        self.active_alerts = []
        
    async def check_price_alerts(self, current_prices):
        """检查价格是否触发预警"""
        triggered_alerts = []
        
        for alert in self.active_alerts:
            if not alert["active"]:
                continue
                
            symbol = alert["symbol"]
            if symbol in current_prices:
                current_price = current_prices[symbol]
                
                if (alert["condition"] == "above" and current_price >= alert["price"]) or \
                   (alert["condition"] == "below" and current_price <= alert["price"]):
                    
                    triggered_alerts.append(alert)
                    alert["active"] = False  # 触发后禁用预警
                    
                    # 这里可以添加发送邮件或通知的逻辑
                    print(f"🚨 预警触发: {symbol} {alert['condition']} {alert['price']}, 当前价格: {current_price}")
        
        return triggered_alerts

alert_service = AlertService()
