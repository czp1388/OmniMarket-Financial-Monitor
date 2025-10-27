"""
OmniMarket Financial Monitor - 超级稳定版本
确保服务在任何情况下都能启动
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
    description="全市场金融监控系统 - 超级稳定版本",
    version="3.0.0",
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

@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "欢迎使用 OmniMarket Financial Monitor API - 超级稳定版本",
        "version": "3.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "OmniMarket Financial Monitor",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/system/info")
async def system_info():
    """系统信息"""
    return {
        "name": "OmniMarket Financial Monitor",
        "version": "3.0.0",
        "description": "多市场金融监控系统 - 稳定运行",
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
    logger.info("🚀 启动 OmniMarket Financial Monitor (超级稳定版)...")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    
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
        # 等待用户输入，防止窗口立即关闭
        input("按Enter键退出...")
