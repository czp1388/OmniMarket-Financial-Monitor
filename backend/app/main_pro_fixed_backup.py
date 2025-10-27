# 寰宇多市场金融监控系统 - 主服务入口（修复版）
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime
import asyncio

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("financial_monitor.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="寰宇多市场金融监控系统",
    description="实时监控多市场金融数据，提供智能预警功能",
    version="2.9.0",
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

# 导入路由和服务（避免阻塞启动）
try:
    from routers.database_api import router as database_api_router
    from routers.user_management import router as user_management_router
from routers.permission_management import router as permission_management_router
    logger.info("✅ 路由导入成功")
except ImportError as e:
    logger.error(f"❌ 路由导入失败: {e}")

# 导入服务
try:
    from services.database_service import database_service
    logger.info("✅ 数据库服务导入成功")
except ImportError as e:
    logger.error(f"❌ 数据库服务导入失败: {e}")
    database_service = None

# 延迟导入数据服务，避免启动阻塞
data_service = None
telegram_service = None

async def initialize_services():
    """异步初始化服务"""
    global data_service, telegram_service
    try:
        # 延迟导入数据服务
        from services.data_service import data_service as ds
        data_service = ds
        logger.info("✅ 数据服务初始化成功")
    except Exception as e:
        logger.warning(f"⚠️ 数据服务初始化失败（不影响核心功能）: {e}")
        data_service = None
    
    try:
        from services.telegram_service import telegram_service as ts
        telegram_service = ts
        logger.info("✅ Telegram服务初始化成功")
    except Exception as e:
        logger.warning(f"⚠️ Telegram服务初始化失败: {e}")
        telegram_service = None

# 包含路由
app.include_router(database_api_router, prefix="/api/v1", tags=["数据库管理"])
app.include_router(user_management_router, prefix="/api/v1", tags=["用户管理"])`napp.include_router(permission_management_router, prefix="/api/v1", tags=["权限管理"])

# 健康检查端点
@app.get("/health")
async def health_check():
    """系统健康检查"""
    db_status = database_service.is_initialized if database_service else False
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.9.0",
        "database_initialized": db_status,
        "services": {
            "database": "available" if database_service else "unavailable",
            "user_management": "available",
            "data_service": "available" if data_service else "unavailable",
            "telegram_service": "available" if telegram_service else "unavailable"
        }
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用寰宇多市场金融监控系统",
        "version": "2.9.0",
        "docs": "/docs",
        "health": "/health"
    }

# 启动时初始化服务
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 启动后台服务初始化...")
    # 在后台异步初始化可能阻塞的服务
    asyncio.create_task(initialize_services())

# 启动应用
if __name__ == "__main__":
    logger.info("🚀 启动寰宇多市场金融监控系统...")
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True
    )


