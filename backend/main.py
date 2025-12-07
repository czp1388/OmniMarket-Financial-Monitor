import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import uvicorn
from typing import List, Dict, Any
import json
import logging

from backend.config import settings
from backend.database import init_db
from backend.api.routes import api_router
from backend.services.data_service import DataService
from backend.services.alert_service import alert_service
from backend.services.websocket_manager import websocket_manager
from backend.services.warrants_monitoring_service import warrants_monitoring_service
from backend.services.data_quality_monitor import data_quality_monitor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    logger.info("初始化数据库连接...")
    await init_db()
    
    # 启动数据服务（使用全局实例）
    logger.info("启动数据服务...")
    from backend.services.data_service import data_service
    asyncio.create_task(data_service.start())
    
    # 启动预警服务
    logger.info("启动预警监控服务...")
    await alert_service.start_monitoring()
    
    # 启动WebSocket服务器
    logger.info("启动WebSocket服务器...")
    websocket_server = await websocket_manager.start_websocket_server()
    
    # 启动牛熊证监控服务
    logger.info("启动牛熊证监控服务...")
    await warrants_monitoring_service.initialize_monitoring()
    
    # 启动数据质量监控服务
    logger.info("启动数据质量监控服务...")
    asyncio.create_task(data_quality_monitor.start_monitoring())
    
    yield  # 应用运行期间
    
    # 关闭时清理
    logger.info("关闭数据服务...")
    try:
        await data_service.stop()
    except Exception as e:
        logger.warning(f"关闭数据服务时出错: {e}")
    
    logger.info("关闭WebSocket管理器...")
    try:
        await websocket_manager.stop()
    except Exception as e:
        logger.warning(f"关闭WebSocket管理器时出错: {e}")

# 创建FastAPI应用
app = FastAPI(
    title="OmniMarket Financial Monitor",
    description="寰宇多市场金融监控系统 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.register(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息
            message = json.loads(data)
            await websocket_manager.handle_message(websocket, message)
    except WebSocketDisconnect:
        await websocket_manager.unregister(websocket)

@app.get("/")
async def root():
    return {
        "message": "欢迎使用寰宇多市场金融监控系统",
        "version": "1.0.0",
        "status": "运行中"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-11-07T00:44:45Z"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
