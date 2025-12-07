from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum, JSON
from sqlalchemy.sql import func
from database import Base
import enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from .market_data import MarketType, Timeframe

class AlertConditionType(enum.Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_PERCENT_CHANGE = "price_percent_change"
    VOLUME_ABOVE = "volume_above"
    VOLUME_PERCENT_CHANGE = "volume_percent_change"
    TECHNICAL_INDICATOR = "technical_indicator"
    PATTERN_RECOGNITION = "pattern_recognition"

class AlertStatus(enum.Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"
    EXPIRED = "expired"

class NotificationType(enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 监控目标
    symbol = Column(String(50), nullable=False)
    market_type = Column(Enum(MarketType), nullable=False)
    exchange = Column(String(50), nullable=False)
    timeframe = Column(Enum(Timeframe), nullable=False)
    
    # 预警条件
    condition_type = Column(Enum(AlertConditionType), nullable=False)
    condition_config = Column(JSON, nullable=False)  # 存储具体的条件配置
    
    # 状态管理
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    is_recurring = Column(Boolean, default=False)
    triggered_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    
    # 通知配置
    notification_types = Column(JSON, default=[])  # 存储通知方式列表
    notification_config = Column(JSON, default={})  # 存储通知相关配置
    
    # 时间控制
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Alert(name={self.name}, symbol={self.symbol}, status={self.status})>"

class AlertTrigger(Base):
    __tablename__ = "alert_triggers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=False, index=True)
    triggered_at = Column(DateTime, nullable=False, default=func.now())
    trigger_data = Column(JSON, nullable=False)  # 存储触发时的数据
    notification_sent = Column(Boolean, default=False)
    notification_results = Column(JSON, default={})  # 存储各种通知方式的发送结果

    def __repr__(self):
        return f"<AlertTrigger(alert_id={self.alert_id}, triggered_at={self.triggered_at})>"

# Pydantic models for API
class AlertConditionConfig(BaseModel):
    """预警条件配置基类"""
    pass

class PriceConditionConfig(AlertConditionConfig):
    threshold: float
    use_percentage: bool = False

class VolumeConditionConfig(AlertConditionConfig):
    threshold: float
    use_percentage: bool = False
    period: int = 1  # 对比周期（单位：根K线）

class TechnicalIndicatorConfig(AlertConditionConfig):
    indicator: str  # 如 "MACD", "RSI", "MA" 等
    parameters: Dict[str, Any]
    condition: str  # 如 "cross_above", "cross_below", "above", "below"

class AlertBase(BaseModel):
    name: str
    description: Optional[str] = None
    symbol: str
    market_type: MarketType
    exchange: str
    timeframe: Timeframe
    condition_type: AlertConditionType
    condition_config: Dict[str, Any]
    is_recurring: bool = False
    notification_types: List[NotificationType] = []
    notification_config: Dict[str, Any] = {}
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

class AlertCreate(AlertBase):
    user_id: int

class AlertUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AlertStatus] = None
    is_recurring: Optional[bool] = None
    notification_types: Optional[List[NotificationType]] = None
    notification_config: Optional[Dict[str, Any]] = None
    valid_until: Optional[datetime] = None

class AlertResponse(AlertBase):
    id: int
    user_id: int
    status: AlertStatus
    triggered_count: int
    last_triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AlertTriggerResponse(BaseModel):
    id: int
    alert_id: int
    triggered_at: datetime
    trigger_data: Dict[str, Any]
    notification_sent: bool
    notification_results: Dict[str, Any]

    class Config:
        orm_mode = True
