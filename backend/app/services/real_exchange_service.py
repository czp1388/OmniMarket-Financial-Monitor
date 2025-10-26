# 寰宇多市场金融监控系统 - 真实交易所数据服务
import ccxt
import asyncio
import logging
from typing import Dict, List, Optional
import time
import aiohttp

logger = logging.getLogger(__name__)

class RealExchangeDataService:
    def __init__(self):
        self.exchanges = {}
        self._initialized = False
        self.realtime_prices = {}
        self.session = None
        
    async def initialize(self):
        """初始化真实交易所连接"""
        if self._initialized:
            return
            
        try:
            # 创建aiohttp会话
            self.session = aiohttp.ClientSession()
            
            # 初始化交易所（使用免费API，无需密钥）
            exchange_configs = {
                'binance': {
                    'class': ccxt.binance,
                    'config': {
                        'timeout': 10000,
                        'enableRateLimit': True,
                        'sandbox': False  # 使用真实市场
                    }
                },
                'okx': {
                    'class': ccxt.okx, 
                    'config': {
                        'timeout': 10000,
                        'enableRateLimit': True
                    }
                }
            }
            
            for name, config in exchange_configs.items():
                try:
                    exchange = config['class'](config['config'])
                    # 测试连接
                    markets = exchange.load_markets()
                    self.exchanges[name] = exchange
                    logger.info(f"✅ 交易所 {name} 连接成功，支持 {len(markets)} 个交易对")
                except Exception as e:
                    logger.warning(f"⚠️ 交易所 {name} 连接失败: {e}")
                    # 继续初始化其他交易所
            
            self._initialized = True
            logger.info("✅ 真实数据服务初始化完成")
            
            # 启动实时数据更新任务
            asyncio.create_task(self._start_realtime_updates())
            
        except Exception as e:
            logger.error(f"❌ 真实数据服务初始化失败: {e}")
            self._initialized = True  # 标记为已初始化，避免阻塞

    async def _start_realtime_updates(self):
        """启动实时数据更新"""
        logger.info("🔄 开始实时数据更新循环...")
        while True:
            try:
                await self._update_all_prices()
                # 每3秒更新一次，避免API限制
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"实时数据更新错误: {e}")
                await asyncio.sleep(5)  # 错误时等待更长时间

    async def _update_all_prices(self):
        """更新所有交易对价格"""
        symbols_to_watch = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 
            'ADA/USDT', 'DOT/USDT', 'LTC/USDT',
            'XRP/USDT', 'LINK/USDT', 'BCH/USDT'
        ]
        
        for exchange_name, exchange in self.exchanges.items():
            for symbol in symbols_to_watch:
                try:
                    # 使用异步方式获取ticker
                    ticker = exchange.fetch_ticker(symbol)
                    
                    self.realtime_prices[symbol] = {
                        'symbol': symbol,
                        'exchange': exchange_name,
                        'price': ticker['last'] if ticker['last'] else ticker['close'],
                        'high': ticker['high'],
                        'low': ticker['low'],
                        'volume': ticker['baseVolume'],
                        'change': ticker['change'] if ticker['change'] else 0,
                        'percentage': ticker['percentage'] if ticker['percentage'] else 0,
                        'timestamp': ticker['timestamp'],
                        'datetime': exchange.iso8601(ticker['timestamp']) if ticker['timestamp'] else None
                    }
                    
                except Exception as e:
                    # 单个交易对失败不影响其他
                    logger.debug(f"获取 {exchange_name} {symbol} 价格失败: {e}")
                    continue

    def get_supported_exchanges(self) -> List[str]:
        return list(self.exchanges.keys())

    def get_symbols(self, exchange: str, limit: int = 20) -> List[str]:
        if exchange in self.exchanges:
            try:
                return list(self.exchanges[exchange].markets.keys())[:limit]
            except:
                return []
        return []

    def get_price(self, exchange: str, symbol: str) -> Optional[Dict]:
        # 首先从实时数据中查找
        for price_data in self.realtime_prices.values():
            if price_data['symbol'] == symbol and price_data['exchange'] == exchange:
                return price_data
        
        # 实时数据中没有，则实时获取
        if exchange in self.exchanges:
            try:
                ticker = self.exchanges[exchange].fetch_ticker(symbol)
                return {
                    'symbol': symbol,
                    'exchange': exchange,
                    'price': ticker['last'] if ticker['last'] else ticker['close'],
                    'high': ticker['high'],
                    'low': ticker['low'],
                    'volume': ticker['baseVolume'],
                    'change': ticker['change'] if ticker['change'] else 0,
                    'percentage': ticker['percentage'] if ticker['percentage'] else 0,
                    'timestamp': ticker['timestamp']
                }
            except Exception as e:
                logger.warning(f"实时获取价格失败 {exchange} {symbol}: {e}")
        
        return None

    def get_realtime_prices(self) -> Dict:
        """获取所有实时价格数据"""
        return self.realtime_prices

    async def close(self):
        """关闭资源"""
        if self.session:
            await self.session.close()

# 创建实例
real_data_service = RealExchangeDataService()
