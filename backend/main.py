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
from backend.services.websocket_manager import WebSocketManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    logger.info("初始化数据库连接...")
    await init_db()
    
    # 启动数据服务
    logger.info("启动数据服务...")
    data_service = DataService()
    asyncio.create_task(data_service.start())
    
    yield  # 应用运行期间
    
    # 关闭时清理
    logger.info("关闭数据服务...")
    await data_service.stop()

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

# WebSocket管理器实例
websocket_manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息
            message = json.loads(data)
            await websocket_manager.handle_message(websocket, message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

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
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
