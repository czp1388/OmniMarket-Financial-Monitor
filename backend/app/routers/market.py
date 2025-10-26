from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sys
import os

# 添加服务路径
sys.path.append(os.path.dirname(__file__))
try:
    from services.data_service import data_service, astock_service
    print("✅ 市场路由成功导入数据服务")
except ImportError as e:
    print(f"❌ 市场路由导入失败: {e}")
    data_service = None
    astock_service = None

router = APIRouter()

@router.get("/exchanges")
async def get_exchanges():
    """获取支持的交易所列表"""
    if data_service:
        return {
            "crypto_exchanges": data_service.get_supported_exchanges(),
            "stock_exchanges": ["A股", "港股", "美股"]
        }
    else:
        return {"crypto_exchanges": [], "stock_exchanges": []}

@router.get("/symbols/{exchange}")
async def get_symbols(exchange: str):
    """获取交易所的交易对列表"""
    if data_service and exchange in data_service.get_supported_exchanges():
        symbols = data_service.get_symbols(exchange)
        return {"exchange": exchange, "symbols": symbols[:50]}
    else:
        return {"exchange": exchange, "symbols": []}

@router.get("/prices/")
async def get_price(
    exchange: str = Query(..., description="交易所"),
    symbol: str = Query(..., description="交易对")
):
    """获取指定交易对价格"""
    if data_service:
        price_data = data_service.get_price(exchange, symbol)
        if price_data:
            return price_data
    raise HTTPException(status_code=404, detail="价格数据获取失败")

@router.get("/ohlcv/")
async def get_ohlcv(
    exchange: str = Query(..., description="交易所"),
    symbol: str = Query(..., description="交易对"),
    timeframe: str = Query("1m", description="时间周期"),
    limit: int = Query(100, description="数据条数")
):
    """获取K线数据"""
    if data_service:
        ohlcv_data = data_service.get_ohlcv(exchange, symbol, timeframe, limit)
        if ohlcv_data:
            return ohlcv_data
    raise HTTPException(status_code=404, detail="K线数据获取失败")

@router.get("/astock/list")
async def get_astock_list():
    """获取A股股票列表"""
    if astock_service:
        return astock_service.get_stock_list()
    return []

@router.get("/astock/price/{symbol}")
async def get_astock_price(symbol: str):
    """获取A股股票价格"""
    if astock_service:
        return astock_service.get_stock_price(symbol)
    return {"symbol": symbol, "price": 0, "change": 0, "volume": 0}

@router.get("/market/status")
async def get_market_status():
    """获取市场状态概览"""
    if not data_service:
        return {
            "total_markets": 0,
            "market_status": "数据服务未就绪",
            "major_pairs": []
        }
    
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