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
    description="稳定版本 - 多市场金融数据实时监控平台 + 实时推送 + Web界面",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修复静态文件服务路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")
public_dir = os.path.join(project_root, "public")

if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
    logger.info(f"✅ 静态文件服务已挂载: {public_dir}")
else:
    logger.warning(f"⚠️ 静态文件目录不存在: {public_dir}，Web界面不可用")
    # 创建public目录
    os.makedirs(public_dir, exist_ok=True)
    logger.info(f"✅ 已创建静态文件目录: {public_dir}")

# 安全导入服务
try:
    from services.safe_data_service import data_service, astock_service
    from services.alert_service import alert_service
    from routers.market import router as market_router
    from routers.alerts import router as alerts_router
    from routers.websocket import router as websocket_router
    logger.info("✅ 所有模块导入成功")
except ImportError as e:
    logger.warning(f"⚠️ 部分模块导入失败: {e}")
    # 创建空服务确保应用能启动
    data_service = None
    astock_service = None  
    alert_service = None
    market_router = None
    alerts_router = None
    websocket_router = None

@app.get("/")
async def root():
    return {
        "message": "寰宇多市场金融监控系统 API - 稳定版 v2.2",
        "status": "运行中", 
        "version": "2.2.0",
        "features": ["市场数据", "价格预警", "多交易所支持", "实时推送", "Web界面", "稳定运行"],
        "websocket": "ws://localhost:8000/ws/realtime",
        "web_interface": "http://localhost:8000/"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "stable",
        "version": "2.2.0",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

@app.get("/test")
async def test_api():
    """测试API连通性"""
    return {
        "test": "success",
        "message": "API服务正常运行",
        "version": "2.2.0",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

# 注册路由
if market_router:
    app.include_router(market_router, prefix="/api/v1", tags=["市场数据"])
    logger.info("✅ 市场路由注册成功")

if alerts_router:
    app.include_router(alerts_router, prefix="/api/v1", tags=["预警管理"]) 
    logger.info("✅ 预警路由注册成功")

if websocket_router:
    app.include_router(websocket_router, prefix="/api/v1", tags=["实时数据"])
    logger.info("✅ WebSocket实时路由注册成功")

@app.on_event("startup")
async def startup_event():
    """安全启动服务"""
    logger.info("🚀 启动寰宇多市场金融监控系统 v2.2...")
    
    # 异步初始化数据服务（不阻塞启动）
    if data_service:
        asyncio.create_task(data_service.initialize())
        logger.info("✅ 数据服务异步初始化已启动")
    
    # 延迟启动预警监控
    if alert_service and data_service:
        async def delayed_monitoring():
            await asyncio.sleep(10)
            await alert_service.start_monitoring(data_service)
            logger.info("✅ 预警监控服务已启动")
        
        asyncio.create_task(delayed_monitoring())
    else:
        logger.info("⚠️ 预警监控服务未启用")

if __name__ == "__main__":
    print("🚀 启动稳定版寰宇多市场金融监控系统 v2.2")
    print("📊 服务将运行在: http://localhost:8000") 
    print("📚 API文档: http://localhost:8000/docs")
    print("🔗 实时数据: ws://localhost:8000/ws/realtime")
    print("🌐 Web界面: http://localhost:8000/")
    print("🔧 版本: 2.2.0 (稳定版 + 实时推送 + Web界面)")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )
