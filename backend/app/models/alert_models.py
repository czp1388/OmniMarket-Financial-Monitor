# 预警规则数据模型
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AlertConditionType(str, Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below" 
    PRICE_BREAKOUT = "price_breakout"
    PRICE_BREAKDOWN = "price_breakdown"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    MACD_CROSSOVER = "macd_crossover"
    MACD_CROSSUNDER = "macd_crossunder"
    VOLUME_SURGE = "volume_surge"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIGGERED = "triggered"

class AlertRuleCreate(BaseModel):
    name: str
    symbol: str
    condition_type: AlertConditionType
    condition_value: Optional[float] = None
    condition_params: Optional[Dict[str, Any]] = None
    interval: str = "1h"
    enabled: bool = True
    notification_types: List[str] = ["in_app"]

class AlertRuleResponse(BaseModel):
    id: int
    name: str
    symbol: str
    condition_type: AlertConditionType
    condition_value: Optional[float] = None
    condition_params: Optional[Dict[str, Any]] = None
    interval: str
    enabled: bool
    status: AlertStatus
    created_at: datetime
    triggered_count: int = 0

class AlertHistoryResponse(BaseModel):
    id: int
    alert_rule_id: int
    symbol: str
    condition_type: str
    triggered_value: float
    condition_value: Optional[float] = None
    message: str
    triggered_at: datetime

class AlertTriggerRequest(BaseModel):
    symbol: str
    current_price: float
    indicators: Optional[Dict[str, Any]] = None
    volume: Optional[float] = None
