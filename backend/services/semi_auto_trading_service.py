from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
from .warrants_analysis_service import WarrantsAnalysisService, WarrantAnalysis, RiskLevel

logger = logging.getLogger(__name__)

class TradingSignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class TradingSignal:
    def __init__(self, warrant_code: str, signal_type: TradingSignalType, 
                 strength: float, confidence: float, price: float, 
                 stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                 reason: str = ""):
        self.warrant_code = warrant_code
        self.signal_type = signal_type
        self.strength = strength  # 0-1, 信号强度
        self.confidence = confidence  # 0-1, 置信度
        self.price = price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.reason = reason
        self.timestamp = datetime.now()

class RiskControlRules:
    def __init__(self):
        self.max_position_per_warrant = 10000  # 单只牛熊证最大仓位(元)
        self.max_daily_trades = 10  # 单日最大交易次数
        self.max_daily_loss = 5000  # 单日最大亏损限额(元)
        self.min_safety_margin = 0.05  # 最小安全边际要求
        self.max_risk_level = RiskLevel.MEDIUM  # 最高可接受风险等级

class SemiAutoTradingService:
    def __init__(self):
        self.warrants_analysis_service = WarrantsAnalysisService()
        self.risk_rules = RiskControlRules()
        self.daily_stats = {
            'trades_today': 0,
            'loss_today': 0.0,
            'last_reset_date': datetime.now().date()
        }
    
    def _reset_daily_stats_if_needed(self):
        """检查是否需要重置每日统计"""
        today = datetime.now().date()
        if today != self.daily_stats['last_reset_date']:
            self.daily_stats = {
                'trades_today': 0,
                'loss_today': 0.0,
                'last_reset_date': today
            }
    
    def generate_trading_signals(self, warrant_data_list: List[Dict], 
                                underlying_data: Dict, 
                                market_conditions: Dict) -> List[TradingSignal]:
        """生成交易信号"""
        signals = []
        
        for warrant_data in warrant_data_list:
            # 使用分析引擎分析牛熊证
            analysis = self.warrants_analysis_service.analyze_warrant_risk(
                warrant_data, underlying_data, market_conditions
            )
            
            # 基于分析结果生成信号
            signal = self._generate_signal_from_analysis(analysis, warrant_data)
            if signal:
                signals.append(signal)
        
        # 按信号强度排序
        signals.sort(key=lambda x: x.strength * x.confidence, reverse=True)
        return signals
    
    def _generate_signal_from_analysis(self, analysis: WarrantAnalysis, 
                                     warrant_data: Dict) -> Optional[TradingSignal]:
        """从分析结果生成交易信号"""
        # 风险控制检查
        if not self._pass_risk_control(analysis):
            return None
        
        signal_type = TradingSignalType.HOLD
        strength = 0.0
        confidence = analysis.signal_strength
        reason = ""
        
        # 基于分析结果决定信号类型
        if analysis.trading_signal == "STRONG_BUY":
            signal_type = TradingSignalType.BUY
            strength = 0.9
            reason = "强买入信号：安全边际高，风险等级低"
        elif analysis.trading_signal == "BUY":
            signal_type = TradingSignalType.BUY
            strength = 0.7
            reason = "买入信号：良好的风险收益比"
        elif analysis.trading_signal == "SELL":
            signal_type = TradingSignalType.SELL
            strength = 0.6
            reason = "卖出信号：风险增加或达到目标"
        elif analysis.trading_signal == "STRONG_SELL":
            signal_type = TradingSignalType.SELL
            strength = 0.8
            reason = "强卖出信号：高风险或触回收概率高"
        
        if signal_type != TradingSignalType.HOLD:
            current_price = warrant_data.get('current_price', 0)
            stop_loss, take_profit = self._calculate_stop_loss_take_profit(
                analysis, current_price, signal_type
            )
            
            return TradingSignal(
                warrant_code=analysis.warrant_code,
                signal_type=signal_type,
                strength=strength,
                confidence=confidence,
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=reason
            )
        
        return None
    
    def _pass_risk_control(self, analysis: WarrantAnalysis) -> bool:
        """风险控制检查"""
        # 检查风险等级
        if analysis.risk_level.value > self.risk_rules.max_risk_level.value:
            return False
        
        # 检查安全边际
        if analysis.safety_margin < self.risk_rules.min_safety_margin:
            return False
        
        return True
    
    def _calculate_stop_loss_take_profit(self, analysis: WarrantAnalysis, 
                                       current_price: float, 
                                       signal_type: TradingSignalType) -> tuple:
        """计算止损止盈价格"""
        if signal_type == TradingSignalType.BUY:
            # 买入时：止损基于回收价安全距离，止盈基于技术分析
            stop_loss = current_price * 0.85  # 15% 止损
            take_profit = current_price * 1.20  # 20% 止盈
        else:  # SELL
            # 卖出时：止损基于向上突破，止盈基于向下支撑
            stop_loss = current_price * 1.15  # 15% 止损
            take_profit = current_price * 0.80  # 20% 止盈
        
        return stop_loss, take_profit
    
    def validate_trade(self, signal: TradingSignal, position_size: float) -> Dict[str, Any]:
        """验证交易是否符合风控规则"""
        self._reset_daily_stats_if_needed()
        
        violations = []
        
        # 检查单只仓位限制
        if position_size > self.risk_rules.max_position_per_warrant:
            violations.append(f"单只仓位超过限制: {position_size} > {self.risk_rules.max_position_per_warrant}")
        
        # 检查每日交易次数
        if self.daily_stats['trades_today'] >= self.risk_rules.max_daily_trades:
            violations.append(f"今日交易次数已达上限: {self.daily_stats['trades_today']}")
        
        # 检查每日亏损限额
        if self.daily_stats['loss_today'] >= self.risk_rules.max_daily_loss:
            violations.append(f"今日亏损已达上限: {self.daily_stats['loss_today']}")
        
        is_valid = len(violations) == 0
        return {
            'is_valid': is_valid,
            'violations': violations,
            'daily_stats': self.daily_stats.copy()
        }
    
    def execute_trade(self, signal: TradingSignal, position_size: float, 
                     user_confirmation: bool = False) -> Dict[str, Any]:
        """执行交易（需要人工确认）"""
        if not user_confirmation:
            return {
                'success': False,
                'message': '需要人工确认才能执行交易',
                'signal': signal.__dict__
            }
        
        # 验证交易
        validation = self.validate_trade(signal, position_size)
        if not validation['is_valid']:
            return {
                'success': False,
                'message': '交易验证失败',
                'violations': validation['violations'],
                'validation': validation
            }
        
        # 模拟执行交易
        try:
            # 这里应该是实际的交易执行逻辑
            # 暂时模拟执行
            trade_result = {
                'trade_id': f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'warrant_code': signal.warrant_code,
                'signal_type': signal.signal_type.value,
                'executed_price': signal.price,
                'position_size': position_size,
                'timestamp': datetime.now().isoformat(),
                'status': 'EXECUTED'
            }
            
            # 更新每日统计
            self.daily_stats['trades_today'] += 1
            
            return {
                'success': True,
                'message': '交易执行成功',
                'trade_result': trade_result,
                'daily_stats': self.daily_stats.copy()
            }
            
        except Exception as e:
            logger.error(f"交易执行失败: {str(e)}")
            return {
                'success': False,
                'message': f'交易执行失败: {str(e)}'
            }
    
    def get_trading_dashboard(self) -> Dict[str, Any]:
        """获取交易仪表板数据"""
        self._reset_daily_stats_if_needed()
        
        return {
            'daily_stats': self.daily_stats,
            'risk_rules': {
                'max_position_per_warrant': self.risk_rules.max_position_per_warrant,
                'max_daily_trades': self.risk_rules.max_daily_trades,
                'max_daily_loss': self.risk_rules.max_daily_loss,
                'min_safety_margin': self.risk_rules.min_safety_margin,
                'max_risk_level': self.risk_rules.max_risk_level.value
            },
            'remaining_today': {
                'trades_remaining': self.risk_rules.max_daily_trades - self.daily_stats['trades_today'],
                'loss_remaining': self.risk_rules.max_daily_loss - self.daily_stats['loss_today']
            }
        }
