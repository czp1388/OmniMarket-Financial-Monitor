"""
LEAN引擎回测API端点
提供策略回测、状态查询和历史记录等功能的RESTful API
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from services.lean_backtest_service import (
    lean_service, BacktestRequest, BacktestResult, StrategyPerformance
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["LEAN引擎"])


class StartBacktestResponse(BaseModel):
    """启动回测响应"""
    backtest_id: str
    status: str
    message: str


class BacktestListResponse(BaseModel):
    """回测列表响应"""
    active_backtests: List[BacktestResult]
    historical_backtests: List[BacktestResult]


class StrategyTemplateResponse(BaseModel):
    """策略模板响应"""
    template_id: str
    name: str
    description: str
    parameters: List[dict]


@router.post("/backtest/start", response_model=StartBacktestResponse)
async def start_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks
):
    """
    启动新的策略回测
    
    参数:
    - strategy_id: 策略ID
    - strategy_code: 策略代码（如果使用模板，可以为空）
    - symbol: 交易标的（例如：AAPL）
    - start_date: 回测开始日期（YYYY-MM-DD）
    - end_date: 回测结束日期（YYYY-MM-DD）
    - initial_capital: 初始资金（默认10000）
    - parameters: 策略参数
    - data_source: 数据源（yfinance, alpha_vantage, akshare）
    """
    try:
        backtest_id = await lean_service.start_backtest(request)
        
        return StartBacktestResponse(
            backtest_id=backtest_id,
            status="started",
            message=f"回测已启动，ID: {backtest_id}"
        )
    except Exception as e:
        logger.error(f"启动回测失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动回测失败: {str(e)}")


@router.get("/backtest/status/{backtest_id}", response_model=BacktestResult)
async def get_backtest_status(backtest_id: str):
    """
    获取回测状态和结果
    """
    result = lean_service.get_backtest_status(backtest_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="回测不存在")
    
    return result


@router.get("/backtest/list", response_model=BacktestListResponse)
async def list_backtests(strategy_id: Optional[str] = None):
    """
    获取回测列表
    
    参数:
    - strategy_id: 可选，按策略ID过滤
    """
    historical = lean_service.get_all_backtests(strategy_id)
    active = list(lean_service.active_backtests.values())
    
    return BacktestListResponse(
        active_backtests=active,
        historical_backtests=historical
    )


@router.post("/backtest/cancel/{backtest_id}")
async def cancel_backtest(backtest_id: str):
    """
    取消正在运行的回测
    """
    success = lean_service.cancel_backtest(backtest_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="回测不存在或无法取消")
    
    return {"message": "回测已取消", "backtest_id": backtest_id}


@router.get("/strategies/templates")
async def get_strategy_templates():
    """
    获取可用的策略模板
    """
    templates = lean_service.get_strategy_templates()
    
    # 为每个模板提供描述
    template_descriptions = {
        "moving_average_crossover": {
            "name": "移动平均线交叉策略",
            "description": "基于快速和慢速移动平均线的交叉信号进行交易",
            "parameters": [
                {"name": "fast_period", "type": "int", "default": 10, "description": "快速移动平均线周期"},
                {"name": "slow_period", "type": "int", "default": 30, "description": "慢速移动平均线周期"}
            ]
        },
        "rsi_strategy": {
            "name": "RSI策略",
            "description": "基于相对强弱指数(RSI)的超买超卖信号进行交易",
            "parameters": [
                {"name": "rsi_period", "type": "int", "default": 14, "description": "RSI计算周期"},
                {"name": "oversold", "type": "float", "default": 30, "description": "超卖阈值"},
                {"name": "overbought", "type": "float", "default": 70, "description": "超买阈值"}
            ]
        },
        "mean_reversion": {
            "name": "均值回归策略",
            "description": "基于布林带指标的均值回归策略",
            "parameters": [
                {"name": "bb_period", "type": "int", "default": 20, "description": "布林带计算周期"},
                {"name": "std_dev", "type": "float", "default": 2.0, "description": "标准差倍数"}
            ]
        }
    }
    
    response = []
    for template_id in templates.keys():
        if template_id in template_descriptions:
            desc = template_descriptions[template_id]
            response.append({
                "template_id": template_id,
                "name": desc["name"],
                "description": desc["description"],
                "parameters": desc["parameters"]
            })
    
    return response


@router.post("/strategies/generate")
async def generate_strategy_from_template(
    template_id: str,
    symbol: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 10000.0,
    parameters: Optional[dict] = None
):
    """
    从模板生成策略代码
    """
    try:
        strategy_code = lean_service.create_strategy_from_template(
            template_id, symbol, start_date, end_date, initial_capital, parameters
        )
        
        return {
            "template_id": template_id,
            "strategy_code": strategy_code,
            "message": "策略代码生成成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"生成策略代码失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成策略代码失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    LEAN引擎健康检查
    """
    return {
        "status": "healthy",
        "service": "lean_backtest_service",
        "active_backtests": len(lean_service.active_backtests),
        "historical_backtests": len(lean_service.backtest_history)
    }
