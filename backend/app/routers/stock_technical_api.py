# A股技术指标API
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from services.enhanced_stock_cn_service import enhanced_stock_cn_service
from services.technical_indicators import technical_indicator_service
from models.market_data_interface import TimeFrame

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/technical/stock_cn", tags=["A股技术指标"])

@router.get("/{symbol}/indicators")
async def calculate_stock_indicators(
    symbol: str,
    timeframe: str = Query("1d", regex="^1m|5m|15m|1h|4h|1d|1w$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """计算A股技术指标"""
    try:
        # 转换时间框架
        tf_mapping = {
            "1m": TimeFrame.MIN1,
            "5m": TimeFrame.MIN5,
            "15m": TimeFrame.MIN15,
            "1h": TimeFrame.HOUR1,
            "4h": TimeFrame.HOUR4,
            "1d": TimeFrame.DAY1,
            "1w": TimeFrame.WEEK1
        }
        tf_enum = tf_mapping.get(timeframe, TimeFrame.DAY1)
        
        # 获取K线数据
        klines = await enhanced_stock_cn_service.get_klines(symbol, tf_enum, limit)
        if not klines:
            raise HTTPException(status_code=404, detail="未找到该股票的K线数据")
        
        # 计算技术指标
        indicators = technical_indicator_service.calculate_all_indicators(klines)
        
        return {
            "symbol": symbol,
            "market": "A股",
            "timeframe": timeframe,
            "data_count": len(klines),
            "indicators": indicators
        }
        
    except Exception as e:
        logger.error(f"计算A股技术指标异常: {e}")
        raise HTTPException(status_code=500, detail="计算技术指标失败")

@router.get("/screener")
async def stock_screener(
    industry: Optional[str] = Query(None, description="行业筛选"),
    area: Optional[str] = Query(None, description="地区筛选")
):
    """A股股票筛选器"""
    try:
        filters = {}
        if industry:
            filters["industry"] = industry
        if area:
            filters["area"] = area
            
        screened_stocks = await enhanced_stock_cn_service.get_stock_screener(filters)
        
        return {
            "market": "A股",
            "filters": filters,
            "stocks_count": len(screened_stocks),
            "stocks": screened_stocks
        }
        
    except Exception as e:
        logger.error(f"股票筛选异常: {e}")
        raise HTTPException(status_code=500, detail="股票筛选失败")

@router.get("/industry/{industry}/stocks")
async def get_industry_stocks(industry: str):
    """获取指定行业的股票列表"""
    try:
        stocks = await enhanced_stock_cn_service.get_industry_stocks(industry)
        
        return {
            "market": "A股",
            "industry": industry,
            "stocks_count": len(stocks),
            "stocks": stocks
        }
        
    except Exception as e:
        logger.error(f"获取行业股票列表异常: {e}")
        raise HTTPException(status_code=500, detail="获取行业股票列表失败")

@router.get("/{symbol}/analysis")
async def get_stock_technical_analysis(
    symbol: str,
    timeframe: str = Query("1d", regex="^1m|5m|15m|1h|4h|1d|1w$")
):
    """获取股票技术分析"""
    try:
        # 获取K线数据
        klines = await enhanced_stock_cn_service.get_klines(symbol, TimeFrame.DAY1, 50)
        if not klines:
            raise HTTPException(status_code=404, detail="未找到该股票的K线数据")
        
        # 提取价格数据
        closes = [kline["close_price"] for kline in klines]
        highs = [kline["high_price"] for kline in klines]
        lows = [kline["low_price"] for kline in klines]
        
        # 计算技术指标
        ma5 = technical_indicator_service.calculate_ma(closes, 5)
        ma20 = technical_indicator_service.calculate_ma(closes, 20)
        rsi = technical_indicator_service.calculate_rsi(closes)
        
        # 生成技术分析
        current_price = closes[-1] if closes else 0
        ma5_current = ma5[-1] if ma5 and ma5[-1] is not None else 0
        ma20_current = ma20[-1] if ma20 and ma20[-1] is not None else 0
        rsi_current = rsi[-1] if rsi and rsi[-1] is not None else 0
        
        # 技术信号
        signals = []
        if current_price > ma5_current and current_price > ma20_current:
            signals.append("价格在均线之上")
        elif current_price < ma5_current and current_price < ma20_current:
            signals.append("价格在均线之下")
            
        if rsi_current > 70:
            signals.append("RSI超买")
        elif rsi_current < 30:
            signals.append("RSI超卖")
        
        analysis = {
            "symbol": symbol,
            "current_price": current_price,
            "technical_indicators": {
                "MA5": ma5_current,
                "MA20": ma20_current,
                "RSI": rsi_current
            },
            "signals": signals,
            "trend": "上涨" if current_price > ma20_current else "下跌",
            "momentum": "强势" if rsi_current > 50 else "弱势"
        }
        
        return {
            "market": "A股",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"技术分析异常: {e}")
        raise HTTPException(status_code=500, detail="技术分析失败")
