"""
助手模式API - 为零基础用户设计的接口
隐藏所有技术细节，用白话和用户沟通

核心原则：
1. 无专业术语 - 用户听得懂的语言
2. 目标导向 - 关注用户想要什么，而非技术参数
3. 行动建议 - 告诉用户该做什么,而非展示数据
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid
from sqlalchemy.orm import Session

from database import get_db
from models.assistant import StrategyInstance, ExecutionHistory, SimpleReport
from services.intent_service import (
    intent_service,
    UserGoal,
    RiskTolerance,
    InvestmentHorizon
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["智能助手"])


# ==================== 请求/响应模型 ====================

class ActivateStrategyRequest(BaseModel):
    """激活策略包请求"""
    user_goal: str = Field(
        ...,
        description="用户投资目标：stable_growth(稳健增长) | aggressive_growth(进取增长) | income_focus(收益优先) | capital_preservation(资本保值)"
    )
    risk_tolerance: str = Field(
        ...,
        description="风险承受度：low(保守) | medium(平衡) | high(激进)"
    )
    investment_amount: float = Field(
        ...,
        gt=0,
        description="投资金额（元）"
    )
    investment_horizon: Optional[str] = Field(
        None,
        description="投资期限：short_term(< 1年) | medium_term(1-3年) | long_term(> 3年)"
    )
    auto_execute: bool = Field(
        False,
        description="是否自动执行交易（当前版本仅虚拟交易）"
    )


class StrategyPackageResponse(BaseModel):
    """策略包响应"""
    strategy_package_id: str
    friendly_name: str
    status: str
    explanation: Dict[str, Any]
    underlying_strategy: Dict[str, Any]
    monitoring: Dict[str, Any]


class PackageListItem(BaseModel):
    """策略包列表项"""
    package_id: str
    friendly_name: str
    icon: str
    tagline: str
    description: str
    risk_score: int
    expected_return: str
    suitable_for: List[str]


class MarketOpportunity(BaseModel):
    """市场机会"""
    opportunity_id: str
    title: str
    explanation: str
    suggestion: str
    risk_level: str
    potential_return: str
    action_button: str
    related_package_id: Optional[str] = None


# ==================== API端点 ====================

@router.post("/strategies/activate", response_model=StrategyPackageResponse)
async def activate_strategy_package(
    request: ActivateStrategyRequest,
    db: Session = Depends(get_db)
):
    """
    激活策略包 - 用户点击"开始定投"等按钮的入口
    
    这个接口完全隐藏技术细节，用户看到的是：
    - "稳健增长定投宝"
    - "预期年化8-12%"
    - "风险：低 - 像定期存款"
    
    示例请求：
    ```json
    {
        "user_goal": "stable_growth",
        "risk_tolerance": "low",
        "investment_amount": 5000,
        "investment_horizon": "long_term",
        "auto_execute": false
    }
    ```
    """
    try:
        # 1. 验证输入参数
        try:
            user_goal = UserGoal(request.user_goal)
            risk_tolerance = RiskTolerance(request.risk_tolerance)
            investment_horizon = (
                InvestmentHorizon(request.investment_horizon)
                if request.investment_horizon
                else InvestmentHorizon.MEDIUM_TERM
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"参数错误: {str(e)}"
            )
        
        # 2. 将用户意图翻译为策略参数
        translation = intent_service.translate_user_intent(
            user_goal=user_goal,
            risk_tolerance=risk_tolerance,
            investment_amount=request.investment_amount,
            investment_horizon=investment_horizon
        )
        
        package = translation["package"]
        
        # 3. 创建策略实例
        instance_id = f"inst_{uuid.uuid4().hex[:12]}"
        
        strategy_instance = StrategyInstance(
            instance_id=instance_id,
            user_id=1,  # TODO: 从JWT token获取真实用户ID
            package_id=package.package_id,
            friendly_name=package.friendly_name,
            strategy_id=package.strategy_id,
            user_goal=request.user_goal,
            risk_tolerance=request.risk_tolerance,
            investment_amount=request.investment_amount,
            investment_horizon=request.investment_horizon or "medium_term",
            strategy_parameters=package.parameters,
            status="active",
            auto_execute=request.auto_execute,
            initial_capital=request.investment_amount,
            current_value=request.investment_amount,
            total_invested=request.investment_amount,
            next_execution_time=datetime.utcnow() + timedelta(days=7)
        )
        
        db.add(strategy_instance)
        db.commit()
        db.refresh(strategy_instance)
        
        logger.info(
            f"策略包激活成功: {package.package_id}, "
            f"实例ID: {instance_id}, "
            f"用户目标: {user_goal}, "
            f"风险偏好: {risk_tolerance}"
        )
        
        # 4. 返回用户友好的响应
        return StrategyPackageResponse(
            strategy_package_id=instance_id,
            friendly_name=package.friendly_name,
            status="activated",
            explanation=translation["user_explanation"],
            underlying_strategy={
                "strategy_id": package.strategy_id,
                "parameters": package.parameters
            },
            monitoring={
                "next_check": _calculate_next_check_date(),
                "notification_channel": "钉钉 + 应用内",
                "instance_id": instance_id,
                "status_url": f"/api/v1/assistant/strategies/running/{instance_id}"
            }
        )
        
    except Exception as e:
        logger.error(f"激活策略包失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"激活策略失败: {str(e)}"
        )


@router.get("/strategies/packages", response_model=List[PackageListItem])
async def list_strategy_packages(
    user_goal: Optional[str] = Query(None, description="筛选目标"),
    risk_tolerance: Optional[str] = Query(None, description="筛选风险偏好")
):
    """
    获取所有可用策略包
    
    返回格式：
    ```json
    [
        {
            "package_id": "stable_growth_low_risk",
            "friendly_name": "稳健增长定投宝",
            "icon": "🛡️",
            "tagline": "睡得着的投资",
            "description": "适合长期投资，波动小，回撤可控",
            "risk_score": 2,
            "expected_return": "8-12% 年化",
            "suitable_for": ["月光族", "稳健型", "长期投资"]
        }
    ]
    ```
    """
    try:
        # 获取所有策略包
        if user_goal and risk_tolerance:
            # 推荐模式
            packages = intent_service.recommend_packages(
                user_goal=UserGoal(user_goal),
                risk_tolerance=RiskTolerance(risk_tolerance)
            )
            return [
                PackageListItem(**pkg.to_dict())
                for pkg in packages
            ]
        else:
            # 列表模式
            packages = intent_service.get_all_packages()
            return [
                PackageListItem(**pkg)
                for pkg in packages
            ]
    
    except Exception as e:
        logger.error(f"获取策略包列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取策略包失败: {str(e)}"
        )


@router.get("/strategies/packages/{package_id}")
async def get_package_detail(package_id: str):
    """
    获取策略包详情
    
    返回完整的策略包信息，包括：
    - 白话说明
    - 历史表现
    - 风险提示
    - 适用人群
    """
    package = intent_service.get_package_by_id(package_id)
    
    if not package:
        raise HTTPException(
            status_code=404,
            detail=f"策略包 {package_id} 不存在"
        )
    
    return {
        **package.to_dict(),
        "detailed_description": _generate_detailed_description(package),
        "faq": _generate_faq(package),
        "historical_performance": {
            "message": "历史数据仅供参考，不代表未来表现",
            "backtest_required": True
        }
    }


@router.get("/opportunities", response_model=List[MarketOpportunity])
async def get_market_opportunities(
    user_goal: Optional[str] = Query(None, description="用户目标"),
    limit: int = Query(5, ge=1, le=20, description="返回数量")
):
    """
    获取市场机会
    
    返回通俗易懂的市场机会，例如：
    - "黄金避险需求上升"
    - "科技股回调，是定投好时机"
    - "美元走弱，考虑配置人民币资产"
    """
    # TODO: 这里应该连接真实的市场分析服务
    # 当前返回模拟数据
    opportunities = [
        MarketOpportunity(
            opportunity_id="opp_001",
            title="市场出现回调机会",
            explanation="标普500指数最近回调3%，历史数据显示这是定投的好时机",
            suggestion="可考虑启动'稳健增长定投宝'策略，分批买入",
            risk_level="低",
            potential_return="预计未来6个月有8-12%收益空间",
            action_button="立即定投",
            related_package_id="stable_growth_low_risk"
        ),
        MarketOpportunity(
            opportunity_id="opp_002",
            title="黄金避险需求上升",
            explanation="国际局势紧张，黄金作为避险资产表现活跃",
            suggestion="可将5-10%资金配置到黄金ETF",
            risk_level="低",
            potential_return="短期波动较大，但长期保值",
            action_button="了解详情",
            related_package_id="capital_preservation_low_risk"
        ),
        MarketOpportunity(
            opportunity_id="opp_003",
            title="科技股超卖信号",
            explanation="纳斯达克RSI指标显示超卖，可能迎来反弹",
            suggestion="适合进取型投资者，快进快出",
            risk_level="高",
            potential_return="短期可能有15-25%收益，但波动大",
            action_button="谨慎参与",
            related_package_id="aggressive_growth_high_risk"
        )
    ]
    
    return opportunities[:limit]


@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """
    获取助手模式仪表盘摘要
    
    返回：
    - 今日待办事项
    - 账户概况（虚拟）
    - 市场机会数
    - 策略运行状态
    """
    return {
        "greeting": f"早上好！今天是 {datetime.now().strftime('%Y年%m月%d日')}",
        "today_actions": [
            {
                "type": "opportunity",
                "title": "市场出现机会",
                "description": "标普500回调3%，是定投好时机",
                "priority": "medium",
                "action_text": "定投500元"
            },
            {
                "type": "profit",
                "title": "收益到账",
                "description": "稳健增长策略本月盈利680元",
                "priority": "low",
                "action_text": "查看详情"
            }
        ],
        "account_summary": {
            "total_assets": 50000,
            "today_profit": 320,
            "total_profit": 5680,
            "profit_rate": 11.36,
            "message": "这是虚拟账户，不涉及真实资金"
        },
        "active_strategies": [
            {
                "package_id": "stable_growth_low_risk",
                "friendly_name": "稳健增长定投宝",
                "status": "running",
                "days_active": 45,
                "profit": 2340
            }
        ],
        "market_opportunities_count": 3,
        "notifications": [
            {
                "type": "info",
                "message": "您的策略运行正常，继续保持",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }


@router.post("/goals/update")
async def update_user_goal(
    user_goal: str,
    risk_tolerance: str,
    investment_amount: float
):
    """
    更新用户目标
    
    用户可以随时调整投资目标和风险偏好
    """
    try:
        # 验证参数
        UserGoal(user_goal)
        RiskTolerance(risk_tolerance)
        
        # TODO: 保存到用户配置表
        
        return {
            "status": "success",
            "message": "投资目标已更新",
            "new_recommendations": intent_service.recommend_packages(
                user_goal=UserGoal(user_goal),
                risk_tolerance=RiskTolerance(risk_tolerance)
            )
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"参数错误: {str(e)}"
        )


@router.get("/strategies/running/{instance_id}")
async def get_running_status(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """
    获取策略运行状态
    
    返回：
    - 当前账户价值
    - 累计收益
    - 下次操作时间和动作
    - 权益曲线数据
    """
    instance = db.query(StrategyInstance).filter(
        StrategyInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=404,
            detail=f"策略实例 {instance_id} 不存在"
        )
    
    # 获取最近执行历史
    recent_executions = db.query(ExecutionHistory).filter(
        ExecutionHistory.instance_id == instance_id
    ).order_by(ExecutionHistory.execution_time.desc()).limit(10).all()
    
    # 生成权益曲线数据
    equity_curve = _generate_equity_curve(instance, recent_executions)
    
    # 计算下次操作
    next_action = _calculate_next_action(instance)
    
    return {
        "instance_id": instance.instance_id,
        "friendly_name": instance.friendly_name,
        "status": instance.status,
        "account_summary": {
            "initial_capital": instance.initial_capital,
            "current_value": instance.current_value,
            "total_invested": instance.total_invested,
            "total_profit": instance.total_profit,
            "profit_rate": instance.profit_rate,
            "plain_text": f"您的投资正在{'稳健' if instance.profit_rate > 0 else '调整中'}增长，目前收益率{instance.profit_rate:.2f}%"
        },
        "next_action": next_action,
        "equity_curve": equity_curve,
        "recent_activities": [
            {
                "date": exec.execution_time.strftime("%Y-%m-%d"),
                "action": exec.action,
                "amount": exec.amount,
                "explanation": exec.plain_explanation
            }
            for exec in recent_executions
        ],
        "days_active": (datetime.utcnow() - instance.activated_at).days,
        "execution_count": instance.total_executions
    }


@router.get("/strategies/report/{instance_id}")
async def get_progress_report(
    instance_id: str,
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    db: Session = Depends(get_db)
):
    """
    获取进度报告（周报/月报）
    
    返回：
    - 本周/本月核心数据
    - 目标进度
    - 本周亮点
    - 下周建议
    """
    instance = db.query(StrategyInstance).filter(
        StrategyInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=404,
            detail=f"策略实例 {instance_id} 不存在"
        )
    
    # 查找或生成最新报告
    report = db.query(SimpleReport).filter(
        SimpleReport.instance_id == instance_id,
        SimpleReport.report_type == period
    ).order_by(SimpleReport.generated_at.desc()).first()
    
    if not report:
        # 生成新报告
        report = _generate_report(instance, period, db)
    
    return {
        "report_id": report.report_id,
        "period": report.report_type,
        "period_range": {
            "start": report.period_start.strftime("%Y-%m-%d"),
            "end": report.period_end.strftime("%Y-%m-%d")
        },
        "core_data": {
            "total_invested": report.total_invested,
            "total_return": report.total_return,
            "return_rate": report.return_rate,
            "account_value": report.account_value,
            "plain_summary": f"本{'周' if period == 'weekly' else '月'}投入 ¥{report.total_invested:.0f}，"
                            f"收益 ¥{report.total_return:.0f}，"
                            f"收益率 {report.return_rate:.2f}%"
        },
        "progress": {
            "target_amount": report.target_amount or instance.initial_capital * 1.2,
            "current_amount": report.account_value,
            "progress_percent": report.current_progress or (report.account_value / (instance.initial_capital * 1.2) * 100)
        },
        "highlights": report.highlights or _generate_default_highlights(instance),
        "next_suggestion": {
            "text": report.next_week_suggestion or "继续保持定投节奏，不要被短期波动影响",
            "action_date": report.next_action_date.strftime("%Y-%m-%d") if report.next_action_date else None,
            "suggested_amount": report.next_action_amount
        }
    }


@router.post("/strategies/{instance_id}/pause")
async def pause_strategy(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """暂停策略"""
    instance = db.query(StrategyInstance).filter(
        StrategyInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="策略实例不存在")
    
    instance.status = "paused"
    db.commit()
    
    return {"status": "success", "message": "策略已暂停"}


@router.post("/strategies/{instance_id}/resume")
async def resume_strategy(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """恢复策略"""
    instance = db.query(StrategyInstance).filter(
        StrategyInstance.instance_id == instance_id
    ).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="策略实例不存在")
    
    instance.status = "active"
    db.commit()
    
    return {"status": "success", "message": "策略已恢复"}


# ==================== 辅助函数 ====================

def _calculate_next_check_date() -> str:
    """计算下次检查日期"""
    next_check = datetime.now() + timedelta(days=7)
    return next_check.strftime("%Y年%m月%d日")


def _generate_equity_curve(instance: StrategyInstance, executions: List[ExecutionHistory]) -> List[Dict]:
    """生成权益曲线"""
    curve_data = []
    
    # 起点
    curve_data.append({
        "date": instance.activated_at.strftime("%Y-%m-%d"),
        "value": instance.initial_capital
    })
    
    # 中间点（基于执行历史）
    for exec in reversed(executions):
        if exec.account_value_after:
            curve_data.append({
                "date": exec.execution_time.strftime("%Y-%m-%d"),
                "value": exec.account_value_after
            })
    
    # 当前点
    curve_data.append({
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "value": instance.current_value
    })
    
    return curve_data


def _calculate_next_action(instance: StrategyInstance) -> Dict:
    """计算下次操作"""
    if instance.next_execution_time:
        return {
            "date": instance.next_execution_time.strftime("%Y-%m-%d"),
            "type": "定投买入",
            "amount": instance.initial_capital * 0.1,  # 默认10%
            "reason": "根据定投策略，每周固定买入",
            "plain_text": f"下次操作：{instance.next_execution_time.strftime('%m月%d日')} 买入约 ¥{instance.initial_capital * 0.1:.0f}"
        }
    else:
        return {
            "date": None,
            "type": "等待中",
            "amount": 0,
            "reason": "策略暂停或已完成",
            "plain_text": "当前无待执行操作"
        }


def _generate_report(instance: StrategyInstance, period: str, db: Session) -> SimpleReport:
    """生成新报告"""
    period_start = datetime.utcnow() - timedelta(days=7 if period == "weekly" else 30)
    period_end = datetime.utcnow()
    
    report = SimpleReport(
        report_id=f"rpt_{uuid.uuid4().hex[:12]}",
        instance_id=instance.instance_id,
        report_type=period,
        period_start=period_start,
        period_end=period_end,
        total_invested=instance.total_invested,
        total_return=instance.total_profit,
        return_rate=instance.profit_rate,
        account_value=instance.current_value,
        target_amount=instance.initial_capital * 1.2,
        current_progress=(instance.current_value / (instance.initial_capital * 1.2)) * 100,
        highlights=_generate_default_highlights(instance),
        next_week_suggestion="继续保持定投，市场波动是正常的",
        next_action_date=datetime.utcnow() + timedelta(days=7),
        next_action_amount=instance.initial_capital * 0.1
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


def _generate_default_highlights(instance: StrategyInstance) -> List[Dict]:
    """生成默认亮点"""
    return [
        {
            "title": "本周投入",
            "value": f"¥{instance.initial_capital * 0.1:.0f}",
            "icon": "💰",
            "trend": "up"
        },
        {
            "title": "累计收益",
            "value": f"¥{instance.total_profit:.0f}",
            "icon": "📈",
            "trend": "up" if instance.total_profit > 0 else "down"
        },
        {
            "title": "收益率",
            "value": f"{instance.profit_rate:.2f}%",
            "icon": "🎯",
            "trend": "up" if instance.profit_rate > 0 else "down"
        },
        {
            "title": "执行次数",
            "value": f"{instance.total_executions}次",
            "icon": "⚡",
            "trend": "neutral"
        }
    ]


def _generate_detailed_description(package) -> str:
    """生成详细说明"""
    return f"""
## {package.friendly_name}

{package.description}

### 适合人群
{', '.join(package.suitable_for)}

### 工作原理
{package.analogy}

### 历史表现
- 预期年化收益：{package.expected_return}
- 最大回撤：{package.max_drawdown}
- 风险评级：{package.risk_score}/5

### 注意事项
1. 历史表现不代表未来收益
2. 市场有风险，投资需谨慎
3. 建议长期持有，不要频繁操作
4. 当前为虚拟交易，不涉及真实资金
"""


def _generate_faq(package) -> List[Dict[str, str]]:
    """生成常见问题"""
    return [
        {
            "question": "这个策略安全吗？",
            "answer": f"风险等级：{package.risk_score}/5。{package.description}"
        },
        {
            "question": "需要多少钱开始？",
            "answer": "建议最低投入5000元，可根据风险偏好调整"
        },
        {
            "question": "多久能看到收益？",
            "answer": f"历史数据显示，{package.expected_return}。建议长期持有（至少6个月）"
        },
        {
            "question": "会亏损吗？",
            "answer": f"有可能。历史最大回撤约{package.max_drawdown}，但长期来看是向上的"
        },
        {
            "question": "可以随时停止吗？",
            "answer": "可以。您随时可以暂停或调整策略"
        }
    ]
