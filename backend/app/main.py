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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "寰宇多市场金融监控系统 API", "status": "运行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 注册路由
if market_router:
    app.include_router(market_router, prefix="/api/v1", tags=["市场数据"])
    print("✅ 市场路由注册成功")
else:
    print("⚠️ 市场路由未注册")

if __name__ == "__main__":
    print("🚀 启动寰宇多市场金融监控系统后端服务...")
    print("📊 服务将运行在: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)