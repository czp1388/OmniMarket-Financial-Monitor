"""
牛熊证分析引擎API端点
提供专业的风险分析、策略分析和模拟回测功能
集成高级风险分析服务
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
import logging

from backend.services.warrants_analysis_service import (
    warrants_analysis_service,
    WarrantAnalysis,
    RiskLevel,
    WarrantType
)
from backend.services.warrants_risk_analysis import (
    warrants_risk_analysis_service,
    WarrantsRiskAnalysisService
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["warrants-analysis"])


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


# 风险分析端点
@router.post("/risk-analysis/comprehensive")
async def comprehensive_risk_analysis(warrant_data: Dict):
    """
    综合风险分析
    使用高级风险分析服务进行全面的风险评估
    
    Args:
        warrant_data: 牛熊证数据
        
    Returns:
        Dict: 综合风险分析结果
    """
    try:
        analysis_result = warrants_risk_analysis_service.comprehensive_risk_analysis(warrant_data)
        return analysis_result
    except Exception as e:
        logger.error(f"综合风险分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"风险分析失败: {str(e)}")


@router.post("/risk-analysis/batch")
async def batch_risk_analysis(warrants_list: List[Dict]):
    """
    批量风险分析
    批量分析多个牛熊证的风险
    
    Args:
        warrants_list: 牛熊证数据列表
        
    Returns:
        List[Dict]: 批量分析结果
    """
    try:
        results = await warrants_risk_analysis_service.analyze_warrants_batch(warrants_list)
        return results
    except Exception as e:
        logger.error(f"批量风险分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量风险分析失败: {str(e)}")


@router.post("/risk-analysis/summary")
async def get_risk_summary(analysis_results: List[Dict]):
    """
    获取风险汇总统计
    根据分析结果生成风险汇总报告
    
    Args:
        analysis_results: 风险分析结果列表
        
    Returns:
        Dict: 风险汇总统计
    """
    try:
        summary = warrants_risk_analysis_service.get_risk_summary(analysis_results)
        return summary
    except Exception as e:
        logger.error(f"生成风险汇总失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"风险汇总生成失败: {str(e)}")


@router.get("/risk-analysis/knock-out-probability")
async def calculate_knock_out_probability(
    current_price: float,
    knock_out_price: float,
    volatility: float,
    time_to_expiry: int,
    warrant_type: str
):
    """
    计算触回收概率
    基于Black-Scholes模型的专业概率计算
    
    Args:
        current_price: 当前正股价格
        knock_out_price: 回收价
        volatility: 年化波动率
        time_to_expiry: 剩余到期天数
        warrant_type: 牛熊证类型 ('BULL' or 'BEAR')
        
    Returns:
        Dict: 触回收概率结果
    """
    try:
        probability = warrants_risk_analysis_service.calculate_knock_out_probability(
            current_price, knock_out_price, volatility, time_to_expiry, warrant_type
        )
        return {
            "knock_out_probability": probability,
            "interpretation": _get_probability_interpretation(probability)
        }
    except Exception as e:
        logger.error(f"触回收概率计算失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"概率计算失败: {str(e)}")


@router.get("/risk-analysis/time-decay")
async def calculate_time_decay(
    current_price: float,
    strike_price: float,
    time_to_expiry: int,
    interest_rate: float = 0.03,
    volatility: float = 0.3
):
    """
    计算时间价值衰减
    估算牛熊证时间价值衰减
    
    Args:
        current_price: 当前正股价格
        strike_price: 行使价
        time_to_expiry: 剩余到期天数
        interest_rate: 无风险利率
        volatility: 年化波动率
        
    Returns:
        Dict: 时间价值衰减分析
    """
    try:
        decay_analysis = warrants_risk_analysis_service.calculate_time_decay_estimate(
            current_price, strike_price, time_to_expiry, interest_rate, volatility
        )
        return decay_analysis
    except Exception as e:
        logger.error(f"时间价值衰减计算失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"时间衰减计算失败: {str(e)}")


@router.get("/risk-analysis/leverage")
async def analyze_leverage_effect(
    warrant_price: float,
    underlying_price: float,
    conversion_ratio: float,
    warrant_type: str
):
    """
    分析杠杆效应
    计算牛熊证的杠杆效应和风险
    
    Args:
        warrant_price: 牛熊证价格
        underlying_price: 正股价格
        conversion_ratio: 兑换比率
        warrant_type: 牛熊证类型
        
    Returns:
        Dict: 杠杆效应分析结果
    """
    try:
        leverage_analysis = warrants_risk_analysis_service.analyze_leverage_effect(
            warrant_price, underlying_price, conversion_ratio, warrant_type
        )
        return leverage_analysis
    except Exception as e:
        logger.error(f"杠杆效应分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"杠杆分析失败: {str(e)}")


@router.get("/risk-analysis/safety-margin")
async def calculate_safety_margin_advanced(
    current_price: float,
    knock_out_price: float,
    warrant_type: str,
    volatility: float
):
    """
    计算安全边际（高级版）
    使用波动率调整的安全边际计算
    
    Args:
        current_price: 当前正股价格
        knock_out_price: 回收价
        warrant_type: 牛熊证类型
        volatility: 波动率
        
    Returns:
        Dict: 安全边际分析结果
    """
    try:
        margin_analysis = warrants_risk_analysis_service.calculate_safety_margin(
            current_price, knock_out_price, warrant_type, volatility
        )
        return margin_analysis
    except Exception as e:
        logger.error(f"安全边际计算失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"安全边际计算失败: {str(e)}")


def _get_probability_interpretation(probability: float) -> str:
    """获取概率解释"""
    if probability >= 0.8:
        return "极高风险 - 随时可能触发回收"
    elif probability >= 0.6:
        return "高风险 - 很可能触发回收"
    elif probability >= 0.4:
        return "中等风险 - 可能触发回收"
    elif probability >= 0.2:
        return "低风险 - 不太可能触发回收"
    else:
        return "极低风险 - 几乎不可能触发回收"


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
