"""
商品期货数据服务
支持: 原油、黄金、白银、天然气、铜等商品期货数据
数据源: Alpha Vantage (免费API) + Yahoo Finance (补充)
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import aiohttp
from models.market_data import KlineData, MarketType, Timeframe
from config import settings

logger = logging.getLogger(__name__)


class CommodityDataService:
    """商品期货数据服务"""
    
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        
        # 商品期货符号映射
        self.commodity_symbols = {
            # 能源
            "CL": {"name": "WTI原油期货", "alpha_vantage": "WTI", "yahoo": "CL=F"},
            "BZ": {"name": "布伦特原油", "alpha_vantage": "BRENT_CRUDE_OIL", "yahoo": "BZ=F"},
            "NG": {"name": "天然气", "alpha_vantage": "NATURAL_GAS", "yahoo": "NG=F"},
            
            # 贵金属
            "GC": {"name": "黄金", "alpha_vantage": "XAU", "yahoo": "GC=F"},
            "SI": {"name": "白银", "alpha_vantage": "XAG", "yahoo": "SI=F"},
            "PL": {"name": "铂金", "alpha_vantage": "XPT", "yahoo": "PL=F"},
            "PA": {"name": "钯金", "alpha_vantage": "XPD", "yahoo": "PA=F"},
            
            # 工业金属
            "HG": {"name": "铜", "alpha_vantage": "COPPER", "yahoo": "HG=F"},
            "ALI": {"name": "铝", "alpha_vantage": "ALUMINUM", "yahoo": "ALI=F"},
            
            # 农产品
            "ZC": {"name": "玉米", "alpha_vantage": "CORN", "yahoo": "ZC=F"},
            "ZW": {"name": "小麦", "alpha_vantage": "WHEAT", "yahoo": "ZW=F"},
            "ZS": {"name": "大豆", "alpha_vantage": "SOYBEAN", "yahoo": "ZS=F"},
            "CT": {"name": "棉花", "alpha_vantage": "COTTON", "yahoo": "CT=F"},
            "SB": {"name": "糖", "alpha_vantage": "SUGAR", "yahoo": "SB=F"},
            "KC": {"name": "咖啡", "alpha_vantage": "COFFEE", "yahoo": "KC=F"},
        }
    
    async def get_commodity_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        limit: int = 1000
    ) -> List[KlineData]:
        """
        获取商品期货K线数据
        
        Args:
            symbol: 商品代码 (如 "GC" for 黄金)
            timeframe: 时间周期
            limit: 数据条数
            
        Returns:
            K线数据列表
        """
        try:
            # 检查是否为支持的商品
            if symbol not in self.commodity_symbols:
                logger.warning(f"不支持的商品代码: {symbol}")
                return []
            
            commodity_info = self.commodity_symbols[symbol]
            logger.info(f"获取{commodity_info['name']}数据: {symbol}")
            
            # 使用Alpha Vantage获取数据
            if self.api_key:
                klines = await self._fetch_from_alpha_vantage(
                    symbol, 
                    commodity_info['alpha_vantage'],
                    timeframe, 
                    limit
                )
                if klines:
                    return klines
            
            # 如果Alpha Vantage失败,尝试使用Yahoo Finance作为备用
            logger.warning(f"Alpha Vantage获取失败,尝试Yahoo Finance")
            klines = await self._fetch_from_yahoo(
                commodity_info['yahoo'],
                symbol,
                timeframe,
                limit
            )
            
            return klines
            
        except Exception as e:
            logger.error(f"获取商品期货数据失败: {symbol} - {e}", exc_info=True)
            return []
    
    async def _fetch_from_alpha_vantage(
        self,
        symbol: str,
        av_symbol: str,
        timeframe: Timeframe,
        limit: int
    ) -> List[KlineData]:
        """从Alpha Vantage获取数据"""
        try:
            # Alpha Vantage商品数据API参数
            # 注意: Alpha Vantage商品数据通常只提供日线数据
            function_map = {
                Timeframe.D1: "TIME_SERIES_DAILY",
                Timeframe.W1: "TIME_SERIES_WEEKLY",
                Timeframe.MN1: "TIME_SERIES_MONTHLY"
            }
            
            # 对于不支持的时间框架,使用日线
            function = function_map.get(timeframe, "TIME_SERIES_DAILY")
            
            params = {
                "function": av_symbol,  # 对于商品,直接使用商品名称作为function
                "interval": "daily",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            # 对于某些商品,使用不同的API端点
            if av_symbol in ["WTI", "BRENT_CRUDE_OIL"]:
                params["function"] = av_symbol
            elif av_symbol.startswith("X"):  # 贵金属 (XAU, XAG, XPT, XPD)
                # 使用外汇API获取贵金属对美元价格
                params["function"] = "FX_DAILY"
                params["from_symbol"] = av_symbol
                params["to_symbol"] = "USD"
            else:
                # 其他商品,尝试使用通用商品API
                params["function"] = "COMMODITY"
                params["symbol"] = av_symbol
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=10) as response:
                    if response.status != 200:
                        logger.error(f"Alpha Vantage请求失败: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    # 检查API错误
                    if "Error Message" in data:
                        logger.error(f"Alpha Vantage API错误: {data['Error Message']}")
                        return []
                    
                    if "Note" in data:
                        logger.warning(f"Alpha Vantage API限流: {data['Note']}")
                        return []
                    
                    # 解析数据 (根据不同的API响应格式)
                    time_series_key = None
                    for key in data.keys():
                        if "Time Series" in key or "FX" in key:
                            time_series_key = key
                            break
                    
                    if not time_series_key:
                        logger.error(f"未找到时间序列数据: {list(data.keys())}")
                        return []
                    
                    time_series = data[time_series_key]
                    
                    # 转换为KlineData格式
                    klines = []
                    for date_str, values in sorted(time_series.items(), reverse=True)[:limit]:
                        try:
                            kline = KlineData(
                                symbol=symbol,
                                timeframe=timeframe,
                                market_type=MarketType.COMMODITY,
                                exchange="alpha_vantage",
                                timestamp=datetime.strptime(date_str, "%Y-%m-%d"),
                                open=float(values.get("1. open", values.get("1a. open (USD)", 0))),
                                high=float(values.get("2. high", values.get("2a. high (USD)", 0))),
                                low=float(values.get("3. low", values.get("3a. low (USD)", 0))),
                                close=float(values.get("4. close", values.get("4a. close (USD)", 0))),
                                volume=float(values.get("5. volume", 0))
                            )
                            klines.append(kline)
                        except (ValueError, KeyError) as e:
                            logger.warning(f"解析数据失败: {date_str} - {e}")
                            continue
                    
                    logger.info(f"从Alpha Vantage获取了 {len(klines)} 条{symbol}数据")
                    return klines
                    
        except Exception as e:
            logger.error(f"Alpha Vantage获取商品数据失败: {e}", exc_info=True)
            return []
    
    async def _fetch_from_yahoo(
        self,
        yahoo_symbol: str,
        symbol: str,
        timeframe: Timeframe,
        limit: int
    ) -> List[KlineData]:
        """从Yahoo Finance获取商品数据 (备用数据源)"""
        try:
            import yfinance as yf
            
            # 时间框架映射
            interval_map = {
                Timeframe.M1: "1m",
                Timeframe.M5: "5m",
                Timeframe.M15: "15m",
                Timeframe.M30: "30m",
                Timeframe.H1: "1h",
                Timeframe.H4: "1h",  # yfinance没有4h,使用1h
                Timeframe.D1: "1d",
                Timeframe.W1: "1wk",
                Timeframe.MN1: "1mo"
            }
            
            period_map = {
                Timeframe.M1: "1d",
                Timeframe.M5: "5d",
                Timeframe.M15: "5d",
                Timeframe.M30: "1mo",
                Timeframe.H1: "1mo",
                Timeframe.H4: "3mo",
                Timeframe.D1: "1y",
                Timeframe.W1: "2y",
                Timeframe.MN1: "5y"
            }
            
            interval = interval_map.get(timeframe, "1d")
            period = period_map.get(timeframe, "1y")
            
            # 获取数据
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"Yahoo Finance未返回{yahoo_symbol}数据")
                return []
            
            # 转换为KlineData格式
            klines = []
            for index, row in df.tail(limit).iterrows():
                try:
                    kline = KlineData(
                        symbol=symbol,
                        timeframe=timeframe,
                        market_type=MarketType.COMMODITY,
                        exchange="yahoo_finance",
                        timestamp=index.to_pydatetime(),
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=float(row['Volume'])
                    )
                    klines.append(kline)
                except Exception as e:
                    logger.warning(f"解析Yahoo Finance数据失败: {e}")
                    continue
            
            logger.info(f"从Yahoo Finance获取了 {len(klines)} 条{symbol}数据")
            return klines
            
        except Exception as e:
            logger.error(f"Yahoo Finance获取商品数据失败: {e}", exc_info=True)
            return []
    
    async def get_commodity_quote(self, symbol: str) -> Optional[Dict]:
        """
        获取商品实时报价
        
        Returns:
            包含价格、变化等信息的字典
        """
        try:
            if symbol not in self.commodity_symbols:
                return None
            
            commodity_info = self.commodity_symbols[symbol]
            
            # 使用Alpha Vantage获取实时报价
            if self.api_key:
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": commodity_info['yahoo'],  # 使用Yahoo符号
                    "apikey": self.api_key
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.base_url, params=params, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if "Global Quote" in data:
                                quote = data["Global Quote"]
                                return {
                                    "symbol": symbol,
                                    "name": commodity_info['name'],
                                    "price": float(quote.get("05. price", 0)),
                                    "change": float(quote.get("09. change", 0)),
                                    "change_percent": float(quote.get("10. change percent", "0%").replace("%", "")),
                                    "volume": int(float(quote.get("06. volume", 0))),
                                    "timestamp": datetime.now()
                                }
            
            # 如果Alpha Vantage失败,尝试Yahoo Finance
            import yfinance as yf
            ticker = yf.Ticker(commodity_info['yahoo'])
            info = ticker.info
            
            return {
                "symbol": symbol,
                "name": commodity_info['name'],
                "price": info.get('regularMarketPrice', 0),
                "change": info.get('regularMarketChange', 0),
                "change_percent": info.get('regularMarketChangePercent', 0),
                "volume": info.get('volume', 0),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"获取商品报价失败: {symbol} - {e}")
            return None
    
    def get_supported_commodities(self) -> List[Dict]:
        """获取支持的商品列表"""
        return [
            {
                "symbol": symbol,
                "name": info['name'],
                "yahoo_symbol": info['yahoo']
            }
            for symbol, info in self.commodity_symbols.items()
        ]


# 全局单例
commodity_data_service = CommodityDataService()
