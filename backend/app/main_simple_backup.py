from fastapi import FastAPI
import uvicorn
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "OmniMarket 简化版", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "omnimarket"}

@app.get("/api/v1/system/info")
async def system_info():
    return {
        "name": "OmniMarket Financial Monitor",
        "version": "1.0.0",
        "description": "简化版服务",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# 简单的A股数据端点
@app.get("/api/v1/market/stock_cn/health")
async def stock_cn_health():
    return {
        "service": "stock_cn_data",
        "status": "healthy",
        "market_type": "A股"
    }

@app.get("/api/v1/market/stock_cn/symbols")
async def get_stock_cn_symbols():
    symbols = [
        {"symbol": "000001.SZ", "name": "平安银行"},
        {"symbol": "000002.SZ", "name": "万科A"},
        {"symbol": "600000.SH", "name": "浦发银行"},
        {"symbol": "600036.SH", "name": "招商银行"},
        {"symbol": "601318.SH", "name": "中国平安"}
    ]
    return {
        "market": "A股",
        "count": len(symbols),
        "symbols": symbols
    }

# 简单的港股数据端点
@app.get("/api/v1/market/stock_hk/health")
async def stock_hk_health():
    return {
        "service": "stock_hk_data",
        "status": "healthy",
        "market_type": "港股"
    }

@app.get("/api/v1/market/stock_hk/symbols")
async def get_stock_hk_symbols():
    symbols = [
        {"symbol": "00700.HK", "name": "腾讯控股"},
        {"symbol": "00941.HK", "name": "中国移动"},
        {"symbol": "01299.HK", "name": "友邦保险"},
        {"symbol": "02318.HK", "name": "中国平安"},
        {"symbol": "03988.HK", "name": "中国银行"}
    ]
    return {
        "market": "港股",
        "count": len(symbols),
        "symbols": symbols
    }

if __name__ == "__main__":
    print("🚀 启动简化版服务...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
