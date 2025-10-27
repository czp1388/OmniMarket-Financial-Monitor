# 技术指标计算服务
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import talib

logger = logging.getLogger(__name__)

class TechnicalIndicatorService:
    def __init__(self):
        self.available_indicators = {
            "MA": "移动平均线",
            "EMA": "指数移动平均线", 
            "MACD": "指数平滑异同移动平均线",
            "RSI": "相对强弱指数",
            "KDJ": "随机指标",
            "BOLL": "布林带",
            "VOLUME": "成交量"
        }
        
    def calculate_ma(self, closes: List[float], period: int = 5) -> List[Optional[float]]:
        """计算移动平均线"""
        try:
            if len(closes) < period:
                return [None] * len(closes)
            return talib.SMA(np.array(closes), timeperiod=period).tolist()
        except Exception as e:
            logger.error(f"计算MA{period}失败: {e}")
            return [None] * len(closes)
    
    def calculate_ema(self, closes: List[float], period: int = 12) -> List[Optional[float]]:
        """计算指数移动平均线"""
        try:
            if len(closes) < period:
                return [None] * len(closes)
            return talib.EMA(np.array(closes), timeperiod=period).tolist()
        except Exception as e:
            logger.error(f"计算EMA{period}失败: {e}")
            return [None] * len(closes)
    
    def calculate_macd(self, closes: List[float], 
                      fastperiod: int = 12, 
                      slowperiod: int = 26, 
                      signalperiod: int = 9) -> Dict[str, List[Optional[float]]]:
        """计算MACD指标"""
        try:
            if len(closes) < slowperiod:
                empty_list = [None] * len(closes)
                return {"macd": empty_list, "signal": empty_list, "histogram": empty_list}
                
            macd, signal, histogram = talib.MACD(np.array(closes), 
                                                fastperiod=fastperiod,
                                                slowperiod=slowperiod, 
                                                signalperiod=signalperiod)
            return {
                "macd": macd.tolist(),
                "signal": signal.tolist(), 
                "histogram": histogram.tolist()
            }
        except Exception as e:
            logger.error(f"计算MACD失败: {e}")
            empty_list = [None] * len(closes)
            return {"macd": empty_list, "signal": empty_list, "histogram": empty_list}
    
    def calculate_rsi(self, closes: List[float], period: int = 14) -> List[Optional[float]]:
        """计算RSI指标"""
        try:
            if len(closes) < period:
                return [None] * len(closes)
            return talib.RSI(np.array(closes), timeperiod=period).tolist()
        except Exception as e:
            logger.error(f"计算RSI{period}失败: {e}")
            return [None] * len(closes)
    
    def calculate_bollinger_bands(self, closes: List[float], period: int = 20, nbdev: int = 2) -> Dict[str, List[Optional[float]]]:
        """计算布林带"""
        try:
            if len(closes) < period:
                empty_list = [None] * len(closes)
                return {"upper": empty_list, "middle": empty_list, "lower": empty_list}
                
            upper, middle, lower = talib.BBANDS(np.array(closes), 
                                               timeperiod=period, 
                                               nbdevup=nbdev, 
                                               nbdevdn=nbdev)
            return {
                "upper": upper.tolist(),
                "middle": middle.tolist(),
                "lower": lower.tolist()
            }
        except Exception as e:
            logger.error(f"计算布林带失败: {e}")
            empty_list = [None] * len(closes)
            return {"upper": empty_list, "middle": empty_list, "lower": empty_list}
    
    def calculate_all_indicators(self, klines: List[Dict]) -> Dict[str, any]:
        """计算所有技术指标"""
        try:
            closes = [kline["close_price"] for kline in klines]
            highs = [kline["high_price"] for kline in klines]
            lows = [kline["low_price"] for kline in klines]
            volumes = [kline["volume"] for kline in klines]
            
            return {
                "MA5": self.calculate_ma(closes, 5),
                "MA10": self.calculate_ma(closes, 10),
                "MA20": self.calculate_ma(closes, 20),
                "MA60": self.calculate_ma(closes, 60),
                "EMA12": self.calculate_ema(closes, 12),
                "EMA26": self.calculate_ema(closes, 26),
                "MACD": self.calculate_macd(closes),
                "RSI": self.calculate_rsi(closes),
                "BOLL": self.calculate_bollinger_bands(closes)
            }
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return {}

# 创建全局技术指标服务实例
technical_indicator_service = TechnicalIndicatorService()
