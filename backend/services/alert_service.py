import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import json

from models.alerts import Alert, AlertTrigger, AlertConditionType, AlertStatus as ModelAlertStatus, NotificationType
from models.market_data import KlineData, MarketType, Timeframe
from services.data_service import data_service
from services.notification_service import notification_service
from database import SessionLocal

logger = logging.getLogger(__name__)

class AlertStatus(Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"

class AlertService:
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_triggers: List[AlertTrigger] = []
        self.alert_handlers: List[Callable] = []
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self):
        """开始监控预警条件"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("预警监控服务已启动")
    
    async def stop_monitoring(self):
        """停止监控预警条件"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("预警监控服务已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                await self._check_all_alerts()
                await asyncio.sleep(1)  # 每秒检查一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"预警监控循环出错: {e}")
                await asyncio.sleep(5)
    
    async def _check_all_alerts(self):
        """检查所有活跃预警"""
        for alert_id, alert in self.active_alerts.items():
            if alert.status != AlertStatus.ACTIVE.value:
                continue
            
            try:
                await self._check_alert(alert)
            except Exception as e:
                logger.error(f"检查预警 {alert_id} 时出错: {e}")
    
    async def _check_alert(self, alert: Alert):
        """检查单个预警条件"""
        # 获取当前价格
        current_price = await data_service.get_current_price(
            alert.symbol, alert.market_type
        )
        
        if current_price == 0:
            return
        
        # 检查条件（使用condition_config）
        if await self._evaluate_condition_config(alert.condition_config, alert.condition_type, current_price, alert.symbol, alert.market_type, alert.timeframe):
            await self._trigger_alert(alert, current_price)
    
    async def _evaluate_condition_config(self, condition_config: Dict[str, Any], condition_type: AlertConditionType, current_price: float, symbol: str, market_type: MarketType, timeframe: str) -> bool:
        """评估条件配置"""
        try:
            if condition_type == AlertConditionType.PRICE_ABOVE:
                threshold = condition_config.get('threshold')
                return current_price > threshold
            elif condition_type == AlertConditionType.PRICE_BELOW:
                threshold = condition_config.get('threshold')
                return current_price < threshold
            elif condition_type == AlertConditionType.PRICE_PERCENT_CHANGE:
                # 需要历史数据来计算百分比变化
                return await self._evaluate_percentage_change(condition_config, current_price, symbol, market_type, timeframe)
            elif condition_type == AlertConditionType.VOLUME_ABOVE:
                # 需要成交量数据
                return await self._evaluate_volume_above(condition_config, symbol, market_type, timeframe)
            elif condition_type == AlertConditionType.VOLUME_PERCENT_CHANGE:
                # 需要成交量百分比变化
                return await self._evaluate_volume_percent_change(condition_config, symbol, market_type, timeframe)
            else:
                logger.warning(f"未知的条件类型: {condition_type}")
                return False
        except Exception as e:
            logger.error(f"评估条件配置时出错: {e}")
            return False
    
    async def _evaluate_percentage_change(self, condition_config: Dict[str, Any], current_price: float, symbol: str, market_type: MarketType, timeframe: str) -> bool:
        """评估百分比变化条件"""
        try:
            threshold = condition_config.get('threshold')
            use_percentage = condition_config.get('use_percentage', False)
            
            # 获取历史数据来计算变化
            klines = await data_service.get_kline_data(
                symbol=symbol,
                timeframe=timeframe,
                market_type=market_type,
                limit=2  # 只需要最近两个K线
            )
            
            if len(klines) < 2:
                return False
            
            previous_close = klines[1].close
            current_close = klines[0].close
            
            if previous_close == 0:
                return False
            
            percentage_change = ((current_close - previous_close) / previous_close) * 100
            
            if use_percentage:
                return percentage_change > threshold
            else:
                # 这里可能需要根据条件配置判断是大于还是小于
                # 简化处理，假设是大于阈值
                return percentage_change > threshold
                
        except Exception as e:
            logger.error(f"计算百分比变化时出错: {e}")
            return False
    
    async def _evaluate_volume_above(self, condition_config: Dict[str, Any], symbol: str, market_type: MarketType, timeframe: str) -> bool:
        """评估成交量 above 条件"""
        try:
            threshold = condition_config.get('threshold')
            
            # 获取成交量数据
            klines = await data_service.get_kline_data(
                symbol=symbol,
                timeframe=timeframe,
                market_type=market_type,
                limit=1
            )
            
            if not klines:
                return False
            
            current_volume = klines[0].volume
            return current_volume > threshold
                
        except Exception as e:
            logger.error(f"评估成交量条件时出错: {e}")
            return False
    
    async def _evaluate_volume_percent_change(self, condition_config: Dict[str, Any], symbol: str, market_type: MarketType, timeframe: str) -> bool:
        """评估成交量百分比变化条件"""
        try:
            threshold = condition_config.get('threshold')
            
            # 获取历史成交量数据
            klines = await data_service.get_kline_data(
                symbol=symbol,
                timeframe=timeframe,
                market_type=market_type,
                limit=2
            )
            
            if len(klines) < 2:
                return False
            
            previous_volume = klines[1].volume
            current_volume = klines[0].volume
            
            if previous_volume == 0:
                return False
            
            volume_percent_change = ((current_volume - previous_volume) / previous_volume) * 100
            return volume_percent_change > threshold
                
        except Exception as e:
            logger.error(f"评估成交量百分比变化时出错: {e}")
            return False
    
    
    async def _trigger_alert(self, alert: Alert, current_value: float):
        """触发预警"""
        trigger = AlertTrigger(
            alert_id=alert.id,
            triggered_at=datetime.now(),
            trigger_data={
                'current_value': current_value,
                'alert_name': alert.name,
                'symbol': alert.symbol,
                'market_type': alert.market_type.value,
                'condition_type': alert.condition_type.value,
                'condition_config': alert.condition_config
            }
        )
        
        # 保存触发记录
        self.alert_triggers.append(trigger)
        
        # 更新预警状态
        alert.status = ModelAlertStatus.TRIGGERED.value
        alert.last_triggered_at = datetime.now()
        alert.triggered_count = (alert.triggered_count or 0) + 1
        
        # 如果不是重复预警，则禁用
        if not alert.is_recurring:
            alert.status = ModelAlertStatus.DISABLED.value
        
        # 调用所有注册的处理程序
        for handler in self.alert_handlers:
            try:
                await handler(alert, trigger)
            except Exception as e:
                logger.error(f"预警处理程序出错: {e}")
        
        # 发送多渠道通知
        await self._send_alert_notifications(alert, trigger, current_value)
        
        logger.info(f"预警触发: {alert.name} - 当前值: {current_value}")
    
    async def _send_alert_notifications(self, alert: Alert, trigger: AlertTrigger, current_value: float):
        """
        发送预警通知到配置的渠道
        """
        try:
            # 获取通知类型配置，默认为应用内通知
            notification_types = alert.notification_types or ["in_app"]
            
            # 构建通知标题和内容
            title = f"预警触发: {alert.name}"
            message = f"""
预警名称: {alert.name}
交易对: {alert.symbol}
市场类型: {alert.market_type.value}
条件类型: {alert.condition_type.value}
触发值: {current_value}
触发时间: {trigger.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
条件配置: {json.dumps(alert.condition_config, ensure_ascii=False)}
            """.strip()
            
            # 额外数据
            additional_data = {
                "alert_id": alert.id,
                "alert_name": alert.name,
                "symbol": alert.symbol,
                "market_type": alert.market_type.value,
                "condition_type": alert.condition_type.value,
                "current_value": current_value,
                "triggered_at": trigger.triggered_at.isoformat(),
                "condition_config": alert.condition_config
            }
            
            # 合并通知配置
            if alert.notification_config:
                additional_data.update(alert.notification_config)
            
            # 发送每种类型的通知
            for notification_type in notification_types:
                # 将NotificationType枚举转换为字符串
                if hasattr(notification_type, 'value'):
                    notification_type_str = notification_type.value
                else:
                    notification_type_str = str(notification_type)
                
                # 映射到notification_service支持的类型
                # notification_service支持: "email", "telegram", "webhook", "in_app", "all"
                if notification_type_str == "sms":
                    # 暂不支持SMS，跳过
                    logger.warning("SMS通知暂不支持，跳过")
                    continue
                
                try:
                    # 对于email类型，可以从notification_config中获取收件人
                    recipients = None
                    if notification_type_str == "email" and alert.notification_config:
                        recipients = alert.notification_config.get("email_recipients")
                    
                    # 发送通知
                    results = await notification_service.send_notification(
                        notification_type=notification_type_str,
                        title=title,
                        message=message,
                        recipients=recipients,
                        additional_data=additional_data
                    )
                    
                    logger.info(f"通知发送结果 ({notification_type_str}): {results}")
                    
                except Exception as e:
                    logger.error(f"发送{notification_type_str}通知失败: {e}")
        
        except Exception as e:
            logger.error(f"发送预警通知时出错: {e}")
    
    def add_alert(self, alert: Alert) -> str:
        """添加预警"""
        self.active_alerts[alert.id] = alert
        logger.info(f"添加预警: {alert.name} (ID: {alert.id})")
        return alert.id
    
    def update_alert(self, alert_id: str, alert: Alert) -> bool:
        """更新预警"""
        if alert_id not in self.active_alerts:
            return False
        
        self.active_alerts[alert_id] = alert
        logger.info(f"更新预警: {alert.name} (ID: {alert_id})")
        return True
    
    def delete_alert(self, alert_id: str) -> bool:
        """删除预警"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            logger.info(f"删除预警: {alert_id}")
            return True
        return False
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """获取预警"""
        return self.active_alerts.get(alert_id)
    
    def get_all_alerts(self) -> List[Alert]:
        """获取所有预警"""
        return list(self.active_alerts.values())
    
    def get_alert_triggers(self, alert_id: Optional[str] = None) -> List[AlertTrigger]:
        """获取预警触发记录"""
        if alert_id:
            return [trigger for trigger in self.alert_triggers if trigger.alert_id == alert_id]
        return self.alert_triggers
    
    def register_alert_handler(self, handler: Callable):
        """注册预警处理程序"""
        self.alert_handlers.append(handler)
        logger.info("注册预警处理程序")
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Optional[Alert]:
        """
        创建新预警
        
        参数:
            alert_data: 预警配置数据，包含：
                - symbol: 交易对
                - market_type: 市场类型
                - alert_type: 预警类型（可选，测试兼容性）
                - condition: 条件类型（可选，测试兼容性）
                - condition_type: AlertConditionType 枚举
                - threshold: 阈值
                - message: 预警消息
                - user_id: 用户ID
                - name: 预警名称（可选）
                - description: 描述（可选）
                - exchange: 交易所（可选，默认binance）
                - timeframe: 时间周期（可选，默认1h）
                - is_active: 是否激活（可选，默认True）
                - is_recurring: 是否重复（可选，默认False）
                - notify_email: 是否邮件通知（可选）
                - notify_sms: 是否短信通知（可选）
                - notify_push: 是否推送通知（可选）
                - expires_at: 过期时间（可选）
        
        返回:
            Alert: 创建的预警对象，失败返回None
        """
        try:
            db = SessionLocal()
            
            # 兼容测试中的参数格式
            symbol = alert_data.get('symbol')
            market_type = alert_data.get('market_type', MarketType.CRYPTO)
            user_id = alert_data.get('user_id')
            
            # 处理条件类型（支持字符串和枚举）
            condition_type = alert_data.get('condition_type')
            
            if isinstance(condition_type, str):
                # 如果是字符串，尝试转换为枚举
                try:
                    condition_type = AlertConditionType[condition_type.upper()]
                except (KeyError, AttributeError):
                    # 兼容测试中的简化条件
                    condition = alert_data.get('condition', '')
                    condition_upper = str(condition).upper()
                    # 支持多种格式：ABOVE, above, percentage_change, PERCENTAGE_CHANGE
                    if condition_upper == 'ABOVE':
                        condition_type = AlertConditionType.PRICE_ABOVE
                    elif condition_upper == 'BELOW':
                        condition_type = AlertConditionType.PRICE_BELOW
                    elif condition_upper in ('PERCENTAGE_CHANGE', 'PRICE_PERCENT_CHANGE'):
                        condition_type = AlertConditionType.PRICE_PERCENT_CHANGE
                    else:
                        condition_type = AlertConditionType.PRICE_ABOVE
            elif not isinstance(condition_type, AlertConditionType):
                # condition_type 不是字符串也不是枚举，检查 condition 字段
                condition = alert_data.get('condition', '')
                condition_upper = str(condition).upper()
                if condition_upper == 'ABOVE':
                    condition_type = AlertConditionType.PRICE_ABOVE
                elif condition_upper == 'BELOW':
                    condition_type = AlertConditionType.PRICE_BELOW
                elif condition_upper in ('PERCENTAGE_CHANGE', 'PRICE_PERCENT_CHANGE'):
                    condition_type = AlertConditionType.PRICE_PERCENT_CHANGE
                else:
                    condition_type = AlertConditionType.PRICE_ABOVE
            
            # 构建条件配置
            condition_config = {
                'threshold': alert_data.get('threshold', 0.0)
            }
            
            # 处理通知类型
            notification_types = []
            if alert_data.get('notify_email', False):
                notification_types.append('email')
            if alert_data.get('notify_sms', False):
                notification_types.append('sms')
            if alert_data.get('notify_push', True):
                notification_types.append('in_app')
            
            if not notification_types:
                notification_types = ['in_app']
            
            # 创建Alert对象
            alert = Alert(
                user_id=user_id,
                name=alert_data.get('name', f"{symbol} 预警"),
                description=alert_data.get('description', alert_data.get('message', '')),
                symbol=symbol,
                market_type=market_type,
                exchange=alert_data.get('exchange', 'binance'),
                timeframe=alert_data.get('timeframe', Timeframe.H1),
                condition_type=condition_type,
                condition_config=condition_config,
                status=ModelAlertStatus.ACTIVE if alert_data.get('is_active', True) else ModelAlertStatus.DISABLED,
                is_recurring=alert_data.get('is_recurring', False),
                notification_types=notification_types,
                notification_config={},
                valid_until=alert_data.get('expires_at')
            )
            
            # 保存到数据库
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # 添加到活跃预警列表
            self.active_alerts[str(alert.id)] = alert
            
            logger.info(f"创建预警成功: {alert.name} (ID: {alert.id})")
            db.close()
            return alert
            
        except Exception as e:
            logger.error(f"创建预警失败: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return None
    
    async def get_alerts_by_user(self, user_id: int) -> List[Alert]:
        """获取用户的所有预警"""
        try:
            db = SessionLocal()
            alerts = db.query(Alert).filter(Alert.user_id == user_id).all()
            db.close()
            return alerts
        except Exception as e:
            logger.error(f"获取用户预警失败: {e}")
            return []
    
    async def get_alerts_by_symbol(self, symbol: str) -> List[Alert]:
        """获取特定品种的预警"""
        try:
            db = SessionLocal()
            alerts = db.query(Alert).filter(Alert.symbol == symbol).all()
            db.close()
            return alerts
        except Exception as e:
            logger.error(f"获取品种预警失败: {e}")
            return []
    
    async def update_alert(self, alert_id: int, updates: Dict, user_id: int) -> bool:
        """更新预警"""
        try:
            db = SessionLocal()
            alert = db.query(Alert).filter(
                Alert.id == alert_id,
                Alert.user_id == user_id
            ).first()
            
            if not alert:
                db.close()
                return False
            
            for key, value in updates.items():
                if hasattr(alert, key):
                    setattr(alert, key, value)
            
            db.commit()
            db.close()
            return True
        except Exception as e:
            logger.error(f"更新预警失败: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return False
    
    async def pause_alert(self, alert_id: int, user_id: int) -> bool:
        """暂停预警"""
        return await self.update_alert(
            alert_id, 
            {'status': ModelAlertStatus.DISABLED}, 
            user_id
        )
    
    async def resume_alert(self, alert_id: int, user_id: int) -> bool:
        """恢复预警"""
        return await self.update_alert(
            alert_id, 
            {'status': ModelAlertStatus.ACTIVE}, 
            user_id
        )
    
    async def get_alert_history(self, user_id: int, limit: int = 10) -> List[AlertTrigger]:
        """获取预警历史"""
        try:
            db = SessionLocal()
            # 获取用户的所有预警ID
            user_alert_ids = db.query(Alert.id).filter(Alert.user_id == user_id).all()
            user_alert_ids = [aid[0] for aid in user_alert_ids]
            
            # 获取这些预警的触发记录
            triggers = db.query(AlertTrigger).filter(
                AlertTrigger.alert_id.in_(user_alert_ids)
            ).order_by(AlertTrigger.triggered_at.desc()).limit(limit).all()
            
            db.close()
            return triggers
        except Exception as e:
            logger.error(f"获取预警历史失败: {e}")
            return []
    
    async def count_active_alerts(self, user_id: int) -> int:
        """统计活跃预警数量"""
        try:
            db = SessionLocal()
            count = db.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.status == ModelAlertStatus.ACTIVE
            ).count()
            db.close()
            return count
        except Exception as e:
            logger.error(f"统计活跃预警失败: {e}")
            return 0
    
    async def batch_delete_alerts(self, alert_ids: List[int], user_id: int) -> bool:
        """批量删除预警"""
        try:
            db = SessionLocal()
            db.query(Alert).filter(
                Alert.id.in_(alert_ids),
                Alert.user_id == user_id
            ).delete(synchronize_session=False)
            db.commit()
            db.close()
            return True
        except Exception as e:
            logger.error(f"批量删除预警失败: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return False
    
    async def get_triggered_alerts_count(self, user_id: int) -> int:
        """获取已触发预警数量"""
        try:
            db = SessionLocal()
            count = db.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.triggered_count > 0
            ).count()
            db.close()
            return count
        except Exception as e:
            logger.error(f"获取触发预警数量失败: {e}")
            return 0
    
    async def export_alerts(self, user_id: int) -> List[Dict]:
        """导出预警配置"""
        try:
            alerts = await self.get_alerts_by_user(user_id)
            exported = []
            for alert in alerts:
                exported.append({
                    'name': alert.name,
                    'symbol': alert.symbol,
                    'market_type': alert.market_type.value if hasattr(alert.market_type, 'value') else str(alert.market_type),
                    'condition_type': alert.condition_type.value if hasattr(alert.condition_type, 'value') else str(alert.condition_type),
                    'condition_config': alert.condition_config,
                    'notification_types': alert.notification_types
                })
            return exported
        except Exception as e:
            logger.error(f"导出预警失败: {e}")
            return []
    
    async def import_alerts(self, alerts_config: List[Dict], user_id: int) -> bool:
        """导入预警配置"""
        try:
            for config in alerts_config:
                config['user_id'] = user_id
                await self.create_alert(config)
            return True
        except Exception as e:
            logger.error(f"导入预警失败: {e}")
            return False
    
    async def send_notification(self, alert: Alert, trigger: AlertTrigger, notification_type: str = "in_app"):
        """发送通知"""
        message = f"预警触发: {alert.name}\n条件: {trigger.condition_details.get('name', 'N/A')}\n当前值: {trigger.current_value}"
        
        if notification_type == "in_app":
            # 应用内通知
            logger.info(f"应用内通知: {message}")
        
        elif notification_type == "email":
            # 邮件通知（需要配置SMTP）
            logger.info(f"邮件通知: {message}")
        
        elif notification_type == "telegram":
            # Telegram通知（需要配置Bot）
            logger.info(f"Telegram通知: {message}")
        
        elif notification_type == "webhook":
            # Webhook通知
            logger.info(f"Webhook通知: {message}")
        
        # 实际实现中，这里需要集成具体的通知服务


# 全局预警服务实例
alert_service = AlertService()
