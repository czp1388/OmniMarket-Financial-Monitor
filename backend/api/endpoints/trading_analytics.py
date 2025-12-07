from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional
from services.trading_analytics_service import trading_analytics_service

router = APIRouter()

@router.get("/statistics")
async def get_trading_statistics():
    """获取交易统计数据"""
    try:
        statistics = await trading_analytics_service.get_trading_statistics()
        return {
            "success": True,
            "data": statistics,
            "message": "交易统计数据获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易统计数据失败: {str(e)}")

@router.get("/risk-metrics")
async def get_risk_metrics():
    """获取风险指标"""
    try:
        risk_metrics = await trading_analytics_service.calculate_risk_metrics()
        return {
            "success": True,
            "data": risk_metrics,
            "message": "风险指标获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取风险指标失败: {str(e)}")

@router.get("/performance")
async def get_performance_analysis():
    """获取绩效分析"""
    try:
        performance = await trading_analytics_service.get_performance_analysis()
        return {
            "success": True,
            "data": performance,
            "message": "绩效分析获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取绩效分析失败: {str(e)}")

@router.get("/report")
async def generate_trading_report():
    """生成交易报告"""
    try:
        report = await trading_analytics_service.generate_trading_report()
        return {
            "success": True,
            "data": report,
            "message": "交易报告生成成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成交易报告失败: {str(e)}")

@router.get("/trades")
async def get_trade_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    symbol: Optional[str] = None,
    strategy: Optional[str] = None,
    limit: int = 100
):
    """获取交易历史记录"""
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 获取交易数据
        trades = await trading_analytics_service.get_trade_history(
            start_date=start_dt,
            end_date=end_dt,
            symbol=symbol,
            strategy=strategy,
            limit=limit
        )
        
        return {
            "success": True,
            "data": trades,
            "message": "交易历史记录获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易历史记录失败: {str(e)}")

@router.get("/portfolio/value")
async def get_portfolio_value_history(
    days: int = 30
):
    """获取投资组合价值历史"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        portfolio_history = await trading_analytics_service.get_portfolio_value_history(
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": portfolio_history,
            "message": "投资组合价值历史获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取投资组合价值历史失败: {str(e)}")

@router.get("/portfolio-summary")
async def get_portfolio_summary():
    """获取投资组合摘要"""
    try:
        portfolio_summary = await trading_analytics_service.get_portfolio_summary()
        return {
            "success": True,
            "data": portfolio_summary,
            "message": "投资组合摘要获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取投资组合摘要失败: {str(e)}")

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """获取仪表板摘要数据"""
    try:
        # 获取交易统计数据
        statistics = await trading_analytics_service.get_trading_statistics()
        
        # 获取风险指标
        risk_metrics = await trading_analytics_service.calculate_risk_metrics()
        
        # 获取绩效分析
        performance = await trading_analytics_service.get_performance_analysis()
        
        # 获取最新的交易记录
        recent_trades = await trading_analytics_service.get_trade_history(limit=10)
        
        # 获取投资组合价值历史（最近7天）
        portfolio_history = await trading_analytics_service.get_portfolio_value_history(days=7)
        
        summary = {
            "trading_statistics": statistics,
            "risk_metrics": risk_metrics,
            "performance_analysis": performance,
            "recent_trades": recent_trades,
            "portfolio_history": portfolio_history,
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": summary,
            "message": "仪表板摘要数据获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表板摘要数据失败: {str(e)}")

@router.delete("/trades/reset")
async def reset_trading_data():
    """重置交易数据（用于测试和开发）"""
    try:
        await trading_analytics_service.reset_data()
        return {
            "success": True,
            "message": "交易数据重置成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置交易数据失败: {str(e)}")
