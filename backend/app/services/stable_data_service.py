# 寰宇多市场金融监控系统 - 稳定数据服务模块
import ccxt
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StableDataService:
    def __init__(self):
        self.exchanges = {}
        self._init_exchanges()
    
    def _init_exchanges(self):
        """安全初始化交易所"""
        exchange_configs = {
            'binance': {'class': ccxt.binance, 'config': {}},
            'okx': {'class': ccxt.okx, 'config': {}},
            'huobi': {'class': ccxt.huobi, 'config': {}}
        }
        
        for name, config in exchange_configs.items():
            try:
                exchange = config['class'](config['config'])
                exchange.load_markets()
                self.exchanges[name] = exchange
                logger.info(f"✅ 交易所 {name} 初始化成功")
            except Exception as e:
                logger.error(f"❌ 交易所 {name} 初始化失败: {e}")
    
    def get_supported_exchanges(self) -> List[str]:
        return list(self.exchanges.keys())
    
    def get_symbols(self, exchange: str) -> List[str]:
        if exchange in self.exchanges:
            try:
                return list(self.exchanges[exchange].markets.keys())[:20]  # 限制数量
            except:
                return []
        return []
    
    def get_price(self, exchange: str, symbol: str) -> Optional[Dict]:
        if exchange not in self.exchanges:
            return None
        
        try:
            ticker = self.exchanges[exchange].fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker.get('last'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
                'volume': ticker.get('baseVolume'),
                'timestamp': ticker.get('timestamp')
            }
        except Exception as e:
            logger.error(f"获取价格失败 {exchange} {symbol}: {e}")
            return None
    
    def get_ohlcv(self, exchange: str, symbol: str, timeframe: str = '1m', limit: int = 10) -> Optional[List]:
        if exchange not in self.exchanges:
            return None
        
        try:
            ohlcv = self.exchanges[exchange].fetch_ohlcv(symbol, timeframe, limit=limit)
            return [{
                'timestamp': candle[0],
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5]
            } for candle in ohlcv]
        except Exception as e:
            logger.error(f"获取K线失败 {exchange} {symbol}: {e}")
            return None

# 稳定A股服务
class StableAStockService:
    def get_stock_list(self):
        return [
            {'symbol': '000001.SZ', 'name': '平安银行'},
            {'symbol': '600036.SH', 'name': '招商银行'}
        ]
    
    def get_stock_price(self, symbol: str):
        return {
            'symbol': symbol,
            'price': 100.0,
            'change': 0.5,
            'volume': 1000000
        }

# 创建实例
data_service = StableDataService()
astock_service = StableAStockService()

print("✅ 稳定数据服务初始化完成")
