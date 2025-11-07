from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum, BigInteger
from sqlalchemy.sql import func
from backend.database import Base
import enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class MarketType(enum.Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    FUTURES = "futures"
    INDEX = "index"

class Timeframe(enum.Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    market_type = Column(Enum(MarketType), nullable=False)
    exchange = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    timeframe = Column(Enum(Timeframe), nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<MarketData(symbol={self.symbol}, timeframe={self.timeframe}, timestamp={self.timestamp})>"

class KlineData(Base):
    __tablename__ = "kline_data"

    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    market_type = Column(Enum(MarketType), nullable=False)
    exchange = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    timeframe = Column(Enum(Timeframe), nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<KlineData(symbol={self.symbol}, timeframe={self.timeframe}, timestamp={self.timestamp})>"

# Pydantic models for API
class KlineBase(BaseModel):
    symbol: str
    market_type: MarketType
    exchange: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
    amount: Optional[float] = None
    timeframe: Timeframe

class KlineCreate(KlineBase):
    pass

class Kline(KlineBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TickerData(BaseModel):
    symbol: str
    market_type: MarketType
    exchange: str
    timestamp: datetime
    last_price: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_volume: Optional[float] = None
    ask_volume: Optional[float] = None

class OrderBookSnapshot(BaseModel):
    symbol: str
    market_type: MarketType
    exchange: str
    timestamp: datetime
    bids: list  # list of [price, volume]
    asks: list  # list of [price, volume]
