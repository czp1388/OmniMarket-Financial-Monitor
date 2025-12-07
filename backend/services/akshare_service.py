import asyncio
import logging
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from models.market_data import KlineData, MarketType, Timeframe

logger = logging.getLogger(__name__)

class AkShareService:
    """AkShare数据服务"""
    
    def __init__(self):
        self.name = "akshare"
        self.supported_markets = [MarketType.STOCK, MarketType.FUND, MarketType.INDEX]
        
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
            # 转换时间框架到AkShare格式
            tf_mapping = {
                Timeframe.DAILY: "D",
                Timeframe.WEEKLY: "W",
                Timeframe.MONTHLY: "M"
            }
            ak_tf = tf_mapping.get(timeframe, "D")
            
            # 获取A股代码格式（AkShare使用类似"000001"的格式）
            stock_code = self._format_stock_code(symbol)
            
            # 获取历史数据
            if ak_tf == "D":
                df = ak.stock_zh_a_hist(symbol=stock_code, period=ak_tf, adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=stock_code, period=ak_tf, adjust="qfq")
            
            if df.empty:
                logger.warning(f"AkShare获取股票数据为空: {symbol}")
                return []
            
            # 限制数据量
            df = df.tail(limit)
            
            klines = []
            for _, row in df.iterrows():
                kline = KlineData(
                    symbol=symbol,
                    timeframe=timeframe,
                    market_type=MarketType.STOCK,
                    exchange='akshare',
                    timestamp=row['日期'] if isinstance(row['日期'], datetime) else datetime.strptime(row['日期'], '%Y-%m-%d'),
                    open=float(row['开盘']),
                    high=float(row['最高']),
                    low=float(row['最低']),
                    close=float(row['收盘']),
                    volume=float(row['成交量'])
                )
                klines.append(kline)
            
            logger.info(f"AkShare获取股票K线数据成功: {symbol}, 数据点: {len(klines)}")
            return klines
            
        except Exception as e:
            logger.error(f"AkShare获取股票K线数据失败: {symbol}, 错误: {e}")
            return []
    
    async def get_index_klines(
        self, 
        symbol: str, 
        timeframe: Timeframe, 
        limit: int = 1000
    ) -> List[KlineData]:
        """获取指数K线数据"""
        try:
            # 转换时间框架
            tf_mapping = {
                Timeframe.DAILY: "D",
                Timeframe.WEEKLY: "W",
                Timeframe.MONTHLY: "M"
            }
            ak_tf = tf_mapping.get(timeframe, "D")
            
            # 获取指数数据（例如上证指数"000001"）
            df = ak.stock_zh_index_hist(symbol=symbol, period=ak_tf)
            
            if df.empty:
                logger.warning(f"AkShare获取指数数据为空: {symbol}")
                return []
            
            df = df.tail(limit)
            
            klines = []
            for _, row in df.iterrows():
                kline = KlineData(
                    symbol=symbol,
                    timeframe=timeframe,
                    market_type=MarketType.INDEX,
                    exchange='akshare',
                    timestamp=row['日期'] if isinstance(row['日期'], datetime) else datetime.strptime(row['日期'], '%Y-%m-%d'),
                    open=float(row['开盘']),
                    high=float(row['最高']),
                    low=float(row['最低']),
                    close=float(row['收盘']),
                    volume=float(row['成交量'])
                )
                klines.append(kline)
            
            logger.info(f"AkShare获取指数K线数据成功: {symbol}, 数据点: {len(klines)}")
            return klines
            
        except Exception as e:
            logger.error(f"AkShare获取指数K线数据失败: {symbol}, 错误: {e}")
            return []
    
    async def get_real_time_quote(self, symbol: str) -> dict:
        """获取实时行情数据"""
        try:
            # 获取A股实时行情
            stock_code = self._format_stock_code(symbol)
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                return {}
            
            # 查找特定股票
            stock_data = df[df['代码'] == stock_code]
            if stock_data.empty:
                return {}
            
            row = stock_data.iloc[0]
            return {
                'symbol': symbol,
                'last_price': float(row['最新价']),
                'change': float(row['涨跌额']),
                'change_percent': float(row['涨跌幅']),
                'volume': float(row['成交量']),
                'amount': float(row['成交额']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'open': float(row['今开']),
                'prev_close': float(row['昨收']),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"AkShare获取实时行情失败: {symbol}, 错误: {e}")
            return {}
    
    def _format_stock_code(self, symbol: str) -> str:
        """格式化股票代码为AkShare格式"""
        # 移除可能的交易所前缀和后缀
        clean_symbol = symbol.upper().replace('SH', '').replace('SZ', '').replace('.', '')
        return clean_symbol
    
    async def test_connection(self) -> bool:
        """测试AkShare连接"""
        try:
            # 尝试获取上证指数数据来测试连接
            test_data = ak.stock_zh_index_hist(symbol="000001", period="D")
            return not test_data.empty
        except Exception as e:
            logger.error(f"AkShare连接测试失败: {e}")
            return False

# 全局AkShare服务实例
akshare_service = AkShareService()
