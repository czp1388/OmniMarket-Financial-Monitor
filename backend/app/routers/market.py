from fastapi import APIRouter, HTTPException
import ccxt
from datetime import datetime

router = APIRouter()

# 初始化交易所
exchanges = {
    \"binance\": ccxt.binance(),
}

@router.get(\"/prices/{symbol}\")
async def get_price(symbol: str = \"BTC/USDT\", exchange: str = \"binance\"):
    \"\"\"获取加密货币价格\"\"\"
    try:
        if exchange not in exchanges:
            raise HTTPException(status_code=400, detail=\"不支持的交易所\")
        
        # 获取行情数据
        ticker = exchanges[exchange].fetch_ticker(symbol)
        
        return {
            \"symbol\": symbol,
            \"price\": ticker['last'],
            \"high\": ticker['high'],
            \"low\": ticker['low'],
            \"volume\": ticker['baseVolume'],
            \"timestamp\": datetime.now().isoformat(),
            \"exchange\": exchange
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f\"获取价格失败: {str(e)}\")

@router.get(\"/exchanges\")
async def get_exchanges():
    \"\"\"获取支持的交易所列表\"\"\"
    return {
        \"exchanges\": list(exchanges.keys()),
        \"count\": len(exchanges)
    }
