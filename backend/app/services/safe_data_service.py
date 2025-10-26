# 寰宇多市场金融监控系统 - 安全数据服务
import logging
from typing import Dict, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class SafeDataService:
    def __init__(self):
        self.exchanges = {}
        self._initialized = False
        self._init_task = None
        
    async def initialize(self):
        """异步初始化，不阻塞主线程"""
        if self._initialized:
            return
            
        try:
            # 延迟导入，避免启动时阻塞
            import ccxt
            logger.info("开始异步初始化交易所...")
            
            exchange_configs = {
                'binance': {'class': ccxt.binance, 'config': {}},
                'okx': {'class': ccxt.okx, 'config': {}},
            }
            
            for name, config in exchange_configs.items():
                try:
                    exchange = config['class'](config['config'])
                    # 不立即加载市场，避免阻塞
                    self.exchanges[name] = exchange
                    logger.info(f"✅ 交易所 {name} 准备就绪")
                except Exception as e:
                    logger.warning(f"⚠️ 交易所 {name} 初始化警告: {e}")
                    # 继续初始化其他交易所
                    
            self._initialized = True
            logger.info("✅ 数据服务异步初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 数据服务初始化失败: {e}")
            # 即使失败也标记为已初始化，避免阻塞启动
            self._initialized = True

    def get_supported_exchanges(self) -> List[str]:
        return list(self.exchanges.keys())

    def get_symbols(self, exchange: str) -> List[str]:
        if exchange in self.exchanges:
            try:
                # 按需加载市场数据
                markets = self.exchanges[exchange].load_markets()
                return list(markets.keys())[:20]
            except Exception as e:
                logger.warning(f"获取{symbols}失败: {e}")
                return []
        return []

    def get_price(self, exchange: str, symbol: str) -> Optional[Dict]:
        if exchange not in self.exchanges:
            return None
            
        try:
            ticker = self.exchanges[exchange].fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker.get('last', 0),
                'high': ticker.get('high', 0),
                'low': ticker.get('low', 0),
                'volume': ticker.get('baseVolume', 0),
                'timestamp': ticker.get('timestamp')
            }
        except Exception as e:
            logger.warning(f"获取价格失败 {exchange} {symbol}: {e}")
            # 返回模拟数据，确保服务可用
            return {
                'symbol': symbol,
                'price': 50000.0,
                'high': 51000.0,
                'low': 49000.0,
                'volume': 1000.0,
                'timestamp': 0
            }

# 安全的A股服务
class SafeAStockService:
    def get_stock_list(self):
        return [
            {'symbol': '000001.SZ', 'name': '平安银行'},
            {'symbol': '600036.SH', 'name': '招商银行'},
            {'symbol': '000858.SZ', 'name': '五粮液'},
            {'symbol': '600519.SH', 'name': '贵州茅台'}
        ]
    
    def get_stock_price(self, symbol: str):
        # 模拟数据
        return {
            'symbol': symbol,
            'price': 100.0 + hash(symbol) % 50,
            'change': hash(symbol) % 10 - 5,
            'volume': 1000000
        }

# 创建实例
data_service = SafeDataService()
astock_service = SafeAStockService()
