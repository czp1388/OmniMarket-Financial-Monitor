import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import asyncio

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="OmniMarket Financial Monitor API",
    description="全市场金融监控系统后端API - 增强版",
    version="2.9.4",
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

# 导入路由
from routers.market_data import router as market_data_router
from routers.technical_indicators import router as technical_indicators_router
from routers.database_api import router as database_api_router
from routers.user_management import router as user_management_router
from routers.permission_management import router as permission_management_router

# 包含路由
app.include_router(market_data_router)
app.include_router(technical_indicators_router)
app.include_router(database_api_router)
app.include_router(user_management_router)
app.include_router(permission_management_router)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        from services.market_data_service import market_data_service
        from services.realtime_monitoring import realtime_monitoring_service
        
        market_data_status = "healthy" if market_data_service.is_initialized else "initializing"
        monitoring_status = "healthy" if realtime_monitoring_service.is_running else "stopped"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.9.4",
            "services": {
                "market_data": market_data_status,
                "realtime_monitoring": monitoring_status
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# 根端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "欢迎使用 OmniMarket Financial Monitor API - 增强版",
        "version": "2.9.4",
        "features": [
            "多市场数据接入",
            "实时K线数据", 
            "技术指标计算",
            "用户权限管理",
            "预警规则框架"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "market_data": "/api/v1/market",
            "technical_indicators": "/api/v1/technical"
        }
    }

# 系统信息端点
@app.get("/api/v1/system/info")
async def system_info():
    """系统信息端点"""
    return {
        "name": "OmniMarket Financial Monitor",
        "version": "2.9.4",
        "description": "全市场金融监控系统",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "supported_markets": ["crypto", "stock", "forex"],
        "supported_intervals": ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
    }

@app.on_event("startup")
async def startup_event():
    """启动时初始化服务"""
    logger.info("🚀 启动 OmniMarket Financial Monitor 服务...")
    
    try:
        # 初始化市场数据服务
        from services.market_data_service import market_data_service
        await market_data_service.initialize()
        
        # 初始化实时监控服务
        from services.realtime_monitoring import realtime_monitoring_service
        await realtime_monitoring_service.initialize()
        
        logger.info("✅ 所有服务初始化完成")
        
    except Exception as e:
        logger.error(f"❌ 服务初始化失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    logger.info("🛑 正在关闭服务...")
    
    try:
        from services.realtime_monitoring import realtime_monitoring_service
        await realtime_monitoring_service.stop_all_monitoring()
        logger.info("✅ 实时监控服务已停止")
    except Exception as e:
        logger.error(f"关闭服务异常: {e}")

# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
