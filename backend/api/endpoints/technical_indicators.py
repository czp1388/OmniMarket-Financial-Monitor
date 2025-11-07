from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.database import get_db
from backend.services.technical_analysis_service import technical_analysis_service

router = APIRouter()

@router.get("/indicators")
async def get_available_indicators():
    """
    获取可用的技术指标列表
    """
    try:
        ta_service = TechnicalAnalysisService()
        indicators = ta_service.get_available_indicators()
        return indicators
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取技术指标列表失败: {str(e)}")

@router.get("/calculate")
async def calculate_technical_indicators(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    indicators: List[str] = Query(..., description="技术指标列表"),
    period: int = Query(100, description="数据周期", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    计算技术指标
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_indicators(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            indicators=indicators,
            period=period
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算技术指标失败: {str(e)}")

@router.get("/ma")
async def calculate_moving_averages(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    periods: List[int] = Query([5, 10, 20], description="移动平均周期"),
    ma_type: str = Query("SMA", description="移动平均类型: SMA, EMA, WMA"),
    db: Session = Depends(get_db)
):
    """
    计算移动平均线
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_moving_averages(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            periods=periods,
            ma_type=ma_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算移动平均线失败: {str(e)}")

@router.get("/macd")
async def calculate_macd(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    fast_period: int = Query(12, description="快线周期"),
    slow_period: int = Query(26, description="慢线周期"),
    signal_period: int = Query(9, description="信号线周期"),
    db: Session = Depends(get_db)
):
    """
    计算MACD指标
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_macd(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算MACD失败: {str(e)}")

@router.get("/rsi")
async def calculate_rsi(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    period: int = Query(14, description="RSI周期"),
    db: Session = Depends(get_db)
):
    """
    计算RSI指标
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_rsi(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            period=period
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算RSI失败: {str(e)}")

@router.get("/bollinger")
async def calculate_bollinger_bands(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    period: int = Query(20, description="布林带周期"),
    std_dev: float = Query(2.0, description="标准差倍数"),
    db: Session = Depends(get_db)
):
    """
    计算布林带
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_bollinger_bands(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            period=period,
            std_dev=std_dev
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算布林带失败: {str(e)}")

@router.get("/stochastic")
async def calculate_stochastic(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    k_period: int = Query(14, description="%K周期"),
    d_period: int = Query(3, description="%D周期"),
    slowing: int = Query(3, description="平滑周期"),
    db: Session = Depends(get_db)
):
    """
    计算随机指标
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_stochastic(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            k_period=k_period,
            d_period=d_period,
            slowing=slowing
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算随机指标失败: {str(e)}")

@router.get("/atr")
async def calculate_atr(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    period: int = Query(14, description="ATR周期"),
    db: Session = Depends(get_db)
):
    """
    计算平均真实波幅(ATR)
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_atr(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            period=period
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算ATR失败: {str(e)}")

@router.get("/support-resistance")
async def calculate_support_resistance(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    lookback_period: int = Query(100, description="回看周期"),
    tolerance: float = Query(0.01, description="容差百分比"),
    db: Session = Depends(get_db)
):
    """
    计算支撑阻力位
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.calculate_support_resistance(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            lookback_period=lookback_period,
            tolerance=tolerance
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算支撑阻力位失败: {str(e)}")

@router.get("/pattern-recognition")
async def pattern_recognition(
    symbol: str = Query(..., description="交易对符号"),
    market_type: str = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: str = Query(..., description="时间周期"),
    patterns: List[str] = Query(["head_shoulders", "double_top", "double_bottom"], description="模式列表"),
    db: Session = Depends(get_db)
):
    """
    形态识别
    """
    try:
        ta_service = TechnicalAnalysisService()
        result = await ta_service.pattern_recognition(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            patterns=patterns
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"形态识别失败: {str(e)}")
