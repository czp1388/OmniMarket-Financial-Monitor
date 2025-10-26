from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from app.routers import market 
 
app = FastAPI() 
 
app.add_middleware( 
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
) 
 
app.include_router(market.router, prefix="/api/v1", tags=["market"]) 
 
@app.get("/") 
async def root(): 
    return {"message": "寰宇多市场金融监控系统 API"} 
 
@app.get("/health") 
async def health_check(): 
    return {"status": "ok"} 
