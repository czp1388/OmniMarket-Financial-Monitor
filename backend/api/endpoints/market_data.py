from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.market_data import Kline, KlineCreate, TickerData, MarketType, Timeframe
from backend.services.data_service import DataService

router = APIRouter()

@router.get("/klines", response_model=List[Kline])
async def get_klines(
    symbol: str = Query(..., description="交易对符号，如 BTC/USDT"),
    market_type: MarketType = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    timeframe: Timeframe = Query(..., description="时间周期"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(1000, description="返回数据条数", ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """
    获取K线数据
    """
    try:
        data_service = DataService()
        klines = await data_service.get_klines(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return klines
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")

@router.get("/tickers")
async def get_tickers(
    symbols: Optional[List[str]] = Query(None, description="交易对符号列表"),
    market_type: Optional[str] = Query(None, description="市场类型，支持: stock, crypto, forex, futures, index, all"),
    exchange: Optional[str] = Query(None, description="交易所名称"),
    db: Session = Depends(get_db)
):
    """
    获取行情数据
    """
    try:
        # 处理 market_type 参数
        market_type_enum = None
        if market_type and market_type.lower() != "all":
            try:
                market_type_enum = MarketType(market_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无效的市场类型: {market_type}. 支持的类型: stock, crypto, forex, futures, index, all"
                )
        
        data_service = DataService()
        tickers = await data_service.get_tickers(
            symbols=symbols,
            market_type=market_type_enum,
            exchange=exchange
        )
        return tickers
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行情数据失败: {str(e)}")

@router.get("/symbols")
async def get_symbols(
    market_type: Optional[MarketType] = Query(None, description="市场类型"),
    exchange: Optional[str] = Query(None, description="交易所名称"),
    db: Session = Depends(get_db)
):
    """
    获取可交易符号列表
    """
    try:
        data_service = DataService()
        symbols = await data_service.get_symbols(
            market_type=market_type,
            exchange=exchange
        )
        return symbols
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取符号列表失败: {str(e)}")

@router.get("/exchanges")
async def get_exchanges():
    """
    获取支持的交易所列表
    """
    try:
        data_service = DataService()
        exchanges = await data_service.get_supported_exchanges()
        return exchanges
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易所列表失败: {str(e)}")

@router.get("/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="交易对符号"),
    market_type: MarketType = Query(..., description="市场类型"),
    exchange: str = Query(..., description="交易所名称"),
    depth: int = Query(20, description="深度数量", ge=1, le=100)
):
    """
    获取订单簿数据
    """
    try:
        data_service = DataService()
        orderbook = await data_service.get_orderbook(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            depth=depth
        )
        return orderbook
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单簿失败: {str(e)}")

@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    market_type: MarketType,
    exchange: str,
    timeframe: Timeframe,
    days: int = Query(30, description="历史天数", ge=1, le=365)
):
    """
    获取历史数据
    """
    try:
        data_service = DataService()
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        historical_data = await data_service.get_klines(
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe,
            start_time=start_time,
            end_time=end_time
        )
        return historical_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")

@router.get("/health")
async def health_check():
    """
    市场数据服务健康检查
    """
    return {
        "status": "healthy", 
        "service": "market-data",
        "timestamp": datetime.now().isoformat()
    }
