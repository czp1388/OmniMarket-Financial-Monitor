# 寰宇多市场金融监控系统 - 高级预警服务
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

# 导入邮件服务
try:
    from services.email_service import email_service
    logger.info("✅ 邮件通知服务导入成功")
except ImportError as e:
    logger.error(f"❌ 邮件通知服务导入失败: {e}")
    email_service = None

# 导入Telegram服务
try:
    from services.telegram_service import telegram_service
    logger.info("✅ Telegram机器人服务导入成功")
except ImportError as e:
    logger.error(f"❌ Telegram机器人服务导入失败: {e}")
    telegram_service = None

class AlertRule:
    def __init__(self, symbol: str, condition: str, threshold: float, notification_type: str = "log", email_recipients: List[str] = None, telegram_chat_ids: List[str] = None):
        self.symbol = symbol
        self.condition = condition  # "above", "below", "change_up", "change_down"
        self.threshold = threshold
        self.notification_type = notification_type
        self.email_recipients = email_recipients or []
        self.telegram_chat_ids = telegram_chat_ids or []
        self.triggered = False
        self.created_at = datetime.now()
        self.last_triggered = None

    def check_condition(self, current_price: float, previous_price: float = None) -> bool:
        """检查预警条件"""
        if self.condition == "above":
            return current_price > self.threshold
        elif self.condition == "below":
            return current_price < self.threshold
        elif self.condition == "change_up" and previous_price:
            change_percent = ((current_price - previous_price) / previous_price) * 100
            return change_percent > self.threshold
        elif self.condition == "change_down" and previous_price:
            change_percent = ((current_price - previous_price) / previous_price) * 100
            return change_percent < -self.threshold
        return False

class AlertHistory:
    """预警历史记录"""
    def __init__(self):
        self.history: List[Dict] = []
        self.max_history = 1000  # 最大历史记录数

    def add_record(self, alert_data: Dict):
        """添加预警记录"""
        record = {
            'id': len(self.history) + 1,
            'timestamp': datetime.now().isoformat(),
            **alert_data
        }
        self.history.append(record)

        # 限制历史记录数量
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self, limit: int = 50, symbol: str = None) -> List[Dict]:
        """获取预警历史"""
        history = self.history.copy()
        history.reverse()  # 最新的在前

        if symbol:
            history = [h for h in history if h.get('symbol') == symbol]

        return history[:limit]

    def clear_history(self):
        """清空历史记录"""
        self.history.clear()

class AdvancedAlertService:
    def __init__(self):
        self.alert_rules: List[AlertRule] = []
        self.price_history: Dict[str, List[float]] = {}
        self.alert_history = AlertHistory()
        self.is_monitoring = False
        self.monitoring_task = None

    async def initialize(self):
        """初始化预警服务"""
        logger.info("✅ 高级预警服务初始化")

    def add_alert_rule(self, symbol: str, condition: str, threshold: float, notification_type: str = "log", email_recipients: List[str] = None, telegram_chat_ids: List[str] = None) -> str:
        """添加预警规则"""
        rule = AlertRule(symbol, condition, threshold, notification_type, email_recipients, telegram_chat_ids)
        self.alert_rules.append(rule)
        logger.info(f"✅ 添加预警规则: {symbol} {condition} {threshold} (通知方式: {notification_type})")
        return f"预警规则已添加: {symbol} {condition} {threshold}"

    def remove_alert_rule(self, symbol: str, condition: str, threshold: float) -> bool:
        """移除预警规则"""
        for rule in self.alert_rules:
            if (rule.symbol == symbol and
                rule.condition == condition and
                rule.threshold == threshold):
                self.alert_rules.remove(rule)
                logger.info(f"✅ 移除预警规则: {symbol} {condition} {threshold}")
                return True
        return False

    def get_alert_rules(self) -> List[Dict]:
        """获取所有预警规则"""
        return [{
            "symbol": rule.symbol,
            "condition": rule.condition,
            "threshold": rule.threshold,
            "notification_type": rule.notification_type,
            "email_recipients": rule.email_recipients,
            "telegram_chat_ids": rule.telegram_chat_ids,
            "triggered": rule.triggered,
            "created_at": rule.created_at.isoformat(),
            "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
        } for rule in self.alert_rules]

    def get_alert_history(self, limit: int = 50, symbol: str = None) -> List[Dict]:
        """获取预警历史记录"""
        return self.alert_history.get_history(limit, symbol)

    async def start_monitoring(self, data_service):
        """开始监控市场价格"""
        if self.is_monitoring:
            logger.warning("⚠️ 预警监控已在运行中")
            return

        self.is_monitoring = True
        logger.info("🚀 启动高级预警监控")

        # 启动监控任务
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(data_service))

    async def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 停止高级预警监控")

    async def _monitoring_loop(self, data_service):
        """监控循环"""
        while self.is_monitoring:
            try:
                await self._check_alerts(data_service)
                await asyncio.sleep(5)  # 每5秒检查一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"预警监控错误: {e}")
                await asyncio.sleep(10)

    async def _check_alerts(self, data_service):
        """检查预警条件"""
        try:
            # 获取当前市场价格
            market_data = data_service.get_realtime_prices() if hasattr(data_service, 'get_realtime_prices') else {}

            for rule in self.alert_rules:
                if rule.symbol in market_data:
                    price_data = market_data[rule.symbol]
                    current_price = price_data.get('price', 0)

                    # 获取历史价格用于变化率计算
                    if rule.symbol not in self.price_history:
                        self.price_history[rule.symbol] = []

                    previous_price = self.price_history[rule.symbol][-1] if self.price_history[rule.symbol] else current_price

                    # 检查条件
                    if rule.check_condition(current_price, previous_price) and not rule.triggered:
                        await self._trigger_alert(rule, current_price, previous_price)
                        rule.triggered = True
                        rule.last_triggered = datetime.now()
                    elif not rule.check_condition(current_price, previous_price):
                        rule.triggered = False

                    # 更新价格历史
                    self.price_history[rule.symbol].append(current_price)
                    if len(self.price_history[rule.symbol]) > 100:  # 保持最近100个价格
                        self.price_history[rule.symbol] = self.price_history[rule.symbol][-100:]

        except Exception as e:
            logger.error(f"检查预警时出错: {e}")

    async def _trigger_alert(self, rule: AlertRule, current_price: float, previous_price: float):
        """触发预警"""
        message = self._format_alert_message(rule, current_price, previous_price)
        logger.warning(f"🚨 预警触发: {message}")

        # 创建预警记录
        alert_data = {
            'symbol': rule.symbol,
            'condition': rule.condition,
            'threshold': rule.threshold,
            'current_price': current_price,
            'previous_price': previous_price,
            'message': message,
            'triggered_time': datetime.now().isoformat()
        }

        # 添加到历史记录
        self.alert_history.add_record(alert_data)

        # 根据通知类型发送通知
        if rule.notification_type == "log":
            # 记录到日志（默认）
            pass
        elif rule.notification_type == "console":
            print(f"🚨 预警: {message}")
        elif rule.notification_type == "email" and rule.email_recipients:
            # 发送邮件通知
            if email_service:
                await email_service.send_alert_notification(alert_data, rule.email_recipients)
            else:
                logger.warning("邮件服务不可用，无法发送邮件通知")
        elif rule.notification_type == "telegram" and rule.telegram_chat_ids:
            # 发送Telegram通知
            if telegram_service:
                await telegram_service.send_alert_notification(alert_data, rule.telegram_chat_ids)
            else:
                logger.warning("Telegram服务不可用，无法发送Telegram通知")
        elif rule.notification_type == "all":
            # 发送所有可用通知
            if email_service and rule.email_recipients:
                await email_service.send_alert_notification(alert_data, rule.email_recipients)
            if telegram_service and rule.telegram_chat_ids:
                await telegram_service.send_alert_notification(alert_data, rule.telegram_chat_ids)

    def _format_alert_message(self, rule: AlertRule, current_price: float, previous_price: float) -> str:
        """格式化预警消息"""
        if rule.condition == "above":
            return f"{rule.symbol} 价格超过 {rule.threshold}，当前价格: {current_price}"
        elif rule.condition == "below":
            return f"{rule.symbol} 价格低于 {rule.threshold}，当前价格: {current_price}"
        elif rule.condition == "change_up":
            change_percent = ((current_price - previous_price) / previous_price) * 100
            return f"{rule.symbol} 涨幅超过 {rule.threshold}%，当前涨幅: {change_percent:.2f}%，价格: {current_price}"
        elif rule.condition == "change_down":
            change_percent = ((current_price - previous_price) / previous_price) * 100
            return f"{rule.symbol} 跌幅超过 {rule.threshold}%，当前跌幅: {abs(change_percent):.2f}%，价格: {current_price}"
        return f"{rule.symbol} 预警触发"

# 创建预警服务实例
advanced_alert_service = AdvancedAlertService()
