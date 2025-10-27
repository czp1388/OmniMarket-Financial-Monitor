# 统一市场数据接口
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class MarketType(Enum):
    CRYPTO = "crypto"      # 加密货币
    STOCK_CN = "stock_cn"  # A股
    STOCK_HK = "stock_hk"  # 港股
    FUTURES = "futures"    # 期货
    FOREX = "forex"        # 外汇
    WARRANT = "warrant"    # 牛熊证

class TimeFrame(Enum):
    MIN1 = "1m"
    MIN5 = "5m" 
    MIN15 = "15m"
    HOUR1 = "1h"
    HOUR4 = "4h"
    DAY1 = "1d"
    WEEK1 = "1w"
    MON1 = "1M"

class MarketDataInterface(ABC):
    """统一市场数据接口"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化数据源"""
        pass
    
    @abstractmethod
    async def get_klines(self, symbol: str, timeframe: TimeFrame, limit: int) -> List[Dict]:
        """获取K线数据"""
        pass
    
    @abstractmethod
    async def get_realtime_price(self, symbol: str) -> Optional[float]:
        """获取实时价格"""
        pass
    
    @abstractmethod
    async def get_market_info(self, symbol: str) -> Optional[Dict]:
        """获取市场信息"""
        pass
    
    @abstractmethod
    async def get_symbol_list(self) -> List[str]:
        """获取交易对列表"""
        pass

class MarketData:
    """K线数据模型"""
    def __init__(self):
        self.symbol = ""
        self.market_type = ""
        self.timeframe = ""
        self.open_time = None
        self.open_price = 0.0
        self.high_price = 0.0
        self.low_price = 0.0
        self.close_price = 0.0
        self.volume = 0.0
        self.turnover = 0.0  # 成交额
        self.trade_count = 0  # 交易笔数
