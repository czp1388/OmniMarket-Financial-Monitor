import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd
from backend.models.market_data import KlineData, MarketType, Timeframe

logger = logging.getLogger(__name__)

class YFinanceDataService:
    """Yahoo Finance数据服务 - 合法合规的免费数据源"""
    
    def __init__(self):
        self.connected = True  # Yahoo Finance不需要连接
    
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
            # 时间框架映射
            period_mapping = {
                Timeframe.MINUTE_1: "1d",  # yfinance最小支持1分钟
                Timeframe.MINUTE_5: "1d",
                Timeframe.MINUTE_15: "1d",
                Timeframe.HOUR_1: "1d",
                Timeframe.HOUR_4: "5d",
                Timeframe.DAILY: "1mo",
                Timeframe.WEEKLY: "3mo",
                Timeframe.MONTHLY: "1y"
            }
            
            interval_mapping = {
                Timeframe.MINUTE_1: "1m",
                Timeframe.MINUTE_5: "5m",
                Timeframe.MINUTE_15: "15m",
                Timeframe.HOUR_1: "1h",
                Timeframe.HOUR_4: "1h",  # yfinance不支持4小时，用1小时替代
                Timeframe.DAILY: "1d",
                Timeframe.WEEKLY: "1wk",
                Timeframe.MONTHLY: "1mo"
            }
            
            period = period_mapping.get(timeframe, "1mo")
            interval = interval_mapping.get(timeframe, "1d")
            
            # 获取股票数据
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"Yahoo Finance返回空数据: {symbol}")
                return await self._get_mock_stock_data(symbol, timeframe, limit)
            
            klines = []
            for timestamp, row in data.iterrows():
                kline = KlineData(
                    symbol=symbol,
                    timeframe=timeframe,
                    market_type=MarketType.STOCK,
                    timestamp=timestamp.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                klines.append(kline)
            
            # 限制返回数量
            return klines[-limit:] if len(klines) > limit else klines
            
        except Exception as e:
            logger.error(f"获取股票K线数据失败: {e}")
            return await self._get_mock_stock_data(symbol, timeframe, limit)
    
    async def _get_mock_stock_data(
        self, 
        symbol: str, 
        timeframe: Timeframe,
        limit: int
    ) -> List[KlineData]:
        """生成股票模拟数据"""
        klines = []
        base_price = 100.0  # 美股典型价格
        current_time = datetime.now()
        
        for i in range(limit):
            timestamp = current_time - self._get_timeframe_delta(timeframe) * i
            
            # 生成随机价格波动
            import random
            change = random.uniform(-5.0, 5.0)
            open_price = base_price + change
            high = open_price + random.uniform(0, 3.0)
            low = open_price - random.uniform(0, 3.0)
            close_price = (high + low) / 2 + random.uniform(-1.0, 1.0)
            volume = random.uniform(1000000, 10000000)  # 美股交易量较大
            
            kline = KlineData(
                symbol=symbol,
                timeframe=timeframe,
                market_type=MarketType.STOCK,
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
        """获取股票实时报价"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d")
            
            if history.empty:
                logger.warning(f"Yahoo Finance返回空报价数据: {symbol}")
                return await self._get_mock_quote(symbol)
            
            latest = history.iloc[-1]
            
            return {
                'symbol': symbol,
                'last_price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': float(latest['Volume']),
                'change': float(info.get('regularMarketChangePercent', 0)) if info else 0,
                'timestamp': datetime.now()
            }
                
        except Exception as e:
            logger.error(f"获取股票报价失败: {e}")
            return await self._get_mock_quote(symbol)
    
    async def _get_mock_quote(self, symbol: str) -> Dict:
        """生成模拟报价数据"""
        import random
        base_price = 100.0
        change = random.uniform(-5.0, 5.0)
        
        return {
            'symbol': symbol,
            'last_price': base_price + change,
            'open': base_price,
            'high': base_price + random.uniform(0, 5.0),
            'low': base_price - random.uniform(0, 5.0),
            'volume': random.uniform(1000000, 10000000),
            'change': change / base_price * 100,
            'timestamp': datetime.now()
        }
    
    async def get_market_summary(self) -> Dict:
        """获取市场摘要"""
        try:
            # 获取主要指数
            indices = {
                '^GSPC': '标普500',
                '^DJI': '道琼斯',
                '^IXIC': '纳斯达克',
                '^HSI': '恒生指数',
                '000001.SS': '上证指数'
            }
            
            summary = {}
            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    history = ticker.history(period="1d")
                    
                    if not history.empty:
                        latest = history.iloc[-1]
                        prev_close = float(info.get('previousClose', latest['Close']))
                        current_price = float(latest['Close'])
                        change_percent = (current_price - prev_close) / prev_close * 100
                        
                        summary[symbol] = {
                            'name': name,
                            'price': current_price,
                            'change': change_percent,
                            'volume': float(latest['Volume']) if 'Volume' in latest else 0
                        }
                except Exception as e:
                    logger.warning(f"获取指数 {symbol} 数据失败: {e}")
            
            return summary
            
        except Exception as e:
            logger.error(f"获取市场摘要失败: {e}")
            return await self._get_mock_market_summary()
    
    async def _get_mock_market_summary(self) -> Dict:
        """生成模拟市场摘要"""
        import random
        indices = {
            '^GSPC': '标普500',
            '^DJI': '道琼斯', 
            '^IXIC': '纳斯达克',
            '^HSI': '恒生指数',
            '000001.SS': '上证指数'
        }
        
        summary = {}
        for symbol, name in indices.items():
            base_price = 3000 if symbol.startswith('^') else 1000
            change = random.uniform(-2.0, 2.0)
            
            summary[symbol] = {
                'name': name,
                'price': base_price + change,
                'change': change,
                'volume': random.uniform(1000000, 10000000)
            }
        
        return summary


# 全局Yahoo Finance数据服务实例
yfinance_data_service = YFinanceDataService()
