from fastapi import APIRouter
from .crypto_data import CryptoData

router = APIRouter(prefix="/api/v1/crypto", tags=["cryptocurrency"])
crypto_data = CryptoData()

@router.get("/health")
async def crypto_health():
    return {"status": "healthy", "service": "crypto_data"}

@router.get("/ticker/{symbol}")
async def get_crypto_ticker(symbol: str = "BTC/USDT"):
    return crypto_data.get_ticker(symbol)

@router.get("/ohlcv/{symbol}")
async def get_crypto_ohlcv(
    symbol: str = "BTC/USDT", 
    timeframe: str = "1m",
    limit: int = 100
):
    return crypto_data.get_ohlcv(symbol, timeframe, limit)
