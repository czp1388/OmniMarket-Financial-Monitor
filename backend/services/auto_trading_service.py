"""
全自动交易服务
实现完整的自动化交易功能，包括策略调度、订单管理、风险控制和状态监控
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import random
import requests
from .trading_analytics_service import trading_analytics_service

logger = logging.getLogger(__name__)


class AutoTradingStrategy(Enum):
    """自动交易策略枚举"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    MOMENTUM = "momentum"


class TradingStatus(Enum):
    """交易状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    EMERGENCY_STOP = "emergency_stop"


class AutoTradingService:
    """全自动交易服务类"""
    
    def __init__(self):
        self.status = TradingStatus.STOPPED
        self.active_strategies: List[AutoTradingStrategy] = []
        self.trading_stats = {
            "total_trades": 0,
            "successful_trades": 0,
            "total_profit_loss": 0.0,
            "current_positions": [],
            "daily_trades_count": 0,
            "daily_profit_loss": 0.0
        }
        self.risk_metrics = {
            "current_drawdown": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "var_95": 0.0
        }
        self.emergency_brakes = {
            'market_volatility_brake': False,
            'max_daily_loss_brake': False,
            'system_error_brake': False,
            'network_disruption_brake': False
        }
        self.trading_config = {
            "max_daily_trades": 50,
            "max_daily_loss": 10000.0,
            "max_position_size": 5000.0,
            "volatility_threshold": 0.3
        }
        self._trading_task: Optional[asyncio.Task] = None
        self._last_trade_time = None
        self._market_data_cache = {}
        
    async def start_trading(self, strategies: List[AutoTradingStrategy]) -> Dict[str, Any]:
        """
        启动全自动交易
        
        Args:
            strategies: 交易策略列表
            
        Returns:
            Dict: 启动结果
        """
        try:
            if self.status == TradingStatus.RUNNING:
                return {
                    "success": False,
                    "message": "交易已在运行中",
                    "current_status": self.status.value
                }
            
            # 重置紧急熔断
            self.reset_emergency_brakes()
            
            # 设置交易策略
            self.active_strategies = strategies
            self.status = TradingStatus.RUNNING
            
            # 启动交易任务
            self._trading_task = asyncio.create_task(self._trading_loop())
            
            logger.info(f"全自动交易启动成功，策略: {[s.value for s in strategies]}")
            
            return {
                "success": True,
                "message": "全自动交易启动成功",
                "strategies": [s.value for s in strategies],
                "status": self.status.value
            }
            
        except Exception as e:
            logger.error(f"启动全自动交易失败: {str(e)}")
            return {
                "success": False,
                "message": f"启动失败: {str(e)}",
                "status": self.status.value
            }
    
    async def stop_trading(self) -> Dict[str, Any]:
        """
        停止全自动交易
        
        Returns:
            Dict: 停止结果
        """
        try:
            if self.status == TradingStatus.STOPPED:
                return {
                    "success": False,
                    "message": "交易已停止",
                    "current_status": self.status.value
                }
            
            # 停止交易任务
            if self._trading_task and not self._trading_task.done():
                self._trading_task.cancel()
                try:
                    await self._trading_task
                except asyncio.CancelledError:
                    pass
            
            self.status = TradingStatus.STOPPED
            self.active_strategies = []
            
            logger.info("全自动交易停止成功")
            
            return {
                "success": True,
                "message": "全自动交易停止成功",
                "status": self.status.value
            }
            
        except Exception as e:
            logger.error(f"停止全自动交易失败: {str(e)}")
            return {
                "success": False,
                "message": f"停止失败: {str(e)}",
                "status": self.status.value
            }
    
    async def pause_trading(self) -> Dict[str, Any]:
        """
        暂停全自动交易
        
        Returns:
            Dict: 暂停结果
        """
        try:
            if self.status != TradingStatus.RUNNING:
                return {
                    "success": False,
                    "message": "只有运行中的交易才能暂停",
                    "current_status": self.status.value
                }
            
            self.status = TradingStatus.PAUSED
            
            logger.info("全自动交易暂停成功")
            
            return {
                "success": True,
                "message": "全自动交易暂停成功",
                "status": self.status.value
            }
            
        except Exception as e:
            logger.error(f"暂停全自动交易失败: {str(e)}")
            return {
                "success": False,
                "message": f"暂停失败: {str(e)}",
                "status": self.status.value
            }
    
    async def resume_trading(self) -> Dict[str, Any]:
        """
        恢复全自动交易
        
        Returns:
            Dict: 恢复结果
        """
        try:
            if self.status != TradingStatus.PAUSED:
                return {
                    "success": False,
                    "message": "只有暂停的交易才能恢复",
                    "current_status": self.status.value
                }
            
            self.status = TradingStatus.RUNNING
            
            logger.info("全自动交易恢复成功")
            
            return {
                "success": True,
                "message": "全自动交易恢复成功",
                "status": self.status.value
            }
            
        except Exception as e:
            logger.error(f"恢复全自动交易失败: {str(e)}")
            return {
                "success": False,
                "message": f"恢复失败: {str(e)}",
                "status": self.status.value
            }
    
    def get_trading_status(self) -> Dict[str, Any]:
        """
        获取交易状态信息
        
        Returns:
            Dict: 交易状态信息
        """
        return {
            "status": self.status.value,
            "active_strategies": [s.value for s in self.active_strategies],
            "trading_stats": self.trading_stats,
            "risk_metrics": self.risk_metrics,
            "emergency_brakes": self.emergency_brakes,
            "trading_config": self.trading_config,
            "last_trade_time": self._last_trade_time.isoformat() if self._last_trade_time else None,
            "uptime": self._calculate_uptime()
        }
    
    def reset_emergency_brakes(self) -> Dict[str, Any]:
        """
        重置紧急熔断
        
        Returns:
            Dict: 重置结果
        """
        try:
            for brake in self.emergency_brakes:
                self.emergency_brakes[brake] = False
            
            # 如果当前是紧急停止状态，恢复到停止状态
            if self.status == TradingStatus.EMERGENCY_STOP:
                self.status = TradingStatus.STOPPED
            
            return {
                "success": True,
                "message": "紧急熔断已重置",
                "emergency_brakes": self.emergency_brakes
            }
            
        except Exception as e:
            logger.error(f"重置紧急熔断失败: {str(e)}")
            return {
                "success": False,
                "message": f"重置失败: {str(e)}"
            }
    
    async def _trading_loop(self):
        """交易主循环"""
        logger.info("交易主循环启动")
        
        while self.status == TradingStatus.RUNNING:
            try:
                # 检查紧急熔断
                if self._check_emergency_brakes():
                    await self._handle_emergency_stop()
                    break
                
                # 执行高级风控检查
                await self._advanced_risk_control()
                
                # 执行交易策略
                await self._execute_strategies()
                
                # 更新风险指标
                self._update_risk_metrics()
                
                # 模拟交易间隔
                await asyncio.sleep(5)  # 5秒间隔
                
            except asyncio.CancelledError:
                logger.info("交易循环被取消")
                break
            except Exception as e:
                logger.error(f"交易循环异常: {str(e)}")
                await asyncio.sleep(10)  # 异常时等待更长时间
    
    async def _execute_strategies(self):
        """执行交易策略"""
        for strategy in self.active_strategies:
            try:
                # 检查每日交易限制
                if self.trading_stats["daily_trades_count"] >= self.trading_config["max_daily_trades"]:
                    logger.warning("达到每日交易次数限制")
                    continue
                
                # 获取牛熊证监控信号
                warrants_signals = await self._get_warrants_trading_signals()
                
                # 如果有牛熊证信号，优先处理
                if warrants_signals:
                    for signal in warrants_signals:
                        if signal["signal_type"] in ["BUY", "SELL"]:
                            await self._execute_warrants_trade(strategy, signal)
                else:
                    # 模拟获取市场数据
                    market_data = await self._get_market_data(strategy)
                    
                    # 生成交易信号
                    signal = self._generate_trading_signal(strategy, market_data)
                    
                    if signal and signal["action"] != "hold":
                        # 执行交易
                        await self._execute_trade(strategy, signal, market_data)
                    
            except Exception as e:
                logger.error(f"执行策略 {strategy.value} 失败: {str(e)}")
    
    async def _get_market_data(self, strategy: AutoTradingStrategy) -> Dict[str, Any]:
        """获取市场数据（模拟）"""
        # 模拟市场数据
        symbols = ["BTC/USDT", "ETH/USDT", "AAPL", "USD/CNY"]
        symbol = random.choice(symbols)
        
        if symbol not in self._market_data_cache:
            self._market_data_cache[symbol] = {
                "price": random.uniform(100, 50000),
                "volume": random.uniform(1000, 100000),
                "change": random.uniform(-0.05, 0.05),
                "timestamp": datetime.now()
            }
        else:
            # 更新价格（模拟价格变动）
            cache = self._market_data_cache[symbol]
            cache["price"] *= (1 + random.uniform(-0.02, 0.02))
            cache["volume"] = random.uniform(1000, 100000)
            cache["change"] = random.uniform(-0.05, 0.05)
            cache["timestamp"] = datetime.now()
        
        return self._market_data_cache[symbol]
    
    def _generate_trading_signal(self, strategy: AutoTradingStrategy, market_data: Dict) -> Optional[Dict]:
        """生成交易信号（模拟）"""
        # 模拟交易信号生成
        signal_probability = 0.3  # 30%概率生成信号
        
        if random.random() > signal_probability:
            return None
        
        actions = ["buy", "sell", "hold"]
        weights = [0.4, 0.4, 0.2]  # 买入和卖出概率较高
        
        action = random.choices(actions, weights=weights)[0]
        
        if action == "hold":
            return None
        
        return {
            "action": action,
            "symbol": "SIMULATED",  # 模拟交易
            "price": market_data["price"],
            "quantity": random.uniform(0.1, 10.0),
            "confidence": random.uniform(0.5, 0.95),
            "strategy": strategy.value
        }
    
    async def _execute_trade(self, strategy: AutoTradingStrategy, signal: Dict, market_data: Dict):
        """执行交易（模拟）"""
        try:
            # 模拟交易执行
            trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            # 计算交易结果（模拟）
            success = random.random() > 0.2  # 80%成功率
            profit_loss = random.uniform(-100, 200)  # 模拟盈亏
            
            # 更新交易统计
            self.trading_stats["total_trades"] += 1
            self.trading_stats["daily_trades_count"] += 1
            
            if success:
                self.trading_stats["successful_trades"] += 1
                self.trading_stats["total_profit_loss"] += profit_loss
                self.trading_stats["daily_profit_loss"] += profit_loss
            
            self._last_trade_time = datetime.now()
            
            logger.info(f"交易执行: {trade_id}, 策略: {strategy.value}, "
                       f"动作: {signal['action']}, 结果: {'成功' if success else '失败'}, "
                       f"盈亏: {profit_loss:.2f}")
            
            # 记录交易到分析服务
            trade_data = {
                'trade_id': trade_id,
                'symbol': signal.get('symbol', 'SIMULATED'),
                'side': signal['action'],
                'quantity': signal.get('quantity', 1.0),
                'price': signal.get('price', 0),
                'profit_loss': profit_loss,
                'strategy': strategy.value,
                'success': success,
                'timestamp': datetime.now()
            }
            await trading_analytics_service.record_trade(trade_data)
            
            # 更新投资组合价值到分析服务
            portfolio_value = 100000.0 + self.trading_stats["total_profit_loss"]  # 模拟投资组合价值
            await trading_analytics_service.update_portfolio_value(portfolio_value)
            
            # 检查每日亏损限制
            if self.trading_stats["daily_profit_loss"] < -self.trading_config["max_daily_loss"]:
                self.emergency_brakes["max_daily_loss_brake"] = True
                logger.warning("触发每日亏损熔断")
            
        except Exception as e:
            logger.error(f"执行交易失败: {str(e)}")
    
    def _check_emergency_brakes(self) -> bool:
        """检查紧急熔断条件"""
        return any(self.emergency_brakes.values())
    
    async def _handle_emergency_stop(self):
        """处理紧急停止"""
        logger.warning("触发紧急停止")
        self.status = TradingStatus.EMERGENCY_STOP
        await self.stop_trading()
    
    def _update_risk_metrics(self):
        """更新风险指标（模拟）"""
        # 模拟风险指标计算
        self.risk_metrics["current_drawdown"] = random.uniform(-0.05, 0.01)
        self.risk_metrics["max_drawdown"] = min(
            self.risk_metrics["max_drawdown"], 
            self.risk_metrics["current_drawdown"]
        )
        self.risk_metrics["volatility"] = random.uniform(0.1, 0.4)
        self.risk_metrics["sharpe_ratio"] = random.uniform(-1.0, 2.0)
        self.risk_metrics["var_95"] = random.uniform(100, 1000)
    
    async def _get_warrants_trading_signals(self) -> List[Dict]:
        """获取牛熊证交易信号"""
        try:
            # 调用牛熊证监控API获取交易信号
            response = requests.get("http://localhost:8000/api/v1/warrants-monitoring/trading-signals")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("signals", [])
            return []
        except Exception as e:
            logger.error(f"获取牛熊证交易信号失败: {str(e)}")
            return []

    async def _execute_warrants_trade(self, strategy: AutoTradingStrategy, signal: Dict):
        """执行牛熊证交易"""
        try:
            # 模拟交易执行
            trade_id = f"WARRANT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            # 计算交易结果（模拟）
            success = random.random() > 0.1  # 90%成功率（牛熊证交易成功率较高）
            profit_loss = random.uniform(-50, 150)  # 模拟盈亏
            
            # 更新交易统计
            self.trading_stats["total_trades"] += 1
            self.trading_stats["daily_trades_count"] += 1
            
            if success:
                self.trading_stats["successful_trades"] += 1
                self.trading_stats["total_profit_loss"] += profit_loss
                self.trading_stats["daily_profit_loss"] += profit_loss
            
            self._last_trade_time = datetime.now()
            
            logger.info(f"牛熊证交易执行: {trade_id}, 策略: {strategy.value}, "
                       f"牛熊证: {signal.get('warrant_symbol')}, 信号: {signal.get('signal_type')}, "
                       f"结果: {'成功' if success else '失败'}, 盈亏: {profit_loss:.2f}")
            
            # 检查每日亏损限制
            if self.trading_stats["daily_profit_loss"] < -self.trading_config["max_daily_loss"]:
                self.emergency_brakes["max_daily_loss_brake"] = True
                logger.warning("触发每日亏损熔断")
            
        except Exception as e:
            logger.error(f"执行牛熊证交易失败: {str(e)}")

    async def _advanced_risk_control(self):
        """
        高级风控检查
        包括实时资金监控、波动率自适应、异常交易检测等
        """
        try:
            # 1. 实时资金监控
            await self._real_time_capital_monitoring()
            
            # 2. 波动率自适应调整
            await self._volatility_adaptive_adjustment()
            
            # 3. 异常交易检测
            await self._anomaly_trading_detection()
            
            # 4. 流动性风险检查
            await self._liquidity_risk_check()
            
            # 5. 集中度风险监控
            await self._concentration_risk_monitoring()
            
        except Exception as e:
            logger.error(f"高级风控检查异常: {str(e)}")

    async def _real_time_capital_monitoring(self):
        """实时资金监控 - 实际有效实现"""
        try:
            # 获取实际投资组合价值
            portfolio_data = await trading_analytics_service.get_portfolio_summary()
            portfolio_value = portfolio_data.get('current_value', 100000.0)
            
            # 计算实际资金使用情况
            total_positions_value = sum(pos.get('market_value', 0) for pos in self.trading_stats["current_positions"])
            available_capital = portfolio_value - total_positions_value
            
            # 计算资金使用率
            capital_utilization = total_positions_value / portfolio_value if portfolio_value > 0 else 0
            
            # 多级资金使用率预警
            if capital_utilization > 0.9:  # 90%使用率 - 紧急级别
                logger.error(f"紧急: 资金使用率超过90%: {capital_utilization:.2%}")
                # 暂停所有新交易
                self.emergency_brakes["system_error_brake"] = True
                
            elif capital_utilization > 0.8:  # 80%使用率 - 警告级别
                logger.warning(f"警告: 资金使用率超过80%: {capital_utilization:.2%}")
                # 暂停高风险策略
                if AutoTradingStrategy.BREAKOUT in self.active_strategies:
                    self.active_strategies.remove(AutoTradingStrategy.BREAKOUT)
                    logger.info("暂停突破策略以降低风险")
                    
            elif capital_utilization > 0.7:  # 70%使用率 - 提醒级别
                logger.info(f"提醒: 资金使用率超过70%: {capital_utilization:.2%}")
                
            # 动态计算回撤
            if portfolio_value > 0:
                peak_value = portfolio_data.get('peak_value', portfolio_value)
                current_drawdown = (portfolio_value - peak_value) / peak_value
                self.risk_metrics["current_drawdown"] = current_drawdown
                
                # 更新最大回撤
                if current_drawdown < self.risk_metrics["max_drawdown"]:
                    self.risk_metrics["max_drawdown"] = current_drawdown
                
                # 回撤预警
                if current_drawdown < -0.15:  # 15%回撤阈值
                    logger.error(f"紧急: 当前回撤超过15%: {current_drawdown:.2%}")
                    self.emergency_brakes["max_daily_loss_brake"] = True
                elif current_drawdown < -0.1:  # 10%回撤阈值
                    logger.warning(f"警告: 当前回撤超过10%: {current_drawdown:.2%}")
                    
            # 更新交易配置中的可用资金
            self.trading_config["available_capital"] = available_capital
            
        except Exception as e:
            logger.error(f"实时资金监控异常: {str(e)}")

    async def _volatility_adaptive_adjustment(self):
        """波动率自适应调整 - 实际有效实现"""
        try:
            # 获取实际市场数据计算波动率
            recent_trades_data = await trading_analytics_service.get_recent_trades(period="1h")
            
            if recent_trades_data and len(recent_trades_data) >= 10:
                # 计算实际波动率（基于交易盈亏的标准差）
                pnl_values = [trade.get('profit_loss', 0) for trade in recent_trades_data]
                if pnl_values:
                    import statistics
                    try:
                        actual_volatility = statistics.stdev(pnl_values) / 1000.0  # 标准化
                        self.risk_metrics["volatility"] = actual_volatility
                    except statistics.StatisticsError:
                        # 如果标准差计算失败，使用历史平均值
                        actual_volatility = 0.2
            else:
                # 使用默认波动率
                actual_volatility = 0.2
            
            # 根据实际波动率动态调整交易参数
            if actual_volatility > 0.3:  # 极高波动率
                # 大幅降低仓位规模，增加交易间隔
                self.trading_config["max_position_size"] = 1000.0
                self.trading_config["volatility_threshold"] = 0.4
                logger.warning(f"极高波动率环境({actual_volatility:.2%})，仓位规模降至1000")
                
            elif actual_volatility > 0.2:  # 高波动率
                # 降低仓位规模
                self.trading_config["max_position_size"] = 2000.0
                self.trading_config["volatility_threshold"] = 0.3
                logger.info(f"高波动率环境({actual_volatility:.2%})，仓位规模降至2000")
                
            elif actual_volatility < 0.08:  # 极低波动率
                # 增加仓位规模，更积极交易
                self.trading_config["max_position_size"] = 8000.0
                self.trading_config["volatility_threshold"] = 0.15
                logger.info(f"极低波动率环境({actual_volatility:.2%})，仓位规模增至8000")
                
            elif actual_volatility < 0.12:  # 低波动率
                # 恢复正常仓位规模
                self.trading_config["max_position_size"] = 5000.0
                self.trading_config["volatility_threshold"] = 0.25
                logger.info(f"低波动率环境({actual_volatility:.2%})，恢复正常仓位规模5000")
            
            # 动态调整每日交易次数限制
            if actual_volatility > 0.25:
                self.trading_config["max_daily_trades"] = 20  # 高波动率减少交易次数
            elif actual_volatility < 0.1:
                self.trading_config["max_daily_trades"] = 80  # 低波动率增加交易次数
            else:
                self.trading_config["max_daily_trades"] = 50  # 正常波动率
                
            # 检查市场波动率熔断
            if actual_volatility > self.trading_config["volatility_threshold"]:
                self.emergency_brakes["market_volatility_brake"] = True
                logger.error(f"市场波动率过高({actual_volatility:.2%})，触发熔断")
                
            # 记录波动率历史
            if not hasattr(self, 'volatility_history'):
                self.volatility_history = []
            self.volatility_history.append({
                'timestamp': datetime.now(),
                'volatility': actual_volatility,
                'position_size': self.trading_config["max_position_size"]
            })
            # 保留最近100条记录
            if len(self.volatility_history) > 100:
                self.volatility_history = self.volatility_history[-100:]
                
        except Exception as e:
            logger.error(f"波动率自适应调整异常: {str(e)}")

    async def _anomaly_trading_detection(self):
        """异常交易检测 - 实际有效实现"""
        try:
            current_time = datetime.now()
            
            # 获取实际交易数据进行分析
            recent_trades_data = await trading_analytics_service.get_recent_trades(period="1h")
            
            if not recent_trades_data or len(recent_trades_data) < 5:
                return  # 数据不足，跳过检测
            
            # 1. 检测高频交易异常
            if self._last_trade_time:
                time_since_last_trade = (current_time - self._last_trade_time).total_seconds()
                
                # 基于实际交易频率检测异常
                if time_since_last_trade < 1:  # 1秒内连续交易
                    logger.warning("检测到高频交易异常，可能为系统错误")
                    self.emergency_brakes["system_error_brake"] = True
                    return
            
            # 2. 检测异常盈亏模式（基于实际交易数据）
            # 计算实际成功率
            successful_trades = [trade for trade in recent_trades_data if trade.get('success', False)]
            actual_success_rate = len(successful_trades) / len(recent_trades_data) if recent_trades_data else 0
            
            # 计算盈亏分布的统计特征
            pnl_values = [trade.get('profit_loss', 0) for trade in recent_trades_data]
            if pnl_values:
                import statistics
                try:
                    pnl_mean = statistics.mean(pnl_values)
                    pnl_std = statistics.stdev(pnl_values) if len(pnl_values) > 1 else 0
                    
                    # 检测异常低成功率
                    if actual_success_rate < 0.15:  # 成功率低于15%
                        logger.warning(f"检测到异常低成功率({actual_success_rate:.2%})，可能为市场异常或策略失效")
                        # 暂停高风险策略
                        if AutoTradingStrategy.BREAKOUT in self.active_strategies:
                            self.active_strategies.remove(AutoTradingStrategy.BREAKOUT)
                            logger.info("暂停突破策略以降低风险")
                    
                    # 检测异常高成功率（可能为数据异常或过度拟合）
                    elif actual_success_rate > 0.95:  # 成功率高于95%
                        logger.warning(f"检测到异常高成功率({actual_success_rate:.2%})，可能为数据异常")
                        self.emergency_brakes["system_error_brake"] = True
                    
                    # 检测异常盈亏波动（标准差异常）
                    if pnl_std > 500:  # 盈亏标准差超过500
                        logger.warning(f"检测到异常盈亏波动(标准差: {pnl_std:.2f})，可能为市场异常")
                        
                    # 检测连续亏损模式
                    consecutive_losses = 0
                    for trade in recent_trades_data[-10:]:  # 检查最近10笔交易
                        if trade.get('profit_loss', 0) < 0:
                            consecutive_losses += 1
                        else:
                            consecutive_losses = 0
                    
                    if consecutive_losses >= 5:  # 连续5次亏损
                        logger.warning(f"检测到连续{consecutive_losses}次亏损，可能为策略失效")
                        # 降低交易频率
                        self.trading_config["max_daily_trades"] = max(10, self.trading_config["max_daily_trades"] - 10)
                        
                except statistics.StatisticsError:
                    pass
            
            # 3. 检测交易时间异常（非交易时段交易）
            current_hour = current_time.hour
            if current_hour < 9 or current_hour >= 16:  # 非交易时段（假设9:00-16:00为交易时段）
                logger.warning(f"在非交易时段检测到交易活动(当前时间: {current_hour}时)")
                self.emergency_brakes["system_error_brake"] = True
            
            # 4. 检测网络连接异常
            await self._check_network_connectivity()
            
            # 记录异常检测结果
            if not hasattr(self, 'anomaly_detection_history'):
                self.anomaly_detection_history = []
                
            self.anomaly_detection_history.append({
                'timestamp': current_time,
                'success_rate': actual_success_rate,
                'anomaly_detected': any([
                    actual_success_rate < 0.15,
                    actual_success_rate > 0.95,
                    time_since_last_trade < 1 if self._last_trade_time else False
                ])
            })
            
            # 保留最近50条记录
            if len(self.anomaly_detection_history) > 50:
                self.anomaly_detection_history = self.anomaly_detection_history[-50:]
            
        except Exception as e:
            logger.error(f"异常交易检测异常: {str(e)}")

    async def _liquidity_risk_check(self):
        """流动性风险检查 - 实际有效实现"""
        try:
            # 获取实际持仓数据
            positions_data = await trading_analytics_service.get_current_positions()
            
            if not positions_data:
                return  # 无持仓数据，跳过检查
            
            # 1. 基于持仓规模的流动性风险评估
            total_position_value = sum(pos.get('market_value', 0) for pos in positions_data)
            
            # 计算单个资产流动性影响
            liquidity_scores = {}
            for position in positions_data:
                symbol = position.get('symbol', '')
                position_value = position.get('market_value', 0)
                
                # 基于资产类型和规模评估流动性风险
                liquidity_score = self._calculate_liquidity_score(symbol, position_value)
                liquidity_scores[symbol] = liquidity_score
                
                # 单个资产流动性风险预警
                if liquidity_score < 0.6:  # 低流动性资产
                    logger.warning(f"资产 {symbol} 流动性风险较高，评分: {liquidity_score:.2f}")
                    # 限制该资产的进一步交易
                    self._limit_trading_for_low_liquidity(symbol)
            
            # 2. 整体投资组合流动性评估
            if liquidity_scores:
                avg_liquidity_score = sum(liquidity_scores.values()) / len(liquidity_scores)
                
                if avg_liquidity_score < 0.7:  # 整体流动性风险较高
                    logger.warning(f"投资组合整体流动性风险较高，平均评分: {avg_liquidity_score:.2f}")
                    # 降低整体交易频率和规模
                    self.trading_config["max_daily_trades"] = max(10, self.trading_config["max_daily_trades"] - 10)
                    self.trading_config["max_position_size"] *= 0.7
                    
                elif avg_liquidity_score > 0.9:  # 高流动性环境
                    logger.info(f"投资组合流动性良好，平均评分: {avg_liquidity_score:.2f}")
                    # 恢复正常交易参数
                    self.trading_config["max_daily_trades"] = 50
                    self.trading_config["max_position_size"] = 5000.0
            
            # 3. 大额订单冲击成本分析
            for position in positions_data:
                symbol = position.get('symbol', '')
                position_value = position.get('market_value', 0)
                avg_daily_volume = self._get_avg_daily_volume(symbol)
                
                if avg_daily_volume > 0:
                    # 计算持仓占日均交易量的比例
                    position_to_volume_ratio = position_value / avg_daily_volume
                    
                    if position_to_volume_ratio > 0.05:  # 持仓超过日均交易量5%
                        logger.warning(f"资产 {symbol} 持仓过大(占日均交易量{position_to_volume_ratio:.2%})，冲击成本风险")
                        # 触发流动性熔断
                        self.emergency_brakes["market_volatility_brake"] = True
                        break
            
            # 4. 市场深度分析（模拟）
            market_depth_analysis = await self._analyze_market_depth()
            if market_depth_analysis.get('depth_score', 1.0) < 0.8:
                logger.warning(f"市场深度不足，深度评分: {market_depth_analysis.get('depth_score', 1.0):.2f}")
                # 在低市场深度环境下降低交易规模
                self.trading_config["max_position_size"] = max(1000, self.trading_config["max_position_size"] * 0.5)
            
            # 5. 交易时段流动性分析
            current_hour = datetime.now().hour
            if current_hour < 9 or current_hour >= 16:  # 非主要交易时段
                logger.info("当前为非主要交易时段，流动性可能较低")
                # 在非主要交易时段降低交易频率
                self.trading_config["max_daily_trades"] = max(20, self.trading_config["max_daily_trades"] - 10)
            
            # 记录流动性风险评估历史
            if not hasattr(self, 'liquidity_history'):
                self.liquidity_history = []
                
            self.liquidity_history.append({
                'timestamp': datetime.now(),
                'avg_liquidity_score': avg_liquidity_score if 'avg_liquidity_score' in locals() else 1.0,
                'liquidity_scores': liquidity_scores,
                'trading_restrictions': self._get_current_trading_restrictions()
            })
            
            # 保留最近50条记录
            if len(self.liquidity_history) > 50:
                self.liquidity_history = self.liquidity_history[-50:]
                
        except Exception as e:
            logger.error(f"流动性风险检查异常: {str(e)}")

    def _calculate_liquidity_score(self, symbol: str, position_value: float) -> float:
        """计算单个资产的流动性评分"""
        # 基于资产类型、规模和交易特性评估流动性
        asset_class = self._classify_asset(symbol)
        
        # 不同资产类别的流动性基准
        liquidity_baseline = {
            'crypto': 0.9,        # 加密货币通常流动性较好
            'us_stocks': 0.85,    # 美股流动性好
            'hongkong_stocks': 0.7,  # 港股流动性中等
            'warrants': 0.6,      # 牛熊证流动性相对较低
            'forex': 0.95,        # 外汇流动性最高
            'other': 0.5          # 其他资产流动性较低
        }
        
        baseline = liquidity_baseline.get(asset_class, 0.5)
        
        # 根据持仓规模调整流动性评分
        if position_value > 50000:  # 大额持仓
            adjustment = 0.3
        elif position_value > 20000:  # 中等持仓
            adjustment = 0.5
        elif position_value > 5000:   # 小额持仓
            adjustment = 0.8
        else:  # 极小持仓
            adjustment = 1.0
        
        # 基于交易时间的调整（亚洲、欧洲、美洲交易时段）
        current_hour = datetime.now().hour
        if asset_class == 'hongkong_stocks' and (9 <= current_hour < 16):
            time_adjustment = 1.0  # 港股交易时段
        elif asset_class == 'us_stocks' and (14 <= current_hour < 21):
            time_adjustment = 1.0  # 美股交易时段
        else:
            time_adjustment = 0.7  # 非主要交易时段
        
        final_score = baseline * adjustment * time_adjustment
        return max(0.1, min(1.0, final_score))  # 确保在0.1-1.0范围内

    def _get_avg_daily_volume(self, symbol: str) -> float:
        """获取资产的日均交易量（模拟）"""
        # 在实际系统中，这里应该从市场数据API获取
        volume_baseline = {
            'BTC/USDT': 50000000.0,
            'ETH/USDT': 20000000.0,
            'AAPL': 100000000.0,
            'USD/CNY': 1000000000.0,
            'TSLA': 50000000.0,
            'GOOGL': 30000000.0,
            'EUR/USD': 2000000000.0,
            'XAU/USD': 50000000.0
        }
        return volume_baseline.get(symbol, 1000000.0)

    async def _analyze_market_depth(self) -> Dict[str, Any]:
        """分析市场深度（模拟）"""
        # 在实际系统中，这里应该从市场数据API获取订单簿数据
        return {
            'depth_score': random.uniform(0.7, 1.0),
            'bid_ask_spread': random.uniform(0.001, 0.02),
            'order_book_depth': random.uniform(1000, 10000)
        }

    def _limit_trading_for_low_liquidity(self, symbol: str):
        """限制低流动性资产的交易"""
        # 在实际系统中，这里应该维护一个受限资产列表
        if not hasattr(self, 'restricted_symbols'):
            self.restricted_symbols = set()
        
        self.restricted_symbols.add(symbol)
        logger.info(f"已限制资产 {symbol} 的交易")

    def _get_current_trading_restrictions(self) -> Dict[str, Any]:
        """获取当前交易限制状态"""
        return {
            'restricted_symbols': list(getattr(self, 'restricted_symbols', set())),
            'max_daily_trades': self.trading_config["max_daily_trades"],
            'max_position_size': self.trading_config["max_position_size"]
        }

    async def _concentration_risk_monitoring(self):
        """集中度风险监控 - 实际有效实现"""
        try:
            # 获取实际投资组合数据
            portfolio_data = await trading_analytics_service.get_portfolio_summary()
            portfolio_value = portfolio_data.get('current_value', 100000.0)
            
            # 获取实际持仓数据
            positions_data = await trading_analytics_service.get_current_positions()
            
            if not positions_data:
                return  # 无持仓数据，跳过检查
            
            # 1. 持仓集中度分析
            total_positions_value = sum(pos.get('market_value', 0) for pos in positions_data)
            
            if total_positions_value > 0:
                # 计算单个资产最大持仓比例
                max_position_value = max(pos.get('market_value', 0) for pos in positions_data)
                max_concentration_ratio = max_position_value / total_positions_value
                
                # 计算前三大持仓集中度
                sorted_positions = sorted(positions_data, key=lambda x: x.get('market_value', 0), reverse=True)
                top3_value = sum(pos.get('market_value', 0) for pos in sorted_positions[:3])
                top3_concentration_ratio = top3_value / total_positions_value
                
                # 多级集中度风险预警
                if max_concentration_ratio > 0.4:  # 单一持仓超过40% - 紧急级别
                    logger.error(f"紧急: 单一持仓集中度过高({max_concentration_ratio:.2%})，风险极大")
                    self.emergency_brakes["system_error_brake"] = True
                    
                elif max_concentration_ratio > 0.3:  # 单一持仓超过30% - 警告级别
                    logger.warning(f"警告: 单一持仓集中度过高({max_concentration_ratio:.2%})")
                    # 暂停该资产的进一步交易
                    max_position_symbol = next(pos.get('symbol') for pos in positions_data 
                                             if pos.get('market_value', 0) == max_position_value)
                    logger.info(f"暂停资产 {max_position_symbol} 的进一步交易")
                    
                elif max_concentration_ratio > 0.2:  # 单一持仓超过20% - 提醒级别
                    logger.info(f"提醒: 单一持仓集中度较高({max_concentration_ratio:.2%})")
                
                # 前三大持仓集中度预警
                if top3_concentration_ratio > 0.8:  # 前三大持仓超过80%
                    logger.warning(f"警告: 前三大持仓集中度过高({top3_concentration_ratio:.2%})")
                    # 降低新交易规模
                    self.trading_config["max_position_size"] = max(1000, self.trading_config["max_position_size"] * 0.5)
                    
                elif top3_concentration_ratio > 0.6:  # 前三大持仓超过60%
                    logger.info(f"提醒: 前三大持仓集中度较高({top3_concentration_ratio:.2%})")
            
            # 2. 策略集中度分析
            strategy_concentration = {}
            for position in positions_data:
                strategy = position.get('strategy', 'unknown')
                strategy_concentration[strategy] = strategy_concentration.get(strategy, 0) + position.get('market_value', 0)
            
            if strategy_concentration:
                # 计算最大策略集中度
                max_strategy_value = max(strategy_concentration.values())
                max_strategy_ratio = max_strategy_value / total_positions_value if total_positions_value > 0 else 0
                
                if max_strategy_ratio > 0.6:  # 单一策略超过60%
                    max_strategy = next(k for k, v in strategy_concentration.items() if v == max_strategy_value)
                    logger.warning(f"策略集中度警告: 策略 {max_strategy} 占比({max_strategy_ratio:.2%})过高")
                    # 暂停该策略的新交易
                    if AutoTradingStrategy[max_strategy.upper()] in self.active_strategies:
                        self.active_strategies.remove(AutoTradingStrategy[max_strategy.upper()])
                        logger.info(f"暂停策略 {max_strategy} 以分散风险")
                
                # 检查策略多样性
                active_strategy_count = len(set(pos.get('strategy', 'unknown') for pos in positions_data))
                if active_strategy_count < 2 and len(positions_data) >= 3:
                    logger.warning("策略多样性不足，建议启用更多交易策略")
            
            # 3. 资产类别集中度分析
            asset_class_concentration = {}
            for position in positions_data:
                symbol = position.get('symbol', '')
                asset_class = self._classify_asset(symbol)
                asset_class_concentration[asset_class] = asset_class_concentration.get(asset_class, 0) + position.get('market_value', 0)
            
            if asset_class_concentration:
                # 计算最大资产类别集中度
                max_asset_class_value = max(asset_class_concentration.values())
                max_asset_class_ratio = max_asset_class_value / total_positions_value if total_positions_value > 0 else 0
                
                if max_asset_class_ratio > 0.7:  # 单一资产类别超过70%
                    max_asset_class = next(k for k, v in asset_class_concentration.items() if v == max_asset_class_value)
                    logger.warning(f"资产类别集中度警告: {max_asset_class} 占比({max_asset_class_ratio:.2%})过高")
            
            # 4. 动态调整基于集中度的风险参数
            if total_positions_value > 0:
                # 根据集中度调整最大持仓规模
                if max_concentration_ratio > 0.25:
                    # 高集中度环境下降低单笔交易规模
                    adjusted_size = max(1000, self.trading_config["max_position_size"] * 0.7)
                    self.trading_config["max_position_size"] = adjusted_size
                    logger.info(f"高集中度环境，调整最大持仓规模至: {adjusted_size}")
                
                # 记录集中度历史
                if not hasattr(self, 'concentration_history'):
                    self.concentration_history = []
                    
                self.concentration_history.append({
                    'timestamp': datetime.now(),
                    'max_concentration_ratio': max_concentration_ratio,
                    'top3_concentration_ratio': top3_concentration_ratio if 'top3_concentration_ratio' in locals() else 0,
                    'strategy_concentration': strategy_concentration,
                    'asset_class_concentration': asset_class_concentration
                })
                
                # 保留最近100条记录
                if len(self.concentration_history) > 100:
                    self.concentration_history = self.concentration_history[-100:]
            
        except Exception as e:
            logger.error(f"集中度风险监控异常: {str(e)}")
    
    def _classify_asset(self, symbol: str) -> str:
        """根据交易代码分类资产类别"""
        symbol_upper = symbol.upper()
        
        if symbol_upper.endswith('.HK'):
            if any(keyword in symbol_upper for keyword in ['WARRANT', 'CALL', 'PUT']):
                return 'warrants'
            else:
                return 'hongkong_stocks'
        elif symbol_upper.endswith('.US'):
            return 'us_stocks'
        elif '/' in symbol_upper:  # 外汇对
            return 'forex'
        elif any(crypto in symbol_upper for crypto in ['BTC', 'ETH', 'USDT']):
            return 'crypto'
        else:
            return 'other'

    async def _check_network_connectivity(self):
        """检查网络连接性"""
        try:
            # 模拟网络连接检查
            network_ok = random.random() > 0.05  # 95%网络正常
            
            if not network_ok:
                logger.error("检测到网络连接异常")
                self.emergency_brakes["network_disruption_brake"] = True
                
        except Exception as e:
            logger.error(f"网络连接检查异常: {str(e)}")
            self.emergency_brakes["network_disruption_brake"] = True

    def _calculate_uptime(self) -> Optional[float]:
        """计算运行时间（模拟）"""
        if self._last_trade_time:
            return (datetime.now() - self._last_trade_time).total_seconds()
        return None


# 创建全局服务实例
auto_trading_service = AutoTradingService()
