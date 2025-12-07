"""
形态识别API端点
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from services.pattern_recognition_service import (
    pattern_recognition_service,
    PatternType,
    SignalDirection,
    PatternMatch
)
from services.data_service import data_service
from models.market_data import MarketType, Timeframe

router = APIRouter()


class PatternMatchResponse(BaseModel):
    """形态匹配响应模型"""
    pattern_type: str = Field(..., description="形态类型")
    signal_direction: str = Field(..., description="信号方向: bullish/bearish/neutral")
    confidence: float = Field(..., ge=0, le=1, description="置信度 0-1")
    start_index: int = Field(..., description="起始K线索引")
    end_index: int = Field(..., description="结束K线索引")
    start_time: Optional[datetime] = Field(None, description="起始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    key_points: List[dict] = Field(..., description="关键点位")
    target_price: Optional[float] = Field(None, description="目标价位")
    stop_loss: Optional[float] = Field(None, description="止损价位")
    description: str = Field(..., description="形态描述")


class PatternDetectionResponse(BaseModel):
    """形态检测响应"""
    symbol: str
    market_type: str
    timeframe: str
    total_patterns: int
    patterns: List[PatternMatchResponse]


@router.get(
    "/patterns/detect",
    response_model=PatternDetectionResponse,
    summary="检测技术形态",
    description="分析K线数据,检测常见技术分析形态(头肩顶/底、双顶/底、三角形、旗形等)"
)
async def detect_patterns(
    symbol: str = Query(..., description="交易品种代码"),
    market_type: MarketType = Query(..., description="市场类型"),
    exchange: Optional[str] = Query(None, description="交易所代码"),
    timeframe: Timeframe = Query(Timeframe.H1, description="时间周期"),
    limit: int = Query(100, ge=20, le=500, description="K线数量"),
    min_confidence: float = Query(0.6, ge=0.0, le=1.0, description="最小置信度阈值")
):
    """
    检测技术形态
    
    支持的形态类型:
    - 反转形态: 头肩顶/底、双顶/底、三重顶/底
    - 持续形态: 三角形、旗形、楔形
    - K线组合: 早晨之星、黄昏之星、吞没形态、锤子线等
    """
    try:
        # 获取K线数据
        klines = await data_service.get_klines(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            limit=limit
        )
        
        if not klines:
            raise HTTPException(status_code=404, detail=f"未找到{symbol}的K线数据")
        
        # 检测形态
        pattern_matches = await pattern_recognition_service.detect_all_patterns(
            klines=klines,
            min_confidence=min_confidence
        )
        
        # 转换为响应格式
        patterns_response = []
        for match in pattern_matches:
            # 添加时间信息
            start_time = klines[match.start_index].timestamp if match.start_index < len(klines) else None
            end_time = klines[match.end_index].timestamp if match.end_index < len(klines) else None
            
            patterns_response.append(
                PatternMatchResponse(
                    pattern_type=match.pattern_type.value,
                    signal_direction=match.signal_direction.value,
                    confidence=match.confidence,
                    start_index=match.start_index,
                    end_index=match.end_index,
                    start_time=start_time,
                    end_time=end_time,
                    key_points=[
                        {
                            "index": idx,
                            "price": price,
                            "time": klines[idx].timestamp if idx < len(klines) else None
                        }
                        for idx, price in match.key_points
                    ],
                    target_price=match.target_price,
                    stop_loss=match.stop_loss,
                    description=match.description
                )
            )
        
        return PatternDetectionResponse(
            symbol=symbol,
            market_type=market_type.value,
            timeframe=timeframe.value,
            total_patterns=len(patterns_response),
            patterns=patterns_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"形态识别失败: {str(e)}")


@router.get(
    "/patterns/types",
    summary="获取支持的形态类型",
    description="返回所有支持的技术形态类型列表"
)
async def get_pattern_types():
    """获取所有支持的形态类型"""
    return {
        "reversal_patterns": [
            {"type": PatternType.HEAD_AND_SHOULDERS.value, "name": "头肩顶", "signal": "看跌"},
            {"type": PatternType.INVERSE_HEAD_AND_SHOULDERS.value, "name": "头肩底", "signal": "看涨"},
            {"type": PatternType.DOUBLE_TOP.value, "name": "双顶", "signal": "看跌"},
            {"type": PatternType.DOUBLE_BOTTOM.value, "name": "双底", "signal": "看涨"},
            {"type": PatternType.TRIPLE_TOP.value, "name": "三重顶", "signal": "看跌"},
            {"type": PatternType.TRIPLE_BOTTOM.value, "name": "三重底", "signal": "看涨"}
        ],
        "continuation_patterns": [
            {"type": PatternType.ASCENDING_TRIANGLE.value, "name": "上升三角形", "signal": "看涨"},
            {"type": PatternType.DESCENDING_TRIANGLE.value, "name": "下降三角形", "signal": "看跌"},
            {"type": PatternType.SYMMETRICAL_TRIANGLE.value, "name": "对称三角形", "signal": "中性"},
            {"type": PatternType.BULL_FLAG.value, "name": "牛旗", "signal": "看涨"},
            {"type": PatternType.BEAR_FLAG.value, "name": "熊旗", "signal": "看跌"},
            {"type": PatternType.RISING_WEDGE.value, "name": "上升楔形", "signal": "看跌"},
            {"type": PatternType.FALLING_WEDGE.value, "name": "下降楔形", "signal": "看涨"}
        ],
        "candlestick_patterns": [
            {"type": PatternType.MORNING_STAR.value, "name": "早晨之星", "signal": "看涨"},
            {"type": PatternType.EVENING_STAR.value, "name": "黄昏之星", "signal": "看跌"},
            {"type": PatternType.ENGULFING_BULLISH.value, "name": "看涨吞没", "signal": "看涨"},
            {"type": PatternType.ENGULFING_BEARISH.value, "name": "看跌吞没", "signal": "看跌"},
            {"type": PatternType.HAMMER.value, "name": "锤子线", "signal": "看涨"},
            {"type": PatternType.SHOOTING_STAR.value, "name": "射击之星", "signal": "看跌"},
            {"type": PatternType.DOJI.value, "name": "十字星", "signal": "中性"}
        ]
    }


@router.get(
    "/patterns/scan",
    summary="批量扫描形态",
    description="对多个交易品种批量扫描技术形态"
)
async def scan_patterns(
    symbols: str = Query(..., description="交易品种列表,逗号分隔"),
    market_type: MarketType = Query(..., description="市场类型"),
    exchange: Optional[str] = Query(None, description="交易所代码"),
    timeframe: Timeframe = Query(Timeframe.H1, description="时间周期"),
    min_confidence: float = Query(0.7, ge=0.0, le=1.0, description="最小置信度")
):
    """
    批量扫描形态
    
    对多个品种同时进行形态扫描,返回检测到的所有高置信度形态
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        
        if len(symbol_list) > 50:
            raise HTTPException(status_code=400, detail="最多同时扫描50个品种")
        
        results = []
        
        for symbol in symbol_list:
            try:
                # 获取K线数据
                klines = await data_service.get_klines(
                    symbol=symbol,
                    market_type=market_type,
                    exchange=exchange,
                    timeframe=timeframe,
                    limit=100
                )
                
                if not klines:
                    continue
                
                # 检测形态
                pattern_matches = await pattern_recognition_service.detect_all_patterns(
                    klines=klines,
                    min_confidence=min_confidence
                )
                
                if pattern_matches:
                    results.append({
                        "symbol": symbol,
                        "pattern_count": len(pattern_matches),
                        "patterns": [
                            {
                                "type": m.pattern_type.value,
                                "signal": m.signal_direction.value,
                                "confidence": m.confidence,
                                "description": m.description
                            }
                            for m in pattern_matches[:3]  # 只返回前3个最高置信度形态
                        ]
                    })
                    
            except Exception as e:
                # 单个品种失败不影响其他品种
                continue
        
        return {
            "total_symbols": len(symbol_list),
            "symbols_with_patterns": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量扫描失败: {str(e)}")
