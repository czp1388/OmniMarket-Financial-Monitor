from fastapi import APIRouter
from .endpoints import market_data, alerts, users, technical_indicators

# 创建主路由
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(market_data.router, prefix="/market", tags=["market-data"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(technical_indicators.router, prefix="/technical", tags=["technical-indicators"])
