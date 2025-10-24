from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TickerData(BaseModel):
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None

class AlertCondition(BaseModel):
    id: str
    symbol: str
    condition_type: str
    operator: str
    value: float
    is_active: bool = True
