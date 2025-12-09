from fastapi import APIRouter
from .endpoints import market_data, alerts, users, technical_indicators, virtual_trading, warrants_analysis, semi_auto_trading, auto_trading, warrants_monitoring, trading_analytics, lean_backtest, system_monitor, health, pattern_recognition, commodity, assistant_api, financial_reports

# 创建主路由
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(health.router, tags=["health"])  # 健康检查端点
api_router.include_router(assistant_api.router, tags=["assistant"])  # 🆕 助手模式API
api_router.include_router(financial_reports.router, tags=["financial-reports"])  # 🆕 财报分析API
api_router.include_router(market_data.router, prefix="/market", tags=["market-data"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(technical_indicators.router, prefix="/technical", tags=["technical-indicators"])
api_router.include_router(pattern_recognition.router, prefix="/patterns", tags=["pattern-recognition"])  # 形态识别
api_router.include_router(commodity.router, prefix="/commodity", tags=["commodity-futures"])  # 商品期货
api_router.include_router(virtual_trading.router, prefix="/virtual", tags=["virtual-trading"])
api_router.include_router(warrants_analysis.router, prefix="/warrants", tags=["warrants-analysis"])
api_router.include_router(semi_auto_trading.router, prefix="/semi-auto-trading", tags=["semi-auto-trading"])
api_router.include_router(auto_trading.router, prefix="/auto-trading", tags=["auto-trading"])
api_router.include_router(warrants_monitoring.router, prefix="/warrants-monitoring", tags=["warrants-monitoring"])
api_router.include_router(trading_analytics.router, prefix="/analytics", tags=["trading-analytics"])
api_router.include_router(lean_backtest.router, prefix="/lean", tags=["lean-engine"])
api_router.include_router(system_monitor.router, prefix="/system", tags=["system-monitor"])
