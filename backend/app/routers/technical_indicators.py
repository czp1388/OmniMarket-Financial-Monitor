# 技术指标API路由
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from services.technical_indicators import technical_indicator_service
from services.market_data_service import market_data_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/technical", tags=["technical_indicators"])

@router.get("/indicators")
async def get_available_indicators():
    """获取可用的技术指标列表"""
    return {
        "indicators": technical_indicator_service.available_indicators,
        "count": len(technical_indicator_service.available_indicators)
    }

@router.get("/{symbol}/calculate")
async def calculate_technical_indicators(
    symbol: str,
    interval: str = Query("1h", regex="^1m|5m|15m|1h|4h|1d|1w$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """计算技术指标"""
    try:
        # 获取K线数据
        klines = await market_data_service.get_crypto_klines(symbol, interval, limit)
        if not klines:
            raise HTTPException(status_code=400, detail="无法获取K线数据")
        
        # 计算技术指标
        indicators = technical_indicator_service.calculate_all_indicators(klines)
        
        return {
            "symbol": symbol,
            "interval": interval,
            "data_count": len(klines),
            "indicators": indicators
        }
        
    except Exception as e:
        logger.error(f"计算技术指标异常: {e}")
        raise HTTPException(status_code=500, detail="计算技术指标失败")

@router.get("/{symbol}/macd")
async def calculate_macd(
    symbol: str,
    interval: str = Query("1h", regex="^1m|5m|15m|1h|4h|1d|1w$"),
    limit: int = Query(100, ge=1, le=1000),
    fastperiod: int = Query(12, ge=5, le=50),
    slowperiod: int = Query(26, ge=10, le=100),
    signalperiod: int = Query(9, ge=5, le=30)
):
    """计算MACD指标"""
    try:
        klines = await market_data_service.get_crypto_klines(symbol, interval, limit)
        if not klines:
            raise HTTPException(status_code=400, detail="无法获取K线数据")
        
        closes = [kline["close_price"] for kline in klines]
        macd_data = technical_indicator_service.calculate_macd(
            closes, fastperiod, slowperiod, signalperiod
        )
        
        return {
            "symbol": symbol,
            "interval": interval,
            "parameters": {
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
                "signalperiod": signalperiod
            },
            "macd": macd_data
        }
        
    except Exception as e:
        logger.error(f"计算MACD异常: {e}")
        raise HTTPException(status_code=500, detail="计算MACD失败")

@router.get("/{symbol}/rsi")
async def calculate_rsi(
    symbol: str,
    interval: str = Query("1h", regex="^1m|5m|15m|1h|4h|1d|1w$"),
    limit: int = Query(100, ge=1, le=1000),
    period: int = Query(14, ge=5, le=30)
):
    """计算RSI指标"""
    try:
        klines = await market_data_service.get_crypto_klines(symbol, interval, limit)
        if not klines:
            raise HTTPException(status_code=400, detail="无法获取K线数据")
        
        closes = [kline["close_price"] for kline in klines]
        rsi_data = technical_indicator_service.calculate_rsi(closes, period)
        
        return {
            "symbol": symbol,
            "interval": interval,
            "period": period,
            "rsi": rsi_data
        }
        
    except Exception as e:
        logger.error(f"计算RSI异常: {e}")
        raise HTTPException(status_code=500, detail="计算RSI失败")
