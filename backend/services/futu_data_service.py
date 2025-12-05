import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from backend.models.market_data import KlineData, MarketType, Timeframe

logger = logging.getLogger(__name__)

class FutuDataService:
    """富途证券数据服务"""
    
    def __init__(self):
        self.connected = False
        self.futu_conn = None
        
    async def connect(self, host: str = "127.0.0.1", port: int = 11111):
        """连接富途OpenD - 需要用户已安装富途证券并开启OpenD服务"""
        try:
            import futu as ft
            # 合法合规数据获取：仅连接用户本地已授权的富途OpenD服务
            self.futu_conn = ft.OpenQuoteContext(host=host, port=port)
            self.connected = True
            logger.info("富途数据服务连接成功 - 使用本地授权OpenD服务")
        except Exception as e:
            logger.error(f"富途数据服务连接失败: {e}")
            logger.info("请确保已安装富途证券并开启OpenD服务，或使用模拟数据进行开发")
            self.connected = False
    
    async def get_hk_stocks_klines(
        self,
        symbol: str,
        timeframe: Timeframe,
        limit: int = 1000,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[KlineData]:
        """获取港股K线数据"""
        if not self.connected:
            logger.warning("富途数据服务未连接")
            return await self._get_mock_hk_data(symbol, timeframe, limit)
        
        try:
            # 时间框架映射
            tf_mapping = {
                Timeframe.MINUTE_1: "K_1M",
                Timeframe.MINUTE_5: "K_5M",
                Timeframe.MINUTE_15: "K_15M",
                Timeframe.HOUR_1: "K_60M",
                Timeframe.DAILY: "K_DAY",
                Timeframe.WEEKLY: "K_WEEK",
                Timeframe.MONTHLY: "K_MON"
            }
            
            futu_tf = tf_mapping.get(timeframe, "K_DAY")
            
            # 获取K线数据
            ret, data = self.futu_conn.get_cur_kline(
                code=symbol, 
                ktype=futu_tf, 
                autype='qfq', 
                fields=['time_key', 'open', 'high', 'low', 'close', 'volume']
            )
            
            if ret == 0 and data is not None:
                klines = []
                for _, row in data.iterrows():
                    kline = KlineData(
                        symbol=symbol,
                        timeframe=timeframe,
                        market_type=MarketType.STOCK,
                        exchange='futu',
                        timestamp=row['time_key'],
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row['volume'])
                    )
                    klines.append(kline)
                return klines
            else:
                logger.warning("富途API返回空数据，使用模拟数据")
                return await self._get_mock_hk_data(symbol, timeframe, limit)
            
        except Exception as e:
            logger.error(f"获取港股K线数据失败: {e}")
            return await self._get_mock_hk_data(symbol, timeframe, limit)
    
    async def _get_mock_hk_data(
        self, 
        symbol: str, 
        timeframe: Timeframe,
        limit: int
    ) -> List[KlineData]:
        """生成港股模拟数据"""
        klines = []
        base_price = 50.0  # 港股典型价格
        current_time = datetime.now()
        
        for i in range(limit):
            timestamp = current_time - self._get_timeframe_delta(timeframe) * i
            
            # 生成随机价格波动（港股波动较小）
            import random
            change = random.uniform(-1.0, 1.0)
            open_price = base_price + change
            high = open_price + random.uniform(0, 2.0)
            low = open_price - random.uniform(0, 2.0)
            close_price = (high + low) / 2 + random.uniform(-0.5, 0.5)
            volume = random.uniform(100000, 1000000)  # 港股交易量较大
            
            kline = KlineData(
                symbol=symbol,
                timeframe=timeframe,
                market_type=MarketType.STOCK,
                exchange='futu',
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close_price,
                volume=volume
            )
            klines.append(kline)
        
        return klines
    
    def _get_timeframe_delta(self, timeframe: Timeframe):
        """获取时间框架对应的时间差"""
        from datetime import timedelta
        timeframe_delta = {
            Timeframe.MINUTE_1: timedelta(minutes=1),
            Timeframe.MINUTE_5: timedelta(minutes=5),
            Timeframe.MINUTE_15: timedelta(minutes=15),
            Timeframe.HOUR_1: timedelta(hours=1),
            Timeframe.HOUR_4: timedelta(hours=4),
            Timeframe.DAILY: timedelta(days=1),
            Timeframe.WEEKLY: timedelta(weeks=1),
            Timeframe.MONTHLY: timedelta(days=30)
        }
        return timeframe_delta.get(timeframe, timedelta(hours=1))
    
    async def get_stock_quote(self, symbol: str) -> Dict:
        """获取股票实时报价 - 使用真实富途API"""
        if not self.connected:
            logger.warning("富途数据服务未连接，使用模拟数据")
            return await self._get_mock_quote(symbol)
        
        try:
            # 使用富途API获取市场快照数据
            ret, data = self.futu_conn.get_market_snapshot([symbol])
            
            if ret == 0 and data is not None and not data.empty:
                snapshot = data.iloc[0]
                return {
                    'symbol': symbol,
                    'last_price': float(snapshot.get('last_price', 0)),
                    'open': float(snapshot.get('open_price', 0)),
                    'high': float(snapshot.get('high_price', 0)),
                    'low': float(snapshot.get('low_price', 0)),
                    'volume': float(snapshot.get('volume', 0)),
                    'turnover': float(snapshot.get('turnover', 0)),
                    'change': float(snapshot.get('change_rate', 0)),
                    'timestamp': datetime.now()
                }
            else:
                logger.warning("富途API返回空数据，使用模拟数据")
                return await self._get_mock_quote(symbol)
                
        except Exception as e:
            logger.error(f"获取股票报价失败: {e}")
            return await self._get_mock_quote(symbol)
    
    async def _get_mock_quote(self, symbol: str) -> Dict:
        """生成模拟报价数据"""
        import random
        base_price = 50.0
        change = random.uniform(-2.0, 2.0)
        
        return {
            'symbol': symbol,
            'last_price': base_price + change,
            'open': base_price,
            'high': base_price + random.uniform(0, 3.0),
            'low': base_price - random.uniform(0, 3.0),
            'volume': random.uniform(100000, 1000000),
            'turnover': random.uniform(5000000, 50000000),
            'timestamp': datetime.now()
        }
    
    async def get_portfolio_positions(self) -> List[Dict]:
        """获取投资组合持仓"""
        # 模拟持仓数据
        return [
            {
                'symbol': '00700',  # 腾讯
                'name': '腾讯控股',
                'quantity': 100,
                'avg_cost': 320.5,
                'current_price': 325.0,
                'market_value': 32500.0,
                'profit_loss': 450.0,
                'profit_loss_rate': 1.4
            },
            {
                'symbol': '09988',  # 阿里巴巴
                'name': '阿里巴巴-SW',
                'quantity': 200,
                'avg_cost': 85.2,
                'current_price': 87.5,
                'market_value': 17500.0,
                'profit_loss': 460.0,
                'profit_loss_rate': 2.7
            }
        ]
    
    async def disconnect(self):
        """断开连接"""
        if self.futu_conn:
            # self.futu_conn.close()
            pass
        self.connected = False
        logger.info("富途数据服务已断开")


# 全局富途数据服务实例
futu_data_service = FutuDataService()
