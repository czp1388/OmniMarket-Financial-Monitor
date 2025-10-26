from fastapi import APIRouter, HTTPException
import ccxt
from datetime import datetime
import asyncio

router = APIRouter()

# 支持更多交易所
exchanges = {
    "binance": ccxt.binance(),
    # 可以添加更多交易所，比如：
    # "huobi": ccxt.huobi(),
    # "okx": ccxt.okx(),
}

@router.get("/prices/")
async def get_price(symbol: str = "BTC/USDT", exchange: str = "binance"):
    try:
        if exchange not in exchanges:
            raise HTTPException(status_code=400, detail="不支持的交易所")

        ticker = exchanges[exchange].fetch_ticker(symbol)

        return {
            "symbol": symbol,
            "price": ticker['last'],
            "high": ticker['high'],
            "low": ticker['low'],
            "volume": ticker['baseVolume'],
            "change": ticker['change'],
            "percentage": ticker['percentage'],
            "timestamp": datetime.now().isoformat(),
            "exchange": exchange
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取价格失败: {str(e)}")

@router.get("/exchanges")
async def get_exchanges():
    return {
        "exchanges": list(exchanges.keys()),
        "count": len(exchanges)
    }

@router.get("/multiple-prices/")
async def get_multiple_prices(symbols: str = "BTC/USDT,ETH/USDT", exchange: str = "binance"):
    """获取多个交易对的价格"""
    try:
        if exchange not in exchanges:
            raise HTTPException(status_code=400, detail="不支持的交易所")
        
        symbol_list = [s.strip() for s in symbols.split(",")]
        results = []
        
        for symbol in symbol_list:
            try:
                ticker = exchanges[exchange].fetch_ticker(symbol)
                results.append({
                    "symbol": symbol,
                    "price": ticker['last'],
                    "change": ticker['change'],
                    "percentage": ticker['percentage'],
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return {
            "exchange": exchange,
            "prices": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取价格失败: {str(e)}")
