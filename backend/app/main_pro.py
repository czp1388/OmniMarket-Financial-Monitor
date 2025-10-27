from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="寰宇多市场金融监控系统",
    description="专业版本 - 多市场金融数据实时监控平台",
    version="2.8.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/")
async def root():
    return {
        "message": "寰宇多市场金融监控系统 API - 专业版 v2.8",
        "status": "运行中",
        "version": "2.6.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "professional"}

# 尝试导入路由 - 使用安全的导入方式
logger.info("🔄 开始导入路由...")

# 市场数据路由
try:
    from routers.market import router as market_router
    app.include_router(market_router, prefix="/api/v1", tags=["市场数据"])
    logger.info("✅ 市场数据路由导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 市场数据路由导入失败: {e}")

# WebSocket路由
try:
    from routers.websocket import router as websocket_router
    app.include_router(websocket_router, prefix="/api/v1", tags=["实时数据"])
    logger.info("✅ WebSocket路由导入成功")
except ImportError as e:
    logger.warning(f"⚠️ WebSocket路由导入失败: {e}")

# 基础预警路由
try:
    from routers.alerts import router as alerts_router
    app.include_router(alerts_router, prefix="/api/v1", tags=["基础预警"])
    logger.info("✅ 基础预警路由导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 基础预警路由导入失败: {e}")

# 高级预警路由
try:
    from routers.advanced_alerts import router as advanced_alerts_router
from routers.telegram_alerts import router as telegram_alerts_router
from routers.database_api import router as database_api_router
    app.include_router(advanced_alerts_router, prefix="/api/v1", tags=["高级预警"])
    logger.info("✅ 高级预警路由导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 高级预警路由导入失败: {e}")

# 静态文件服务
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")
public_dir = os.path.join(project_root, "public")

if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
    logger.info(f"✅ 静态文件服务已挂载: {public_dir}")
else:
    logger.warning(f"⚠️ 静态文件目录不存在: {public_dir}")

@app.on_event("startup")
async def startup_event():
    """安全启动服务"""
    logger.info("🚀 启动寰宇多市场金融监控系统 专业版 v2.8...")
    
    # 尝试初始化数据服务
    try:
        from services.real_exchange_service import real_data_service
        asyncio.create_task(real_data_service.initialize())
        logger.info("✅ 真实数据服务初始化已启动")
    except ImportError as e:
        logger.warning(f"⚠️ 真实数据服务导入失败: {e}")
        try:
            from services.safe_data_service import data_service
            logger.info("✅ 使用模拟数据服务")
        except ImportError:
            logger.warning("⚠️ 所有数据服务都不可用")
    
    # 尝试初始化高级预警服务
    try:
        from services.advanced_alert_service import advanced_alert_service
        await advanced_alert_service.initialize()
        logger.info("✅ 高级预警服务初始化完成")
        
        # 延迟启动预警监控
        async def delayed_alert_monitoring():
            await asyncio.sleep(10)
            try:
                from services.real_exchange_service import real_data_service
                await advanced_alert_service.start_monitoring(real_data_service)
                logger.info("✅ 高级预警监控已启动")
            except:
                logger.warning("⚠️ 预警监控启动失败")
        
        asyncio.create_task(delayed_alert_monitoring())
    except ImportError as e:
        logger.warning(f"⚠️ 高级预警服务导入失败: {e}")
    
    # 检查邮件服务
    try:
        from services.email_service import email_service
        status = email_service.get_config_status()
        if status['enabled']:
            logger.info("✅ 邮件通知服务已就绪")
        else:
            logger.info("ℹ️ 邮件服务未配置")
    except ImportError as e:
        logger.warning(f"⚠️ 邮件服务导入失败: {e}")

if __name__ == "__main__":
    print("🚀 启动专业版寰宇多市场金融监控系统 v2.6")
    print("📊 服务将运行在: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
