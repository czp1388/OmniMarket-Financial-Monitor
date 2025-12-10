import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any, Tuple
from enum import Enum
import json
from collections import defaultdict, deque

from models.alerts import Alert, AlertTrigger, AlertConditionType, AlertStatus as ModelAlertStatus, NotificationType
from models.market_data import KlineData, MarketType, Timeframe
from services.data_service import data_service
from services.notification_service import notification_service
from services.technical_analysis_service import technical_analysis_service
from database import SessionLocal

logger = logging.getLogger(__name__)

class AlertStatus(Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"

class AlertPriority(Enum):
    """预警优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertService:
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_triggers: List[AlertTrigger] = []
        self.alert_handlers: List[Callable] = []
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # 预警历史缓存（最近1000条）
        self.trigger_history: deque = deque(maxlen=1000)
        
        # 预警统计
        self.alert_stats = {
            'total_triggers': 0,
            'triggers_by_type': defaultdict(int),
            'triggers_by_symbol': defaultdict(int),
            'false_triggers': 0,  # 误报次数
            'average_trigger_time': 0.0,  # 平均触发时间
        }
        
        # 预警冷却期管理（防止重复触发）
        self.cooldown_periods: Dict[str, datetime] = {}  # alert_id -> last_trigger_time
        
        # 技术分析服务（延迟初始化）
        self._technical_service = None
    
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
        """检查单个预警条件（增强版）"""
        # 检查是否在冷却期内
        if not self._can_trigger(alert):
            return
        
        # 检查预警是否过期
        if alert.valid_until and datetime.now() > alert.valid_until:
            alert.status = ModelAlertStatus.EXPIRED.value
            logger.info(f"预警已过期: {alert.name} (ID: {alert.id})")
            return
        
        # 获取当前价格
        current_price = await data_service.get_current_price(
            alert.symbol, alert.market_type
        )
        
        if current_price == 0:
            return
        
        # 评估条件
        is_triggered, trigger_value, trigger_details = await self._evaluate_condition_enhanced(
            alert, current_price
        )
        
        if is_triggered:
            await self._trigger_alert_enhanced(alert, trigger_value, trigger_details)
    
    def _can_trigger(self, alert: Alert) -> bool:
        """检查预警是否可以触发（冷却期检查）"""
        alert_id = str(alert.id)
        
        # 如果是重复预警，检查冷却期
        if alert.is_recurring:
            last_trigger = self.cooldown_periods.get(alert_id)
            if last_trigger:
                # 默认冷却期：5分钟
                cooldown_seconds = alert.condition_config.get('cooldown_seconds', 300)
                if (datetime.now() - last_trigger).total_seconds() < cooldown_seconds:
                    return False
        
        return True
    
    async def _evaluate_condition_enhanced(
        self, alert: Alert, current_price: float
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """
        增强的条件评估
        
        返回:
            (is_triggered, trigger_value, trigger_details)
        """
        condition_type = alert.condition_type
        config = alert.condition_config
        
        try:
            # 价格条件
            if condition_type == AlertConditionType.PRICE_ABOVE:
                threshold = config.get('threshold')
                return current_price > threshold, current_price, {'threshold': threshold}
            
            elif condition_type == AlertConditionType.PRICE_BELOW:
                threshold = config.get('threshold')
                return current_price < threshold, current_price, {'threshold': threshold}
            
            elif condition_type == AlertConditionType.PRICE_PERCENT_CHANGE:
                return await self._evaluate_percentage_change(config, current_price, alert.symbol, alert.market_type, alert.timeframe)
            
            # 新增：价格穿越均线
            elif condition_type == AlertConditionType.PRICE_CROSS_MA:
                return await self._evaluate_price_cross_ma(config, alert)
            
            # 新增：突破阻力位
            elif condition_type == AlertConditionType.PRICE_BREAK_RESISTANCE:
                return await self._evaluate_price_break_level(config, current_price, alert, is_resistance=True)
            
            # 新增：跌破支撑位
            elif condition_type == AlertConditionType.PRICE_BREAK_SUPPORT:
                return await self._evaluate_price_break_level(config, current_price, alert, is_resistance=False)
            
            # 成交量条件
            elif condition_type == AlertConditionType.VOLUME_ABOVE:
                return await self._evaluate_volume_above(config, alert.symbol, alert.market_type, alert.timeframe)
            
            elif condition_type == AlertConditionType.VOLUME_PERCENT_CHANGE:
                return await self._evaluate_volume_percent_change(config, alert.symbol, alert.market_type, alert.timeframe)
            
            # 新增：成交量激增
            elif condition_type == AlertConditionType.VOLUME_SPIKE:
                return await self._evaluate_volume_spike(config, alert)
            
            # 新增：RSI超买/超卖
            elif condition_type == AlertConditionType.RSI_OVERBOUGHT:
                return await self._evaluate_rsi_condition(alert, overbought=True)
            
            elif condition_type == AlertConditionType.RSI_OVERSOLD:
                return await self._evaluate_rsi_condition(alert, overbought=False)
            
            # 新增：MACD金叉/死叉
            elif condition_type == AlertConditionType.MACD_CROSS:
                return await self._evaluate_macd_cross(alert)
            
            # 新增：布林带突破
            elif condition_type == AlertConditionType.BOLLINGER_BREAKOUT:
                return await self._evaluate_bollinger_breakout(alert)
            
            # 新增：金叉/死叉
            elif condition_type == AlertConditionType.GOLDEN_CROSS:
                return await self._evaluate_ma_cross(alert, golden=True)
            
            elif condition_type == AlertConditionType.DEATH_CROSS:
                return await self._evaluate_ma_cross(alert, golden=False)
            
            # 新增：止损/止盈
            elif condition_type == AlertConditionType.STOP_LOSS:
                return await self._evaluate_stop_loss(config, current_price, alert)
            
            elif condition_type == AlertConditionType.TAKE_PROFIT:
                return await self._evaluate_take_profit(config, current_price, alert)
            
            # 新增：组合条件
            elif condition_type == AlertConditionType.COMPOSITE_AND:
                return await self._evaluate_composite_condition(config, alert, use_and=True)
            
            elif condition_type == AlertConditionType.COMPOSITE_OR:
                return await self._evaluate_composite_condition(config, alert, use_and=False)
            
            else:
                logger.warning(f"未知的条件类型: {condition_type}")
                return False, 0.0, {}
                
        except Exception as e:
            logger.error(f"评估条件时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_percentage_change(self, condition_config: Dict[str, Any], current_price: float, symbol: str, market_type: MarketType, timeframe: str) -> Tuple[bool, float, Dict]:
        """评估百分比变化条件（返回元组）"""
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
                return False, 0.0, {}
            
            previous_close = klines[1].close
            current_close = klines[0].close
            
            if previous_close == 0:
                return False, 0.0, {}
            
            percentage_change = ((current_close - previous_close) / previous_close) * 100
            
            is_triggered = percentage_change > threshold if use_percentage else percentage_change > threshold
            
            return is_triggered, percentage_change, {
                'previous_close': previous_close,
                'current_close': current_close,
                'percentage_change': percentage_change,
                'threshold': threshold
            }
                
        except Exception as e:
            logger.error(f"计算百分比变化时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_volume_above(self, condition_config: Dict[str, Any], symbol: str, market_type: MarketType, timeframe: str) -> Tuple[bool, float, Dict]:
        """评估成交量 above 条件（返回元组）"""
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
                return False, 0.0, {}
            
            current_volume = klines[0].volume
            is_triggered = current_volume > threshold
            
            return is_triggered, current_volume, {
                'current_volume': current_volume,
                'threshold': threshold
            }
                
        except Exception as e:
            logger.error(f"评估成交量条件时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_volume_percent_change(self, condition_config: Dict[str, Any], symbol: str, market_type: MarketType, timeframe: str) -> Tuple[bool, float, Dict]:
        """评估成交量百分比变化条件（返回元组）"""
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
                return False, 0.0, {}
            
            previous_volume = klines[1].volume
            current_volume = klines[0].volume
            
            if previous_volume == 0:
                return False, 0.0, {}
            
            volume_percent_change = ((current_volume - previous_volume) / previous_volume) * 100
            is_triggered = volume_percent_change > threshold
            
            return is_triggered, volume_percent_change, {
                'previous_volume': previous_volume,
                'current_volume': current_volume,
                'volume_percent_change': volume_percent_change,
                'threshold': threshold
            }
                
        except Exception as e:
            logger.error(f"评估成交量百分比变化时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_price_cross_ma(self, config: Dict, alert: Alert) -> Tuple[bool, float, Dict]:
        """评估价格穿越均线"""
        try:
            ma_period = config.get('ma_period', 20)
            cross_direction = config.get('direction', 'above')  # above或below
            
            # 获取K线数据
            klines = await data_service.get_kline_data(
                symbol=alert.symbol,
                timeframe=alert.timeframe,
                market_type=alert.market_type,
                limit=ma_period + 2
            )
            
            if len(klines) < ma_period + 2:
                return False, 0.0, {}
            
            # 计算均线
            closes = [k.close for k in klines]
            ma_current = sum(closes[:ma_period]) / ma_period
            ma_previous = sum(closes[1:ma_period+1]) / ma_period
            
            current_price = closes[0]
            previous_price = closes[1]
            
            # 检查穿越
            if cross_direction == 'above':
                # 向上穿越：之前在MA下方，现在在MA上方
                is_triggered = previous_price <= ma_previous and current_price > ma_current
            else:
                # 向下穿越：之前在MA上方，现在在MA下方
                is_triggered = previous_price >= ma_previous and current_price < ma_current
            
            return is_triggered, current_price, {
                'ma_period': ma_period,
                'ma_value': ma_current,
                'current_price': current_price,
                'direction': cross_direction
            }
            
        except Exception as e:
            logger.error(f"评估价格穿越均线时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_price_break_level(self, config: Dict, current_price: float, alert: Alert, is_resistance: bool) -> Tuple[bool, float, Dict]:
        """评估价格突破支撑/阻力位"""
        try:
            level = config.get('level')  # 支撑/阻力位价格
            
            # 获取前一个价格
            klines = await data_service.get_kline_data(
                symbol=alert.symbol,
                timeframe=alert.timeframe,
                market_type=alert.market_type,
                limit=2
            )
            
            if len(klines) < 2:
                return False, 0.0, {}
            
            previous_price = klines[1].close
            
            if is_resistance:
                # 突破阻力位：之前在阻力位下方，现在突破
                is_triggered = previous_price <= level and current_price > level
                level_type = "resistance"
            else:
                # 跌破支撑位：之前在支撑位上方，现在跌破
                is_triggered = previous_price >= level and current_price < level
                level_type = "support"
            
            return is_triggered, current_price, {
                'level': level,
                'level_type': level_type,
                'current_price': current_price,
                'previous_price': previous_price
            }
            
        except Exception as e:
            logger.error(f"评估价格突破时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_volume_spike(self, config: Dict, alert: Alert) -> Tuple[bool, float, Dict]:
        """评估成交量激增（相比平均量）"""
        try:
            spike_multiplier = config.get('multiplier', 2.0)  # 倍数阈值
            lookback_periods = config.get('lookback', 20)  # 回看周期
            
            # 获取历史成交量数据
            klines = await data_service.get_kline_data(
                symbol=alert.symbol,
                timeframe=alert.timeframe,
                market_type=alert.market_type,
                limit=lookback_periods + 1
            )
            
            if len(klines) < lookback_periods + 1:
                return False, 0.0, {}
            
            current_volume = klines[0].volume
            average_volume = sum(k.volume for k in klines[1:]) / lookback_periods
            
            if average_volume == 0:
                return False, 0.0, {}
            
            volume_ratio = current_volume / average_volume
            is_triggered = volume_ratio >= spike_multiplier
            
            return is_triggered, volume_ratio, {
                'current_volume': current_volume,
                'average_volume': average_volume,
                'volume_ratio': volume_ratio,
                'multiplier': spike_multiplier
            }
            
        except Exception as e:
            logger.error(f"评估成交量激增时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_rsi_condition(self, alert: Alert, overbought: bool) -> Tuple[bool, float, Dict]:
        """评估RSI超买/超卖"""
        try:
            period = alert.condition_config.get('rsi_period', 14)
            threshold = alert.condition_config.get('threshold', 70 if overbought else 30)
            
            # 获取K线数据
            klines = await data_service.get_kline_data(
                symbol=alert.symbol,
                timeframe=alert.timeframe,
                market_type=alert.market_type,
                limit=period + 10
            )
            
            if len(klines) < period + 1:
                return False, 0.0, {}
            
            # 计算RSI（简化版）
            closes = [k.close for k in reversed(klines)]
            gains = []
            losses = []
            
            for i in range(1, len(closes)):
                change = closes[i] - closes[i-1]
                gains.append(max(change, 0))
                losses.append(max(-change, 0))
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            if overbought:
                is_triggered = rsi >= threshold
            else:
                is_triggered = rsi <= threshold
            
            return is_triggered, rsi, {
                'rsi': rsi,
                'threshold': threshold,
                'condition': 'overbought' if overbought else 'oversold'
            }
            
        except Exception as e:
            logger.error(f"评估RSI条件时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_macd_cross(self, alert: Alert) -> Tuple[bool, float, Dict]:
        """评估MACD金叉/死叉"""
        try:
            cross_type = alert.condition_config.get('cross_type', 'golden')  # golden或death
            
            # 获取K线数据（需要足够的数据计算MACD）
            klines = await data_service.get_kline_data(
                symbol=alert.symbol,
                timeframe=alert.timeframe,
                market_type=alert.market_type,
                limit=50
            )
            
            if len(klines) < 30:
                return False, 0.0, {}
            
            # 简化的MACD计算（12, 26, 9）
            closes = [k.close for k in reversed(klines)]
            
            # 计算EMA
            def ema(data, period):
                multiplier = 2 / (period + 1)
                ema_values = [sum(data[:period]) / period]
                for price in data[period:]:
                    ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
                return ema_values
            
            ema12 = ema(closes, 12)
            ema26 = ema(closes, 26)
            
            # MACD线
            macd_line = [ema12[i] - ema26[i] for i in range(len(ema26))]
            
            # 信号线（MACD的9日EMA）
            signal_line = ema(macd_line, 9)
            
            # 检查交叉
            if len(signal_line) < 2:
                return False, 0.0, {}
            
            macd_current = macd_line[-1]
            signal_current = signal_line[-1]
            macd_previous = macd_line[-2]
            signal_previous = signal_line[-2]
            
            if cross_type == 'golden':
                # 金叉：MACD从下方穿越信号线
                is_triggered = macd_previous <= signal_previous and macd_current > signal_current
            else:
                # 死叉：MACD从上方穿越信号线
                is_triggered = macd_previous >= signal_previous and macd_current < signal_current
            
            return is_triggered, macd_current, {
                'macd': macd_current,
                'signal': signal_current,
                'cross_type': cross_type
            }
            
        except Exception as e:
            logger.error(f"评估MACD交叉时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_bollinger_breakout(self, alert: Alert) -> Tuple[bool, float, Dict]:
        """评估布林带突破"""
        try:
            period = alert.condition_config.get('period', 20)
            std_dev = alert.condition_config.get('std_dev', 2)
            breakout_direction = alert.condition_config.get('direction', 'upper')  # upper或lower
            
            # 获取K线数据
            klines = await data_service.get_kline_data(
                symbol=alert.symbol,
                timeframe=alert.timeframe,
                market_type=alert.market_type,
                limit=period + 2
            )
            
            if len(klines) < period + 1:
                return False, 0.0, {}
            
            closes = [k.close for k in klines[:period]]
            current_price = klines[0].close
            
            # 计算布林带
            middle_band = sum(closes) / period
            variance = sum((x - middle_band) ** 2 for x in closes) / period
            std = variance ** 0.5
            
            upper_band = middle_band + (std_dev * std)
            lower_band = middle_band - (std_dev * std)
            
            # 检查突破
            if breakout_direction == 'upper':
                is_triggered = current_price > upper_band
            else:
                is_triggered = current_price < lower_band
            
            return is_triggered, current_price, {
                'current_price': current_price,
                'upper_band': upper_band,
                'middle_band': middle_band,
                'lower_band': lower_band,
                'direction': breakout_direction
            }
            
        except Exception as e:
            logger.error(f"评估布林带突破时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_ma_cross(self, alert: Alert, golden: bool) -> Tuple[bool, float, Dict]:
        """评估均线金叉/死叉"""
        try:
            fast_period = alert.condition_config.get('fast_period', 5)
            slow_period = alert.condition_config.get('slow_period', 20)
            
            # 获取K线数据
            klines = await data_service.get_kline_data(
                symbol=alert.symbol,
                timeframe=alert.timeframe,
                market_type=alert.market_type,
                limit=slow_period + 2
            )
            
            if len(klines) < slow_period + 2:
                return False, 0.0, {}
            
            closes = [k.close for k in klines]
            
            # 计算快慢均线（当前和前一周期）
            fast_ma_current = sum(closes[:fast_period]) / fast_period
            fast_ma_previous = sum(closes[1:fast_period+1]) / fast_period
            slow_ma_current = sum(closes[:slow_period]) / slow_period
            slow_ma_previous = sum(closes[1:slow_period+1]) / slow_period
            
            if golden:
                # 金叉：快线从下方穿越慢线
                is_triggered = fast_ma_previous <= slow_ma_previous and fast_ma_current > slow_ma_current
                cross_type = "golden_cross"
            else:
                # 死叉：快线从上方穿越慢线
                is_triggered = fast_ma_previous >= slow_ma_previous and fast_ma_current < slow_ma_current
                cross_type = "death_cross"
            
            return is_triggered, fast_ma_current, {
                'fast_ma': fast_ma_current,
                'slow_ma': slow_ma_current,
                'cross_type': cross_type,
                'fast_period': fast_period,
                'slow_period': slow_period
            }
            
        except Exception as e:
            logger.error(f"评估均线交叉时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_stop_loss(self, config: Dict, current_price: float, alert: Alert) -> Tuple[bool, float, Dict]:
        """评估止损"""
        try:
            stop_price = config.get('stop_price')
            position_type = config.get('position_type', 'long')  # long或short
            
            if position_type == 'long':
                # 多头止损：价格跌破止损价
                is_triggered = current_price <= stop_price
            else:
                # 空头止损：价格涨破止损价
                is_triggered = current_price >= stop_price
            
            return is_triggered, current_price, {
                'stop_price': stop_price,
                'current_price': current_price,
                'position_type': position_type
            }
            
        except Exception as e:
            logger.error(f"评估止损时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_take_profit(self, config: Dict, current_price: float, alert: Alert) -> Tuple[bool, float, Dict]:
        """评估止盈"""
        try:
            target_price = config.get('target_price')
            position_type = config.get('position_type', 'long')
            
            if position_type == 'long':
                # 多头止盈：价格涨至目标价
                is_triggered = current_price >= target_price
            else:
                # 空头止盈：价格跌至目标价
                is_triggered = current_price <= target_price
            
            return is_triggered, current_price, {
                'target_price': target_price,
                'current_price': current_price,
                'position_type': position_type
            }
            
        except Exception as e:
            logger.error(f"评估止盈时出错: {e}")
            return False, 0.0, {}
    
    async def _evaluate_composite_condition(self, config: Dict, alert: Alert, use_and: bool) -> Tuple[bool, float, Dict]:
        """评估组合条件（AND/OR）"""
        try:
            sub_conditions = config.get('conditions', [])
            
            if not sub_conditions:
                return False, 0.0, {}
            
            results = []
            details = []
            
            for sub_cond in sub_conditions:
                # 递归评估子条件
                condition_type = AlertConditionType[sub_cond['type'].upper()]
                is_met, value, detail = await self._evaluate_condition_enhanced(
                    Alert(
                        id=alert.id,
                        symbol=alert.symbol,
                        market_type=alert.market_type,
                        timeframe=alert.timeframe,
                        condition_type=condition_type,
                        condition_config=sub_cond.get('config', {})
                    ),
                    await data_service.get_current_price(alert.symbol, alert.market_type)
                )
                results.append(is_met)
                details.append({
                    'type': sub_cond['type'],
                    'is_met': is_met,
                    'value': value,
                    'details': detail
                })
            
            # AND/OR逻辑
            if use_and:
                is_triggered = all(results)
            else:
                is_triggered = any(results)
            
            return is_triggered, 1.0 if is_triggered else 0.0, {
                'logic': 'AND' if use_and else 'OR',
                'sub_conditions': details,
                'total_conditions': len(sub_conditions),
                'met_conditions': sum(results)
            }
            
        except Exception as e:
            logger.error(f"评估组合条件时出错: {e}")
            return False, 0.0, {}
    
    
    async def _trigger_alert_enhanced(self, alert: Alert, trigger_value: float, trigger_details: Dict[str, Any]):
        """触发预警（增强版）"""
        trigger_time = datetime.now()
        
        trigger = AlertTrigger(
            alert_id=alert.id,
            triggered_at=trigger_time,
            trigger_data={
                'trigger_value': trigger_value,
                'alert_name': alert.name,
                'symbol': alert.symbol,
                'market_type': alert.market_type.value,
                'condition_type': alert.condition_type.value,
                'condition_config': alert.condition_config,
                'trigger_details': trigger_details
            }
        )
        
        # 保存触发记录
        self.alert_triggers.append(trigger)
        self.trigger_history.append({
            'alert_id': alert.id,
            'alert_name': alert.name,
            'symbol': alert.symbol,
            'triggered_at': trigger_time,
            'trigger_value': trigger_value,
            'details': trigger_details
        })
        
        # 更新统计
        self.alert_stats['total_triggers'] += 1
        self.alert_stats['triggers_by_type'][alert.condition_type.value] += 1
        self.alert_stats['triggers_by_symbol'][alert.symbol] += 1
        
        # 更新预警状态
        alert.status = ModelAlertStatus.TRIGGERED.value
        alert.last_triggered_at = trigger_time
        alert.triggered_count = (alert.triggered_count or 0) + 1
        
        # 设置冷却期
        self.cooldown_periods[str(alert.id)] = trigger_time
        
        # 如果不是重复预警，则禁用
        if not alert.is_recurring:
            alert.status = ModelAlertStatus.DISABLED.value
            logger.info(f"预警 {alert.name} 触发后已禁用（非重复预警）")
        
        # 调用所有注册的处理程序
        for handler in self.alert_handlers:
            try:
                await handler(alert, trigger)
            except Exception as e:
                logger.error(f"预警处理程序出错: {e}")
        
        # 发送多渠道通知
        await self._send_alert_notifications(alert, trigger, trigger_value)
        
        logger.info(f"预警触发: {alert.name} - 触发值: {trigger_value}, 详情: {trigger_details}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """获取预警统计信息"""
        active_count = sum(1 for a in self.active_alerts.values() if a.status == ModelAlertStatus.ACTIVE.value)
        triggered_count = sum(1 for a in self.active_alerts.values() if a.status == ModelAlertStatus.TRIGGERED.value)
        disabled_count = sum(1 for a in self.active_alerts.values() if a.status == ModelAlertStatus.DISABLED.value)
        
        # 统计最常触发的预警类型
        top_trigger_types = sorted(
            self.alert_stats['triggers_by_type'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # 统计最常触发的交易对
        top_trigger_symbols = sorted(
            self.alert_stats['triggers_by_symbol'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_alerts': len(self.active_alerts),
            'active_alerts': active_count,
            'triggered_alerts': triggered_count,
            'disabled_alerts': disabled_count,
            'total_triggers': self.alert_stats['total_triggers'],
            'top_trigger_types': [{'type': t[0], 'count': t[1]} for t in top_trigger_types],
            'top_trigger_symbols': [{'symbol': s[0], 'count': s[1]} for s in top_trigger_symbols],
            'trigger_history_size': len(self.trigger_history),
            'false_triggers': self.alert_stats['false_triggers'],
            'is_monitoring': self.is_running
        }
    
    def get_recent_triggers(self, limit: int = 20) -> List[Dict]:
        """获取最近的触发记录"""
        return list(self.trigger_history)[-limit:]
    
    def clear_alert_history(self, before_date: Optional[datetime] = None):
        """清理预警历史"""
        if before_date is None:
            before_date = datetime.now() - timedelta(days=30)  # 默认清理30天前的记录
        
        self.alert_triggers = [
            t for t in self.alert_triggers
            if t.triggered_at > before_date
        ]
        
        logger.info(f"清理了 {before_date} 之前的预警历史")
    
    async def mark_false_trigger(self, trigger_id: int):
        """标记误报"""
        self.alert_stats['false_triggers'] += 1
        logger.info(f"标记误报: trigger_id={trigger_id}")
    
    async def get_alert_performance(self, alert_id: int) -> Dict[str, Any]:
        """获取单个预警的性能指标"""
        triggers = [t for t in self.alert_triggers if t.alert_id == alert_id]
        
        if not triggers:
            return {
                'alert_id': alert_id,
                'total_triggers': 0,
                'average_interval': 0,
                'last_trigger': None
            }
        
        # 计算平均触发间隔
        if len(triggers) > 1:
            intervals = []
            for i in range(1, len(triggers)):
                interval = (triggers[i].triggered_at - triggers[i-1].triggered_at).total_seconds()
                intervals.append(interval)
            average_interval = sum(intervals) / len(intervals)
        else:
            average_interval = 0
        
        return {
            'alert_id': alert_id,
            'total_triggers': len(triggers),
            'average_interval_seconds': average_interval,
            'last_trigger': triggers[-1].triggered_at.isoformat() if triggers else None,
            'first_trigger': triggers[0].triggered_at.isoformat() if triggers else None
        }
    
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
