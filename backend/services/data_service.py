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
    
    def get_supported_exchanges(self) -> List[str]:
        """
        获取支持的交易所列表（同步方法）
        
        Returns:
            交易所名称列表
        """
        # 返回已配置的交易所加上常见交易所
        supported = list(self.exchanges.keys())
        
        # 添加其他支持的交易所
        additional_exchanges = ['binance', 'okx', 'bybit', 'huobi', 'kraken', 'coinbase']
        for ex in additional_exchanges:
            if ex not in supported:
                supported.append(ex)
        
        return supported
    
    async def get_quote(
        self,
        symbol: str,
        market_type: MarketType,
        exchange: str = "binance"
    ) -> Optional[Dict]:
        """
        获取实时报价数据
        
        参数:
            symbol: 交易对符号
            market_type: 市场类型
            exchange: 交易所名称
        
        返回:
            包含报价信息的字典，包括：
            - symbol: 交易对
            - price: 当前价格
            - bid: 买入价
            - ask: 卖出价
            - high: 24小时最高价
            - low: 24小时最低价
            - volume: 24小时成交量
            - change: 24小时价格变化
            - change_percent: 24小时价格变化百分比
            - timestamp: 时间戳
        """
        try:
            # 生成缓存键
            cache_key = f"quote_{symbol}_{market_type.value}_{exchange}"
            
            # 尝试从缓存获取
            cached_data = await data_cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"从缓存获取报价: {symbol}")
                return cached_data
            
            quote = None
            
            if market_type == MarketType.CRYPTO:
                # 加密货币报价
                try:
                    # 优先使用 CoinGecko
                    quote = await coingecko_service.get_crypto_quote(symbol)
                    if quote:
                        logger.info(f"使用CoinGecko获取加密货币报价: {symbol}")
                except Exception as e1:
                    logger.warning(f"CoinGecko获取报价失败，尝试交易所: {e1}")
                    try:
                        # 使用交易所API
                        if exchange in self.exchanges:
                            ex = self.exchanges[exchange]
                            ticker = await asyncio.to_thread(ex.fetch_ticker, symbol)
                            quote = {
                                'symbol': symbol,
                                'price': ticker.get('last', 0),
                                'bid': ticker.get('bid', 0),
                                'ask': ticker.get('ask', 0),
                                'high': ticker.get('high', 0),
                                'low': ticker.get('low', 0),
                                'volume': ticker.get('quoteVolume', 0),
                                'change': ticker.get('change', 0),
                                'change_percent': ticker.get('percentage', 0),
                                'timestamp': datetime.now().isoformat()
                            }
                            logger.info(f"使用{exchange}交易所获取报价: {symbol}")
                    except Exception as e2:
                        logger.warning(f"交易所获取报价失败: {e2}")
            
            elif market_type == MarketType.STOCK:
                # 股票报价
                try:
                    # 优先使用 yfinance
                    quote = await yfinance_data_service.get_stock_quote(symbol)
                    if quote:
                        logger.info(f"使用yfinance获取股票报价: {symbol}")
                except Exception as e1:
                    logger.warning(f"yfinance获取报价失败，尝试Alpha Vantage: {e1}")
                    try:
                        quote = await alpha_vantage_service.get_stock_quote(symbol)
                        if quote:
                            logger.info(f"使用Alpha Vantage获取股票报价: {symbol}")
                    except Exception as e2:
                        logger.warning(f"Alpha Vantage获取报价失败: {e2}")
            
            elif market_type == MarketType.FOREX:
                # 外汇报价
                try:
                    quote = await alpha_vantage_service.get_forex_quote(symbol)
                    if quote:
                        logger.info(f"使用Alpha Vantage获取外汇报价: {symbol}")
                except Exception as e:
                    logger.warning(f"获取外汇报价失败: {e}")
            
            # 如果所有数据源都失败，返回模拟数据
            if not quote:
                import random
                quote = {
                    'symbol': symbol,
                    'price': round(random.uniform(90, 110), 2),
                    'bid': round(random.uniform(89, 99), 2),
                    'ask': round(random.uniform(91, 101), 2),
                    'high': round(random.uniform(100, 120), 2),
                    'low': round(random.uniform(80, 100), 2),
                    'volume': round(random.uniform(1000000, 10000000), 2),
                    'change': round(random.uniform(-5, 5), 2),
                    'change_percent': round(random.uniform(-5, 5), 2),
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"所有数据源失败，返回模拟报价: {symbol}")
            
            # 缓存报价数据（TTL=10秒）
            if quote:
                await data_cache_service.set(cache_key, quote, ttl=10)
            
            return quote
            
        except Exception as e:
            logger.error(f"获取报价失败: {e}")
            # 返回基本的模拟数据
            return {
                'symbol': symbol,
                'price': 100.0,
                'timestamp': datetime.now().isoformat()
            }
    
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
    
    async def get_market_symbols(
        self,
        market_type: MarketType,
        exchange: str = "binance",
        limit: int = 100
    ) -> List[Dict]:
        """
        获取市场品种列表
        
        Args:
            market_type: 市场类型
            exchange: 交易所名称
            limit: 返回数量限制
        
        Returns:
            品种列表，包含 symbol, name, price 等信息
        """
        try:
            if market_type == MarketType.CRYPTO:
                # 加密货币市场
                if exchange in self.exchanges:
                    try:
                        markets = self.exchanges[exchange].load_markets()
                        symbols_list = []
                        
                        for symbol, market in list(markets.items())[:limit]:
                            if '/USDT' in symbol or '/USD' in symbol:
                                symbols_list.append({
                                    'symbol': symbol,
                                    'name': market.get('base', symbol.split('/')[0]),
                                    'exchange': exchange,
                                    'type': 'crypto'
                                })
                        
                        if symbols_list:
                            return symbols_list
                    except Exception as e:
                        logger.warning(f"从交易所加载市场失败: {e}")
                
                # 降级到默认列表
                return [
                    {'symbol': 'BTC/USDT', 'name': 'Bitcoin', 'exchange': exchange, 'type': 'crypto'},
                    {'symbol': 'ETH/USDT', 'name': 'Ethereum', 'exchange': exchange, 'type': 'crypto'},
                    {'symbol': 'BNB/USDT', 'name': 'Binance Coin', 'exchange': exchange, 'type': 'crypto'},
                    {'symbol': 'SOL/USDT', 'name': 'Solana', 'exchange': exchange, 'type': 'crypto'},
                    {'symbol': 'XRP/USDT', 'name': 'Ripple', 'exchange': exchange, 'type': 'crypto'},
                ][:limit]
            
            elif market_type == MarketType.STOCK:
                # 股票市场
                return [
                    {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ', 'type': 'stock'},
                    {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'exchange': 'NASDAQ', 'type': 'stock'},
                    {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ', 'type': 'stock'},
                    {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ', 'type': 'stock'},
                    {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ', 'type': 'stock'},
                    {'symbol': '600519.SS', 'name': '贵州茅台', 'exchange': 'SSE', 'type': 'stock'},
                    {'symbol': '000001.SZ', 'name': '平安银行', 'exchange': 'SZSE', 'type': 'stock'},
                ][:limit]
            
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取市场品种列表失败: {e}")
            return []
    
    async def get_historical_data(
        self,
        symbol: str,
        market_type: MarketType,
        start_date: datetime,
        end_date: datetime,
        timeframe: Timeframe = Timeframe.D1
    ) -> List[KlineData]:
        """
        获取历史数据
        
        Args:
            symbol: 品种代码
            market_type: 市场类型
            start_date: 开始日期
            end_date: 结束日期
            timeframe: 时间周期
        
        Returns:
            历史K线数据列表
        """
        try:
            # 复用 get_klines 方法
            exchange = "binance" if market_type == MarketType.CRYPTO else "nasdaq"
            
            # 计算需要的数据量
            days_diff = (end_date - start_date).days
            limit = max(days_diff, 100)
            
            klines = await self.get_klines(
                symbol=symbol,
                market_type=market_type,
                exchange=exchange,
                timeframe=timeframe,
                limit=limit
            )
            
            # 过滤日期范围
            filtered_klines = [
                k for k in klines
                if start_date <= k.timestamp <= end_date
            ]
            
            return filtered_klines
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return []
    
    async def search_symbols(
        self,
        keyword: str,
        market_type: Optional[MarketType] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        搜索品种
        
        Args:
            keyword: 搜索关键词
            market_type: 市场类型（可选）
            limit: 返回数量限制
        
        Returns:
            匹配的品种列表
        """
        try:
            keyword_upper = keyword.upper()
            results = []
            
            # 搜索范围
            markets_to_search = [market_type] if market_type else [
                MarketType.CRYPTO,
                MarketType.STOCK
            ]
            
            for mtype in markets_to_search:
                symbols = await self.get_market_symbols(mtype, limit=100)
                
                # 过滤匹配的品种
                for sym_info in symbols:
                    if (keyword_upper in sym_info['symbol'].upper() or 
                        keyword_upper in sym_info.get('name', '').upper()):
                        results.append(sym_info)
                        
                        if len(results) >= limit:
                            return results
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"搜索品种失败: {e}")
            return []
    
    async def validate_symbol(
        self,
        symbol: str,
        market_type: MarketType,
        exchange: str = "binance"
    ) -> bool:
        """
        验证品种代码是否有效
        
        Args:
            symbol: 品种代码
            market_type: 市场类型
            exchange: 交易所
        
        Returns:
            True 如果有效，否则 False
        """
        try:
            if market_type == MarketType.CRYPTO:
                if exchange in self.exchanges:
                    markets = self.exchanges[exchange].load_markets()
                    return symbol in markets
                else:
                    # 基本验证格式
                    return '/' in symbol and len(symbol.split('/')) == 2
            
            elif market_type == MarketType.STOCK:
                # 股票代码基本格式验证
                if len(symbol) >= 1:
                    return True
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"验证品种失败: {e}")
            return False
    
    async def get_market_info(
        self,
        symbol: str,
        market_type: MarketType,
        exchange: str = "binance"
    ) -> Optional[Dict]:
        """
        获取市场信息
        
        Args:
            symbol: 品种代码
            market_type: 市场类型
            exchange: 交易所
        
        Returns:
            市场信息字典
        """
        try:
            if market_type == MarketType.CRYPTO:
                if exchange in self.exchanges:
                    markets = self.exchanges[exchange].load_markets()
                    if symbol in markets:
                        market = markets[symbol]
                        return {
                            'symbol': symbol,
                            'base': market.get('base'),
                            'quote': market.get('quote'),
                            'active': market.get('active', True),
                            'exchange': exchange,
                            'type': 'crypto',
                            'precision': market.get('precision', {}),
                            'limits': market.get('limits', {}),
                        }
            
            # 返回基本信息
            return {
                'symbol': symbol,
                'market_type': market_type.value,
                'exchange': exchange,
                'active': True
            }
            
        except Exception as e:
            logger.error(f"获取市场信息失败: {e}")
            return None
    
    def get_supported_timeframes(self) -> List[str]:
        """
        获取支持的时间周期列表
        
        Returns:
            时间周期列表
        """
        return [
            '1m', '5m', '15m', '30m',
            '1h', '4h', '12h',
            '1d', '1w', '1M'
        ]


# 全局数据服务实例
data_service = DataService()
