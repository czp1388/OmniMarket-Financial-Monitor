# 市场数据服务
import logging
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.data_sources = {}
        self.is_initialized = False
        
    async def initialize(self):
        """初始化市场数据服务"""
        try:
            logger.info("🔄 初始化市场数据服务...")
            
            # 初始化数据源配置
            self.data_sources = {
                "crypto": {
                    "name": "加密货币",
                    "base_url": "https://api.binance.com/api/v3",
                    "enabled": True
                },
                "stock": {
                    "name": "A股数据", 
                    "base_url": "",
                    "enabled": False  # 待实现
                }
            }
            
            # 测试连接
            await self.test_connections()
            
            self.is_initialized = True
            logger.info("✅ 市场数据服务初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 市场数据服务初始化失败: {e}")
            return False
    
    async def test_connections(self):
        """测试数据源连接"""
        try:
            # 测试加密货币数据源
            if self.data_sources["crypto"]["enabled"]:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.data_sources['crypto']['base_url']}/ping") as response:
                        if response.status == 200:
                            logger.info("✅ 加密货币数据源连接正常")
                        else:
                            logger.warning("⚠️ 加密货币数据源连接不稳定")
        except Exception as e:
            logger.warning(f"⚠️ 数据源连接测试失败: {e}")
    
    async def get_crypto_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> Optional[List[Dict]]:
        """获取加密货币K线数据"""
        try:
            url = f"{self.data_sources['crypto']['base_url']}/klines"
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_binance_klines(data, symbol, interval)
                    else:
                        logger.error(f"获取K线数据失败: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"获取加密货币K线数据异常: {e}")
            return None
    
    def _parse_binance_klines(self, raw_data: List, symbol: str, interval: str) -> List[Dict]:
        """解析Binance K线数据"""
        klines = []
        for item in raw_data:
            kline = {
                "symbol": symbol,
                "interval": interval,
                "open_time": datetime.fromtimestamp(item[0] / 1000),
                "open_price": float(item[1]),
                "high_price": float(item[2]),
                "low_price": float(item[3]),
                "close_price": float(item[4]),
                "volume": float(item[5]),
                "close_time": datetime.fromtimestamp(item[6] / 1000),
                "quote_volume": float(item[7]),
                "trade_count": int(item[8]),
                "taker_buy_base_volume": float(item[9]),
                "taker_buy_quote_volume": float(item[10])
            }
            klines.append(kline)
        return klines
    
    async def get_symbol_info(self, symbol: str, market_type: str = "crypto") -> Optional[Dict]:
        """获取交易对信息"""
        try:
            if market_type == "crypto":
                url = f"{self.data_sources['crypto']['base_url']}/exchangeInfo"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            for s in data["symbols"]:
                                if s["symbol"] == symbol.upper():
                                    return {
                                        "symbol": s["symbol"],
                                        "base_asset": s["baseAsset"],
                                        "quote_asset": s["quoteAsset"],
                                        "status": s["status"]
                                    }
            return None
        except Exception as e:
            logger.error(f"获取交易对信息失败: {e}")
            return None
    
    async def get_multiple_symbols_data(self, symbols: List[str], interval: str = "1h") -> Dict[str, List[Dict]]:
        """批量获取多个交易对数据"""
        tasks = []
        for symbol in symbols:
            task = self.get_crypto_klines(symbol, interval)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result is not None:
                data[symbols[i]] = result
                
        return data

# 创建全局市场数据服务实例
market_data_service = MarketDataService()
