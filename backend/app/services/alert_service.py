# 寰宇多市场金融监控系统 - 预警服务模块
from typing import Dict, List, Callable
import asyncio
from datetime import datetime
import json

class AlertRule:
    def __init__(self, id: str, name: str, condition: str, target: str, enabled: bool = True):
        self.id = id
        self.name = name
        self.condition = condition  # 例如: "price > 50000"
        self.target = target  # 例如: "binance:BTC/USDT"
        self.enabled = enabled
        self.last_triggered = None
    
    def evaluate(self, current_price: float) -> bool:
        """评估预警条件"""
        try:
            # 简单的条件评估（生产环境需要更安全的实现）
            return eval(self.condition, {"price": current_price})
        except:
            return False

class AlertService:
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.is_monitoring = False
        self.alert_handlers: List[Callable] = []
    
    def add_rule(self, rule: AlertRule):
        """添加预警规则"""
        self.rules[rule.id] = rule
    
    def remove_rule(self, rule_id: str):
        """移除预警规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def add_alert_handler(self, handler: Callable):
        """添加预警处理器"""
        self.alert_handlers.append(handler)
    
    async def trigger_alert(self, rule: AlertRule, current_price: float):
        """触发预警"""
        rule.last_triggered = datetime.now()
        alert_message = {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "target": rule.target,
            "current_price": current_price,
            "condition": rule.condition,
            "triggered_at": rule.last_triggered.isoformat()
        }
        
        # 调用所有预警处理器
        for handler in self.alert_handlers:
            try:
                handler(alert_message)
            except Exception as e:
                print(f"预警处理器错误: {e}")
        
        print(f"🚨 预警触发: {rule.name} - {rule.target} 价格: {current_price}")
    
    async def start_monitoring(self, data_service):
        """开始监控"""
        self.is_monitoring = True
        print("🔔 启动预警监控服务...")
        
        while self.is_monitoring:
            for rule_id, rule in self.rules.items():
                if not rule.enabled:
                    continue
                
                # 解析目标 (exchange:symbol)
                try:
                    exchange, symbol = rule.target.split(":")
                    current_data = data_service.get_price(exchange, symbol)
                    
                    if current_data and 'price' in current_data:
                        current_price = current_data['price']
                        
                        if rule.evaluate(current_price):
                            await self.trigger_alert(rule, current_price)
                
                except Exception as e:
                    print(f"预警规则评估失败 {rule_id}: {e}")
            
            # 每10秒检查一次
            await asyncio.sleep(10)
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False

# 全局预警服务实例
alert_service = AlertService()

# 默认预警处理器 - 控制台输出
def console_alert_handler(alert_message):
    print(f"💥 预警: {alert_message['rule_name']}")
    print(f"   目标: {alert_message['target']}")
    print(f"   价格: {alert_message['current_price']}")
    print(f"   条件: {alert_message['condition']}")

alert_service.add_alert_handler(console_alert_handler)
