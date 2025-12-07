import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import ccxt
from models.market_data import KlineData, MarketType, Timeframe
from database import get_influxdb
from .websocket_manager import websocket_manager
from .yfinance_data_service import yfinance_data_service
from .alpha_vantage_service import alpha_vantage_service
from .coingecko_service import coingecko_service
from .akshare_service import akshare_service
from .commodity_data_service import commodity_data_service
from .data_cache_service import data_cache_service
from .data_quality_monitor import data_quality_monitor

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.exchanges = {}
        self.setup_exchanges()
        self._register_data_sources()
        
    def _register_data_sources(self):
        """注册数据源到质量监控器"""
        sources = [
            "coingecko",
            "alpha_vantage", 
            "yfinance",
            "akshare",
            "ccxt_binance",
            "commodity",
            "mock"
        ]
        for source in sources:
            data_quality_monitor.register_source(source)
    
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
        """获取K线数据 - 集成多个免费数据源"""
        try:
            # 生成缓存键
            cache_key = f"klines_{symbol}_{market_type.value}_{timeframe.value}_{limit}"
            
            # 尝试从缓存获取
            cached_data = await data_cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"从缓存获取K线数据: {symbol}")
                return cached_data
            
            klines = []
            
            if market_type == MarketType.CRYPTO:
                # 优先使用CoinGecko，其次是Alpha Vantage，最后是交易所
                start_time = time.time()
                try:
                    klines = await coingecko_service.get_crypto_klines(symbol, timeframe, limit)
                    if klines:
                        response_time = time.time() - start_time
                        data_quality_monitor.record_success("coingecko", response_time)
                        logger.info(f"使用CoinGecko获取加密货币K线数据: {symbol}")
                except Exception as e1:
                    data_quality_monitor.record_error("coingecko")
                    logger.warning(f"CoinGecko获取失败，尝试Alpha Vantage: {e1}")
                    start_time_av = time.time()
                    try:
                        klines = await alpha_vantage_service.get_crypto_klines(symbol, timeframe, limit)
                        if klines:
                            response_time = time.time() - start_time_av
                            data_quality_monitor.record_success("alpha_vantage", response_time)
                            logger.info(f"使用Alpha Vantage获取加密货币K线数据: {symbol}")
                    except Exception as e2:
                        data_quality_monitor.record_error("alpha_vantage")
                        logger.warning(f"Alpha Vantage获取失败，尝试交易所: {e2}")
                        start_time_ex = time.time()
                        try:
                            exchange_instance = self.exchanges.get('binance')
                            if exchange_instance:
                                # 转换时间框架到ccxt格式
                                tf_mapping = {
                                    Timeframe.M1: '1m',
                                    Timeframe.M5: '5m',
                                    Timeframe.M15: '15m',
                                    Timeframe.H1: '1h',
                                    Timeframe.H4: '4h',
                                    Timeframe.D1: '1d',
                                    Timeframe.W1: '1w',
                                    Timeframe.MN1: '1M'
                                }
                                ccxt_tf = tf_mapping.get(timeframe, '1h')
                                
                                ohlcv = exchange_instance.fetch_ohlcv(symbol, ccxt_tf, limit=limit)
                                klines = []
                                for data in ohlcv:
                                    kline = KlineData(
                                        symbol=symbol,
                                        timeframe=timeframe,
                                        market_type=market_type,
                                        exchange='binance',
                                        timestamp=datetime.fromtimestamp(data[0] / 1000),
                                        open=data[1],
                                        high=data[2],
                                        low=data[3],
                                        close=data[4],
                                        volume=data[5]
                                    )
                                    klines.append(kline)
                                response_time = time.time() - start_time_ex
                                data_quality_monitor.record_success("ccxt_binance", response_time)
                                logger.info(f"使用交易所获取加密货币K线数据: {symbol}")
                        except Exception as e3:
                            data_quality_monitor.record_error("ccxt_binance")
                            logger.error(f"所有加密货币数据源都失败: {e3}")
                
            elif market_type == MarketType.STOCK:
                # 优先使用Alpha Vantage，其次是Yahoo Finance，最后是AkShare
                start_time_av = time.time()
                try:
                    klines = await alpha_vantage_service.get_stock_klines(symbol, timeframe, limit, start_time, end_time)
                    if klines:
                        response_time = time.time() - start_time_av
                        data_quality_monitor.record_success("alpha_vantage", response_time)
                        logger.info(f"使用Alpha Vantage获取股票K线数据: {symbol}")
                except Exception as e1:
                    data_quality_monitor.record_error("alpha_vantage")
                    logger.warning(f"Alpha Vantage获取失败，尝试Yahoo Finance: {e1}")
                    start_time_yf = time.time()
                    try:
                        klines = await yfinance_data_service.get_stock_klines(symbol, timeframe, limit, start_time, end_time)
                        if klines:
                            response_time = time.time() - start_time_yf
                            data_quality_monitor.record_success("yfinance", response_time)
                            logger.info(f"使用Yahoo Finance获取股票K线数据: {symbol}")
                    except Exception as e2:
                        data_quality_monitor.record_error("yfinance")
                        logger.warning(f"Yahoo Finance获取失败，尝试AkShare: {e2}")
                        start_time_ak = time.time()
                        try:
                            klines = await akshare_service.get_stock_klines(symbol, timeframe, limit, start_time, end_time)
                            if klines:
                                response_time = time.time() - start_time_ak
                                data_quality_monitor.record_success("akshare", response_time)
                                logger.info(f"使用AkShare获取股票K线数据: {symbol}")
                        except Exception as e3:
                            data_quality_monitor.record_error("akshare")
                            logger.error(f"所有股票数据源都失败: {e3}")
            
            elif market_type == MarketType.FOREX:
                # 使用Alpha Vantage获取外汇数据
                start_time_av = time.time()
                try:
                    klines = await alpha_vantage_service.get_forex_klines(symbol, timeframe, limit)
                    if klines:
                        response_time = time.time() - start_time_av
                        data_quality_monitor.record_success("alpha_vantage", response_time)
                        logger.info(f"使用Alpha Vantage获取外汇K线数据: {symbol}")
                except Exception as e:
                    data_quality_monitor.record_error("alpha_vantage")
                    logger.error(f"外汇数据获取失败: {e}")
            
            elif market_type == MarketType.COMMODITY:
                # 商品期货数据
                start_time_commodity = time.time()
                try:
                    klines = await commodity_data_service.get_commodity_klines(symbol, timeframe, limit)
                    if klines:
                        response_time = time.time() - start_time_commodity
                        data_quality_monitor.record_success("commodity", response_time)
                        logger.info(f"获取商品期货K线数据: {symbol}")
                except Exception as e:
                    data_quality_monitor.record_error("commodity")
                    logger.error(f"商品期货数据获取失败: {e}")
            
            else:
                # 其他市场类型使用模拟数据
                start_time_mock = time.time()
                klines = await self._get_mock_data(symbol, timeframe, market_type, limit)
                response_time = time.time() - start_time_mock
                data_quality_monitor.record_success("mock", response_time)
                logger.info(f"使用模拟数据: {symbol}")
            
            # 如果获取到数据，保存到缓存
            if klines:
                await data_cache_service.set(cache_key, klines, ttl=300)  # 缓存5分钟
                # 保存到InfluxDB
                await self._save_to_influxdb(klines)
            
            if not klines:
                # 如果所有数据源都失败，使用模拟数据作为后备
                start_time_mock = time.time()
                klines = await self._get_mock_data(symbol, timeframe, market_type, limit)
                response_time = time.time() - start_time_mock
                data_quality_monitor.record_success("mock", response_time)
                logger.info(f"所有数据源失败，使用模拟数据: {symbol}")
                
            return klines
                
        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            start_time_mock = time.time()
            mock_data = await self._get_mock_data(symbol, timeframe, market_type, limit)
            response_time = time.time() - start_time_mock
            data_quality_monitor.record_success("mock", response_time)
            return mock_data
    
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
        
        # 根据市场类型确定交易所
        exchange_mapping = {
            MarketType.CRYPTO: "binance",
            MarketType.STOCK: "mock_exchange",
            MarketType.FOREX: "mock_forex",
            MarketType.FUTURES: "mock_futures",
            MarketType.INDEX: "mock_index",
            MarketType.FUND: "mock_fund"
        }
        exchange = exchange_mapping.get(market_type, "mock_exchange")
        
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
                exchange=exchange,
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
            Timeframe.M1: 1,
            Timeframe.M5: 5,
            Timeframe.M15: 15,
            Timeframe.H1: 60,
            Timeframe.H4: 240,
            Timeframe.D1: 1440,
            Timeframe.W1: 10080,
            Timeframe.MN1: 43200
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
            elif market_type == MarketType.STOCK:
                # 使用Yahoo Finance获取股票实时价格
                quote = await yfinance_data_service.get_stock_quote(symbol)
                return quote['last_price']
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
    
    async def start_real_time_updates(self):
        """启动实时数据更新服务"""
        logger.info("启动实时数据更新服务")
        # 启动定时任务，定期推送实时数据
        asyncio.create_task(self._real_time_update_loop())
    
    async def _real_time_update_loop(self):
        """实时数据更新循环"""
        while True:
            try:
                # 获取最新的行情数据
                tickers = await self.get_tickers()
                
                # 向所有订阅者广播实时数据
                for ticker in tickers:
                    await websocket_manager.broadcast_to_subscribers(
                        ticker['symbol'],
                        {
                            'type': 'price_update',
                            'symbol': ticker['symbol'],
                            'price': ticker['last'],
                            'change': ticker['change'],
                            'change_percent': ticker['change_percent'],
                            'volume': ticker['volume'],
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                
                # 每5秒更新一次
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"实时数据更新循环出错: {e}")
                await asyncio.sleep(10)  # 出错时等待更长时间
    
    async def start(self):
        """启动数据服务"""
        logger.info("数据服务已启动")
        # 启动实时数据更新
        await self.start_real_time_updates()
    
    async def stop(self):
        """停止数据服务"""
        logger.info("数据服务已停止")
        # 这里可以添加数据服务停止时的清理逻辑


# 全局数据服务实例
data_service = DataService()
