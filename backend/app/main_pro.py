# 寰宇多市场金融监控系统 - 专业版主服务
import logging
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 导入数据库服务
try:
    from services.database_service import database_service
    logger.info("✅ 数据库服务导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 数据库服务导入失败: {e}")
    database_service = None

# 导入Telegram服务
try:
    from services.telegram_service import telegram_service
    logger.info("✅ Telegram机器人服务导入成功")
except ImportError as e:
    logger.warning(f"⚠️ Telegram机器人服务导入失败: {e}")
    telegram_service = None

# 导入其他服务
try:
    from services.data_service import data_service
    logger.info("✅ 数据服务导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 数据服务导入失败: {e}")
    data_service = None

try:
    from services.advanced_alert_service import advanced_alert_service
    logger.info("✅ 高级预警服务导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 高级预警服务导入失败: {e}")
    advanced_alert_service = None

try:
    from services.email_service import email_service
    logger.info("✅ 邮件通知服务导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 邮件通知服务导入失败: {e}")
    email_service = None

# 导入路由
from routers import market_data, alert_rules, system_info, telegram_alerts
from routers.database_api import router as database_api_router
from routers.user_management import router as user_management_router

# 数据库初始化函数
async def initialize_database():
    """初始化数据库"""
    if database_service:
        await database_service.initialize()
        if database_service.is_initialized:
            logger.info("✅ 数据库服务初始化完成")
        else:
            logger.warning("⚠️ 数据库服务初始化失败")
    else:
        logger.warning("⚠️ 数据库服务不可用")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期管理"""
    # 启动服务
    await startup_event()
    yield
    # 关闭服务
    await shutdown_event()

async def startup_event():
    """安全启动服务"""
    logger.info("🚀 启动寰宇多市场金融监控系统 专业版 v2.8...")
    
    # 初始化数据库
    await initialize_database()
    
    # 初始化数据服务
    if data_service:
        await data_service.initialize()
        logger.info("✅ 数据服务初始化完成")
    
    # 初始化预警服务
    if advanced_alert_service:
        await advanced_alert_service.initialize()
        logger.info("✅ 高级预警服务初始化完成")
        
        # 启动预警监控
        if data_service:
            await advanced_alert_service.start_monitoring(data_service)
            logger.info("✅ 高级预警监控已启动")
    
    # 初始化Telegram机器人
    if telegram_service:
        await telegram_service.initialize()
        logger.info("✅ Telegram机器人服务初始化完成")
    
    # 初始化邮件服务
    if email_service:
        await email_service.initialize()
        logger.info("✅ 邮件服务初始化完成")
    
    logger.info("🎉 所有服务启动完成！")

async def shutdown_event():
    """关闭事件"""
    logger.info("🛑 正在停止服务...")
    
    # 停止预警监控
    if advanced_alert_service:
        await advanced_alert_service.stop_monitoring()
        logger.info("✅ 高级预警监控已停止")
    
    logger.info("👋 服务已停止")

# 创建FastAPI应用
app = FastAPI(
    title="寰宇多市场金融监控系统 专业版 v2.8",
    description="实时多市场金融数据监控和预警系统",
    version="2.8.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(market_data.router, prefix="/api/v1", tags=["市场数据"])
app.include_router(alert_rules.router, prefix="/api/v1", tags=["预警规则"])
app.include_router(system_info.router, prefix="/api/v1", tags=["系统信息"])
app.include_router(telegram_alerts.router, prefix="/api/v1", tags=["Telegram通知"])
app.include_router(database_api_router, prefix="/api/v1", tags=["数据库管理"])

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用寰宇多市场金融监控系统 专业版 v2.8",
        "status": "running",
        "version": "2.8.0"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.8.0",
        "database_initialized": database_service.is_initialized if database_service else False
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_pro:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
