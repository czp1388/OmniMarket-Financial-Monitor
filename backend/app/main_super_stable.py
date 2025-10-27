"""
OmniMarket Financial Monitor - 集成增强版主服务
包含增强版A股数据功能
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('service.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="OmniMarket Financial Monitor API",
    description="全市场金融监控系统 - 集成增强版A股数据",
    version="3.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含增强版A股数据路由
from routers.enhanced_stock_cn_api import router as enhanced_stock_cn_router
app.include_router(enhanced_stock_cn_router)

@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "欢迎使用 OmniMarket Financial Monitor API - 集成增强版A股数据",
        "version": "3.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "new_features": ["增强版A股数据", "实时行情", "历史数据", "股票搜索"]
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    from services.enhanced_stock_cn_service import enhanced_stock_cn_service
    
    enhanced_status = "healthy" if enhanced_stock_cn_service.is_initialized else "initializing"
    
    return {
        "status": "healthy",
        "service": "OmniMarket Financial Monitor",
        "version": "3.1.0",
        "services": {
            "enhanced_a_share_data": enhanced_status
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/system/info")
async def system_info():
    """系统信息"""
    from services.enhanced_stock_cn_service import enhanced_stock_cn_service
    
    stocks = await enhanced_stock_cn_service.get_stock_list()
    
    return {
        "name": "OmniMarket Financial Monitor",
        "version": "3.1.0",
        "description": "多市场金融监控系统 - 集成增强版A股数据",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "增强版A股数据服务",
            "实时行情监控", 
            "历史数据分析",
            "多市场数据接入"
        ],
        "statistics": {
            "supported_a_share_stocks": len(stocks),
            "supported_markets": ["A股", "港股"],
            "data_sources": ["enhanced_mock", "akshare_ready"]
        }
    }

# 原有的简单A股数据端点（保持兼容）
@app.get("/api/v1/market/stock_cn/health")
async def stock_cn_health():
    return {
        "service": "stock_cn_data",
        "status": "healthy",
        "market_type": "A股",
        "supported_symbols": 5
    }

@app.get("/api/v1/market/stock_cn/symbols")
async def get_stock_cn_symbols():
    symbols = [
        {"symbol": "000001.SZ", "name": "平安银行", "market": "sz"},
        {"symbol": "000002.SZ", "name": "万科A", "market": "sz"},
        {"symbol": "600000.SH", "name": "浦发银行", "market": "sh"},
        {"symbol": "600036.SH", "name": "招商银行", "market": "sh"},
        {"symbol": "601318.SH", "name": "中国平安", "market": "sh"}
    ]
    return {
        "market": "A股",
        "count": len(symbols),
        "symbols": symbols
    }

# 原有的港股数据端点
@app.get("/api/v1/market/stock_hk/health")
async def stock_hk_health():
    return {
        "service": "stock_hk_data", 
        "status": "healthy",
        "market_type": "港股",
        "supported_symbols": 5
    }

@app.get("/api/v1/market/stock_hk/symbols")
async def get_stock_hk_symbols():
    symbols = [
        {"symbol": "00700.HK", "name": "腾讯控股", "currency": "HKD"},
        {"symbol": "00941.HK", "name": "中国移动", "currency": "HKD"},
        {"symbol": "01299.HK", "name": "友邦保险", "currency": "HKD"},
        {"symbol": "02318.HK", "name": "中国平安", "currency": "HKD"},
        {"symbol": "03988.HK", "name": "中国银行", "currency": "HKD"}
    ]
    return {
        "market": "港股", 
        "count": len(symbols),
        "symbols": symbols
    }

if __name__ == "__main__":
    logger.info("🚀 启动 OmniMarket Financial Monitor (集成增强版)...")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    
    # 初始化增强版服务
    async def initialize_services():
        from services.enhanced_stock_cn_service import enhanced_stock_cn_service
        await enhanced_stock_cn_service.initialize()
    
    import asyncio
    asyncio.run(initialize_services())
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        logger.error("详细错误信息:", exc_info=True)
        input("按Enter键退出...")
