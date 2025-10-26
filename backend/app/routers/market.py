from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from services.safe_data_service import data_service, astock_service
    logger.info("✅ 市场路由使用安全数据服务")
except ImportError as e:
    logger.warning(f"⚠️ 安全数据服务导入失败: {e}")
    data_service = None
    astock_service = None

router = APIRouter()

@router.get("/exchanges")
async def get_exchanges():
    """获取支持的交易所列表"""
    if data_service and data_service._initialized:
        return {
            "crypto_exchanges": data_service.get_supported_exchanges(),
            "stock_exchanges": ["A股", "港股", "美股"]
        }
    else:
        return {
            "crypto_exchanges": ["binance", "okx"],
            "stock_exchanges": ["A股"],
            "status": "数据服务初始化中"
        }

@router.get("/symbols/{exchange}")
async def get_symbols(exchange: str):
    """获取交易所的交易对列表"""
    if data_service and exchange in ["binance", "okx"]:
        symbols = data_service.get_symbols(exchange)
        return {"exchange": exchange, "symbols": symbols}
    else:
        return {"exchange": exchange, "symbols": ["BTC/USDT", "ETH/USDT"], "message": "基础数据"}

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
    
    # 返回模拟数据
    return {
        "symbol": symbol,
        "price": 50000.0,
        "high": 51000.0, 
        "low": 49000.0,
        "volume": 1000.0,
        "timestamp": 0,
        "message": "模拟数据"
    }

@router.get("/astock/list")
async def get_astock_list():
    """获取A股股票列表"""
    if astock_service:
        return astock_service.get_stock_list()
    return [
        {"symbol": "000001.SZ", "name": "平安银行"},
        {"symbol": "600036.SH", "name": "招商银行"}
    ]

@router.get("/astock/price/{symbol}")
async def get_astock_price(symbol: str):
    """获取A股股票价格"""
    if astock_service:
        return astock_service.get_stock_price(symbol)
    return {"symbol": symbol, "price": 100.0, "change": 1.5, "volume": 1000000}

@router.get("/market/status")
async def get_market_status():
    """获取市场状态概览"""
    return {
        "total_markets": 3,
        "market_status": "稳定运行",
        "service_version": "2.0.0",
        "major_pairs": [
            {"symbol": "BTC/USDT", "price": 50000.0, "exchange": "binance"},
            {"symbol": "ETH/USDT", "price": 3000.0, "exchange": "binance"}
        ]
    }
