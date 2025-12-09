"""
财报分析 API 端点
提供财务报表数据查询接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from services.financial_report_service import financial_report_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial-reports", tags=["财报分析"])


class FinancialReportResponse(BaseModel):
    """财报数据响应模型"""
    symbol: str
    companyName: str
    quarter: str
    revenue: float
    netIncome: float
    grossProfit: float
    operatingIncome: float
    eps: float
    totalAssets: float
    totalLiabilities: float
    totalEquity: float
    currentAssets: float
    currentLiabilities: float
    cash: float
    operatingCashFlow: float
    investingCashFlow: float
    financingCashFlow: float
    freeCashFlow: float
    revenueGrowth: float
    profitMargin: float
    grossMargin: float
    roe: float
    roa: float
    currentRatio: float
    debtToEquity: float
    peRatio: float
    pbRatio: float


class HistoricalDataResponse(BaseModel):
    """历史数据响应模型"""
    quarter: str
    revenue: float
    netIncome: float
    profitMargin: float
    grossMargin: float
    roe: float
    eps: float


@router.get("/", response_model=FinancialReportResponse)
async def get_financial_report(
    symbol: str = Query(..., description="股票代码，如 AAPL, MSFT, TSLA, GOOGL")
):
    """
    获取公司最新财报数据
    
    参数:
        symbol: 股票代码
    
    返回:
        完整的财报数据，包括利润表、资产负债表、现金流量表和财务比率
    """
    try:
        data = await financial_report_service.get_financial_report(symbol.upper())
        
        if not data:
            raise HTTPException(
                status_code=404, 
                detail=f"未找到股票代码 {symbol} 的财报数据"
            )
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取财报数据失败 ({symbol}): {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取财报数据失败: {str(e)}"
        )


@router.get("/historical", response_model=List[HistoricalDataResponse])
async def get_historical_data(
    symbol: str = Query(..., description="股票代码"),
    periods: int = Query(4, description="返回的季度数量，默认4个季度", ge=1, le=20)
):
    """
    获取历史财报数据
    
    参数:
        symbol: 股票代码
        periods: 返回的季度数量（1-20）
    
    返回:
        历史财报数据列表，按时间倒序排列
    """
    try:
        data = await financial_report_service.get_historical_data(symbol.upper(), periods)
        
        if not data:
            raise HTTPException(
                status_code=404, 
                detail=f"未找到股票代码 {symbol} 的历史数据"
            )
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取历史数据失败 ({symbol}): {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取历史数据失败: {str(e)}"
        )


@router.get("/search")
async def search_symbols(
    keyword: str = Query(..., description="搜索关键词")
):
    """
    搜索股票代码
    
    参数:
        keyword: 搜索关键词（公司名称或代码）
    
    返回:
        匹配的股票列表
    """
    # 简单的模拟实现
    mock_symbols = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "GOOGL", "name": "Alphabet Inc."},
        {"symbol": "TSLA", "name": "Tesla, Inc."},
        {"symbol": "AMZN", "name": "Amazon.com, Inc."},
        {"symbol": "META", "name": "Meta Platforms, Inc."},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co."}
    ]
    
    keyword_lower = keyword.lower()
    results = [
        s for s in mock_symbols 
        if keyword_lower in s['symbol'].lower() or keyword_lower in s['name'].lower()
    ]
    
    return results
