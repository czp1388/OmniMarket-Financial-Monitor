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
    description="专业版本 - 多市场金融数据实时监控平台 + 真实交易所数据 + 高级预警 + Web界面",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由 - 放在最前面
@app.get("/")
async def root():
    return {
        "message": "寰宇多市场金融监控系统 API - 专业版 v2.5",
        "status": "运行中",
        "version": "2.5.0",
        "features": ["真实市场数据", "高级价格预警", "多交易所支持", "实时推送", "Web界面", "专业级"],
        "websocket": "ws://localhost:8000/ws/realtime",
        "web_interface": "http://localhost:8000/",
        "data_source": "真实交易所 + 模拟数据"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "professional",
        "version": "2.5.0",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "data_source": "hybrid"
    }

@app.get("/test")
async def test_api():
    """测试API连通性"""
    return {
        "test": "success",
        "message": "API服务正常运行",
        "version": "2.5.0",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "data_source": "hybrid"
    }

# 导入和注册路由
try:
    # 尝试导入真实数据服务
    from services.real_exchange_service import real_data_service
    logger.info("✅ 真实数据服务导入成功")
    data_service = real_data_service
except ImportError as e:
    logger.warning(f"⚠️ 真实数据服务导入失败: {e}")
    # 回退到模拟数据
    try:
        from services.safe_data_service import data_service
        logger.info("✅ 使用模拟数据服务")
    except ImportError:
        logger.error("❌ 所有数据服务都不可用")
        data_service = None

# 导入高级预警服务
try:
    from services.advanced_alert_service import advanced_alert_service
    logger.info("✅ 高级预警服务导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 高级预警服务导入失败: {e}")
    advanced_alert_service = None

# 导入路由
try:
    from routers.market import router as market_router
    from routers.alerts import router as alerts_router
    from routers.websocket import router as websocket_router
    from routers.advanced_alerts import router as advanced_alerts_router
    
    # 注册路由
    app.include_router(market_router, prefix="/api/v1", tags=["市场数据"])
    app.include_router(alerts_router, prefix="/api/v1", tags=["基础预警"])
    app.include_router(advanced_alerts_router, prefix="/api/v1", tags=["高级预警"])
    app.include_router(websocket_router, prefix="/api/v1", tags=["实时数据"])
    
    logger.info("✅ 所有路由注册成功")
except ImportError as e:
    logger.error(f"❌ 路由导入失败: {e}")

# 最后挂载静态文件服务
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
    logger.info("🚀 启动寰宇多市场金融监控系统 专业版 v2.5...")
    
    # 异步初始化数据服务
    if data_service:
        asyncio.create_task(data_service.initialize())
        logger.info("✅ 数据服务异步初始化已启动")
    else:
        logger.warning("⚠️ 无数据服务可用")
    
    # 初始化高级预警服务
    if advanced_alert_service:
        await advanced_alert_service.initialize()
        logger.info("✅ 高级预警服务初始化完成")
        
        # 延迟启动预警监控（等待数据服务就绪）
        if data_service:
            async def delayed_alert_monitoring():
                await asyncio.sleep(20)  # 等待数据服务完全就绪
                await advanced_alert_service.start_monitoring(data_service)
                logger.info("✅ 高级预警监控已启动")
            
            asyncio.create_task(delayed_alert_monitoring())

if __name__ == "__main__":
    print("🚀 启动专业版寰宇多市场金融监控系统 v2.5")
    print("📊 服务将运行在: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔗 实时数据: ws://localhost:8000/ws/realtime")
    print("🌐 Web界面: http://localhost:8000/")
    print("🚨 高级预警: 价格监控 + 自动通知")
    print("💎 数据源: 真实交易所 + 模拟数据")
    print("🔧 版本: 2.5.0 (专业版 + 高级预警)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
