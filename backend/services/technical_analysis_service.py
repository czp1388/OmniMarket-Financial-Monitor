import logging
from typing import List, Dict, Any, Optional
import numpy as np
from backend.models.market_data import KlineData

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    def __init__(self):
        pass
    
    def calculate_sma(self, prices: List[float], period: int) -> List[Optional[float]]:
        """计算简单移动平均线"""
        if len(prices) < period:
            return [None] * len(prices)
        
        sma_values = []
        for i in range(len(prices)):
            if i < period - 1:
                sma_values.append(None)
            else:
                sma = sum(prices[i-period+1:i+1]) / period
                sma_values.append(sma)
        
        return sma_values
    
    def calculate_ema(self, prices: List[float], period: int) -> List[Optional[float]]:
        """计算指数移动平均线"""
        if len(prices) < period:
            return [None] * len(prices)
        
        ema_values = [None] * (period - 1)
        multiplier = 2 / (period + 1)
        
        # 第一个EMA是前period个值的SMA
        first_ema = sum(prices[:period]) / period
        ema_values.append(first_ema)
        
        for i in range(period, len(prices)):
            ema = (prices[i] - ema_values[-1]) * multiplier + ema_values[-1]
            ema_values.append(ema)
        
        return ema_values
    
    def calculate_macd(self, prices: List[float], 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> Dict[str, List[Optional[float]]]:
        """计算MACD指标"""
        if len(prices) < slow_period + signal_period:
            return {
                "macd": [None] * len(prices),
                "signal": [None] * len(prices),
                "histogram": [None] * len(prices)
            }
        
        # 计算EMA
        ema_fast = self.calculate_ema(prices, fast_period)
        ema_slow = self.calculate_ema(prices, slow_period)
        
        # 计算MACD线
        macd_line = []
        for i in range(len(prices)):
            if ema_fast[i] is None or ema_slow[i] is None:
                macd_line.append(None)
            else:
                macd_line.append(ema_fast[i] - ema_slow[i])
        
        # 计算信号线 (MACD的EMA)
        signal_line = self.calculate_ema(
            [x if x is not None else 0 for x in macd_line], 
            signal_period
        )
        
        # 计算柱状图
        histogram = []
        for i in range(len(prices)):
            if macd_line[i] is None or signal_line[i] is None:
                histogram.append(None)
            else:
                histogram.append(macd_line[i] - signal_line[i])
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[Optional[float]]:
        """计算RSI指标"""
        if len(prices) <= period:
            return [None] * len(prices)
        
        # 计算价格变化
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [max(change, 0) for change in changes]
        losses = [max(-change, 0) for change in changes]
        
        rsi_values = [None] * period
        
        # 计算初始平均值
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(rsi)
        
        # 计算后续RSI值
        for i in range(period, len(changes)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        # 在前面添加None以匹配原始价格数组长度
        rsi_values = [None] + rsi_values
        
        return rsi_values
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, 
                                 std_dev: float = 2) -> Dict[str, List[Optional[float]]]:
        """计算布林带"""
        if len(prices) < period:
            return {
                "upper": [None] * len(prices),
                "middle": [None] * len(prices),
                "lower": [None] * len(prices)
            }
        
        upper_band = []
        middle_band = []
        lower_band = []
        
        for i in range(len(prices)):
            if i < period - 1:
                upper_band.append(None)
                middle_band.append(None)
                lower_band.append(None)
            else:
                window = prices[i-period+1:i+1]
                sma = sum(window) / period
                std = np.std(window)
                
                middle_band.append(sma)
                upper_band.append(sma + std_dev * std)
                lower_band.append(sma - std_dev * std)
        
        return {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band
        }
    
    def calculate_atr(self, high_prices: List[float], low_prices: List[float], 
                     close_prices: List[float], period: int = 14) -> List[Optional[float]]:
        """计算平均真实波幅(ATR)"""
        if len(high_prices) < period + 1:
            return [None] * len(high_prices)
        
        # 计算真实波幅(TR)
        tr_values = []
        for i in range(1, len(high_prices)):
            tr1 = high_prices[i] - low_prices[i]
            tr2 = abs(high_prices[i] - close_prices[i-1])
            tr3 = abs(low_prices[i] - close_prices[i-1])
            tr = max(tr1, tr2, tr3)
            tr_values.append(tr)
        
        # 计算ATR
        atr_values = [None] * period
        atr = sum(tr_values[:period]) / period
        atr_values.append(atr)
        
        for i in range(period, len(tr_values)):
            atr = (atr * (period - 1) + tr_values[i]) / period
            atr_values.append(atr)
        
        # 在前面添加None以匹配原始数组长度
        atr_values = [None] + atr_values
        
        return atr_values
    
    def detect_golden_cross(self, short_ma: List[Optional[float]], 
                           long_ma: List[Optional[float]]) -> List[bool]:
        """检测金叉信号"""
        signals = [False] * len(short_ma)
        
        for i in range(1, len(short_ma)):
            if (short_ma[i-1] is not None and long_ma[i-1] is not None and
                short_ma[i] is not None and long_ma[i] is not None):
                if (short_ma[i-1] <= long_ma[i-1] and short_ma[i] > long_ma[i]):
                    signals[i] = True
        
        return signals
    
    def detect_death_cross(self, short_ma: List[Optional[float]], 
                          long_ma: List[Optional[float]]) -> List[bool]:
        """检测死叉信号"""
        signals = [False] * len(short_ma)
        
        for i in range(1, len(short_ma)):
            if (short_ma[i-1] is not None and long_ma[i-1] is not None and
                short_ma[i] is not None and long_ma[i] is not None):
                if (short_ma[i-1] >= long_ma[i-1] and short_ma[i] < long_ma[i]):
                    signals[i] = True
        
        return signals


# 全局技术分析服务实例
technical_analysis_service = TechnicalAnalysisService()
