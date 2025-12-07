import asyncio
import logging
import aiohttp
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from models.market_data import KlineData, MarketType, Timeframe

logger = logging.getLogger(__name__)

class CoinGeckoService:
    """CoinGecko数据服务 - 免费加密货币数据API"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit = 10  # 每分钟请求限制（免费版）
        self.last_request_time = 0
        self.session = None
        self.connected = True
        
        # 加密货币符号映射
        self.symbol_mapping = {
            "BTC/USDT": "bitcoin",
            "ETH/USDT": "ethereum", 
            "BNB/USDT": "binancecoin",
            "ADA/USDT": "cardano",
            "DOT/USDT": "polkadot",
            "LINK/USDT": "chainlink",
            "LTC/USDT": "litecoin",
            "BCH/USDT": "bitcoin-cash",
            "XRP/USDT": "ripple",
            "EOS/USDT": "eos",
            "XLM/USDT": "stellar",
            "TRX/USDT": "tron",
            "ATOM/USDT": "cosmos",
            "SOL/USDT": "solana",
            "DOGE/USDT": "dogecoin"
        }
    
    async def get_session(self):
        """获取aiohttp会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _rate_limit(self):
        """API速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 60 / self.rate_limit:
            await asyncio.sleep(60 / self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    async def get_crypto_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        limit: int = 1000
    ) -> List[KlineData]:
        """获取加密货币K线数据"""
        try:
            await self._rate_limit()
            
            # 获取CoinGecko ID
            coin_id = self._get_coin_id(symbol)
            if not coin_id:
                logger.warning(f"未找到加密货币映射: {symbol}")
                return await self._get_mock_data(symbol, timeframe, limit)
            
            # 时间框架映射到天数
            days_mapping = {
                Timeframe.MINUTE_1: 1,
                Timeframe.MINUTE_5: 1,
                Timeframe.MINUTE_15: 7,
                Timeframe.HOUR_1: 30,
                Timeframe.HOUR_4: 90,
                Timeframe.DAILY: 365,
                Timeframe.WEEKLY: 730,  # 2年
                Timeframe.MONTHLY: 1825  # 5年
            }
            
            days = days_mapping.get(timeframe, 30)
            
            # 对于分钟级数据，使用更精确的端点
            if timeframe in [Timeframe.MINUTE_1, Timeframe.MINUTE_5, Timeframe.MINUTE_15]:
                return await self._get_intraday_data(coin_id, symbol, timeframe, limit)
            
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": self._get_interval(timeframe)
            }
            
            session = await self.get_session()
            async with session.get(f"{self.base_url}/coins/{coin_id}/market_chart", params=params) as response:
                if response.status != 200:
                    logger.warning(f"CoinGecko API请求失败: {response.status}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                data = await response.json()
                
                # 解析价格数据
                prices = data.get("prices", [])
                klines = []
                
                for price_data in prices:
                    timestamp = datetime.fromtimestamp(price_data[0] / 1000)
                    price = price_data[1]
                    
                    # 对于OHLC数据，使用相同价格（CoinGecko只提供价格）
                    kline = KlineData(
                        symbol=symbol,
                        timeframe=timeframe,
                        market_type=MarketType.CRYPTO,
                        exchange='coingecko',
                        timestamp=timestamp,
                        open=price,
                        high=price,
                        low=price,
                        close=price,
                        volume=0.0  # CoinGecko不提供交易量数据
                    )
                    klines.append(kline)
                
                # 限制返回数量
                return klines[-limit:] if len(klines) > limit else klines
                
        except Exception as e:
            logger.error(f"获取CoinGecko加密货币K线数据失败: {e}")
            return await self._get_mock_data(symbol, timeframe, limit)
    
    async def _get_intraday_data(
        self,
        coin_id: str,
        symbol: str,
        timeframe: Timeframe,
        limit: int
    ) -> List[KlineData]:
        """获取日内数据"""
        try:
            # 对于分钟级数据，使用OHLC端点
            params = {
                "vs_currency": "usd",
                "days": 1  # 只获取最近1天的数据
            }
            
            session = await self.get_session()
            async with session.get(f"{self.base_url}/coins/{coin_id}/ohlc", params=params) as response:
                if response.status != 200:
                    logger.warning(f"CoinGecko OHLC API请求失败: {response.status}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                data = await response.json()
                klines = []
                
                for ohlc_data in data:
                    timestamp = datetime.fromtimestamp(ohlc_data[0] / 1000)
                    
                    kline = KlineData(
                        symbol=symbol,
                        timeframe=timeframe,
                        market_type=MarketType.CRYPTO,
                        exchange='coingecko',
                        timestamp=timestamp,
                        open=ohlc_data[1],
                        high=ohlc_data[2],
                        low=ohlc_data[3],
                        close=ohlc_data[4],
                        volume=0.0
                    )
                    klines.append(kline)
                
                # 限制返回数量
                return klines[-limit:] if len(klines) > limit else klines
                
        except Exception as e:
            logger.error(f"获取CoinGecko日内数据失败: {e}")
            return await self._get_mock_data(symbol, timeframe, limit)
    
    def _get_coin_id(self, symbol: str) -> Optional[str]:
        """获取CoinGecko币种ID"""
        # 移除交易对后缀
        base_symbol = symbol.split("/")[0] if "/" in symbol else symbol.replace("USDT", "")
        return self.symbol_mapping.get(symbol) or self._find_coin_id_by_symbol(base_symbol)
    
    def _find_coin_id_by_symbol(self, symbol: str) -> Optional[str]:
        """通过符号查找币种ID"""
        # 简化的映射查找
        symbol_lower = symbol.lower()
        for coin_symbol, coin_id in self.symbol_mapping.items():
            if symbol_lower in coin_symbol.lower():
                return coin_id
        return None
    
    def _get_interval(self, timeframe: Timeframe) -> str:
        """获取时间间隔"""
        interval_mapping = {
            Timeframe.MINUTE_1: "minutely",
            Timeframe.MINUTE_5: "minutely", 
            Timeframe.MINUTE_15: "minutely",
            Timeframe.HOUR_1: "hourly",
            Timeframe.HOUR_4: "4hourly",
            Timeframe.DAILY: "daily",
            Timeframe.WEEKLY: "weekly",
            Timeframe.MONTHLY: "monthly"
        }
        return interval_mapping.get(timeframe, "daily")
    
    async def get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        try:
            await self._rate_limit()
            
            coin_id = self._get_coin_id(symbol)
            if not coin_id:
                logger.warning(f"未找到加密货币映射: {symbol}")
                return 0.0
            
            params = {
                "ids": coin_id,
                "vs_currencies": "usd"
            }
            
            session = await self.get_session()
            async with session.get(f"{self.base_url}/simple/price", params=params) as response:
                if response.status != 200:
                    logger.warning(f"CoinGecko价格API请求失败: {response.status}")
                    return 0.0
                
                data = await response.json()
                price_data = data.get(coin_id, {})
                return price_data.get("usd", 0.0)
                
        except Exception as e:
            logger.error(f"获取CoinGecko当前价格失败: {e}")
            return 0.0
    
    async def get_market_data(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """获取市场数据"""
        try:
            await self._rate_limit()
            
            if not symbols:
                # 获取主要加密货币
                coin_ids = list(self.symbol_mapping.values())[:10]  # 限制数量避免API限制
            else:
                coin_ids = [self._get_coin_id(symbol) for symbol in symbols if self._get_coin_id(symbol)]
                coin_ids = [coin_id for coin_id in coin_ids if coin_id]  # 移除None值
            
            if not coin_ids:
                return []
            
            params = {
                "ids": ",".join(coin_ids),
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": len(coin_ids),
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h"
            }
            
            session = await self.get_session()
            async with session.get(f"{self.base_url}/coins/markets", params=params) as response:
                if response.status != 200:
                    logger.warning(f"CoinGecko市场数据API请求失败: {response.status}")
                    return []
                
                data = await response.json()
                market_data = []
                
                for coin in data:
                    # 反向查找符号
                    symbol = self._get_symbol_by_coin_id(coin["id"])
                    if not symbol:
                        continue
                    
                    market_data.append({
                        'symbol': symbol,
                        'name': coin.get("name", ""),
                        'current_price': coin.get("current_price", 0),
                        'market_cap': coin.get("market_cap", 0),
                        'market_cap_rank': coin.get("market_cap_rank", 0),
                        'total_volume': coin.get("total_volume", 0),
                        'high_24h': coin.get("high_24h", 0),
                        'low_24h': coin.get("low_24h", 0),
                        'price_change_24h': coin.get("price_change_24h", 0),
                        'price_change_percentage_24h': coin.get("price_change_percentage_24h", 0),
                        'last_updated': datetime.now()
                    })
                
                return market_data
                
        except Exception as e:
            logger.error(f"获取CoinGecko市场数据失败: {e}")
            return []
    
    def _get_symbol_by_coin_id(self, coin_id: str) -> Optional[str]:
        """通过币种ID获取符号"""
        for symbol, id_val in self.symbol_mapping.items():
            if id_val == coin_id:
                return symbol
        return None
    
    async def _get_mock_data(
        self, 
        symbol: str, 
        timeframe: Timeframe,
        limit: int
    ) -> List[KlineData]:
        """生成模拟数据"""
        klines = []
        base_price = 100.0
        current_time = datetime.now()
        
        for i in range(limit):
            timestamp = current_time - timedelta(minutes=i * self._get_timeframe_minutes(timeframe))
            
            # 生成随机价格波动
            import random
            change = random.uniform(-2.0, 2.0)
            open_price = base_price + change
            high = open_price + random.uniform(0, 3.0)
            low = open_price - random.uniform(0, 3.0)
            close_price = (high + low) / 2 + random.uniform(-1.0, 1.0)
            volume = random.uniform(1000, 10000)
            
            kline = KlineData(
                symbol=symbol,
                timeframe=timeframe,
                market_type=MarketType.CRYPTO,
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close_price,
                volume=volume
            )
            klines.append(kline)
        
        return klines
    
    def _get_timeframe_minutes(self, timeframe: Timeframe) -> int:
        """获取时间框架对应的分钟数"""
        timeframe_minutes = {
            Timeframe.MINUTE_1: 1,
            Timeframe.MINUTE_5: 5,
            Timeframe.MINUTE_15: 15,
            Timeframe.HOUR_1: 60,
            Timeframe.HOUR_4: 240,
            Timeframe.DAILY: 1440,
            Timeframe.WEEKLY: 10080,
            Timeframe.MONTHLY: 43200
        }
        return timeframe_minutes.get(timeframe, 60)
    
    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()
            self.session = None


# 全局CoinGecko服务实例
coingecko_service = CoinGeckoService()
