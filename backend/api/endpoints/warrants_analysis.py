"""
牛熊证分析引擎API端点
提供专业的风险分析、策略分析和模拟回测功能
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
import logging

from services.warrants_analysis_service import (
    warrants_analysis_service,
    WarrantAnalysis,
    RiskLevel,
    WarrantType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/warrants-analysis", tags=["warrants-analysis"])


@router.post("/analyze-single", response_model=WarrantAnalysis)
async def analyze_single_warrant(
    warrant_data: Dict,
    underlying_data: List[Dict],
    market_conditions: Optional[Dict] = None
):
    """
    分析单只牛熊证风险
    
    Args:
        warrant_data: 牛熊证数据
        underlying_data: 正股历史数据
        market_conditions: 市场条件
        
    Returns:
        WarrantAnalysis: 分析结果
    """
    try:
        analysis = warrants_analysis_service.analyze_warrant_risk(
            warrant_data, underlying_data, market_conditions or {}
        )
        return analysis
    except Exception as e:
        logger.error(f"分析单只牛熊证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/analyze-batch", response_model=List[WarrantAnalysis])
async def analyze_batch_warrants(
    warrants_data: List[Dict],
    underlying_data_dict: Dict[str, List[Dict]]
):
    """
    批量分析牛熊证
    
    Args:
        warrants_data: 牛熊证数据列表
        underlying_data_dict: 正股数据字典 {code: data_list}
        
    Returns:
        List[WarrantAnalysis]: 分析结果列表
    """
    try:
        analyses = warrants_analysis_service.batch_analyze_warrants(
            warrants_data, underlying_data_dict
        )
        return analyses
    except Exception as e:
        logger.error(f"批量分析牛熊证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")


@router.post("/backtest")
async def backtest_strategy(
    strategy_type: str,
    historical_data: Dict[str, List[Dict]],
    initial_capital: float = 100000
):
    """
    策略回测
    
    Args:
        strategy_type: 策略类型
        historical_data: 历史数据
        initial_capital: 初始资金
        
    Returns:
        Dict: 回测结果
    """
    try:
        result = warrants_analysis_service.backtest_strategy(
            strategy_type, historical_data, initial_capital
        )
        return result
    except Exception as e:
        logger.error(f"策略回测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"回测失败: {str(e)}")


@router.get("/risk-assessment")
async def assess_risk_level(
    distance_to_knock_out: float,
    probability_knock_out: float,
    effective_leverage: float
):
    """
    评估风险等级
    
    Args:
        distance_to_knock_out: 距回收价幅度(%)
        probability_knock_out: 触回收概率(%)
        effective_leverage: 有效杠杆
        
    Returns:
        Dict: 风险等级信息
    """
    try:
        risk_level = warrants_analysis_service._assess_risk_level(
            distance_to_knock_out, probability_knock_out, effective_leverage
        )
        
        return {
            "risk_level": risk_level.value,
            "description": _get_risk_description(risk_level),
            "recommendation": _get_risk_recommendation(risk_level)
        }
    except Exception as e:
        logger.error(f"风险评估失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"风险评估失败: {str(e)}")


@router.get("/safety-margin")
async def calculate_safety_margin(
    distance_to_knock_out: float,
    probability_knock_out: float,
    effective_leverage: float
):
    """
    计算安全边际
    
    Args:
        distance_to_knock_out: 距回收价幅度(%)
        probability_knock_out: 触回收概率(%)
        effective_leverage: 有效杠杆
        
    Returns:
        Dict: 安全边际信息
    """
    try:
        safety_margin = warrants_analysis_service._calculate_safety_margin(
            distance_to_knock_out, probability_knock_out, effective_leverage
        )
        
        return {
            "safety_margin": safety_margin,
            "safety_level": _get_safety_level(safety_margin),
            "interpretation": _get_safety_interpretation(safety_margin)
        }
    except Exception as e:
        logger.error(f"安全边际计算失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"安全边际计算失败: {str(e)}")


@router.post("/trading-signal")
async def generate_trading_signal(
    warrant_data: Dict,
    underlying_data: List[Dict]
):
    """
    生成交易信号
    
    Args:
        warrant_data: 牛熊证数据
        underlying_data: 正股历史数据
        
    Returns:
        Dict: 交易信号信息
    """
    try:
        # 计算必要参数
        warrant_type = WarrantType.BULL if warrant_data.get('type') == 'bull' else WarrantType.BEAR
        underlying_price = warrant_data.get('underlying_price', 0)
        knock_out_price = warrant_data.get('knock_out_price', 0)
        
        # 计算距回收价幅度
        if warrant_type == WarrantType.BULL:
            distance_to_knock_out = ((knock_out_price - underlying_price) / underlying_price) * 100
        else:
            distance_to_knock_out = ((underlying_price - knock_out_price) / underlying_price) * 100
        
        # 计算触回收概率
        probability_knock_out = warrants_analysis_service._calculate_knock_out_probability(
            underlying_data, knock_out_price, warrant_type, warrant_data.get('expiry_date')
        )
        
        # 计算有效杠杆
        effective_leverage = warrants_analysis_service._calculate_effective_leverage(
            warrant_data, underlying_data
        )
        
        # 计算安全边际
        safety_margin = warrants_analysis_service._calculate_safety_margin(
            distance_to_knock_out, probability_knock_out, effective_leverage
        )
        
        # 评估风险等级
        risk_level = warrants_analysis_service._assess_risk_level(
            distance_to_knock_out, probability_knock_out, effective_leverage
        )
        
        # 生成交易信号
        trading_signal, signal_strength = warrants_analysis_service._generate_trading_signal(
            warrant_data, underlying_data, distance_to_knock_out,
            probability_knock_out, safety_margin, risk_level
        )
        
        return {
            "trading_signal": trading_signal,
            "signal_strength": signal_strength,
            "risk_level": risk_level.value,
            "safety_margin": safety_margin,
            "distance_to_knock_out": distance_to_knock_out,
            "probability_knock_out": probability_knock_out,
            "effective_leverage": effective_leverage
        }
    except Exception as e:
        logger.error(f"交易信号生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"交易信号生成失败: {str(e)}")


def _get_risk_description(risk_level: RiskLevel) -> str:
    """获取风险等级描述"""
    descriptions = {
        RiskLevel.LOW: "低风险 - 距回收价较远，触回收概率较低",
        RiskLevel.MEDIUM: "中等风险 - 需要关注价格波动",
        RiskLevel.HIGH: "高风险 - 距回收价较近，建议谨慎操作",
        RiskLevel.EXTREME: "极高风险 - 随时可能触发回收，建议立即处理"
    }
    return descriptions.get(risk_level, "未知风险等级")


def _get_risk_recommendation(risk_level: RiskLevel) -> str:
    """获取风险等级建议"""
    recommendations = {
        RiskLevel.LOW: "可以考虑建仓或持有",
        RiskLevel.MEDIUM: "建议密切关注，设置止损",
        RiskLevel.HIGH: "建议减仓或设置严格止损",
        RiskLevel.EXTREME: "强烈建议立即平仓或对冲"
    }
    return recommendations.get(risk_level, "暂无建议")


def _get_safety_level(safety_margin: float) -> str:
    """获取安全等级"""
    if safety_margin >= 0.7:
        return "非常安全"
    elif safety_margin >= 0.5:
        return "相对安全"
    elif safety_margin >= 0.3:
        return "需要注意"
    else:
        return "危险"


def _get_safety_interpretation(safety_margin: float) -> str:
    """获取安全边际解释"""
    if safety_margin >= 0.7:
        return "投资安全边际很高，风险可控"
    elif safety_margin >= 0.5:
        return "投资安全边际良好，需要关注市场变化"
    elif safety_margin >= 0.3:
        return "投资安全边际较低，建议谨慎操作"
    else:
        return "投资安全边际极低，建议避免或立即处理"


# 示例数据端点
@router.get("/sample-data")
async def get_sample_data():
    """
    获取示例数据用于测试
    """
    return {
        "sample_warrant": {
            "code": "12345.HK",
            "type": "bull",
            "price": 0.25,
            "strike_price": 180.0,
            "knock_out_price": 200.0,
            "underlying": "00700.HK",
            "underlying_price": 185.5,
            "expiry_date": "2025-06-30",
            "conversion_ratio": 100
        },
        "sample_underlying_data": [
            {"date": "2025-11-01", "close": 182.0},
            {"date": "2025-11-02", "close": 183.5},
            {"date": "2025-11-03", "close": 184.0},
            {"date": "2025-11-04", "close": 185.0},
            {"date": "2025-11-05", "close": 185.5},
            {"date": "2025-11-06", "close": 186.0},
            {"date": "2025-11-07", "close": 185.8},
            {"date": "2025-11-08", "close": 186.2},
            {"date": "2025-11-09", "close": 185.5},
            {"date": "2025-11-10", "close": 186.0}
        ]
    }
