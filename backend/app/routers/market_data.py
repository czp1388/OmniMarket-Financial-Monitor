# 市场数据API路由
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from services.market_data_service import market_data_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/market", tags=["market_data"])

@router.get("/health")
async def market_data_health():
    """市场数据服务健康检查"""
    return {
        "service": "market_data",
        "status": "healthy" if market_data_service.is_initialized else "initializing",
        "data_sources": list(market_data_service.data_sources.keys())
    }

@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = Query("1h", regex="^1m|5m|15m|1h|4h|1d|1w$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """获取K线数据"""
    try:
        data = await market_data_service.get_crypto_klines(symbol, interval, limit)
        if data is None:
            raise HTTPException(status_code=400, detail="获取K线数据失败")
        
        return {
            "symbol": symbol,
            "interval": interval,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        logger.error(f"获取K线数据API异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/symbols/{symbol}/info")
async def get_symbol_info(symbol: str):
    """获取交易对信息"""
    try:
        info = await market_data_service.get_symbol_info(symbol)
        if info is None:
            raise HTTPException(status_code=404, detail="交易对不存在")
        return info
    except Exception as e:
        logger.error(f"获取交易对信息异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.post("/batch/klines")
async def get_batch_klines(
    symbols: List[str],
    interval: str = Query("1h", regex="^1m|5m|15m|1h|4h|1d|1w$")
):
    """批量获取K线数据"""
    try:
        if len(symbols) > 20:
            raise HTTPException(status_code=400, detail="一次最多查询20个交易对")
        
        data = await market_data_service.get_multiple_symbols_data(symbols, interval)
        return {
            "interval": interval,
            "symbols_count": len(data),
            "data": data
        }
    except Exception as e:
        logger.error(f"批量获取K线数据异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
