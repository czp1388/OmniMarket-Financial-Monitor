from fastapi import FastAPI
import uvicorn
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "OmniMarket 简化版", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "omnimarket"}

if __name__ == "__main__":
    print("🚀 启动简化版服务...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
