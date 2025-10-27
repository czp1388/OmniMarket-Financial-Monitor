import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
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

# 导入路由和服务（避免阻塞启动）
try:
    from routers.database_api import router as database_api_router
    from routers.user_management import router as user_management_router
    from routers.permission_management import router as permission_management_router
    logger.info("✅ 路由导入成功")
except ImportError as e:
    logger.error(f"❌ 路由导入失败: {e}")

# 包含路由
try:
    app.include_router(database_api_router, prefix="/api/v1", tags=["数据库管理"])
    app.include_router(user_management_router, prefix="/api/v1", tags=["用户管理"])
    app.include_router(permission_management_router, prefix="/api/v1", tags=["权限管理"])
    logger.info("✅ 路由包含成功")
except Exception as e:
    logger.error(f"❌ 路由包含失败: {e}")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        from services.database_service import database_service
        db_status = database_service.is_initialized if database_service else False
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.9.3",
            "database_initialized": db_status
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
        "message": "欢迎使用 OmniMarket Financial Monitor API",
        "version": "2.9.3",
        "docs": "/docs",
        "health": "/health"
    }

# 启动服务
if __name__ == "__main__":
    # 初始化数据库服务
    try:
        from services.database_service import database_service
        from services.auth_service import auth_service
        
        # 初始化数据库
        if database_service.initialize():
            logger.info("✅ 数据库初始化成功")
        else:
            logger.error("❌ 数据库初始化失败")
            
        # 初始化认证服务
        auth_service.initialize()
        logger.info("✅ 认证服务初始化成功")
        
    except Exception as e:
        logger.error(f"❌ 服务初始化失败: {e}")
    
    # 启动UVicorn服务器
    uvicorn.run(
        "main_pro_fixed:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
