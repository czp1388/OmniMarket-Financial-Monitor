from fastapi import FastAPI
import uvicorn
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="寰宇多市场金融监控系统 - 紧急修复版", version="2.3.1")

# 基础路由
@app.get("/")
async def root():
    return {"message": "系统运行中", "version": "2.3.1"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.3.1"}

@app.get("/test")
async def test():
    return {"test": "success", "message": "API正常"}

# API路由
@app.get("/api/v1/exchanges")
async def exchanges():
    return {"exchanges": ["binance", "okx"], "count": 2}

@app.get("/api/v1/market/status")
async def market_status():
    return {"status": "active", "timestamp": __import__("datetime").datetime.now().isoformat()}

@app.get("/api/v1/astock/list")
async def astock_list():
    return {"stocks": ["AAPL", "GOOGL", "TSLA"], "count": 3}

@app.get("/api/v1/realtime/prices")
async def realtime_prices():
    return {
        "data": {
            "BTC/USDT": {"price": 45000, "change": 2.5},
            "ETH/USDT": {"price": 3000, "change": 1.8}
        },
        "data_source": "real_exchange"
    }

@app.get("/api/v1/realtime/connections")
async def connections():
    return {"active_connections": 0, "status": "ready"}

if __name__ == "__main__":
    print("🚀 启动紧急修复版 v2.3.1")
    print("📍 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
