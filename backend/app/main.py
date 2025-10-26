from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import asyncio

# 添加当前目录到Python路径，修复导入问题
sys.path.append(os.path.dirname(__file__))

try:
    # 直接导入服务模块
    from services.data_service import data_service
    from services.alert_service import alert_service
    from routers.market import router as market_router
    from routers.alerts import router as alerts_router
    print("✅ 成功导入所有路由和服务")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    market_router = None
    alerts_router = None
    data_service = None
    alert_service = None

app = FastAPI(
    title="寰宇多市场金融监控系统",
    description="多市场金融数据实时监控平台 - MVP版本",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "寰宇多市场金融监控系统 API",
        "status": "运行中",
        "version": "1.1.0",
        "features": ["市场数据", "价格预警", "多交易所支持"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.now().isoformat()}

# 注册路由
if market_router:
    app.include_router(market_router, prefix="/api/v1", tags=["市场数据"])
    print("✅ 市场路由注册成功")

if alerts_router:
    app.include_router(alerts_router, prefix="/api/v1", tags=["预警管理"])
    print("✅ 预警路由注册成功")

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化服务"""
    print("🚀 初始化监控服务...")
    # 启动预警监控（在后台运行）
    if alerts_router and alert_service and data_service:
        asyncio.create_task(alert_service.start_monitoring(data_service))
        print("✅ 预警监控服务已启动")
    else:
        print("⚠️ 预警监控服务未启动，缺少依赖")

if __name__ == "__main__":
    print("🚀 启动寰宇多市场金融监控系统后端服务...")
    print("📊 服务将运行在: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔔 预警系统: 已启用")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)