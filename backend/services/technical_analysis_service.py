import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from models.market_data import KlineData

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    def __init__(self):
        pass
    
    def calculate_sma(self, prices: List[float], period: int) -> List[Optional[float]]:
        """计算简单移动平均线 - 优化版本使用numpy"""
        if len(prices) < period:
            return [None] * len(prices)
        
        # 使用numpy进行向量化计算以提高性能
        prices_array = np.array(prices)
        sma_values = [None] * (period - 1)
        
        for i in range(period - 1, len(prices_array)):
            window = prices_array[i-period+1:i+1]
            sma = np.mean(window)
            sma_values.append(float(sma))
        
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

    def calculate_stochastic(self, high_prices: List[float], low_prices: List[float], 
                           close_prices: List[float], k_period: int = 14, 
                           d_period: int = 3) -> Dict[str, List[Optional[float]]]:
        """计算随机指标(Stochastic Oscillator)"""
        if len(high_prices) < k_period:
            return {
                "k": [None] * len(high_prices),
                "d": [None] * len(high_prices)
            }
        
        k_values = [None] * (k_period - 1)
        d_values = [None] * (k_period - 1)
        
        for i in range(k_period - 1, len(high_prices)):
            # 计算%K
            highest_high = max(high_prices[i-k_period+1:i+1])
            lowest_low = min(low_prices[i-k_period+1:i+1])
            
            if highest_high == lowest_low:
                k_value = 50.0  # 避免除以零
            else:
                k_value = ((close_prices[i] - lowest_low) / (highest_high - lowest_low)) * 100
            k_values.append(k_value)
        
        # 计算%D (%K的SMA)
        for i in range(len(k_values)):
            if k_values[i] is None:
                d_values.append(None)
            elif i < k_period + d_period - 2:
                d_values.append(None)
            else:
                d_window = k_values[i-d_period+1:i+1]
                d_value = sum(d_window) / d_period
                d_values.append(d_value)
        
        return {
            "k": k_values,
            "d": d_values
        }

    def calculate_cci(self, high_prices: List[float], low_prices: List[float], 
                     close_prices: List[float], period: int = 20) -> List[Optional[float]]:
        """计算商品通道指数(CCI)"""
        if len(high_prices) < period:
            return [None] * len(high_prices)
        
        cci_values = [None] * (period - 1)
        
        for i in range(period - 1, len(high_prices)):
            # 计算典型价格
            typical_prices = [(high_prices[j] + low_prices[j] + close_prices[j]) / 3 
                             for j in range(i-period+1, i+1)]
            
            # 计算简单移动平均
            sma = sum(typical_prices) / period
            
            # 计算平均偏差
            mean_deviation = sum(abs(tp - sma) for tp in typical_prices) / period
            
            # 计算CCI
            current_tp = (high_prices[i] + low_prices[i] + close_prices[i]) / 3
            if mean_deviation == 0:
                cci = 0.0
            else:
                cci = (current_tp - sma) / (0.015 * mean_deviation)
            
            cci_values.append(cci)
        
        return cci_values

    def calculate_momentum(self, prices: List[float], period: int = 10) -> List[Optional[float]]:
        """计算动量指标"""
        if len(prices) < period:
            return [None] * len(prices)
        
        momentum_values = [None] * period
        
        for i in range(period, len(prices)):
            momentum = prices[i] - prices[i-period]
            momentum_values.append(momentum)
        
        return momentum_values

    def calculate_volume_profile(self, prices: List[float], volumes: List[float], 
                                price_levels: int = 20) -> Dict[str, List[float]]:
        """计算成交量分布"""
        if not prices or not volumes:
            return {"price_levels": [], "volumes": []}
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return {"price_levels": [min_price], "volumes": [sum(volumes)]}
        
        # 创建价格水平
        level_size = price_range / price_levels
        price_levels_list = [min_price + i * level_size for i in range(price_levels + 1)]
        
        # 计算每个价格水平的成交量
        volume_at_levels = [0.0] * price_levels
        
        for price, volume in zip(prices, volumes):
            level_index = int((price - min_price) / level_size)
            level_index = min(level_index, price_levels - 1)  # 确保不超过范围
            volume_at_levels[level_index] += volume
        
        return {
            "price_levels": price_levels_list,
            "volumes": volume_at_levels
        }

    def calculate_support_resistance(self, prices: List[float], window: int = 10) -> Dict[str, List[float]]:
        """计算支撑和阻力位"""
        if len(prices) < window * 2:
            return {"support": [], "resistance": []}
        
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(prices) - window):
            # 检查是否为局部最小值（支撑）
            if all(prices[i] <= prices[j] for j in range(i-window, i+window+1) if j != i):
                support_levels.append(prices[i])
            
            # 检查是否为局部最大值（阻力）
            if all(prices[i] >= prices[j] for j in range(i-window, i+window+1) if j != i):
                resistance_levels.append(prices[i])
        
        return {
            "support": support_levels,
            "resistance": resistance_levels
        }

    def calculate_vwap(self, high_prices: List[float], low_prices: List[float], 
                      close_prices: List[float], volumes: List[float]) -> List[Optional[float]]:
        """计算成交量加权平均价(VWAP)"""
        if len(high_prices) == 0:
            return [None]
        
        vwap_values = []
        cumulative_volume = 0.0
        cumulative_price_volume = 0.0
        
        for i in range(len(high_prices)):
            # 典型价格
            typical_price = (high_prices[i] + low_prices[i] + close_prices[i]) / 3
            
            cumulative_price_volume += typical_price * volumes[i]
            cumulative_volume += volumes[i]
            
            if cumulative_volume == 0:
                vwap_values.append(None)
            else:
                vwap = cumulative_price_volume / cumulative_volume
                vwap_values.append(vwap)
        
        return vwap_values


# 全局技术分析服务实例
technical_analysis_service = TechnicalAnalysisService()
