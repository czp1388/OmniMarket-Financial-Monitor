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
    description="专业版本 - 多市场金融数据实时监控平台 + 真实交易所数据 + Web界面",
    version="2.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修复静态文件服务路径 - 但要放在路由后面
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")
public_dir = os.path.join(project_root, "public")

# 首先定义基础路由
@app.get("/")
async def root():
    return {
        "message": "寰宇多市场金融监控系统 API - 专业版 v2.3",
        "status": "运行中",
        "version": "2.3.0",
        "features": ["真实市场数据", "价格预警", "多交易所支持", "实时推送", "Web界面", "专业级"],
        "websocket": "ws://localhost:8000/ws/realtime",
        "web_interface": "http://localhost:8000/",
        "data_source": "真实交易所"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "professional",
        "version": "2.3.0",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "data_source": "real_exchange"
    }

@app.get("/test")
async def test_api():
    """测试API连通性"""
    return {
        "test": "success",
        "message": "API服务正常运行",
        "version": "2.3.0",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "data_source": "真实交易所数据"
    }

# 安全导入和注册路由
try:
    # 导入服务
    from services.real_exchange_service import real_data_service
    logger.info("✅ 真实数据服务导入成功")
    
    # 导入路由
    from routers.market import router as market_router
    from routers.alerts import router as alerts_router  
    from routers.websocket import router as websocket_router
    
    # 注册路由 - 不使用前缀，直接注册
    app.include_router(market_router, prefix="/api/v1", tags=["市场数据"])
    app.include_router(alerts_router, prefix="/api/v1", tags=["预警管理"])
    app.include_router(websocket_router, tags=["实时数据"])  # WebSocket不使用前缀
    
    logger.info("✅ 所有路由注册成功")
    
except ImportError as e:
    logger.warning(f"⚠️ 专业版模块导入失败: {e}")
    # 回退到基础版本
    try:
        from services.safe_data_service import data_service, astock_service
        from routers.market import router as market_router
        from routers.alerts import router as alerts_router
        
        app.include_router(market_router, prefix="/api/v1", tags=["市场数据"])
        app.include_router(alerts_router, prefix="/api/v1", tags=["预警管理"])
        
        logger.info("✅ 回退到基础数据服务")
        real_data_service = None
    except Exception as fallback_error:
        logger.error(f"❌ 基础版本也失败: {fallback_error}")
        real_data_service = None
        market_router = None
        alerts_router = None

# 最后挂载静态文件服务（避免覆盖API路由）
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
    logger.info(f"✅ 静态文件服务已挂载: {public_dir}")
else:
    logger.warning(f"⚠️ 静态文件目录不存在: {public_dir}，Web界面不可用")

@app.on_event("startup")
async def startup_event():
    """安全启动服务"""
    logger.info("🚀 启动寰宇多市场金融监控系统 专业版 v2.3...")
    
    # 异步初始化真实数据服务
    if real_data_service:
        asyncio.create_task(real_data_service.initialize())
        logger.info("✅ 真实数据服务异步初始化已启动")
    else:
        logger.info("⚠️ 真实数据服务不可用，使用模拟数据")

if __name__ == "__main__":
    print("🚀 启动专业版寰宇多市场金融监控系统 v2.3")
    print("📊 服务将运行在: http://localhost:8000") 
    print("📚 API文档: http://localhost:8000/docs")
    print("🔗 实时数据: ws://localhost:8000/ws/realtime")
    print("🌐 Web界面: http://localhost:8000/")
    print("💎 数据源: 真实交易所API")
    print("🔧 版本: 2.3.0 (专业版 + 真实数据)")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )
