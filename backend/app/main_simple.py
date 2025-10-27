import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="OmniMarket Financial Monitor API",
    description="全市场金融监控系统后端API",
    version="2.9.3",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.9.3",
        "database_initialized": False
    }

# 根端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "欢迎使用 OmniMarket Financial Monitor API",
        "version": "2.9.3",
        "docs": "/docs",
        "health": "/health"
    }

# 启动服务
# 市场数据端点
from routers.market_data import router as market_data_router
app.include_router(market_data_router)

@app.on_event("startup")
async def startup_event():
    """启动时初始化服务"""
    logger.info("初始化市场数据服务...")
    try:
        from services.market_data_service import market_data_service
        await market_data_service.initialize()
    except Exception as e:
        logger.warning(f"市场数据服务初始化失败: {e}")

if __name__ == "__main__":
    logger.info("🚀 启动 OmniMarket Financial Monitor 服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

