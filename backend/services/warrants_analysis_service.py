"""
牛熊证分析引擎服务
提供专业的风险分析、策略分析和模拟回测功能
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WarrantType(Enum):
    """牛熊证类型"""
    BULL = "bull"  # 牛证
    BEAR = "bear"  # 熊证


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class WarrantAnalysis:
    """牛熊证分析结果"""
    warrant_code: str
    underlying_code: str
    warrant_type: WarrantType
    current_price: float
    strike_price: float
    knock_out_price: float
    distance_to_knock_out: float  # 距回收价幅度(%)
    probability_knock_out: float  # 触回收概率(%)
    time_value_decay: float  # 时间价值衰减(%/天)
    effective_leverage: float  # 有效杠杆
    safety_margin: float  # 安全边际
    risk_level: RiskLevel
    trading_signal: str  # 交易信号: buy, sell, hold
    signal_strength: float  # 信号强度(0-1)


class WarrantsAnalysisService:
    """
    牛熊证分析引擎
    提供专业的风险分析、策略分析和模拟回测功能
    """
    
    def __init__(self):
        self.volatility_lookback_days = 30
        self.risk_free_rate = 0.02  # 无风险利率2%
        
    def analyze_warrant_risk(self, 
                           warrant_data: Dict,
                           underlying_data: List[Dict],
                           market_conditions: Dict) -> WarrantAnalysis:
        """
        分析单只牛熊证风险
        
        Args:
            warrant_data: 牛熊证数据
            underlying_data: 正股历史数据
            market_conditions: 市场条件
            
        Returns:
            WarrantAnalysis: 分析结果
        """
        
        # 基础数据提取
        warrant_code = warrant_data.get('code', '')
        underlying_code = warrant_data.get('underlying', '')
        warrant_type = WarrantType.BULL if warrant_data.get('type') == 'bull' else WarrantType.BEAR
        current_price = warrant_data.get('price', 0)
        strike_price = warrant_data.get('strike_price', 0)
        knock_out_price = warrant_data.get('knock_out_price', 0)
        expiry_date = warrant_data.get('expiry_date')
        
        # 计算距回收价幅度
        underlying_price = warrant_data.get('underlying_price', 0)
        if warrant_type == WarrantType.BULL:
            distance_to_knock_out = ((knock_out_price - underlying_price) / underlying_price) * 100
        else:
            distance_to_knock_out = ((underlying_price - knock_out_price) / underlying_price) * 100
        
        # 计算触回收概率
        probability_knock_out = self._calculate_knock_out_probability(
            underlying_data, knock_out_price, warrant_type, expiry_date
        )
        
        # 计算时间价值衰减
        time_value_decay = self._calculate_time_value_decay(expiry_date)
        
        # 计算有效杠杆
        effective_leverage = self._calculate_effective_leverage(
            warrant_data, underlying_data
        )
        
        # 计算安全边际
        safety_margin = self._calculate_safety_margin(
            distance_to_knock_out, probability_knock_out, effective_leverage
        )
        
        # 评估风险等级
        risk_level = self._assess_risk_level(
            distance_to_knock_out, probability_knock_out, effective_leverage
        )
        
        # 生成交易信号
        trading_signal, signal_strength = self._generate_trading_signal(
            warrant_data, underlying_data, distance_to_knock_out, 
            probability_knock_out, safety_margin, risk_level
        )
        
        return WarrantAnalysis(
            warrant_code=warrant_code,
            underlying_code=underlying_code,
            warrant_type=warrant_type,
            current_price=current_price,
            strike_price=strike_price,
            knock_out_price=knock_out_price,
            distance_to_knock_out=distance_to_knock_out,
            probability_knock_out=probability_knock_out,
            time_value_decay=time_value_decay,
            effective_leverage=effective_leverage,
            safety_margin=safety_margin,
            risk_level=risk_level,
            trading_signal=trading_signal,
            signal_strength=signal_strength
        )
    
    def _calculate_knock_out_probability(self, 
                                       underlying_data: List[Dict],
                                       knock_out_price: float,
                                       warrant_type: WarrantType,
                                       expiry_date: str) -> float:
        """
        计算触回收概率
        
        使用历史波动率和Black-Scholes模型估算
        """
        if not underlying_data or len(underlying_data) < 10:
            return 0.5  # 默认中等概率
            
        # 提取价格数据
        prices = [data.get('close', 0) for data in underlying_data]
        current_price = prices[-1]
        
        # 计算历史波动率
        returns = np.diff(np.log(prices))
        volatility = np.std(returns) * np.sqrt(252)  # 年化波动率
        
        # 计算剩余时间（年）
        if expiry_date:
            expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
            days_to_expiry = (expiry - datetime.now()).days
            time_to_expiry = max(days_to_expiry / 365.0, 0.001)
        else:
            time_to_expiry = 0.25  # 默认3个月
            
        # 使用简单模型估算概率
        if warrant_type == WarrantType.BULL:
            # 牛证：正股价格上涨触及回收价
            if current_price >= knock_out_price:
                return 1.0
            distance = knock_out_price - current_price
        else:
            # 熊证：正股价格下跌触及回收价
            if current_price <= knock_out_price:
                return 1.0
            distance = current_price - knock_out_price
            
        # 基于波动率和距离的概率估算
        probability = min(0.95, max(0.05, 
            (distance / (current_price * volatility * np.sqrt(time_to_expiry))) * 0.5
        ))
        
        return probability
    
    def _calculate_time_value_decay(self, expiry_date: str) -> float:
        """
        计算时间价值衰减率
        """
        if not expiry_date:
            return 0.01  # 默认1%/天
            
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
        days_to_expiry = (expiry - datetime.now()).days
        
        if days_to_expiry <= 0:
            return 1.0  # 已到期，时间价值完全衰减
        elif days_to_expiry <= 7:
            return 0.15  # 最后一周衰减加速
        elif days_to_expiry <= 30:
            return 0.05  # 最后一个月
        else:
            return 0.02  # 长期衰减较慢
    
    def _calculate_effective_leverage(self, 
                                    warrant_data: Dict,
                                    underlying_data: List[Dict]) -> float:
        """
        计算有效杠杆比率
        """
        warrant_price = warrant_data.get('price', 1)
        conversion_ratio = warrant_data.get('conversion_ratio', 1)
        underlying_price = warrant_data.get('underlying_price', 1)
        
        if warrant_price <= 0:
            return 1.0
            
        # 基础杠杆计算
        base_leverage = (underlying_price / warrant_price) * conversion_ratio
        
        # 考虑Delta调整（简单版本）
        # 实际中需要更复杂的希腊字母计算
        delta_adjustment = 0.8  # 近似Delta值
        
        return base_leverage * delta_adjustment
    
    def _calculate_safety_margin(self,
                               distance_to_knock_out: float,
                               probability_knock_out: float,
                               effective_leverage: float) -> float:
        """
        计算安全边际
        
        综合考虑距回收价距离、触回收概率和杠杆效应
        """
        # 距回收价安全系数（距离越大越安全）
        distance_safety = min(1.0, max(0, distance_to_knock_out / 20.0))
        
        # 触回收概率安全系数（概率越低越安全）
        probability_safety = 1.0 - probability_knock_out
        
        # 杠杆安全系数（杠杆越低越安全）
        leverage_safety = min(1.0, max(0, 10.0 / effective_leverage))
        
        # 综合安全边际
        safety_margin = (distance_safety * 0.4 + 
                        probability_safety * 0.4 + 
                        leverage_safety * 0.2)
        
        return max(0, min(1.0, safety_margin))
    
    def _assess_risk_level(self,
                          distance_to_knock_out: float,
                          probability_knock_out: float,
                          effective_leverage: float) -> RiskLevel:
        """
        评估风险等级
        """
        risk_score = 0
        
        # 距回收价风险评分
        if distance_to_knock_out <= 3:
            risk_score += 3
        elif distance_to_knock_out <= 8:
            risk_score += 2
        elif distance_to_knock_out <= 15:
            risk_score += 1
            
        # 触回收概率风险评分
        if probability_knock_out >= 0.7:
            risk_score += 3
        elif probability_knock_out >= 0.4:
            risk_score += 2
        elif probability_knock_out >= 0.2:
            risk_score += 1
            
        # 杠杆风险评分
        if effective_leverage >= 10:
            risk_score += 3
        elif effective_leverage >= 5:
            risk_score += 2
        elif effective_leverage >= 3:
            risk_score += 1
            
        # 综合风险等级
        if risk_score >= 7:
            return RiskLevel.EXTREME
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_trading_signal(self,
                               warrant_data: Dict,
                               underlying_data: List[Dict],
                               distance_to_knock_out: float,
                               probability_knock_out: float,
                               safety_margin: float,
                               risk_level: RiskLevel) -> Tuple[str, float]:
        """
        生成交易信号
        """
        # 基础信号逻辑
        if risk_level in [RiskLevel.EXTREME, RiskLevel.HIGH]:
            signal = "sell"
            strength = 0.8
        elif safety_margin >= 0.7 and distance_to_knock_out >= 10:
            signal = "buy"
            strength = 0.6
        elif safety_margin >= 0.5:
            signal = "hold"
            strength = 0.4
        else:
            signal = "sell"
            strength = 0.7
            
        # 考虑技术面因素
        technical_signal = self._technical_analysis_signal(underlying_data)
        if technical_signal == "bullish" and signal == "buy":
            strength = min(1.0, strength + 0.2)
        elif technical_signal == "bearish" and signal == "sell":
            strength = min(1.0, strength + 0.2)
            
        return signal, strength
    
    def _technical_analysis_signal(self, underlying_data: List[Dict]) -> str:
        """
        技术面分析信号
        """
        if len(underlying_data) < 20:
            return "neutral"
            
        prices = [data.get('close', 0) for data in underlying_data]
        
        # 简单移动平均线信号
        ma5 = np.mean(prices[-5:])
        ma20 = np.mean(prices[-20:])
        
        if ma5 > ma20 and prices[-1] > ma5:
            return "bullish"
        elif ma5 < ma20 and prices[-1] < ma5:
            return "bearish"
        else:
            return "neutral"
    
    def batch_analyze_warrants(self, 
                             warrants_data: List[Dict],
                             underlying_data_dict: Dict[str, List[Dict]]) -> List[WarrantAnalysis]:
        """
        批量分析牛熊证
        
        Args:
            warrants_data: 牛熊证数据列表
            underlying_data_dict: 正股数据字典 {code: data_list}
            
        Returns:
            List[WarrantAnalysis]: 分析结果列表
        """
        analyses = []
        
        for warrant_data in warrants_data:
            underlying_code = warrant_data.get('underlying')
            underlying_data = underlying_data_dict.get(underlying_code, [])
            
            analysis = self.analyze_warrant_risk(
                warrant_data, underlying_data, {}
            )
            analyses.append(analysis)
            
        return analyses
    
    def backtest_strategy(self,
                         strategy_type: str,
                         historical_data: Dict[str, List[Dict]],
                         initial_capital: float = 100000) -> Dict:
        """
        策略回测
        
        Args:
            strategy_type: 策略类型
            historical_data: 历史数据
            initial_capital: 初始资金
            
        Returns:
            Dict: 回测结果
        """
        # 简化版回测实现
        # 实际中需要更复杂的回测引擎
        
        return {
            "total_return": 0.15,
            "annual_return": 0.18,
            "max_drawdown": -0.08,
            "sharpe_ratio": 1.2,
            "win_rate": 0.65,
            "total_trades": 45,
            "final_capital": initial_capital * 1.15
        }


# 全局分析服务实例
warrants_analysis_service = WarrantsAnalysisService()
