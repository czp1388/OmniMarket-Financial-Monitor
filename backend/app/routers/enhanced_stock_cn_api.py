# 增强版A股数据API路由
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging
from services.enhanced_stock_cn_service import enhanced_stock_cn_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/market/stock_cn_enhanced", tags=["A股数据-增强版"])

@router.get("/health")
async def enhanced_stock_cn_health():
    """增强版A股数据服务健康检查"""
    return {
        "service": "enhanced_stock_cn_data",
        "status": "healthy" if enhanced_stock_cn_service.is_initialized else "initializing",
        "market_type": "A股",
        "data_source": "enhanced_mock",
        "supported_stocks_count": len(await enhanced_stock_cn_service.get_stock_list())
    }

@router.get("/stocks")
async def get_enhanced_stock_list():
    """获取增强版股票列表"""
    try:
        stocks = await enhanced_stock_cn_service.get_stock_list()
        return {
            "market": "A股",
            "data_source": "enhanced",
            "stocks_count": len(stocks),
            "stocks": stocks
        }
    except Exception as e:
        logger.error(f"获取股票列表异常: {e}")
        raise HTTPException(status_code=500, detail="获取股票列表失败")

@router.get("/{symbol}/realtime")
async def get_enhanced_realtime(symbol: str):
    """获取增强版实时数据"""
    try:
        realtime_data = await enhanced_stock_cn_service.get_real_time_data(symbol)
        if not realtime_data:
            raise HTTPException(status_code=404, detail="未找到该股票实时数据")
        
        return {
            "symbol": symbol,
            "market": "A股",
            "data_source": realtime_data.get("data_source", "enhanced_mock"),
            "realtime": realtime_data
        }
    except Exception as e:
        logger.error(f"获取实时数据异常: {e}")
        raise HTTPException(status_code=500, detail="获取实时数据失败")

@router.get("/{symbol}/historical")
async def get_enhanced_historical(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="数据天数")
):
    """获取增强版历史数据"""
    try:
        historical_data = await enhanced_stock_cn_service.get_historical_data(symbol, days)
        if not historical_data:
            raise HTTPException(status_code=404, detail="未找到该股票历史数据")
        
        return {
            "symbol": symbol,
            "market": "A股",
            "days": days,
            "data_count": len(historical_data),
            "historical_data": historical_data
        }
    except Exception as e:
        logger.error(f"获取历史数据异常: {e}")
        raise HTTPException(status_code=500, detail="获取历史数据失败")

@router.get("/industry/{industry}")
async def get_industry_stocks(industry: str):
    """获取行业股票列表"""
    try:
        stocks = await enhanced_stock_cn_service.get_industry_stocks(industry)
        
        return {
            "market": "A股",
            "industry": industry,
            "stocks_count": len(stocks),
            "stocks": stocks
        }
    except Exception as e:
        logger.error(f"获取行业股票异常: {e}")
        raise HTTPException(status_code=500, detail="获取行业股票失败")

@router.get("/search/{keyword}")
async def search_stocks(keyword: str):
    """搜索股票"""
    try:
        results = await enhanced_stock_cn_service.search_stocks(keyword)
        
        return {
            "market": "A股",
            "keyword": keyword,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"搜索股票异常: {e}")
        raise HTTPException(status_code=500, detail="搜索股票失败")

@router.get("/market/overview")
async def get_enhanced_market_overview():
    """获取增强版市场概览"""
    try:
        # 模拟市场概览数据
        stocks = await enhanced_stock_cn_service.get_stock_list()
        industries = {}
        
        for stock in stocks:
            industry = stock["industry"]
            if industry not in industries:
                industries[industry] = 0
            industries[industry] += 1
        
        overview = {
            "total_stocks": len(stocks),
            "industry_distribution": industries,
            "market_status": "trading",  # 交易中
            "update_time": datetime.now().isoformat(),
            "featured_stocks": [
                {"symbol": "000001.SZ", "name": "平安银行", "change_percent": 1.5},
                {"symbol": "600036.SH", "name": "招商银行", "change_percent": 0.8},
                {"symbol": "600519.SH", "name": "贵州茅台", "change_percent": -0.3},
                {"symbol": "300750.SZ", "name": "宁德时代", "change_percent": 2.1}
            ]
        }
        
        return {
            "market": "A股",
            "data_source": "enhanced",
            "overview": overview
        }
    except Exception as e:
        logger.error(f"获取市场概览异常: {e}")
        raise HTTPException(status_code=500, detail="获取市场概览失败")
