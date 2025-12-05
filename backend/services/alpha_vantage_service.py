import asyncio
import logging
import aiohttp
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from backend.models.market_data import KlineData, MarketType, Timeframe

logger = logging.getLogger(__name__)

class AlphaVantageService:
    """Alpha Vantage数据服务 - 免费金融数据API"""
    
    def __init__(self):
        self.base_url = "https://www.alphavantage.co/query"
        self.api_key = "demo"  # 免费API密钥，生产环境应替换
        self.rate_limit = 5  # 每分钟请求限制
        self.last_request_time = 0
        self.session = None
        self.connected = True
    
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
    
    async def get_stock_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        limit: int = 1000,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[KlineData]:
        """获取股票K线数据"""
        try:
            await self._rate_limit()
            
            # 时间框架映射
            function_mapping = {
                Timeframe.MINUTE_1: "TIME_SERIES_INTRADAY",
                Timeframe.MINUTE_5: "TIME_SERIES_INTRADAY",
                Timeframe.MINUTE_15: "TIME_SERIES_INTRADAY",
                Timeframe.HOUR_1: "TIME_SERIES_INTRADAY",
                Timeframe.DAILY: "TIME_SERIES_DAILY",
                Timeframe.WEEKLY: "TIME_SERIES_WEEKLY",
                Timeframe.MONTHLY: "TIME_SERIES_MONTHLY"
            }
            
            interval_mapping = {
                Timeframe.MINUTE_1: "1min",
                Timeframe.MINUTE_5: "5min",
                Timeframe.MINUTE_15: "15min",
                Timeframe.HOUR_1: "60min",
                Timeframe.DAILY: "daily",
                Timeframe.WEEKLY: "weekly",
                Timeframe.MONTHLY: "monthly"
            }
            
            function = function_mapping.get(timeframe, "TIME_SERIES_DAILY")
            interval = interval_mapping.get(timeframe, "daily")
            
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "full" if limit > 100 else "compact"
            }
            
            if function == "TIME_SERIES_INTRADAY":
                params["interval"] = interval
            
            session = await self.get_session()
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Alpha Vantage API请求失败: {response.status}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                data = await response.json()
                
                # 解析数据
                time_series_key = None
                for key in data.keys():
                    if "Time Series" in key:
                        time_series_key = key
                        break
                
                if not time_series_key:
                    logger.warning(f"Alpha Vantage返回数据格式异常: {symbol}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                time_series = data[time_series_key]
                klines = []
                
                for timestamp_str, values in time_series.items():
                    try:
                        # 解析时间戳
                        if " " in timestamp_str:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        else:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                        
                        kline = KlineData(
                            symbol=symbol,
                            timeframe=timeframe,
                            market_type=MarketType.STOCK,
                            exchange='alpha_vantage',
                            timestamp=timestamp,
                            open=float(values["1. open"]),
                            high=float(values["2. high"]),
                            low=float(values["3. low"]),
                            close=float(values["4. close"]),
                            volume=float(values["5. volume"])
                        )
                        klines.append(kline)
                    except Exception as e:
                        logger.warning(f"解析Alpha Vantage数据失败: {e}")
                        continue
                
                # 按时间排序并限制数量
                klines.sort(key=lambda x: x.timestamp)
                return klines[-limit:] if len(klines) > limit else klines
                
        except Exception as e:
            logger.error(f"获取Alpha Vantage股票K线数据失败: {e}")
            return await self._get_mock_data(symbol, timeframe, limit)
    
    async def get_crypto_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        limit: int = 1000
    ) -> List[KlineData]:
        """获取加密货币K线数据"""
        try:
            await self._rate_limit()
            
            # 时间框架映射
            function_mapping = {
                Timeframe.MINUTE_1: "CRYPTO_INTRADAY",
                Timeframe.MINUTE_5: "CRYPTO_INTRADAY",
                Timeframe.MINUTE_15: "CRYPTO_INTRADAY",
                Timeframe.HOUR_1: "CRYPTO_INTRADAY",
                Timeframe.DAILY: "DIGITAL_CURRENCY_DAILY",
                Timeframe.WEEKLY: "DIGITAL_CURRENCY_WEEKLY",
                Timeframe.MONTHLY: "DIGITAL_CURRENCY_MONTHLY"
            }
            
            interval_mapping = {
                Timeframe.MINUTE_1: "1min",
                Timeframe.MINUTE_5: "5min",
                Timeframe.MINUTE_15: "15min",
                Timeframe.HOUR_1: "60min",
                Timeframe.DAILY: "daily",
                Timeframe.WEEKLY: "weekly",
                Timeframe.MONTHLY: "monthly"
            }
            
            function = function_mapping.get(timeframe, "DIGITAL_CURRENCY_DAILY")
            interval = interval_mapping.get(timeframe, "daily")
            
            # 提取基础货币和报价货币
            if "/" in symbol:
                base_currency, quote_currency = symbol.split("/")
            else:
                base_currency = symbol.replace("USD", "")
                quote_currency = "USD"
            
            params = {
                "function": function,
                "symbol": base_currency,
                "market": quote_currency,
                "apikey": self.api_key
            }
            
            if function == "CRYPTO_INTRADAY":
                params["interval"] = interval
            
            session = await self.get_session()
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Alpha Vantage加密货币API请求失败: {response.status}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                data = await response.json()
                
                # 解析数据
                time_series_key = None
                for key in data.keys():
                    if "Time Series" in key:
                        time_series_key = key
                        break
                
                if not time_series_key:
                    logger.warning(f"Alpha Vantage加密货币返回数据格式异常: {symbol}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                time_series = data[time_series_key]
                klines = []
                
                for timestamp_str, values in time_series.items():
                    try:
                        # 解析时间戳
                        if " " in timestamp_str:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        else:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                        
                        # 根据API返回的键名调整
                        open_key = "1. open" if "1. open" in values else "1a. open (USD)"
                        high_key = "2. high" if "2. high" in values else "2a. high (USD)"
                        low_key = "3. low" if "3. low" in values else "3a. low (USD)"
                        close_key = "4. close" if "4. close" in values else "4a. close (USD)"
                        volume_key = "5. volume" if "5. volume" in values else "5. volume"
                        
                        kline = KlineData(
                            symbol=symbol,
                            timeframe=timeframe,
                            market_type=MarketType.CRYPTO,
                            exchange='alpha_vantage',
                            timestamp=timestamp,
                            open=float(values[open_key]),
                            high=float(values[high_key]),
                            low=float(values[low_key]),
                            close=float(values[close_key]),
                            volume=float(values[volume_key])
                        )
                        klines.append(kline)
                    except Exception as e:
                        logger.warning(f"解析Alpha Vantage加密货币数据失败: {e}")
                        continue
                
                # 按时间排序并限制数量
                klines.sort(key=lambda x: x.timestamp)
                return klines[-limit:] if len(klines) > limit else klines
                
        except Exception as e:
            logger.error(f"获取Alpha Vantage加密货币K线数据失败: {e}")
            return await self._get_mock_data(symbol, timeframe, limit)
    
    async def get_forex_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        limit: int = 1000
    ) -> List[KlineData]:
        """获取外汇K线数据"""
        try:
            await self._rate_limit()
            
            # 时间框架映射
            function_mapping = {
                Timeframe.MINUTE_1: "FX_INTRADAY",
                Timeframe.MINUTE_5: "FX_INTRADAY",
                Timeframe.MINUTE_15: "FX_INTRADAY",
                Timeframe.HOUR_1: "FX_INTRADAY",
                Timeframe.DAILY: "FX_DAILY",
                Timeframe.WEEKLY: "FX_WEEKLY",
                Timeframe.MONTHLY: "FX_MONTHLY"
            }
            
            interval_mapping = {
                Timeframe.MINUTE_1: "1min",
                Timeframe.MINUTE_5: "5min",
                Timeframe.MINUTE_15: "15min",
                Timeframe.HOUR_1: "60min",
                Timeframe.DAILY: "daily",
                Timeframe.WEEKLY: "weekly",
                Timeframe.MONTHLY: "monthly"
            }
            
            function = function_mapping.get(timeframe, "FX_DAILY")
            interval = interval_mapping.get(timeframe, "daily")
            
            # 提取基础货币和报价货币
            if "/" in symbol:
                from_currency, to_currency = symbol.split("/")
            else:
                from_currency = symbol[:3]
                to_currency = symbol[3:]
            
            params = {
                "function": function,
                "from_symbol": from_currency,
                "to_symbol": to_currency,
                "apikey": self.api_key,
                "outputsize": "full" if limit > 100 else "compact"
            }
            
            if function == "FX_INTRADAY":
                params["interval"] = interval
            
            session = await self.get_session()
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Alpha Vantage外汇API请求失败: {response.status}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                data = await response.json()
                
                # 解析数据
                time_series_key = None
                for key in data.keys():
                    if "Time Series" in key:
                        time_series_key = key
                        break
                
                if not time_series_key:
                    logger.warning(f"Alpha Vantage外汇返回数据格式异常: {symbol}")
                    return await self._get_mock_data(symbol, timeframe, limit)
                
                time_series = data[time_series_key]
                klines = []
                
                for timestamp_str, values in time_series.items():
                    try:
                        # 解析时间戳
                        if " " in timestamp_str:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        else:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                        
                        kline = KlineData(
                            symbol=symbol,
                            timeframe=timeframe,
                            market_type=MarketType.FOREX,
                            exchange='alpha_vantage',
                            timestamp=timestamp,
                            open=float(values["1. open"]),
                            high=float(values["2. high"]),
                            low=float(values["3. low"]),
                            close=float(values["4. close"]),
                            volume=0.0  # 外汇数据通常没有交易量
                        )
                        klines.append(kline)
                    except Exception as e:
                        logger.warning(f"解析Alpha Vantage外汇数据失败: {e}")
                        continue
                
                # 按时间排序并限制数量
                klines.sort(key=lambda x: x.timestamp)
                return klines[-limit:] if len(klines) > limit else klines
                
        except Exception as e:
            logger.error(f"获取Alpha Vantage外汇K线数据失败: {e}")
            return await self._get_mock_data(symbol, timeframe, limit)
    
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
                market_type=MarketType.STOCK,
                exchange='alpha_vantage',
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
    
    async def get_current_price(self, symbol: str, market_type: MarketType) -> float:
        """获取当前价格"""
        try:
            await self._rate_limit()
            
            if market_type == MarketType.STOCK:
                function = "GLOBAL_QUOTE"
            elif market_type == MarketType.CRYPTO:
                function = "CURRENCY_EXCHANGE_RATE"
            elif market_type == MarketType.FOREX:
                function = "CURRENCY_EXCHANGE_RATE"
            else:
                return 0.0
            
            params = {
                "function": function,
                "apikey": self.api_key
            }
            
            if market_type == MarketType.STOCK:
                params["symbol"] = symbol
            elif market_type in [MarketType.CRYPTO, MarketType.FOREX]:
                if "/" in symbol:
                    from_currency, to_currency = symbol.split("/")
                else:
                    from_currency = symbol.replace("USD", "")
                    to_currency = "USD"
                params["from_currency"] = from_currency
                params["to_currency"] = to_currency
            
            session = await self.get_session()
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Alpha Vantage实时价格API请求失败: {response.status}")
                    return 0.0
                
                data = await response.json()
                
                if market_type == MarketType.STOCK:
                    quote = data.get("Global Quote", {})
                    return float(quote.get("05. price", 0))
                else:
                    rate = data.get("Realtime Currency Exchange Rate", {})
                    return float(rate.get("5. Exchange Rate", 0))
                
        except Exception as e:
            logger.error(f"获取Alpha Vantage当前价格失败: {e}")
            return 0.0
    
    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()
            self.session = None


# 全局Alpha Vantage服务实例
alpha_vantage_service = AlphaVantageService()
