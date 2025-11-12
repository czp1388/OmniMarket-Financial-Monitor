import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import ccxt
from backend.models.market_data import KlineData, MarketType, Timeframe
from backend.database import get_influxdb

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.exchanges = {}
        self.setup_exchanges()
    
    def setup_exchanges(self):
        """初始化交易所连接"""
        try:
            # 加密货币交易所
            self.exchanges['binance'] = ccxt.binance({
                'enableRateLimit': True,
                'timeout': 30000,
            })
            # 可以添加更多交易所
            # self.exchanges['okx'] = ccxt.okx()
            # self.exchanges['bybit'] = ccxt.bybit()
            
        except Exception as e:
            logger.error(f"初始化交易所失败: {e}")
    
    async def get_klines(
        self, 
        symbol: str, 
        market_type: MarketType,
        exchange: str,
        timeframe: Timeframe,
        limit: int = 1000,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[KlineData]:
        """获取K线数据"""
        try:
            if market_type == MarketType.CRYPTO:
                exchange = self.exchanges.get('binance')
                if not exchange:
                    raise ValueError("加密货币交易所未初始化")
                
                # 转换时间框架到ccxt格式
                tf_mapping = {
                    Timeframe.MINUTE_1: '1m',
                    Timeframe.MINUTE_5: '5m',
                    Timeframe.MINUTE_15: '15m',
                    Timeframe.HOUR_1: '1h',
                    Timeframe.HOUR_4: '4h',
                    Timeframe.DAILY: '1d',
                    Timeframe.WEEKLY: '1w',
                    Timeframe.MONTHLY: '1M'
                }
                
                ccxt_tf = tf_mapping.get(timeframe, '1h')
                
                # 获取OHLCV数据
                ohlcv = exchange.fetch_ohlcv(symbol, ccxt_tf, limit=limit)
                
                klines = []
                for data in ohlcv:
                    kline = KlineData(
                        symbol=symbol,
                        timeframe=timeframe,
                        market_type=market_type,
                        timestamp=datetime.fromtimestamp(data[0] / 1000),
                        open=data[1],
                        high=data[2],
                        low=data[3],
                        close=data[4],
                        volume=data[5]
                    )
                    klines.append(kline)
                
                # 保存到InfluxDB
                await self._save_to_influxdb(klines)
                
                return klines
                
            else:
                # 其他市场类型的实现（股票、外汇等）
                # 这里可以集成其他数据源API
                return await self._get_mock_data(symbol, timeframe, market_type, limit)
                
        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            return []
    
    async def _save_to_influxdb(self, klines: List[KlineData]):
        """保存数据到InfluxDB"""
        try:
            influx_client, influx_write_api, influx_query_api = get_influxdb()
            if not influx_client:
                return
            
            points = []
            for kline in klines:
                point = {
                    "measurement": "kline_data",
                    "tags": {
                        "symbol": kline.symbol,
                        "timeframe": kline.timeframe.value,
                        "market_type": kline.market_type.value
                    },
                    "time": kline.timestamp,
                    "fields": {
                        "open": kline.open,
                        "high": kline.high,
                        "low": kline.low,
                        "close": kline.close,
                        "volume": kline.volume
                    }
                }
                points.append(point)
            
            # 写入数据
            # 注意：这里需要根据实际的InfluxDB客户端API调整
            # influx_write_api.write(bucket=settings.INFLUXDB_BUCKET, record=points)
            
        except Exception as e:
            logger.error(f"保存数据到InfluxDB失败: {e}")
    
    async def _get_mock_data(
        self, 
        symbol: str, 
        timeframe: Timeframe,
        market_type: MarketType,
        limit: int
    ) -> List[KlineData]:
        """生成模拟数据（用于开发和测试）"""
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
                market_type=market_type,
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
            if market_type == MarketType.CRYPTO:
                exchange = self.exchanges.get('binance')
                if exchange:
                    ticker = exchange.fetch_ticker(symbol)
                    return ticker['last']
            return 0.0
        except Exception as e:
            logger.error(f"获取当前价格失败: {e}")
            return 0.0
    
    async def get_orderbook(self, symbol: str, market_type: MarketType, exchange: str, depth: int = 20) -> Dict:
        """获取订单簿数据"""
        try:
            if market_type == MarketType.CRYPTO:
                exchange_instance = self.exchanges.get(exchange)
                if exchange_instance:
                    order_book = exchange_instance.fetch_order_book(symbol, depth)
                    return order_book
            return {'bids': [], 'asks': []}
        except Exception as e:
            logger.error(f"获取订单簿失败: {e}")
            return {'bids': [], 'asks': []}
    
    async def get_tickers(self, symbols: Optional[List[str]] = None, market_type: Optional[MarketType] = None, exchange: Optional[str] = None) -> List[Dict]:
        """获取行情数据"""
        try:
            # 如果指定了市场类型为加密货币，尝试从交易所获取数据
            if market_type == MarketType.CRYPTO:
                exchange_instance = self.exchanges.get(exchange or 'binance')
                if exchange_instance:
                    try:
                        if symbols:
                            tickers = []
                            for symbol in symbols:
                                ticker = exchange_instance.fetch_ticker(symbol)
                                tickers.append({
                                    'symbol': symbol,
                                    'last': ticker['last'],
                                    'open': ticker['open'],
                                    'high': ticker['high'],
                                    'low': ticker['low'],
                                    'close': ticker['close'],
                                    'volume': ticker['baseVolume'],
                                    'timestamp': datetime.fromtimestamp(ticker['timestamp'] / 1000),
                                    'change': ticker['last'] - ticker['open'],
                                    'change_percent': ((ticker['last'] - ticker['open']) / ticker['open']) * 100 if ticker['open'] else 0
                                })
                            return tickers
                        else:
                            # 获取所有交易对的ticker
                            tickers = exchange_instance.fetch_tickers()
                            return [{
                                'symbol': symbol,
                                'last': ticker['last'],
                                'open': ticker['open'],
                                'high': ticker['high'],
                                'low': ticker['low'],
                                'close': ticker['close'],
                                'volume': ticker['baseVolume'],
                                'timestamp': datetime.fromtimestamp(ticker['timestamp'] / 1000),
                                'change': ticker['last'] - ticker['open'],
                                'change_percent': ((ticker['last'] - ticker['open']) / ticker['open']) * 100 if ticker['open'] else 0
                            } for symbol, ticker in tickers.items()]
                    except Exception as exchange_error:
                        logger.warning(f"从交易所获取数据失败，使用模拟数据: {exchange_error}")
                        # 如果交易所获取失败，使用模拟数据
                        return await self._get_mock_tickers(symbols, market_type)
            
            # 如果没有指定市场类型或不是加密货币，使用模拟数据
            return await self._get_mock_tickers(symbols, market_type)
        except Exception as e:
            logger.error(f"获取行情数据失败: {e}")
            return await self._get_mock_tickers(symbols, market_type)
    
    async def _get_mock_tickers(self, symbols: Optional[List[str]] = None, market_type: Optional[MarketType] = None) -> List[Dict]:
        """生成模拟行情数据"""
        import random
        from datetime import datetime
        
        # 默认的模拟交易对
        default_symbols = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT",
            "LINK/USDT", "LTC/USDT", "BCH/USDT", "XRP/USDT", "EOS/USDT",
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "EUR/USD", "GBP/USD", "USD/JPY", "USD/CNY", "AUD/USD"
        ]
        
        if symbols:
            target_symbols = symbols
        else:
            target_symbols = default_symbols
        
        tickers = []
        for symbol in target_symbols:
            # 根据符号类型设置基础价格
            if "BTC" in symbol:
                base_price = 42567.39
            elif "ETH" in symbol:
                base_price = 2345.67
            elif "AAPL" in symbol:
                base_price = 182.45
            elif "MSFT" in symbol:
                base_price = 345.67
            elif "GOOGL" in symbol:
                base_price = 2789.12
            elif "AMZN" in symbol:
                base_price = 3456.78
            elif "TSLA" in symbol:
                base_price = 245.67
            elif "EUR" in symbol:
                base_price = 1.0850
            elif "GBP" in symbol:
                base_price = 1.2650
            elif "JPY" in symbol:
                base_price = 150.25
            elif "CNY" in symbol:
                base_price = 7.1987
            elif "AUD" in symbol:
                base_price = 0.6580
            else:
                base_price = 100.0
            
            # 生成随机价格波动
            change_percent = random.uniform(-5.0, 5.0)
            change_amount = base_price * (change_percent / 100)
            last_price = base_price + change_amount
            
            open_price = base_price
            high = max(base_price, last_price) + random.uniform(0, base_price * 0.02)
            low = min(base_price, last_price) - random.uniform(0, base_price * 0.02)
            volume = random.uniform(1000, 1000000)
            
            ticker = {
                'symbol': symbol,
                'last': round(last_price, 4),
                'open': round(open_price, 4),
                'high': round(high, 4),
                'low': round(low, 4),
                'close': round(last_price, 4),
                'volume': round(volume, 2),
                'timestamp': datetime.now(),
                'change': round(change_amount, 4),
                'change_percent': round(change_percent, 2)
            }
            tickers.append(ticker)
        
        return tickers
    
    async def get_symbols(self, market_type: Optional[MarketType] = None, exchange: Optional[str] = None) -> List[str]:
        """获取可交易符号列表"""
        try:
            if market_type == MarketType.CRYPTO:
                exchange_instance = self.exchanges.get(exchange or 'binance')
                if exchange_instance:
                    markets = exchange_instance.load_markets()
                    return list(markets.keys())
            return []
        except Exception as e:
            logger.error(f"获取符号列表失败: {e}")
            return []
    
    async def get_supported_exchanges(self) -> List[str]:
        """获取支持的交易所列表"""
        return list(self.exchanges.keys())
    
    async def start(self):
        """启动数据服务"""
        logger.info("数据服务已启动")
        # 这里可以添加数据服务启动时的初始化逻辑
        # 例如：开始定时获取数据、监控市场等
    
    async def stop(self):
        """停止数据服务"""
        logger.info("数据服务已停止")
        # 这里可以添加数据服务停止时的清理逻辑


# 全局数据服务实例
data_service = DataService()
