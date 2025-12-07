"""
商品期货API端点
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from pydantic import BaseModel, Field

from services.commodity_data_service import commodity_data_service
from services.data_service import data_service
from models.market_data import MarketType, Timeframe

router = APIRouter()


class CommodityInfo(BaseModel):
    """商品信息"""
    symbol: str
    name: str
    yahoo_symbol: str


class CommodityQuote(BaseModel):
    """商品报价"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str


@router.get(
    "/commodities/list",
    response_model=List[CommodityInfo],
    summary="获取支持的商品列表",
    description="返回系统支持的所有商品期货品种"
)
async def get_supported_commodities():
    """获取支持的商品期货列表"""
    try:
        commodities = commodity_data_service.get_supported_commodities()
        return commodities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商品列表失败: {str(e)}")


@router.get(
    "/commodities/{symbol}/quote",
    response_model=Optional[CommodityQuote],
    summary="获取商品实时报价",
    description="获取指定商品的实时价格、涨跌幅等信息"
)
async def get_commodity_quote(
    symbol: str = Path(..., description="商品代码,如 GC(黄金)、CL(原油)")
):
    """获取商品实时报价"""
    try:
        quote = await commodity_data_service.get_commodity_quote(symbol)
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"未找到商品 {symbol} 的报价数据")
        
        # 转换时间戳为ISO格式字符串
        quote['timestamp'] = quote['timestamp'].isoformat()
        
        return quote
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商品报价失败: {str(e)}")


@router.get(
    "/commodities/{symbol}/klines",
    summary="获取商品K线数据",
    description="获取指定商品的历史K线数据"
)
async def get_commodity_klines(
    symbol: str = Path(..., description="商品代码"),
    timeframe: Timeframe = Query(Timeframe.D1, description="时间周期"),
    limit: int = Query(100, ge=1, le=1000, description="数据条数")
):
    """获取商品K线数据"""
    try:
        klines = await data_service.get_klines(
            symbol=symbol,
            market_type=MarketType.COMMODITY,
            exchange="commodity",
            timeframe=timeframe,
            limit=limit
        )
        
        if not klines:
            raise HTTPException(status_code=404, detail=f"未找到商品 {symbol} 的K线数据")
        
        # 转换为字典格式
        result = []
        for kline in klines:
            result.append({
                "timestamp": kline.timestamp.isoformat(),
                "open": kline.open,
                "high": kline.high,
                "low": kline.low,
                "close": kline.close,
                "volume": kline.volume
            })
        
        return {
            "symbol": symbol,
            "timeframe": timeframe.value,
            "total_count": len(result),
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商品K线数据失败: {str(e)}")


@router.get(
    "/commodities/categories",
    summary="获取商品分类",
    description="返回商品按类别分组的信息"
)
async def get_commodity_categories():
    """获取商品分类"""
    try:
        all_commodities = commodity_data_service.get_supported_commodities()
        
        # 根据名称进行分类
        categories = {
            "能源": [],
            "贵金属": [],
            "工业金属": [],
            "农产品": []
        }
        
        for commodity in all_commodities:
            name = commodity['name']
            if any(keyword in name for keyword in ['原油', '天然气']):
                categories["能源"].append(commodity)
            elif any(keyword in name for keyword in ['黄金', '白银', '铂金', '钯金']):
                categories["贵金属"].append(commodity)
            elif any(keyword in name for keyword in ['铜', '铝']):
                categories["工业金属"].append(commodity)
            elif any(keyword in name for keyword in ['玉米', '小麦', '大豆', '棉花', '糖', '咖啡']):
                categories["农产品"].append(commodity)
        
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商品分类失败: {str(e)}")
