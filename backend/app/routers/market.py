from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
import os

# 添加服务路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.data_service import data_service, astock_service

router = APIRouter()

@router.get("/exchanges")
async def get_exchanges():
    """获取支持的交易所列表"""
    return {
        "crypto_exchanges": data_service.get_supported_exchanges(),
        "stock_exchanges": ["A股", "港股", "美股"]
    }

@router.get("/symbols/{exchange}")
async def get_symbols(exchange: str):
    """获取交易所的交易对列表"""
    if exchange in data_service.get_supported_exchanges():
        symbols = data_service.get_symbols(exchange)
        return {"exchange": exchange, "symbols": symbols[:50]}  # 限制返回数量
    else:
        return {"exchange": exchange, "symbols": []}

@router.get("/prices/")
async def get_price(
    exchange: str = Query(..., description="交易所"),
    symbol: str = Query(..., description="交易对")
):
    """获取指定交易对价格"""
    price_data = data_service.get_price(exchange, symbol)
    if price_data:
        return price_data
    else:
        raise HTTPException(status_code=404, detail="价格数据获取失败")

@router.get("/ohlcv/")
async def get_ohlcv(
    exchange: str = Query(..., description="交易所"),
    symbol: str = Query(..., description="交易对"),
    timeframe: str = Query("1m", description="时间周期"),
    limit: int = Query(100, description="数据条数")
):
    """获取K线数据"""
    ohlcv_data = data_service.get_ohlcv(exchange, symbol, timeframe, limit)
    if ohlcv_data:
        return ohlcv_data
    else:
        raise HTTPException(status_code=404, detail="K线数据获取失败")

@router.get("/astock/list")
async def get_astock_list():
    """获取A股股票列表"""
    return astock_service.get_stock_list()

@router.get("/astock/price/{symbol}")
async def get_astock_price(symbol: str):
    """获取A股股票价格"""
    return astock_service.get_stock_price(symbol)

@router.get("/market/status")
async def get_market_status():
    """获取市场状态概览"""
    # 获取几个主要交易对的状态
    major_pairs = [
        {"exchange": "binance", "symbol": "BTC/USDT"},
        {"exchange": "binance", "symbol": "ETH/USDT"},
        {"exchange": "okx", "symbol": "BTC/USDT"}
    ]
    
    status = []
    for pair in major_pairs:
        price_data = data_service.get_price(pair["exchange"], pair["symbol"])
        if price_data:
            status.append(price_data)
    
    return {
        "total_markets": len(data_service.get_supported_exchanges()),
        "market_status": "正常运行",
        "major_pairs": status
    }
