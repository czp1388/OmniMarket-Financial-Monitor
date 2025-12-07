import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from models.warrants import (
    WarrantData, WarrantMonitoringAlert, WarrantAnalysisResult, 
    WarrantType, WarrantStatus, WarrantTradingSignal, WarrantPortfolio
)
from services.data_service import data_service
from services.technical_analysis_service import technical_analysis_service
from services.auto_trading_service import AutoTradingStrategy
from services.warrants_data_service import warrants_data_service
from services.trading_analytics_service import trading_analytics_service


class WarrantsMonitoringService:
    """牛熊证监控服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_warrants: Dict[str, WarrantData] = {}
        self.active_alerts: Dict[str, WarrantMonitoringAlert] = {}
        self.analysis_results: Dict[str, WarrantAnalysisResult] = {}
        
    async def initialize_monitoring(self):
        """初始化牛熊证监控"""
        self.logger.info("初始化牛熊证监控服务")
        # 这里可以添加初始化的牛熊证数据
        await self.load_sample_warrants()
        
        # 启动实时监控循环
        asyncio.create_task(self._monitoring_loop())
        
    async def _monitoring_loop(self):
        """实时监控循环"""
        while True:
            try:
                # 更新所有活跃牛熊证的指标
                for warrant_symbol in list(self.active_warrants.keys()):
                    await self.update_warrant_metrics(warrant_symbol)
                
                # 生成交易信号
                await self._generate_trading_signals()
                
                # 每30秒更新一次
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"监控循环异常: {str(e)}")
                await asyncio.sleep(60)  # 异常时等待更长时间
        
    async def load_sample_warrants(self):
        """加载牛熊证数据 - 使用数据服务获取真实数据"""
        try:
            # 使用牛熊证数据服务获取牛熊证列表
            warrants_list = await warrants_data_service.get_warrants_list()
            
            if not warrants_list:
                self.logger.warning("未能从数据服务获取牛熊证列表，使用模拟数据")
                warrants_list = await self._get_fallback_warrants()
            
            for warrant in warrants_list:
                self.active_warrants[warrant.symbol] = warrant
                await self.initialize_warrant_monitoring(warrant)
                
            self.logger.info(f"已加载 {len(warrants_list)} 个牛熊证到监控系统")
            
        except Exception as e:
            self.logger.error(f"加载牛熊证数据失败: {str(e)}，使用模拟数据回退")
            await self._load_fallback_warrants()
    
    async def _get_fallback_warrants(self) -> List[WarrantData]:
        """获取回退的模拟牛熊证数据"""
        return [
            WarrantData(
                symbol="12345.HK",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BULL,
                strike_price=180.0,
                knock_out_price=200.0,
                current_price=0.25,
                leverage=15.2,
                time_to_maturity=180,
                status=WarrantStatus.ACTIVE,
                volume=1500000,
                average_volume=800000
            ),
            WarrantData(
                symbol="67890.HK",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BEAR,
                strike_price=220.0,
                knock_out_price=200.0,
                current_price=0.18,
                leverage=12.8,
                time_to_maturity=150,
                status=WarrantStatus.ACTIVE,
                volume=800000,
                average_volume=500000
            )
        ]
    
    async def _load_fallback_warrants(self):
        """加载回退的模拟牛熊证数据"""
        fallback_warrants = await self._get_fallback_warrants()
        for warrant in fallback_warrants:
            self.active_warrants[warrant.symbol] = warrant
            await self.initialize_warrant_monitoring(warrant)
        self.logger.info(f"已加载 {len(fallback_warrants)} 个回退牛熊证")
        
    async def initialize_warrant_monitoring(self, warrant: WarrantData):
        """初始化单个牛熊证监控"""
        try:
            # 计算初始监控指标
            await self.update_warrant_metrics(warrant.symbol)
            
            # 设置初始预警
            await self.setup_initial_alerts(warrant)
            
            self.logger.info(f"已初始化牛熊证监控: {warrant.symbol}")
            
        except Exception as e:
            self.logger.error(f"初始化牛熊证监控失败 {warrant.symbol}: {str(e)}")
            
    async def update_warrant_metrics(self, warrant_symbol: str):
        """更新牛熊证监控指标"""
        if warrant_symbol not in self.active_warrants:
            return
            
        warrant = self.active_warrants[warrant_symbol]
        
        try:
            # 获取实时正股价格（模拟）
            underlying_price = await self.get_underlying_price(warrant.underlying_symbol)
            
            # 计算距回收价幅度
            distance_to_knock_out = self.calculate_distance_to_knock_out(
                warrant.warrant_type, underlying_price, warrant.knock_out_price
            )
            
            # 计算有效杠杆（使用WarrantData模型中的leverage字段）
            effective_leverage = warrant.leverage
            
            # 计算时间价值衰减（基于剩余到期时间）
            time_decay = self.calculate_time_decay(warrant.time_to_maturity)
            
            # 更新分析结果
            self.analysis_results[warrant_symbol] = WarrantAnalysisResult(
                warrant_symbol=warrant_symbol,
                underlying_symbol=warrant.underlying_symbol,
                warrant_type=warrant.warrant_type,
                distance_to_knock_out=distance_to_knock_out,
                leverage_ratio=effective_leverage,
                time_value_decay=time_decay,
                analysis_time=datetime.now()
            )
            
            # 检查预警条件
            await self.check_alerts(warrant_symbol)
            
        except Exception as e:
            self.logger.error(f"更新牛熊证指标失败 {warrant_symbol}: {str(e)}")
            
    async def get_underlying_price(self, symbol: str) -> float:
        """获取正股价格 - 使用数据服务获取真实数据"""
        try:
            # 使用牛熊证数据服务获取正股实时数据
            underlying_data = await warrants_data_service.get_underlying_realtime_data(symbol)
            return underlying_data.get('last_price', 100.0)
        except Exception as e:
            self.logger.error(f"获取正股价格失败 {symbol}: {str(e)}，使用模拟数据")
            # 回退到模拟数据
            price_mapping = {
                "00700.HK": 185.5 + (datetime.now().second % 10 - 5) * 0.1,
            }
            return price_mapping.get(symbol, 100.0)
        
    def calculate_distance_to_knock_out(self, warrant_type: WarrantType, 
                                      underlying_price: float, 
                                      knock_out_price: float) -> float:
        """计算距回收价幅度"""
        if warrant_type == WarrantType.BULL:
            return ((knock_out_price - underlying_price) / underlying_price) * 100
        else:
            return ((underlying_price - knock_out_price) / underlying_price) * 100
            
    def calculate_effective_leverage(self, warrant_price: float, 
                                  conversion_ratio: int, 
                                  underlying_price: float) -> float:
        """计算有效杠杆"""
        if warrant_price <= 0:
            return 0.0
        return (underlying_price / warrant_price) * conversion_ratio
        
    def calculate_time_decay(self, time_to_maturity: float) -> float:
        """计算时间价值衰减"""
        if time_to_maturity <= 0:
            return 1.0  # 已过期
        return 1.0 - (time_to_maturity / 365.0)  # 简化的时间衰减计算
        
    async def setup_initial_alerts(self, warrant: WarrantData):
        """设置初始预警 - 增强版"""
        # 距回收价三级预警
        alert_levels = [
            (8.0, "warning", "距回收价8%预警"),
            (5.0, "warning", "距回收价5%预警"), 
            (3.0, "danger", "距回收价3%预警"),
            (1.0, "danger", "距回收价1%紧急预警")
        ]
        
        for level, alert_type, description in alert_levels:
            alert = WarrantMonitoringAlert(
                warrant_symbol=warrant.symbol,
                alert_type=f"knock_out_distance_{level}%",
                alert_level=alert_type,
                current_distance=level,
                trigger_price=self._calculate_trigger_price(warrant, level),
                created_at=datetime.now(),
                is_active=True,
                description=description
            )
            self.active_alerts[f"{warrant.symbol}_{level}"] = alert
            
        # 杠杆率异常预警
        leverage_alerts = [
            (20.0, "danger", "杠杆率过高预警"),
            (15.0, "warning", "杠杆率偏高预警")
        ]
        
        for level, alert_type, description in leverage_alerts:
            alert = WarrantMonitoringAlert(
                warrant_symbol=warrant.symbol,
                alert_type=f"leverage_{level}x",
                alert_level=alert_type,
                current_distance=level,
                trigger_price=0.0,  # 杠杆预警不基于价格
                created_at=datetime.now(),
                is_active=True,
                description=description
            )
            self.active_alerts[f"{warrant.symbol}_leverage_{level}"] = alert
            
        # 成交量异常预警
        volume_alerts = [
            (3.0, "danger", "成交量异常放大"),
            (2.0, "warning", "成交量显著增加")
        ]
        
        for ratio, alert_type, description in volume_alerts:
            alert = WarrantMonitoringAlert(
                warrant_symbol=warrant.symbol,
                alert_type=f"volume_ratio_{ratio}x",
                alert_level=alert_type,
                current_distance=ratio,
                trigger_price=0.0,  # 成交量预警不基于价格
                created_at=datetime.now(),
                is_active=True,
                description=description
            )
            self.active_alerts[f"{warrant.symbol}_volume_{ratio}"] = alert
            
        # 时间价值衰减预警
        time_decay_alerts = [
            (0.5, "danger", "时间价值快速衰减"),
            (0.3, "warning", "时间价值衰减警告")
        ]
        
        for decay_rate, alert_type, description in time_decay_alerts:
            alert = WarrantMonitoringAlert(
                warrant_symbol=warrant.symbol,
                alert_type=f"time_decay_{decay_rate}",
                alert_level=alert_type,
                current_distance=decay_rate,
                trigger_price=0.0,  # 时间衰减预警不基于价格
                created_at=datetime.now(),
                is_active=True,
                description=description
            )
            self.active_alerts[f"{warrant.symbol}_time_decay_{decay_rate}"] = alert
            
    def _calculate_trigger_price(self, warrant: WarrantData, distance_percent: float) -> float:
        """计算触发价格"""
        if warrant.warrant_type == WarrantType.BULL:
            return warrant.knock_out_price * (1 - distance_percent / 100)
        else:
            return warrant.knock_out_price * (1 + distance_percent / 100)
            
    async def check_alerts(self, warrant_symbol: str):
        """检查预警条件"""
        if warrant_symbol not in self.analysis_results:
            return
            
        analysis = self.analysis_results[warrant_symbol]
        distance = analysis.distance_to_knock_out
        
        # 检查距回收价预警
        for alert_key, alert in list(self.active_alerts.items()):
            if alert.warrant_symbol == warrant_symbol and "knock_out_distance" in alert.alert_type:
                threshold = alert.current_distance
                if distance <= threshold and not alert.triggered:
                    alert.triggered = True
                    alert.triggered_at = datetime.now()
                    self.logger.warning(
                        f"牛熊证预警触发: {warrant_symbol} 距回收价 {distance:.2f}% <= {threshold}%"
                    )
                    
                    # 触发自动交易信号
                    warrant = self.active_warrants.get(warrant_symbol)
                    if warrant:
                        await self._trigger_auto_trading_signal(warrant_symbol, "knock_out_warning", {
                            "distance": distance,
                            "threshold": threshold,
                            "underlying_price": await self.get_underlying_price(warrant.underlying_symbol)
                        })
                    
    async def get_monitoring_data(self) -> List[Dict]:
        """获取监控数据"""
        monitoring_data = []
        
        for warrant_symbol, warrant in self.active_warrants.items():
            analysis = self.analysis_results.get(warrant_symbol)
            
            if analysis:
                # 获取实时正股价格
                underlying_price = await self.get_underlying_price(warrant.underlying_symbol)
                
                data = {
                    "symbol": warrant_symbol,
                    "underlying_symbol": warrant.underlying_symbol,
                    "warrant_type": warrant.warrant_type.value,
                    "current_price": warrant.current_price,
                    "underlying_price": underlying_price,
                    "distance_to_knock_out": analysis.distance_to_knock_out,
                    "effective_leverage": analysis.leverage_ratio,
                    "time_to_maturity": warrant.time_to_maturity,
                    "last_updated": analysis.analysis_time.isoformat(),
                    "alerts": self.get_active_alerts(warrant_symbol)
                }
                monitoring_data.append(data)
                
        return monitoring_data
        
    def get_active_alerts(self, warrant_symbol: str) -> List[Dict]:
        """获取指定牛熊证的活跃预警"""
        alerts = []
        for alert_key, alert in self.active_alerts.items():
            if alert.warrant_symbol == warrant_symbol and alert.triggered:
                alerts.append({
                    "type": alert.alert_type,
                    "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
                })
        return alerts

    async def get_all_active_alerts(self) -> List[WarrantMonitoringAlert]:
        """获取所有活跃预警"""
        return [alert for alert in self.active_alerts.values() if alert.triggered]
        
    async def add_warrant(self, warrant_data: Dict):
        """添加牛熊证到监控"""
        try:
            warrant = WarrantData(**warrant_data)
            self.active_warrants[warrant.symbol] = warrant
            await self.initialize_warrant_monitoring(warrant)
            
            self.logger.info(f"已添加牛熊证到监控: {warrant.symbol}")
            return {"success": True, "message": f"牛熊证 {warrant.symbol} 已添加到监控"}
            
        except Exception as e:
            self.logger.error(f"添加牛熊证失败: {str(e)}")
            return {"success": False, "message": f"添加失败: {str(e)}"}
            
    async def remove_warrant(self, warrant_symbol: str):
        """从监控中移除牛熊证"""
        if warrant_symbol in self.active_warrants:
            del self.active_warrants[warrant_symbol]
            
            # 移除相关预警
            alert_keys_to_remove = [
                key for key in self.active_alerts.keys() 
                if key.startswith(warrant_symbol)
            ]
            for key in alert_keys_to_remove:
                del self.active_alerts[key]
                
            # 移除分析结果
            if warrant_symbol in self.analysis_results:
                del self.analysis_results[warrant_symbol]
                
            self.logger.info(f"已从监控中移除牛熊证: {warrant_symbol}")
            return {"success": True, "message": f"牛熊证 {warrant_symbol} 已从监控中移除"}
        else:
            return {"success": False, "message": f"牛熊证 {warrant_symbol} 不在监控中"}
            
    async def _generate_trading_signals(self):
        """生成交易信号"""
        for warrant_symbol, warrant in self.active_warrants.items():
            if warrant_symbol not in self.analysis_results:
                continue
                
            analysis = self.analysis_results[warrant_symbol]
            underlying_price = await self.get_underlying_price(warrant.underlying_symbol)
            
            # 基于分析结果生成交易信号
            signal = await self._analyze_trading_opportunity(warrant, analysis, underlying_price)
            
            if signal:
                self.logger.info(f"生成交易信号: {warrant_symbol} - {signal.signal_type}")
                
                # 记录交易到分析系统
                try:
                    # 模拟交易数量和盈亏计算
                    quantity = 1000  # 模拟交易数量
                    transaction_price = warrant.current_price
                    
                    # 根据信号类型计算模拟盈亏
                    if signal.signal_type == "BUY":
                        profit_loss = 0.0  # 买入时盈亏为0
                    else:  # SELL
                        # 卖出时模拟盈利（基于价格波动）
                        price_change = (datetime.now().second % 10 - 5) * 0.01  # 模拟价格变化
                        profit_loss = quantity * transaction_price * price_change
                    
                    # 构建交易原因 - 基于分析结果
                    reason = f"{signal.signal_type} signal - Distance to KO: {analysis.distance_to_knock_out:.1f}%, Leverage: {analysis.leverage_ratio:.1f}x"
                    
                    # 记录交易
                    trade_record = {
                        "symbol": warrant_symbol,
                        "side": signal.signal_type,
                        "quantity": quantity,
                        "price": transaction_price,
                        "profit_loss": profit_loss,
                        "timestamp": datetime.now(),
                        "strategy": "warrants_monitoring",
                        "confidence": signal.confidence,
                        "reason": reason
                    }
                    
                    await trading_analytics_service.record_trade(trade_record)
                    self.logger.info(f"已记录交易到分析系统: {warrant_symbol} - {signal.signal_type}")
                    
                except Exception as e:
                    self.logger.error(f"记录交易到分析系统失败: {str(e)}")
                
    async def _analyze_trading_opportunity(self, warrant: WarrantData, 
                                         analysis: WarrantAnalysisResult,
                                         underlying_price: float) -> Optional[WarrantTradingSignal]:
        """分析交易机会"""
        
        # 检查回收风险
        if analysis.distance_to_knock_out <= 5.0:
            return WarrantTradingSignal(
                warrant_symbol=warrant.symbol,
                signal_type="SELL",
                signal_strength=0.9,
                reason=f"距回收价仅{analysis.distance_to_knock_out:.1f}%，高风险",
                target_price=warrant.current_price * 0.95,  # 目标价下调5%
                stop_loss_price=warrant.current_price * 1.05,  # 止损价上调5%
                confidence=0.85,
                strategy_type=AutoTradingStrategy.BREAKOUT.value,
                generated_at=datetime.now()
            )
            
        # 检查买入机会
        elif (analysis.distance_to_knock_out >= 15.0 and 
              analysis.leverage_ratio <= 20.0 and 
              warrant.time_to_maturity >= 30):
            
            # 计算预期收益
            expected_return = self._calculate_expected_return(warrant, underlying_price)
            
            if expected_return >= 0.1:  # 预期收益10%以上
                return WarrantTradingSignal(
                    warrant_symbol=warrant.symbol,
                    signal_type="BUY",
                    signal_strength=0.7,
                    reason=f"安全边际高{analysis.distance_to_knock_out:.1f}%，杠杆适中{analysis.leverage_ratio:.1f}x",
                    target_price=warrant.current_price * 1.15,  # 目标价上调15%
                    stop_loss_price=warrant.current_price * 0.85,  # 止损价下调15%
                    confidence=0.75,
                    strategy_type=AutoTradingStrategy.TREND_FOLLOWING.value,
                    generated_at=datetime.now()
                )
                
        return None
        
    def _calculate_expected_return(self, warrant: WarrantData, underlying_price: float) -> float:
        """计算预期收益"""
        # 简化的预期收益计算
        base_return = 0.05  # 基础收益5%
        leverage_boost = min(warrant.leverage * 0.01, 0.1)  # 杠杆提升，最多10%
        time_decay_penalty = max((365 - warrant.time_to_maturity) / 365 * 0.1, 0)  # 时间衰减惩罚
        
        return base_return + leverage_boost - time_decay_penalty
        
    async def _trigger_auto_trading_signal(self, warrant_symbol: str, signal_type: str, data: Dict):
        """触发自动交易信号"""
        try:
            # 这里可以集成自动交易服务
            self.logger.info(f"触发自动交易信号: {warrant_symbol} - {signal_type}")
            # 在实际系统中，这里会调用auto_trading_service来处理信号
            
        except Exception as e:
            self.logger.error(f"触发自动交易信号失败: {str(e)}")
            
    async def get_all_warrants(self) -> List[WarrantData]:
        """获取所有被监控的牛熊证"""
        return list(self.active_warrants.values())

    async def get_trading_signals(self) -> List[Dict]:
        """获取交易信号（用于API）"""
        signals = []
        for warrant_symbol, warrant in self.active_warrants.items():
            analysis = self.analysis_results.get(warrant_symbol)
            if not analysis:
                continue
                
            # 基于分析结果生成信号
            signal_type = "BUY" if analysis.distance_to_knock_out > 10 else "SELL"
            confidence = 0.75 if analysis.distance_to_knock_out > 10 else 0.85
            reason = "安全边际充足" if analysis.distance_to_knock_out > 10 else "接近回收价"
            
            signal = {
                "warrant_symbol": warrant_symbol,
                "signal_type": signal_type,
                "confidence": confidence,
                "reason": reason,
                "generated_at": datetime.now().isoformat()
            }
            signals.append(signal)
        return signals

    async def get_warrant(self, warrant_symbol: str) -> Optional[WarrantData]:
        """获取指定牛熊证数据"""
        return self.active_warrants.get(warrant_symbol)

    async def acknowledge_alert(self, warrant_symbol: str) -> bool:
        """确认预警"""
        # 这里实现预警确认逻辑
        # 目前简单返回成功
        return True

    async def get_monitoring_status(self) -> Dict:
        """获取监控系统状态"""
        warrants_count = len(self.active_warrants)
        active_alerts_count = len([alert for alert in self.active_alerts.values() if alert.triggered])
        
        return {
            "status": "running",
            "warrants_monitored": warrants_count,
            "active_alerts": active_alerts_count,
            "last_update": datetime.now().isoformat()
        }


# 全局监控服务实例
warrants_monitoring_service = WarrantsMonitoringService()
