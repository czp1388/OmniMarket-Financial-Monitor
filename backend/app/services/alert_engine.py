# 增强版预警引擎
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from models.alert_models import AlertConditionType, AlertStatus

logger = logging.getLogger(__name__)

class EnhancedAlertEngine:
    def __init__(self):
        self.alert_rules = {}
        self.alert_history = []
        self.rule_counter = 0
        self.is_evaluating = False
        
    async def add_alert_rule(self, rule_data: Dict) -> int:
        """添加预警规则"""
        try:
            self.rule_counter += 1
            rule_id = self.rule_counter
            
            rule = {
                "id": rule_id,
                "name": rule_data["name"],
                "symbol": rule_data["symbol"],
                "condition_type": rule_data["condition_type"],
                "condition_value": rule_data.get("condition_value"),
                "condition_params": rule_data.get("condition_params", {}),
                "interval": rule_data.get("interval", "1h"),
                "enabled": rule_data.get("enabled", True),
                "status": AlertStatus.ACTIVE,
                "created_at": datetime.now(),
                "triggered_count": 0,
                "notification_types": rule_data.get("notification_types", ["in_app"])
            }
            
            self.alert_rules[rule_id] = rule
            logger.info(f"✅ 添加预警规则: {rule['name']} (ID: {rule_id})")
            return rule_id
            
        except Exception as e:
            logger.error(f"添加预警规则失败: {e}")
            return -1
    
    async def evaluate_alert_conditions(self, symbol: str, market_data: Dict, indicators: Dict = None) -> List[Dict]:
        """评估预警条件"""
        triggered_alerts = []
        
        try:
            current_price = market_data.get("close_price")
            volume = market_data.get("volume")
            
            for rule_id, rule in self.alert_rules.items():
                if not rule["enabled"] or rule["symbol"] != symbol:
                    continue
                    
                if await self._check_single_condition(rule, current_price, volume, indicators):
                    triggered_alerts.append(rule)
                    await self._record_alert_trigger(rule, current_price, market_data)
                    
        except Exception as e:
            logger.error(f"评估预警条件异常: {e}")
            
        return triggered_alerts
    
    async def _check_single_condition(self, rule: Dict, current_price: float, volume: float, indicators: Dict) -> bool:
        """检查单个预警条件"""
        condition_type = rule["condition_type"]
        condition_value = rule["condition_value"]
        
        try:
            if condition_type == AlertConditionType.PRICE_ABOVE:
                return current_price > condition_value
                
            elif condition_type == AlertConditionType.PRICE_BELOW:
                return current_price < condition_value
                
            elif condition_type == AlertConditionType.RSI_OVERBOUGHT:
                if indicators and "RSI" in indicators:
                    rsi_values = indicators["RSI"]
                    if rsi_values and rsi_values[-1] is not None:
                        return rsi_values[-1] > (condition_value or 70)
                return False
                
            elif condition_type == AlertConditionType.RSI_OVERSOLD:
                if indicators and "RSI" in indicators:
                    rsi_values = indicators["RSI"]
                    if rsi_values and rsi_values[-1] is not None:
                        return rsi_values[-1] < (condition_value or 30)
                return False
                
            elif condition_type == AlertConditionType.MACD_CROSSOVER:
                if indicators and "MACD" in indicators:
                    macd_data = indicators["MACD"]
                    if (len(macd_data["macd"]) >= 2 and 
                        len(macd_data["signal"]) >= 2):
                        # 检查MACD线上穿信号线
                        prev_macd = macd_data["macd"][-2]
                        curr_macd = macd_data["macd"][-1]
                        prev_signal = macd_data["signal"][-2]
                        curr_signal = macd_data["signal"][-1]
                        
                        if (prev_macd is not None and curr_macd is not None and
                            prev_signal is not None and curr_signal is not None):
                            return (prev_macd < prev_signal and 
                                   curr_macd > curr_signal)
                return False
                
            elif condition_type == AlertConditionType.VOLUME_SURGE:
                if volume and condition_value:
                    # 这里需要历史成交量数据来比较，简化实现
                    return volume > condition_value
                return False
                
            return False
            
        except Exception as e:
            logger.error(f"检查预警条件失败: {e}")
            return False
    
    async def _record_alert_trigger(self, rule: Dict, current_price: float, market_data: Dict):
        """记录预警触发"""
        try:
            rule["triggered_count"] += 1
            
            alert_record = {
                "id": len(self.alert_history) + 1,
                "alert_rule_id": rule["id"],
                "symbol": rule["symbol"],
                "condition_type": rule["condition_type"],
                "triggered_value": current_price,
                "condition_value": rule["condition_value"],
                "message": self._generate_alert_message(rule, current_price),
                "triggered_at": datetime.now(),
                "market_data": market_data
            }
            
            self.alert_history.append(alert_record)
            logger.info(f"🚨 预警触发: {alert_record['message']}")
            
            # 发送通知
            await self._send_notifications(rule, alert_record)
            
        except Exception as e:
            logger.error(f"记录预警触发失败: {e}")
    
    def _generate_alert_message(self, rule: Dict, current_value: float) -> str:
        """生成预警消息"""
        symbol = rule["symbol"]
        condition_type = rule["condition_type"]
        condition_value = rule["condition_value"]
        
        messages = {
            AlertConditionType.PRICE_ABOVE: f"{symbol} 价格突破 {condition_value}，当前价格: {current_value}",
            AlertConditionType.PRICE_BELOW: f"{symbol} 价格跌破 {condition_value}，当前价格: {current_value}",
            AlertConditionType.RSI_OVERBOUGHT: f"{symbol} RSI超买 ({current_value:.1f})",
            AlertConditionType.RSI_OVERSOLD: f"{symbol} RSI超卖 ({current_value:.1f})",
            AlertConditionType.MACD_CROSSOVER: f"{symbol} MACD金叉信号",
            AlertConditionType.MACD_CROSSUNDER: f"{symbol} MACD死叉信号",
            AlertConditionType.VOLUME_SURGE: f"{symbol} 成交量异动"
        }
        
        return messages.get(condition_type, f"{symbol} 预警触发")
    
    async def _send_notifications(self, rule: Dict, alert_record: Dict):
        """发送通知"""
        # 这里实现各种通知方式
        # 目前只记录日志，后续可以扩展邮件、短信、Webhook等
        for notification_type in rule.get("notification_types", []):
            if notification_type == "in_app":
                logger.info(f"📱 应用内通知: {alert_record['message']}")
            elif notification_type == "email":
                logger.info(f"📧 邮件通知: {alert_record['message']}")
            elif notification_type == "webhook":
                logger.info(f"🌐 Webhook通知: {alert_record['message']}")
    
    async def get_alert_rules(self, symbol: Optional[str] = None) -> List[Dict]:
        """获取预警规则列表"""
        if symbol:
            return [rule for rule in self.alert_rules.values() if rule["symbol"] == symbol]
        return list(self.alert_rules.values())
    
    async def get_alert_history(self, rule_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """获取预警历史"""
        history = self.alert_history.copy()
        history.reverse()  # 最新的在前面
        
        if rule_id:
            history = [h for h in history if h["alert_rule_id"] == rule_id]
            
        return history[:limit]
    
    async def update_alert_rule(self, rule_id: int, updates: Dict) -> bool:
        """更新预警规则"""
        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].update(updates)
            logger.info(f"✅ 更新预警规则: {rule_id}")
            return True
        return False
    
    async def delete_alert_rule(self, rule_id: int) -> bool:
        """删除预警规则"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"✅ 删除预警规则: {rule_id}")
            return True
        return False

# 创建全局预警引擎实例
alert_engine = EnhancedAlertEngine()
