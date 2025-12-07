"""
简化版 FastAPI 启动文件 - 只加载 API，不启动后台服务
用于测试助手模式 API 端点
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from api.routes import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """简化的生命周期管理 - 只初始化数据库"""
    logger.info("🚀 启动简化版后端服务...")
    logger.info("📦 初始化数据库连接...")
    try:
        await init_db()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.warning(f"⚠️  数据库连接失败: {e}，服务将继续运行")
    
    logger.info("✅ 服务启动完成！")
    logger.info(f"📍 API 地址: http://localhost:8000")
    logger.info(f"📚 API 文档: http://localhost:8000/docs")
    logger.info(f"🤖 助手模式 API: http://localhost:8000/api/v1/assistant")
    
    yield  # 应用运行期间
    
    logger.info("👋 关闭服务...")

# 创建 FastAPI 应用
app = FastAPI(
    title="OmniMarket Financial Monitor (简化版)",
    description="助手模式 API 测试服务",
    version="1.0.0-lite",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router, prefix="/api/v1")

# 根路径
@app.get("/")
async def root():
    return {
        "message": "OmniMarket Financial Monitor API (简化版)",
        "version": "1.0.0-lite",
        "status": "running",
        "docs": "/docs",
        "assistant_api": "/api/v1/assistant",
        "note": "这是用于测试助手模式 API 的简化版本"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
