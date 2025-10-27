# A股数据API路由
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from services.market_data_stock_cn import stock_cn_service
from models.market_data_interface import TimeFrame

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/market/stock_cn", tags=["A股数据"])

@router.get("/health")
async def stock_cn_health():
    """A股数据服务健康检查"""
    return {
        "service": "stock_cn_data",
        "status": "healthy" if stock_cn_service.is_initialized else "initializing",
        "market_type": "A股",
        "supported_symbols_count": len(await stock_cn_service.get_symbol_list())
    }

@router.get("/symbols")
async def get_stock_symbols():
    """获取A股股票列表"""
    try:
        symbols = await stock_cn_service.get_symbol_list()
        return {
            "market": "A股",
            "symbols_count": len(symbols),
            "symbols": symbols
        }
    except Exception as e:
        logger.error(f"获取A股股票列表异常: {e}")
        raise HTTPException(status_code=500, detail="获取股票列表失败")

@router.get("/klines/{symbol}")
async def get_stock_klines(
    symbol: str,
    timeframe: str = Query("1d", regex="^1m|5m|15m|1h|4h|1d|1w$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """获取A股K线数据"""
    try:
        # 转换时间框架
        tf_mapping = {
            "1m": TimeFrame.MIN1,
            "5m": TimeFrame.MIN5,
            "15m": TimeFrame.MIN15,
            "1h": TimeFrame.HOUR1,
            "4h": TimeFrame.HOUR4,
            "1d": TimeFrame.DAY1,
            "1w": TimeFrame.WEEK1
        }
        tf_enum = tf_mapping.get(timeframe, TimeFrame.DAY1)
        
        klines = await stock_cn_service.get_klines(symbol, tf_enum, limit)
        
        if not klines:
            raise HTTPException(status_code=404, detail="未找到该股票的K线数据")
        
        return {
            "symbol": symbol,
            "market": "A股",
            "timeframe": timeframe,
            "data_count": len(klines),
            "klines": klines
        }
        
    except Exception as e:
        logger.error(f"获取A股K线数据异常: {e}")
        raise HTTPException(status_code=500, detail="获取K线数据失败")

@router.get("/{symbol}/info")
async def get_stock_info(symbol: str):
    """获取A股股票信息"""
    try:
        info = await stock_cn_service.get_market_info(symbol)
        if not info:
            raise HTTPException(status_code=404, detail="未找到该股票信息")
        
        return {
            "symbol": symbol,
            "market": "A股",
            "info": info
        }
    except Exception as e:
        logger.error(f"获取A股股票信息异常: {e}")
        raise HTTPException(status_code=500, detail="获取股票信息失败")

@router.get("/{symbol}/price")
async def get_stock_price(symbol: str):
    """获取A股实时价格"""
    try:
        price = await stock_cn_service.get_realtime_price(symbol)
        if price is None:
            raise HTTPException(status_code=404, detail="未找到该股票价格")
        
        return {
            "symbol": symbol,
            "market": "A股",
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取A股实时价格异常: {e}")
        raise HTTPException(status_code=500, detail="获取实时价格失败")

@router.get("/sectors/overview")
async def get_sectors_overview():
    """获取A股板块概览"""
    try:
        # 这里可以实现板块数据的获取
        sectors = [
            {"name": "金融", "code": "finance", "stock_count": 150, "avg_change": 0.5},
            {"name": "科技", "code": "tech", "stock_count": 200, "avg_change": 1.2},
            {"name": "医药", "code": "medical", "stock_count": 120, "avg_change": 0.8},
            {"name": "消费", "code": "consumer", "stock_count": 180, "avg_change": 0.3},
            {"name": "能源", "code": "energy", "stock_count": 80, "avg_change": -0.2}
        ]
        
        return {
            "market": "A股",
            "sectors_count": len(sectors),
            "sectors": sectors
        }
    except Exception as e:
        logger.error(f"获取A股板块概览异常: {e}")
        raise HTTPException(status_code=500, detail="获取板块概览失败")

@router.get("/market/overview")
async def get_market_overview():
    """获取A股市场概览"""
    try:
        # 模拟市场概览数据
        overview = {
            "total_market_cap": 85000000000000,  # 85万亿
            "daily_turnover": 800000000000,      # 8000亿
            "advance_decline": {
                "advance": 1500,
                "decline": 1000,
                "unchanged": 200
            },
            "indexes": [
                {"name": "上证指数", "code": "000001", "price": 3200.15, "change": 0.5},
                {"name": "深证成指", "code": "399001", "price": 11500.45, "change": 0.8},
                {"name": "创业板指", "code": "399006", "price": 2400.67, "change": 1.2}
            ]
        }
        
        return {
            "market": "A股",
            "overview": overview,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取A股市场概览异常: {e}")
        raise HTTPException(status_code=500, detail="获取市场概览失败")
