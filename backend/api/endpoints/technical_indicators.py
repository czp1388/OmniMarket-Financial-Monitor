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
        indicators = [
            {"name": "SMA", "description": "简单移动平均线", "parameters": ["period"]},
            {"name": "EMA", "description": "指数移动平均线", "parameters": ["period"]},
            {"name": "MACD", "description": "移动平均收敛散度", "parameters": ["fast_period", "slow_period", "signal_period"]},
            {"name": "RSI", "description": "相对强弱指数", "parameters": ["period"]},
            {"name": "Bollinger Bands", "description": "布林带", "parameters": ["period", "std_dev"]},
            {"name": "ATR", "description": "平均真实波幅", "parameters": ["period"]},
            {"name": "Stochastic", "description": "随机指标", "parameters": ["k_period", "d_period"]},
            {"name": "CCI", "description": "商品通道指数", "parameters": ["period"]},
            {"name": "Momentum", "description": "动量指标", "parameters": ["period"]},
            {"name": "VWAP", "description": "成交量加权平均价", "parameters": []},
            {"name": "Volume Profile", "description": "成交量分布", "parameters": ["price_levels"]},
            {"name": "Support Resistance", "description": "支撑阻力位", "parameters": ["window"]}
        ]
        return indicators
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取技术指标列表失败: {str(e)}")

@router.get("/calculate")
async def calculate_technical_indicators(
    prices: List[float] = Query(..., description="价格数据"),
    indicators: List[str] = Query(..., description="技术指标列表"),
    periods: List[int] = Query([], description="周期参数")
):
    """
    计算技术指标
    """
    try:
        results = {}
        
        for indicator in indicators:
            if indicator.upper() == "SMA":
                if len(periods) > 0:
                    period = periods[0]
                    results["SMA"] = technical_analysis_service.calculate_sma(prices, period)
            elif indicator.upper() == "EMA":
                if len(periods) > 0:
                    period = periods[0]
                    results["EMA"] = technical_analysis_service.calculate_ema(prices, period)
            elif indicator.upper() == "MACD":
                fast_period = 12
                slow_period = 26
                signal_period = 9
                if len(periods) >= 3:
                    fast_period, slow_period, signal_period = periods[0], periods[1], periods[2]
                results["MACD"] = technical_analysis_service.calculate_macd(prices, fast_period, slow_period, signal_period)
            elif indicator.upper() == "RSI":
                period = 14
                if len(periods) > 0:
                    period = periods[0]
                results["RSI"] = technical_analysis_service.calculate_rsi(prices, period)
            elif indicator.upper() == "BOLLINGER":
                period = 20
                std_dev = 2.0
                if len(periods) >= 2:
                    period, std_dev = periods[0], periods[1]
                results["Bollinger Bands"] = technical_analysis_service.calculate_bollinger_bands(prices, period, std_dev)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算技术指标失败: {str(e)}")

@router.get("/ma")
async def calculate_moving_averages(
    prices: List[float] = Query(..., description="价格数据"),
    periods: List[int] = Query([5, 10, 20], description="移动平均周期"),
    ma_type: str = Query("SMA", description="移动平均类型: SMA, EMA")
):
    """
    计算移动平均线
    """
    try:
        results = {}
        for period in periods:
            if ma_type.upper() == "SMA":
                results[f"SMA_{period}"] = technical_analysis_service.calculate_sma(prices, period)
            elif ma_type.upper() == "EMA":
                results[f"EMA_{period}"] = technical_analysis_service.calculate_ema(prices, period)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算移动平均线失败: {str(e)}")

@router.get("/macd")
async def calculate_macd(
    prices: List[float] = Query(..., description="价格数据"),
    fast_period: int = Query(12, description="快线周期"),
    slow_period: int = Query(26, description="慢线周期"),
    signal_period: int = Query(9, description="信号线周期")
):
    """
    计算MACD指标
    """
    try:
        result = technical_analysis_service.calculate_macd(prices, fast_period, slow_period, signal_period)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算MACD失败: {str(e)}")

@router.get("/rsi")
async def calculate_rsi(
    prices: List[float] = Query(..., description="价格数据"),
    period: int = Query(14, description="RSI周期")
):
    """
    计算RSI指标
    """
    try:
        result = technical_analysis_service.calculate_rsi(prices, period)
        return {"RSI": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算RSI失败: {str(e)}")

@router.get("/bollinger")
async def calculate_bollinger_bands(
    prices: List[float] = Query(..., description="价格数据"),
    period: int = Query(20, description="布林带周期"),
    std_dev: float = Query(2.0, description="标准差倍数")
):
    """
    计算布林带
    """
    try:
        result = technical_analysis_service.calculate_bollinger_bands(prices, period, std_dev)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算布林带失败: {str(e)}")

@router.get("/atr")
async def calculate_atr(
    high_prices: List[float] = Query(..., description="最高价数据"),
    low_prices: List[float] = Query(..., description="最低价数据"),
    close_prices: List[float] = Query(..., description="收盘价数据"),
    period: int = Query(14, description="ATR周期")
):
    """
    计算平均真实波幅(ATR)
    """
    try:
        result = technical_analysis_service.calculate_atr(high_prices, low_prices, close_prices, period)
        return {"ATR": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算ATR失败: {str(e)}")

@router.get("/stochastic")
async def calculate_stochastic(
    high_prices: List[float] = Query(..., description="最高价数据"),
    low_prices: List[float] = Query(..., description="最低价数据"),
    close_prices: List[float] = Query(..., description="收盘价数据"),
    k_period: int = Query(14, description="%K周期"),
    d_period: int = Query(3, description="%D周期")
):
    """
    计算随机指标
    """
    try:
        result = technical_analysis_service.calculate_stochastic(high_prices, low_prices, close_prices, k_period, d_period)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算随机指标失败: {str(e)}")

@router.get("/cci")
async def calculate_cci(
    high_prices: List[float] = Query(..., description="最高价数据"),
    low_prices: List[float] = Query(..., description="最低价数据"),
    close_prices: List[float] = Query(..., description="收盘价数据"),
    period: int = Query(20, description="CCI周期")
):
    """
    计算商品通道指数(CCI)
    """
    try:
        result = technical_analysis_service.calculate_cci(high_prices, low_prices, close_prices, period)
        return {"CCI": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算CCI失败: {str(e)}")

@router.get("/momentum")
async def calculate_momentum(
    prices: List[float] = Query(..., description="价格数据"),
    period: int = Query(10, description="动量周期")
):
    """
    计算动量指标
    """
    try:
        result = technical_analysis_service.calculate_momentum(prices, period)
        return {"Momentum": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算动量指标失败: {str(e)}")

@router.get("/vwap")
async def calculate_vwap(
    high_prices: List[float] = Query(..., description="最高价数据"),
    low_prices: List[float] = Query(..., description="最低价数据"),
    close_prices: List[float] = Query(..., description="收盘价数据"),
    volumes: List[float] = Query(..., description="成交量数据")
):
    """
    计算成交量加权平均价(VWAP)
    """
    try:
        result = technical_analysis_service.calculate_vwap(high_prices, low_prices, close_prices, volumes)
        return {"VWAP": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算VWAP失败: {str(e)}")

@router.get("/volume-profile")
async def calculate_volume_profile(
    prices: List[float] = Query(..., description="价格数据"),
    volumes: List[float] = Query(..., description="成交量数据"),
    price_levels: int = Query(20, description="价格水平数量")
):
    """
    计算成交量分布
    """
    try:
        result = technical_analysis_service.calculate_volume_profile(prices, volumes, price_levels)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算成交量分布失败: {str(e)}")

@router.get("/support-resistance-levels")
async def calculate_support_resistance_levels(
    prices: List[float] = Query(..., description="价格数据"),
    window: int = Query(10, description="窗口大小")
):
    """
    计算支撑和阻力位
    """
    try:
        result = technical_analysis_service.calculate_support_resistance(prices, window)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算支撑阻力位失败: {str(e)}")

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
