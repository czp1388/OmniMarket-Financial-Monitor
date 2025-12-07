"""
形态识别服务 - 检测常见技术分析形态
支持: 头肩顶/底、双顶/底、三角形、旗形、楔形等
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime
from models.market_data import KlineData

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """形态类型枚举"""
    # 反转形态
    HEAD_AND_SHOULDERS = "head_and_shoulders"  # 头肩顶
    INVERSE_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"  # 头肩底
    DOUBLE_TOP = "double_top"  # 双顶
    DOUBLE_BOTTOM = "double_bottom"  # 双底
    TRIPLE_TOP = "triple_top"  # 三重顶
    TRIPLE_BOTTOM = "triple_bottom"  # 三重底
    
    # 持续形态
    ASCENDING_TRIANGLE = "ascending_triangle"  # 上升三角形
    DESCENDING_TRIANGLE = "descending_triangle"  # 下降三角形
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"  # 对称三角形
    BULL_FLAG = "bull_flag"  # 牛旗
    BEAR_FLAG = "bear_flag"  # 熊旗
    RISING_WEDGE = "rising_wedge"  # 上升楔形
    FALLING_WEDGE = "falling_wedge"  # 下降楔形
    
    # K线组合
    MORNING_STAR = "morning_star"  # 早晨之星
    EVENING_STAR = "evening_star"  # 黄昏之星
    ENGULFING_BULLISH = "engulfing_bullish"  # 看涨吞没
    ENGULFING_BEARISH = "engulfing_bearish"  # 看跌吞没
    HAMMER = "hammer"  # 锤子线
    SHOOTING_STAR = "shooting_star"  # 射击之星
    DOJI = "doji"  # 十字星


class SignalDirection(Enum):
    """信号方向"""
    BULLISH = "bullish"  # 看涨
    BEARISH = "bearish"  # 看跌
    NEUTRAL = "neutral"  # 中性


@dataclass
class PatternMatch:
    """形态匹配结果"""
    pattern_type: PatternType
    signal_direction: SignalDirection
    confidence: float  # 置信度 0-1
    start_index: int  # 起始K线索引
    end_index: int  # 结束K线索引
    key_points: List[Tuple[int, float]]  # 关键点位 (索引, 价格)
    target_price: Optional[float] = None  # 目标价位
    stop_loss: Optional[float] = None  # 止损价位
    description: str = ""  # 形态描述


class PatternRecognitionService:
    """形态识别服务"""
    
    def __init__(self):
        self.min_pattern_length = 10  # 最小形态长度
        self.max_pattern_length = 100  # 最大形态长度
        self.price_tolerance = 0.02  # 价格容差 (2%)
        self.volume_surge_threshold = 1.5  # 成交量突破阈值
        
    async def detect_all_patterns(
        self, 
        klines: List[KlineData],
        min_confidence: float = 0.6
    ) -> List[PatternMatch]:
        """
        检测所有形态
        
        Args:
            klines: K线数据列表
            min_confidence: 最小置信度阈值
            
        Returns:
            形态匹配列表
        """
        if len(klines) < self.min_pattern_length:
            logger.warning(f"K线数据不足: {len(klines)} < {self.min_pattern_length}")
            return []
        
        patterns = []
        
        try:
            # 检测反转形态
            patterns.extend(await self._detect_head_and_shoulders(klines))
            patterns.extend(await self._detect_double_top_bottom(klines))
            patterns.extend(await self._detect_triple_top_bottom(klines))
            
            # 检测持续形态
            patterns.extend(await self._detect_triangles(klines))
            patterns.extend(await self._detect_flags(klines))
            patterns.extend(await self._detect_wedges(klines))
            
            # 检测K线组合
            patterns.extend(await self._detect_candlestick_patterns(klines))
            
            # 过滤低置信度形态
            patterns = [p for p in patterns if p.confidence >= min_confidence]
            
            # 按置信度排序
            patterns.sort(key=lambda x: x.confidence, reverse=True)
            
            logger.info(f"检测到 {len(patterns)} 个形态 (置信度>={min_confidence})")
            
        except Exception as e:
            logger.error(f"形态识别失败: {e}", exc_info=True)
        
        return patterns
    
    async def _detect_head_and_shoulders(
        self, 
        klines: List[KlineData]
    ) -> List[PatternMatch]:
        """检测头肩顶/底形态"""
        patterns = []
        prices = [k.high for k in klines]  # 用最高价检测头肩顶
        
        # 寻找5个关键点: 左肩-左谷-头-右谷-右肩
        for i in range(20, len(prices) - 20):
            # 寻找局部极值
            peaks = self._find_local_peaks(prices[i-20:i+20], distance=5)
            valleys = self._find_local_valleys(prices[i-20:i+20], distance=5)
            
            if len(peaks) >= 3 and len(valleys) >= 2:
                # 检查是否符合头肩形态
                left_shoulder = peaks[0]
                head = peaks[1]
                right_shoulder = peaks[2]
                left_valley = valleys[0]
                right_valley = valleys[1]
                
                # 验证形态特征
                if (self._is_similar_price(left_shoulder[1], right_shoulder[1]) and
                    head[1] > left_shoulder[1] * 1.02 and  # 头部明显高于肩部
                    head[1] > right_shoulder[1] * 1.02 and
                    self._is_similar_price(left_valley[1], right_valley[1])):  # 颈线水平
                    
                    # 计算置信度
                    confidence = self._calculate_hns_confidence(
                        left_shoulder[1], head[1], right_shoulder[1],
                        left_valley[1], right_valley[1]
                    )
                    
                    # 计算目标价位 (头部到颈线的距离)
                    neckline = (left_valley[1] + right_valley[1]) / 2
                    target = neckline - (head[1] - neckline)
                    
                    pattern = PatternMatch(
                        pattern_type=PatternType.HEAD_AND_SHOULDERS,
                        signal_direction=SignalDirection.BEARISH,
                        confidence=confidence,
                        start_index=i - 20 + left_shoulder[0],
                        end_index=i - 20 + right_shoulder[0],
                        key_points=[
                            (i - 20 + left_shoulder[0], left_shoulder[1]),
                            (i - 20 + head[0], head[1]),
                            (i - 20 + right_shoulder[0], right_shoulder[1])
                        ],
                        target_price=target,
                        stop_loss=head[1],
                        description="头肩顶形态 - 强烈看跌信号"
                    )
                    patterns.append(pattern)
        
        # 同样方法检测头肩底 (使用最低价)
        prices = [k.low for k in klines]
        for i in range(20, len(prices) - 20):
            peaks = self._find_local_peaks(prices[i-20:i+20], distance=5)
            valleys = self._find_local_valleys(prices[i-20:i+20], distance=5)
            
            if len(valleys) >= 3 and len(peaks) >= 2:
                left_shoulder = valleys[0]
                head = valleys[1]
                right_shoulder = valleys[2]
                left_peak = peaks[0]
                right_peak = peaks[1]
                
                if (self._is_similar_price(left_shoulder[1], right_shoulder[1]) and
                    head[1] < left_shoulder[1] * 0.98 and
                    head[1] < right_shoulder[1] * 0.98 and
                    self._is_similar_price(left_peak[1], right_peak[1])):
                    
                    confidence = self._calculate_hns_confidence(
                        left_shoulder[1], head[1], right_shoulder[1],
                        left_peak[1], right_peak[1]
                    )
                    
                    neckline = (left_peak[1] + right_peak[1]) / 2
                    target = neckline + (neckline - head[1])
                    
                    pattern = PatternMatch(
                        pattern_type=PatternType.INVERSE_HEAD_AND_SHOULDERS,
                        signal_direction=SignalDirection.BULLISH,
                        confidence=confidence,
                        start_index=i - 20 + left_shoulder[0],
                        end_index=i - 20 + right_shoulder[0],
                        key_points=[
                            (i - 20 + left_shoulder[0], left_shoulder[1]),
                            (i - 20 + head[0], head[1]),
                            (i - 20 + right_shoulder[0], right_shoulder[1])
                        ],
                        target_price=target,
                        stop_loss=head[1],
                        description="头肩底形态 - 强烈看涨信号"
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_double_top_bottom(
        self, 
        klines: List[KlineData]
    ) -> List[PatternMatch]:
        """检测双顶/双底形态"""
        patterns = []
        
        # 双顶检测
        prices = [k.high for k in klines]
        peaks = self._find_local_peaks(prices, distance=10)
        
        for i in range(len(peaks) - 1):
            peak1 = peaks[i]
            peak2 = peaks[i + 1]
            
            # 检查两个峰值是否在相似价位
            if self._is_similar_price(peak1[1], peak2[1]):
                # 找中间的谷底
                valley_prices = prices[peak1[0]:peak2[0]]
                if len(valley_prices) > 0:
                    valley_price = min(valley_prices)
                    valley_idx = peak1[0] + valley_prices.index(valley_price)
                    
                    # 验证形态 (峰值高于谷底足够多)
                    if peak1[1] > valley_price * 1.03:
                        confidence = self._calculate_double_pattern_confidence(
                            peak1[1], peak2[1], valley_price
                        )
                        
                        target = valley_price - (peak1[1] - valley_price)
                        
                        pattern = PatternMatch(
                            pattern_type=PatternType.DOUBLE_TOP,
                            signal_direction=SignalDirection.BEARISH,
                            confidence=confidence,
                            start_index=peak1[0],
                            end_index=peak2[0],
                            key_points=[
                                (peak1[0], peak1[1]),
                                (valley_idx, valley_price),
                                (peak2[0], peak2[1])
                            ],
                            target_price=target,
                            stop_loss=max(peak1[1], peak2[1]),
                            description="双顶形态 - 看跌信号"
                        )
                        patterns.append(pattern)
        
        # 双底检测
        prices = [k.low for k in klines]
        valleys = self._find_local_valleys(prices, distance=10)
        
        for i in range(len(valleys) - 1):
            valley1 = valleys[i]
            valley2 = valleys[i + 1]
            
            if self._is_similar_price(valley1[1], valley2[1]):
                peak_prices = prices[valley1[0]:valley2[0]]
                if len(peak_prices) > 0:
                    peak_price = max(peak_prices)
                    peak_idx = valley1[0] + peak_prices.index(peak_price)
                    
                    if valley1[1] < peak_price * 0.97:
                        confidence = self._calculate_double_pattern_confidence(
                            valley1[1], valley2[1], peak_price
                        )
                        
                        target = peak_price + (peak_price - valley1[1])
                        
                        pattern = PatternMatch(
                            pattern_type=PatternType.DOUBLE_BOTTOM,
                            signal_direction=SignalDirection.BULLISH,
                            confidence=confidence,
                            start_index=valley1[0],
                            end_index=valley2[0],
                            key_points=[
                                (valley1[0], valley1[1]),
                                (peak_idx, peak_price),
                                (valley2[0], valley2[1])
                            ],
                            target_price=target,
                            stop_loss=min(valley1[1], valley2[1]),
                            description="双底形态 - 看涨信号"
                        )
                        patterns.append(pattern)
        
        return patterns
    
    async def _detect_triple_top_bottom(
        self, 
        klines: List[KlineData]
    ) -> List[PatternMatch]:
        """检测三重顶/底形态 (简化实现)"""
        patterns = []
        
        # 三重顶检测
        prices = [k.high for k in klines]
        peaks = self._find_local_peaks(prices, distance=8)
        
        for i in range(len(peaks) - 2):
            peak1, peak2, peak3 = peaks[i], peaks[i+1], peaks[i+2]
            
            if (self._is_similar_price(peak1[1], peak2[1]) and
                self._is_similar_price(peak2[1], peak3[1])):
                
                confidence = 0.75  # 三重顶相对少见,给予中等置信度
                
                pattern = PatternMatch(
                    pattern_type=PatternType.TRIPLE_TOP,
                    signal_direction=SignalDirection.BEARISH,
                    confidence=confidence,
                    start_index=peak1[0],
                    end_index=peak3[0],
                    key_points=[(peak1[0], peak1[1]), (peak2[0], peak2[1]), (peak3[0], peak3[1])],
                    description="三重顶形态 - 强看跌信号"
                )
                patterns.append(pattern)
        
        # 三重底检测
        prices = [k.low for k in klines]
        valleys = self._find_local_valleys(prices, distance=8)
        
        for i in range(len(valleys) - 2):
            valley1, valley2, valley3 = valleys[i], valleys[i+1], valleys[i+2]
            
            if (self._is_similar_price(valley1[1], valley2[1]) and
                self._is_similar_price(valley2[1], valley3[1])):
                
                confidence = 0.75
                
                pattern = PatternMatch(
                    pattern_type=PatternType.TRIPLE_BOTTOM,
                    signal_direction=SignalDirection.BULLISH,
                    confidence=confidence,
                    start_index=valley1[0],
                    end_index=valley3[0],
                    key_points=[(valley1[0], valley1[1]), (valley2[0], valley2[1]), (valley3[0], valley3[1])],
                    description="三重底形态 - 强看涨信号"
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_triangles(
        self, 
        klines: List[KlineData]
    ) -> List[PatternMatch]:
        """检测三角形形态"""
        patterns = []
        
        # 简化实现: 使用线性回归检测趋势线
        window = 30  # 检测窗口
        
        for i in range(window, len(klines)):
            highs = [k.high for k in klines[i-window:i]]
            lows = [k.low for k in klines[i-window:i]]
            
            # 计算上下趋势线斜率
            upper_slope = self._calculate_trendline_slope(highs)
            lower_slope = self._calculate_trendline_slope(lows)
            
            # 上升三角形: 上轨水平,下轨上升
            if abs(upper_slope) < 0.001 and lower_slope > 0.002:
                pattern = PatternMatch(
                    pattern_type=PatternType.ASCENDING_TRIANGLE,
                    signal_direction=SignalDirection.BULLISH,
                    confidence=0.7,
                    start_index=i - window,
                    end_index=i,
                    key_points=[(i-window, lows[0]), (i, highs[-1])],
                    description="上升三角形 - 看涨持续形态"
                )
                patterns.append(pattern)
            
            # 下降三角形: 下轨水平,上轨下降
            elif abs(lower_slope) < 0.001 and upper_slope < -0.002:
                pattern = PatternMatch(
                    pattern_type=PatternType.DESCENDING_TRIANGLE,
                    signal_direction=SignalDirection.BEARISH,
                    confidence=0.7,
                    start_index=i - window,
                    end_index=i,
                    key_points=[(i-window, highs[0]), (i, lows[-1])],
                    description="下降三角形 - 看跌持续形态"
                )
                patterns.append(pattern)
            
            # 对称三角形: 上轨下降,下轨上升
            elif upper_slope < -0.001 and lower_slope > 0.001:
                pattern = PatternMatch(
                    pattern_type=PatternType.SYMMETRICAL_TRIANGLE,
                    signal_direction=SignalDirection.NEUTRAL,
                    confidence=0.65,
                    start_index=i - window,
                    end_index=i,
                    key_points=[(i-window, highs[0]), (i-window, lows[0]), (i, (highs[-1]+lows[-1])/2)],
                    description="对称三角形 - 突破方向待确认"
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_flags(
        self, 
        klines: List[KlineData]
    ) -> List[PatternMatch]:
        """检测旗形形态"""
        patterns = []
        
        # 旗形特征: 急速上涨/下跌后的短期横盘整理
        for i in range(20, len(klines) - 10):
            # 检测旗杆 (前期快速运动)
            pole_start = i - 20
            pole_end = i - 10
            pole_change = (klines[pole_end].close - klines[pole_start].close) / klines[pole_start].close
            
            # 检测旗面 (后期横盘)
            flag_prices = [k.close for k in klines[i-10:i]]
            flag_volatility = np.std(flag_prices) / np.mean(flag_prices)
            
            # 牛旗: 大幅上涨 + 小幅整理
            if pole_change > 0.1 and flag_volatility < 0.03:
                pattern = PatternMatch(
                    pattern_type=PatternType.BULL_FLAG,
                    signal_direction=SignalDirection.BULLISH,
                    confidence=0.75,
                    start_index=pole_start,
                    end_index=i,
                    key_points=[(pole_start, klines[pole_start].close), (pole_end, klines[pole_end].close)],
                    target_price=klines[i].close * (1 + pole_change),  # 预期继续上涨相同幅度
                    description="牛旗形态 - 上涨中继"
                )
                patterns.append(pattern)
            
            # 熊旗: 大幅下跌 + 小幅整理
            elif pole_change < -0.1 and flag_volatility < 0.03:
                pattern = PatternMatch(
                    pattern_type=PatternType.BEAR_FLAG,
                    signal_direction=SignalDirection.BEARISH,
                    confidence=0.75,
                    start_index=pole_start,
                    end_index=i,
                    key_points=[(pole_start, klines[pole_start].close), (pole_end, klines[pole_end].close)],
                    target_price=klines[i].close * (1 + pole_change),  # 预期继续下跌
                    description="熊旗形态 - 下跌中继"
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_wedges(
        self, 
        klines: List[KlineData]
    ) -> List[PatternMatch]:
        """检测楔形形态"""
        patterns = []
        
        window = 30
        for i in range(window, len(klines)):
            highs = [k.high for k in klines[i-window:i]]
            lows = [k.low for k in klines[i-window:i]]
            
            upper_slope = self._calculate_trendline_slope(highs)
            lower_slope = self._calculate_trendline_slope(lows)
            
            # 上升楔形: 两条趋势线都上升,但上轨上升更慢 (看跌)
            if lower_slope > 0 and 0 < upper_slope < lower_slope * 0.7:
                pattern = PatternMatch(
                    pattern_type=PatternType.RISING_WEDGE,
                    signal_direction=SignalDirection.BEARISH,
                    confidence=0.7,
                    start_index=i - window,
                    end_index=i,
                    key_points=[(i-window, lows[0]), (i, highs[-1])],
                    description="上升楔形 - 看跌反转信号"
                )
                patterns.append(pattern)
            
            # 下降楔形: 两条趋势线都下降,但下轨下降更慢 (看涨)
            elif upper_slope < 0 and lower_slope < 0 and lower_slope > upper_slope * 0.7:
                pattern = PatternMatch(
                    pattern_type=PatternType.FALLING_WEDGE,
                    signal_direction=SignalDirection.BULLISH,
                    confidence=0.7,
                    start_index=i - window,
                    end_index=i,
                    key_points=[(i-window, highs[0]), (i, lows[-1])],
                    description="下降楔形 - 看涨反转信号"
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _detect_candlestick_patterns(
        self, 
        klines: List[KlineData]
    ) -> List[PatternMatch]:
        """检测K线组合形态"""
        patterns = []
        
        for i in range(2, len(klines)):
            k_prev2 = klines[i-2]
            k_prev = klines[i-1]
            k_curr = klines[i]
            
            # 早晨之星: 下跌 -> 小实体 -> 大阳线
            if self._is_morning_star(k_prev2, k_prev, k_curr):
                pattern = PatternMatch(
                    pattern_type=PatternType.MORNING_STAR,
                    signal_direction=SignalDirection.BULLISH,
                    confidence=0.8,
                    start_index=i-2,
                    end_index=i,
                    key_points=[(i-2, k_prev2.close), (i, k_curr.close)],
                    description="早晨之星 - 强看涨信号"
                )
                patterns.append(pattern)
            
            # 黄昏之星: 上涨 -> 小实体 -> 大阴线
            elif self._is_evening_star(k_prev2, k_prev, k_curr):
                pattern = PatternMatch(
                    pattern_type=PatternType.EVENING_STAR,
                    signal_direction=SignalDirection.BEARISH,
                    confidence=0.8,
                    start_index=i-2,
                    end_index=i,
                    key_points=[(i-2, k_prev2.close), (i, k_curr.close)],
                    description="黄昏之星 - 强看跌信号"
                )
                patterns.append(pattern)
            
            # 看涨吞没
            if self._is_bullish_engulfing(k_prev, k_curr):
                pattern = PatternMatch(
                    pattern_type=PatternType.ENGULFING_BULLISH,
                    signal_direction=SignalDirection.BULLISH,
                    confidence=0.75,
                    start_index=i-1,
                    end_index=i,
                    key_points=[(i-1, k_prev.close), (i, k_curr.close)],
                    description="看涨吞没 - 看涨信号"
                )
                patterns.append(pattern)
            
            # 看跌吞没
            elif self._is_bearish_engulfing(k_prev, k_curr):
                pattern = PatternMatch(
                    pattern_type=PatternType.ENGULFING_BEARISH,
                    signal_direction=SignalDirection.BEARISH,
                    confidence=0.75,
                    start_index=i-1,
                    end_index=i,
                    key_points=[(i-1, k_prev.close), (i, k_curr.close)],
                    description="看跌吞没 - 看跌信号"
                )
                patterns.append(pattern)
            
            # 锤子线
            if self._is_hammer(k_curr):
                pattern = PatternMatch(
                    pattern_type=PatternType.HAMMER,
                    signal_direction=SignalDirection.BULLISH,
                    confidence=0.7,
                    start_index=i,
                    end_index=i,
                    key_points=[(i, k_curr.close)],
                    description="锤子线 - 底部反转信号"
                )
                patterns.append(pattern)
            
            # 射击之星
            elif self._is_shooting_star(k_curr):
                pattern = PatternMatch(
                    pattern_type=PatternType.SHOOTING_STAR,
                    signal_direction=SignalDirection.BEARISH,
                    confidence=0.7,
                    start_index=i,
                    end_index=i,
                    key_points=[(i, k_curr.close)],
                    description="射击之星 - 顶部反转信号"
                )
                patterns.append(pattern)
            
            # 十字星
            elif self._is_doji(k_curr):
                pattern = PatternMatch(
                    pattern_type=PatternType.DOJI,
                    signal_direction=SignalDirection.NEUTRAL,
                    confidence=0.6,
                    start_index=i,
                    end_index=i,
                    key_points=[(i, k_curr.close)],
                    description="十字星 - 市场犹豫,趋势可能反转"
                )
                patterns.append(pattern)
        
        return patterns
    
    # ============ 辅助方法 ============
    
    def _find_local_peaks(
        self, 
        prices: List[float], 
        distance: int = 5
    ) -> List[Tuple[int, float]]:
        """查找局部峰值"""
        peaks = []
        for i in range(distance, len(prices) - distance):
            if all(prices[i] >= prices[i-j] for j in range(1, distance+1)) and \
               all(prices[i] >= prices[i+j] for j in range(1, distance+1)):
                peaks.append((i, prices[i]))
        return peaks
    
    def _find_local_valleys(
        self, 
        prices: List[float], 
        distance: int = 5
    ) -> List[Tuple[int, float]]:
        """查找局部谷底"""
        valleys = []
        for i in range(distance, len(prices) - distance):
            if all(prices[i] <= prices[i-j] for j in range(1, distance+1)) and \
               all(prices[i] <= prices[i+j] for j in range(1, distance+1)):
                valleys.append((i, prices[i]))
        return valleys
    
    def _is_similar_price(self, price1: float, price2: float) -> bool:
        """判断两个价格是否相似"""
        diff = abs(price1 - price2) / ((price1 + price2) / 2)
        return diff < self.price_tolerance
    
    def _calculate_hns_confidence(
        self, 
        left_shoulder: float,
        head: float,
        right_shoulder: float,
        left_valley: float,
        right_valley: float
    ) -> float:
        """计算头肩形态置信度"""
        # 肩部对称性
        shoulder_symmetry = 1 - abs(left_shoulder - right_shoulder) / ((left_shoulder + right_shoulder) / 2)
        
        # 颈线水平性
        neckline_level = 1 - abs(left_valley - right_valley) / ((left_valley + right_valley) / 2)
        
        # 头部显著性
        head_prominence = min((head - left_shoulder) / left_shoulder, 
                              (head - right_shoulder) / right_shoulder) / 0.05  # 5%为满分
        
        confidence = (shoulder_symmetry * 0.3 + neckline_level * 0.3 + 
                     min(head_prominence, 1.0) * 0.4)
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_double_pattern_confidence(
        self, 
        peak1: float,
        peak2: float,
        valley: float
    ) -> float:
        """计算双顶/双底置信度"""
        # 峰值对称性
        peak_symmetry = 1 - abs(peak1 - peak2) / ((peak1 + peak2) / 2)
        
        # 深度显著性
        depth = abs(peak1 - valley) / peak1
        depth_score = min(depth / 0.05, 1.0)  # 5%为满分
        
        confidence = peak_symmetry * 0.6 + depth_score * 0.4
        return max(0.0, min(1.0, confidence))
    
    def _calculate_trendline_slope(self, prices: List[float]) -> float:
        """计算趋势线斜率 (使用线性回归)"""
        if len(prices) < 2:
            return 0.0
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # 简单线性回归
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope / y_mean  # 归一化斜率
    
    def _is_morning_star(self, k1: KlineData, k2: KlineData, k3: KlineData) -> bool:
        """判断是否为早晨之星"""
        # K1: 大阴线
        # K2: 小实体 (十字星或小K线)
        # K3: 大阳线
        
        body1 = abs(k1.close - k1.open)
        body2 = abs(k2.close - k2.open)
        body3 = abs(k3.close - k3.open)
        
        is_k1_bearish = k1.close < k1.open and body1 > (k1.high - k1.low) * 0.6
        is_k2_small = body2 < (k2.high - k2.low) * 0.3
        is_k3_bullish = k3.close > k3.open and body3 > (k3.high - k3.low) * 0.6
        
        return is_k1_bearish and is_k2_small and is_k3_bullish
    
    def _is_evening_star(self, k1: KlineData, k2: KlineData, k3: KlineData) -> bool:
        """判断是否为黄昏之星"""
        body1 = abs(k1.close - k1.open)
        body2 = abs(k2.close - k2.open)
        body3 = abs(k3.close - k3.open)
        
        is_k1_bullish = k1.close > k1.open and body1 > (k1.high - k1.low) * 0.6
        is_k2_small = body2 < (k2.high - k2.low) * 0.3
        is_k3_bearish = k3.close < k3.open and body3 > (k3.high - k3.low) * 0.6
        
        return is_k1_bullish and is_k2_small and is_k3_bearish
    
    def _is_bullish_engulfing(self, k1: KlineData, k2: KlineData) -> bool:
        """判断是否为看涨吞没"""
        return (k1.close < k1.open and  # K1阴线
                k2.close > k2.open and  # K2阳线
                k2.open < k1.close and  # K2开盘低于K1收盘
                k2.close > k1.open)     # K2收盘高于K1开盘
    
    def _is_bearish_engulfing(self, k1: KlineData, k2: KlineData) -> bool:
        """判断是否为看跌吞没"""
        return (k1.close > k1.open and  # K1阳线
                k2.close < k2.open and  # K2阴线
                k2.open > k1.close and  # K2开盘高于K1收盘
                k2.close < k1.open)     # K2收盘低于K1开盘
    
    def _is_hammer(self, k: KlineData) -> bool:
        """判断是否为锤子线"""
        body = abs(k.close - k.open)
        lower_shadow = min(k.close, k.open) - k.low
        upper_shadow = k.high - max(k.close, k.open)
        
        return (lower_shadow > body * 2 and  # 下影线至少是实体的2倍
                upper_shadow < body * 0.3)   # 上影线很短
    
    def _is_shooting_star(self, k: KlineData) -> bool:
        """判断是否为射击之星"""
        body = abs(k.close - k.open)
        lower_shadow = min(k.close, k.open) - k.low
        upper_shadow = k.high - max(k.close, k.open)
        
        return (upper_shadow > body * 2 and  # 上影线至少是实体的2倍
                lower_shadow < body * 0.3)   # 下影线很短
    
    def _is_doji(self, k: KlineData) -> bool:
        """判断是否为十字星"""
        body = abs(k.close - k.open)
        total_range = k.high - k.low
        
        return body < total_range * 0.1  # 实体不超过总范围的10%


# 导出全局单例
pattern_recognition_service = PatternRecognitionService()
