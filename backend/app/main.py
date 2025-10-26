from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# 添加当前目录到Python路径，修复导入问题
sys.path.append(os.path.dirname(__file__))

try:
    from routers.market import router as market_router
    print("✅ 成功导入市场路由")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    market_router = None

app = FastAPI(
    title="寰宇多市场金融监控系统",
    description="多市场金融数据实时监控平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（如果成功导入）
if market_router:
    app.include_router(market_router, prefix="/api/v1", tags=["market"])
    print("✅ 市场路由注册成功")
else:
    print("⚠️  市场路由未注册")

@app.get("/")
async def root():
    return {
        "message": "欢迎使用寰宇多市场金融监控系统",
        "status": "运行正常",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动寰宇多市场金融监控系统后端服务...")
    print("📊 服务将运行在: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
