from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WarrantType(str, Enum):
    """牛熊证类型枚举"""
    BULL = "bull"  # 牛证
    BEAR = "bear"  # 熊证


class WarrantStatus(str, Enum):
    """牛熊证状态枚举"""
    ACTIVE = "active"      # 活跃
    KNOCKED_OUT = "knocked_out"  # 已回收
    EXPIRED = "expired"    # 已到期


class WarrantData(BaseModel):
    """牛熊证基础数据模型"""
    symbol: str = Field(..., description="牛熊证代码")
    underlying_symbol: str = Field(..., description="正股代码")
    warrant_type: WarrantType = Field(..., description="牛熊证类型")
    strike_price: float = Field(..., description="行使价")
    knock_out_price: float = Field(..., description="回收价")
    current_price: float = Field(..., description="当前价格")
    leverage: float = Field(..., description="有效杠杆")
    time_to_maturity: float = Field(..., description="剩余到期时间（天）")
    status: WarrantStatus = Field(..., description="状态")
    volume: Optional[float] = Field(None, description="当日成交量")
    average_volume: Optional[float] = Field(None, description="平均成交量")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")


class WarrantMonitoringAlert(BaseModel):
    """牛熊证监控预警模型"""
    warrant_symbol: str = Field(..., description="牛熊证代码")
    alert_type: str = Field(..., description="预警类型")
    alert_level: str = Field(..., description="预警级别")
    current_distance: float = Field(..., description="当前距回收价距离")
    trigger_price: float = Field(..., description="触发价格")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    is_active: bool = Field(default=True, description="是否活跃")
    triggered: bool = Field(default=False, description="是否已触发")
    triggered_at: Optional[datetime] = Field(None, description="触发时间")


class WarrantAnalysisResult(BaseModel):
    """牛熊证分析结果模型"""
    warrant_symbol: str = Field(..., description="牛熊证代码")
    underlying_symbol: str = Field(..., description="正股代码")
    warrant_type: WarrantType = Field(..., description="牛熊证类型")
    
    # 风险分析
    knock_out_probability: float = Field(default=0.0, description="触回收概率")
    time_value_decay: float = Field(default=0.0, description="时间价值衰减率")
    safety_margin: float = Field(default=0.0, description="安全边际")
    
    # 技术分析
    underlying_trend: str = Field(default="neutral", description="正股趋势")
    price_divergence: float = Field(default=0.0, description="价格背离度")
    
    # 风险评估
    max_loss_estimate: float = Field(default=0.0, description="最大损失估算")
    reward_risk_ratio: float = Field(default=0.0, description="收益风险比")
    
    # 监控数据
    distance_to_knock_out: float = Field(..., description="距回收价距离")
    leverage_ratio: float = Field(default=0.0, description="杠杆比率")
    volume_anomaly: bool = Field(default=False, description="成交量异常")
    
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析时间")


class WarrantTradingSignal(BaseModel):
    """牛熊证交易信号模型"""
    warrant_symbol: str = Field(..., description="牛熊证代码")
    signal_type: str = Field(..., description="信号类型")
    signal_strength: float = Field(..., description="信号强度")
    entry_price: Optional[float] = Field(None, description="建议入场价格")
    stop_loss: Optional[float] = Field(None, description="止损价格")
    take_profit: Optional[float] = Field(None, description="止盈价格")
    confidence: float = Field(..., description="置信度")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")


class WarrantPortfolio(BaseModel):
    """牛熊证投资组合模型"""
    user_id: str = Field(..., description="用户ID")
    warrant_positions: List[Dict[str, Any]] = Field(default_factory=list, description="牛熊证持仓")
    total_value: float = Field(..., description="总价值")
    unrealized_pnl: float = Field(..., description="未实现盈亏")
    risk_score: float = Field(..., description="风险评分")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
