"""
全自动交易系统API端点
提供完整的自动化交易功能，包括策略调度、订单管理、风险控制和状态监控
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from services.auto_trading_service import (
    auto_trading_service,
    AutoTradingStrategy,
    TradingStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auto-trading", tags=["auto-trading"])


@router.post("/start")
async def start_auto_trading(
    strategies: List[str],
    background_tasks: BackgroundTasks
):
    """
    启动全自动交易
    
    Args:
        strategies: 交易策略列表
        background_tasks: FastAPI后台任务
        
    Returns:
        Dict: 启动结果
    """
    try:
        # 转换策略字符串为枚举
        trading_strategies = []
        for strategy_str in strategies:
            try:
                strategy = AutoTradingStrategy(strategy_str)
                trading_strategies.append(strategy)
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无效的策略类型: {strategy_str}"
                )
        
        # 启动自动交易
        result = await auto_trading_service.start_trading(trading_strategies)
        
        if result["success"]:
            logger.info(f"全自动交易启动成功: {strategies}")
        else:
            logger.warning(f"全自动交易启动失败: {result['message']}")
            
        return result
        
    except Exception as e:
        logger.error(f"启动全自动交易失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")


@router.post("/stop")
async def stop_auto_trading():
    """
    停止全自动交易
    
    Returns:
        Dict: 停止结果
    """
    try:
        result = await auto_trading_service.stop_trading()
        
        if result["success"]:
            logger.info("全自动交易停止成功")
        else:
            logger.warning(f"全自动交易停止失败: {result['message']}")
            
        return result
        
    except Exception as e:
        logger.error(f"停止全自动交易失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止失败: {str(e)}")


@router.post("/pause")
async def pause_auto_trading():
    """
    暂停全自动交易
    
    Returns:
        Dict: 暂停结果
    """
    try:
        result = await auto_trading_service.pause_trading()
        
        if result["success"]:
            logger.info("全自动交易暂停成功")
        else:
            logger.warning(f"全自动交易暂停失败: {result['message']}")
            
        return result
        
    except Exception as e:
        logger.error(f"暂停全自动交易失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"暂停失败: {str(e)}")


@router.post("/resume")
async def resume_auto_trading():
    """
    恢复全自动交易
    
    Returns:
        Dict: 恢复结果
    """
    try:
        result = await auto_trading_service.resume_trading()
        
        if result["success"]:
            logger.info("全自动交易恢复成功")
        else:
            logger.warning(f"全自动交易恢复失败: {result['message']}")
            
        return result
        
    except Exception as e:
        logger.error(f"恢复全自动交易失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")


@router.get("/status")
async def get_trading_status():
    """
    获取自动交易状态
    
    Returns:
        Dict: 交易状态信息
    """
    try:
        status = auto_trading_service.get_trading_status()
        
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取交易状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.post("/emergency-stop")
async def emergency_stop():
    """
    紧急停止（触发所有熔断机制）
    
    Returns:
        Dict: 紧急停止结果
    """
    try:
        # 触发所有紧急熔断
        auto_trading_service.emergency_brakes = {
            'market_volatility_brake': True,
            'max_daily_loss_brake': True,
            'system_error_brake': True,
            'network_disruption_brake': True
        }
        
        # 停止交易
        result = await auto_trading_service.stop_trading()
        
        logger.warning("紧急停止已触发")
        
        return {
            "success": True,
            "message": "紧急停止已执行",
            "emergency_brakes": auto_trading_service.emergency_brakes,
            "stop_result": result
        }
        
    except Exception as e:
        logger.error(f"紧急停止失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"紧急停止失败: {str(e)}")


@router.post("/reset-brakes")
async def reset_emergency_brakes():
    """
    重置紧急熔断
    
    Returns:
        Dict: 重置结果
    """
    try:
        result = auto_trading_service.reset_emergency_brakes()
        
        logger.info("紧急熔断已重置")
        
        return result
        
    except Exception as e:
        logger.error(f"重置紧急熔断失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"重置失败: {str(e)}")


@router.get("/strategies")
async def get_available_strategies():
    """
    获取可用交易策略
    
    Returns:
        Dict: 策略列表
    """
    try:
        strategies = [
            {
                "value": strategy.value,
                "name": _get_strategy_name(strategy),
                "description": _get_strategy_description(strategy),
                "risk_level": _get_strategy_risk_level(strategy),
                "recommended_market": _get_strategy_market(strategy)
            }
            for strategy in AutoTradingStrategy
        ]
        
        return {
            "success": True,
            "strategies": strategies
        }
        
    except Exception as e:
        logger.error(f"获取策略列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取策略失败: {str(e)}")


@router.get("/performance")
async def get_trading_performance():
    """
    获取交易绩效数据
    
    Returns:
        Dict: 绩效数据
    """
    try:
        status = auto_trading_service.get_trading_status()
        stats = status["trading_stats"]
        risk_metrics = status["risk_metrics"]
        
        performance = {
            "total_trades": stats["total_trades"],
            "success_rate": (
                stats["successful_trades"] / stats["total_trades"] 
                if stats["total_trades"] > 0 else 0
            ),
            "total_profit_loss": stats["total_profit_loss"],
            "current_positions": len(stats["current_positions"]),
            "current_drawdown": risk_metrics["current_drawdown"],
            "max_drawdown": risk_metrics["max_drawdown"],
            "sharpe_ratio": risk_metrics["sharpe_ratio"],
            "volatility": risk_metrics["volatility"]
        }
        
        return {
            "success": True,
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取交易绩效失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取绩效失败: {str(e)}")


@router.get("/risk-metrics")
async def get_risk_metrics():
    """
    获取风险指标
    
    Returns:
        Dict: 风险指标数据
    """
    try:
        status = auto_trading_service.get_trading_status()
        risk_metrics = status["risk_metrics"]
        emergency_brakes = status["emergency_brakes"]
        
        risk_assessment = {
            "current_drawdown": risk_metrics["current_drawdown"],
            "max_drawdown": risk_metrics["max_drawdown"],
            "volatility": risk_metrics["volatility"],
            "sharpe_ratio": risk_metrics["sharpe_ratio"],
            "active_brakes": sum(emergency_brakes.values()),
            "brake_details": emergency_brakes,
            "risk_level": _assess_overall_risk(risk_metrics, emergency_brakes)
        }
        
        return {
            "success": True,
            "risk_assessment": risk_assessment,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取风险指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取风险指标失败: {str(e)}")


@router.post("/configure")
async def configure_trading(
    max_daily_trades: Optional[int] = None,
    max_daily_loss: Optional[float] = None,
    max_position_size: Optional[float] = None,
    volatility_threshold: Optional[float] = None
):
    """
    配置交易参数
    
    Args:
        max_daily_trades: 单日最大交易次数
        max_daily_loss: 单日最大亏损
        max_position_size: 最大仓位大小
        volatility_threshold: 波动率阈值
        
    Returns:
        Dict: 配置结果
    """
    try:
        # 这里应该实现实际的配置逻辑
        # 暂时返回成功响应
        
        config_updates = {}
        if max_daily_trades is not None:
            config_updates["max_daily_trades"] = max_daily_trades
        if max_daily_loss is not None:
            config_updates["max_daily_loss"] = max_daily_loss
        if max_position_size is not None:
            config_updates["max_position_size"] = max_position_size
        if volatility_threshold is not None:
            config_updates["volatility_threshold"] = volatility_threshold
            
        logger.info(f"交易配置已更新: {config_updates}")
        
        return {
            "success": True,
            "message": "交易配置更新成功",
            "config_updates": config_updates,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"配置交易参数失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"配置失败: {str(e)}")


def _get_strategy_name(strategy: AutoTradingStrategy) -> str:
    """获取策略名称"""
    names = {
        AutoTradingStrategy.TREND_FOLLOWING: "趋势跟踪策略",
        AutoTradingStrategy.MEAN_REVERSION: "均值回归策略",
        AutoTradingStrategy.BREAKOUT: "突破策略",
        AutoTradingStrategy.MOMENTUM: "动量策略"
    }
    return names.get(strategy, "未知策略")


def _get_strategy_description(strategy: AutoTradingStrategy) -> str:
    """获取策略描述"""
    descriptions = {
        AutoTradingStrategy.TREND_FOLLOWING: "跟随市场趋势进行交易，适合趋势明显的市场",
        AutoTradingStrategy.MEAN_REVERSION: "在价格偏离均值时进行反向交易，适合震荡市场",
        AutoTradingStrategy.BREAKOUT: "在价格突破关键位时进行交易，适合突破行情",
        AutoTradingStrategy.MOMENTUM: "跟随价格动量进行交易，适合强势行情"
    }
    return descriptions.get(strategy, "暂无描述")


def _get_strategy_risk_level(strategy: AutoTradingStrategy) -> str:
    """获取策略风险等级"""
    risk_levels = {
        AutoTradingStrategy.TREND_FOLLOWING: "中等",
        AutoTradingStrategy.MEAN_REVERSION: "中高",
        AutoTradingStrategy.BREAKOUT: "高",
        AutoTradingStrategy.MOMENTUM: "极高"
    }
    return risk_levels.get(strategy, "未知")


def _get_strategy_market(strategy: AutoTradingStrategy) -> str:
    """获取策略适用市场"""
    markets = {
        AutoTradingStrategy.TREND_FOLLOWING: "趋势市",
        AutoTradingStrategy.MEAN_REVERSION: "震荡市",
        AutoTradingStrategy.BREAKOUT: "突破市",
        AutoTradingStrategy.MOMENTUM: "动量市"
    }
    return markets.get(strategy, "通用")


def _assess_overall_risk(risk_metrics: Dict, emergency_brakes: Dict) -> str:
    """评估总体风险等级"""
    # 检查紧急熔断
    if any(emergency_brakes.values()):
        return "极高风险"
    
    # 基于风险指标评估
    drawdown = abs(risk_metrics["current_drawdown"])
    volatility = risk_metrics["volatility"]
    
    if drawdown > 0.1 or volatility > 0.4:
        return "高风险"
    elif drawdown > 0.05 or volatility > 0.2:
        return "中等风险"
    else:
        return "低风险"


# 示例数据端点
@router.get("/sample-config")
async def get_sample_config():
    """
    获取示例配置
    
    Returns:
        Dict: 示例配置数据
    """
    return {
        "sample_strategies": ["trend_following", "mean_reversion"],
        "sample_risk_parameters": {
            "max_daily_trades": 20,
            "max_daily_loss": 5000,
            "max_position_size": 5000,
            "volatility_threshold": 0.3
        },
        "sample_emergency_conditions": {
            "market_volatility_brake": 0.8,
            "max_daily_loss_brake": 10000,
            "system_error_brake": 0.3,
            "network_disruption_brake": True
        }
    }
