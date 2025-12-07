"""
意图理解服务 - 双模架构的大脑
将用户目标翻译为技术参数，让零基础用户也能使用专业量化引擎

核心理念：
- 用户说"想稳定赚钱" → 系统翻译为 RSI定投策略 + 低风险参数
- 用户说"追求高收益" → 系统翻译为 趋势追踪 + 高仓位配置
- 所有技术细节对用户透明
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UserGoal(str, Enum):
    """用户投资目标 - 用白话定义"""
    STABLE_GROWTH = "stable_growth"              # 稳健增长
    AGGRESSIVE_GROWTH = "aggressive_growth"      # 进取增长
    INCOME_FOCUS = "income_focus"                # 收益优先
    CAPITAL_PRESERVATION = "capital_preservation"  # 资本保值
    WEALTH_ACCUMULATION = "wealth_accumulation"  # 财富积累


class RiskTolerance(str, Enum):
    """风险承受度"""
    LOW = "low"        # 保守型 - 不能接受大幅波动
    MEDIUM = "medium"  # 平衡型 - 可接受适度波动
    HIGH = "high"      # 激进型 - 追求高收益，接受高风险


class InvestmentHorizon(str, Enum):
    """投资期限"""
    SHORT_TERM = "short_term"    # 短期（< 1年）
    MEDIUM_TERM = "medium_term"  # 中期（1-3年）
    LONG_TERM = "long_term"      # 长期（> 3年）


class StrategyPackage:
    """策略包 - 预配置的策略组合"""
    
    def __init__(
        self,
        package_id: str,
        friendly_name: str,
        icon: str,
        tagline: str,
        description: str,
        strategy_id: str,
        parameters: Dict[str, Any],
        expected_return: str,
        max_drawdown: str,
        suitable_for: List[str],
        analogy: str,
        risk_score: int
    ):
        self.package_id = package_id
        self.friendly_name = friendly_name
        self.icon = icon
        self.tagline = tagline
        self.description = description
        self.strategy_id = strategy_id
        self.parameters = parameters
        self.expected_return = expected_return
        self.max_drawdown = max_drawdown
        self.suitable_for = suitable_for
        self.analogy = analogy
        self.risk_score = risk_score
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "package_id": self.package_id,
            "friendly_name": self.friendly_name,
            "icon": self.icon,
            "tagline": self.tagline,
            "description": self.description,
            "strategy_id": self.strategy_id,
            "parameters": self.parameters,
            "expected_return": self.expected_return,
            "max_drawdown": self.max_drawdown,
            "suitable_for": self.suitable_for,
            "analogy": self.analogy,
            "risk_score": self.risk_score
        }


class IntentService:
    """意图理解服务 - 将用户意图转化为策略参数"""
    
    def __init__(self):
        self.strategy_packages = self._initialize_strategy_packages()
    
    def _initialize_strategy_packages(self) -> Dict[str, StrategyPackage]:
        """初始化策略包库"""
        packages = {}
        
        # 1. 稳健增长 + 低风险 = RSI定投策略
        packages["stable_growth_low_risk"] = StrategyPackage(
            package_id="stable_growth_low_risk",
            friendly_name="稳健增长定投宝",
            icon="🛡️",
            tagline="睡得着的投资",
            description="适合长期投资，波动小，回撤可控。就像定期存款，但收益更好",
            strategy_id="rsi_strategy",  # 使用RSI超卖买入策略
            parameters={
                "rsi_period": 14,
                "rsi_overbought": 70,
                "rsi_oversold": 30,
                "stop_loss": 0.05,      # 5%止损
                "take_profit": 0.15     # 15%止盈
            },
            expected_return="8-12% 年化",
            max_drawdown="< 15%",
            suitable_for=["月光族", "稳健型", "长期投资", "养老规划"],
            analogy="就像超市促销时多买，平时少买，长期成本更低",
            risk_score=2
        )
        
        # 2. 稳健增长 + 中风险 = 均线交叉策略
        packages["stable_growth_medium_risk"] = StrategyPackage(
            package_id="stable_growth_medium_risk",
            friendly_name="稳健趋势跟随",
            icon="📈",
            tagline="顺势而为",
            description="跟随市场趋势，涨时持有，跌时离场",
            strategy_id="moving_average_crossover",
            parameters={
                "fast_period": 10,
                "slow_period": 30,
                "stop_loss": 0.08,
                "take_profit": 0.20
            },
            expected_return="12-18% 年化",
            max_drawdown="< 20%",
            suitable_for=["平衡型", "中长期投资", "追求稳定收益"],
            analogy="像冲浪，顺着浪头前进，浪退了就先上岸",
            risk_score=3
        )
        
        # 3. 进取增长 + 高风险 = 趋势突破策略
        packages["aggressive_growth_high_risk"] = StrategyPackage(
            package_id="aggressive_growth_high_risk",
            friendly_name="趋势追踪器",
            icon="🚀",
            tagline="追风口，抓热点",
            description="追踪热点，收益高但波动大。适合风险承受力强的投资者",
            strategy_id="moving_average_crossover",
            parameters={
                "fast_period": 5,
                "slow_period": 20,
                "stop_loss": 0.10,
                "take_profit": 0.30
            },
            expected_return="20-40% 年化",
            max_drawdown="< 30%",
            suitable_for=["进取型", "追求高收益", "风险承受力强", "短期投资"],
            analogy="像追风口，抓住热点快进快出",
            risk_score=4
        )
        
        # 4. 资本保值 + 低风险 = 防守型策略
        packages["capital_preservation_low_risk"] = StrategyPackage(
            package_id="capital_preservation_low_risk",
            friendly_name="资本守护者",
            icon="🏦",
            tagline="守住本金最重要",
            description="优先保护本金，收益其次。适合退休人士或风险厌恶者",
            strategy_id="rsi_strategy",
            parameters={
                "rsi_period": 21,
                "rsi_overbought": 65,
                "rsi_oversold": 35,
                "stop_loss": 0.03,      # 3%严格止损
                "take_profit": 0.10     # 10%适度止盈
            },
            expected_return="5-8% 年化",
            max_drawdown="< 10%",
            suitable_for=["退休人士", "风险厌恶", "保守型", "短期闲钱"],
            analogy="像银行理财，本金安全是第一位的",
            risk_score=1
        )
        
        # 5. 收益优先 + 中高风险 = 波段操作策略
        packages["income_focus_medium_risk"] = StrategyPackage(
            package_id="income_focus_medium_risk",
            friendly_name="波段捕手",
            icon="🎯",
            tagline="高抛低吸，频繁操作",
            description="利用市场波动，频繁买卖赚取差价",
            strategy_id="mean_reversion",
            parameters={
                "lookback_period": 20,
                "entry_threshold": 1.5,
                "exit_threshold": 0.5,
                "stop_loss": 0.06,
                "take_profit": 0.12
            },
            expected_return="15-25% 年化",
            max_drawdown="< 25%",
            suitable_for=["有经验投资者", "追求高频收益", "可承受波动"],
            analogy="像倒买倒卖，低价买进高价卖出",
            risk_score=3
        )
        
        return packages
    
    def translate_user_intent(
        self,
        user_goal: UserGoal,
        risk_tolerance: RiskTolerance,
        investment_amount: float,
        investment_horizon: Optional[InvestmentHorizon] = None
    ) -> Dict[str, Any]:
        """
        将用户意图转化为策略包
        
        Args:
            user_goal: 用户投资目标
            risk_tolerance: 风险承受度
            investment_amount: 投资金额
            investment_horizon: 投资期限（可选）
        
        Returns:
            包含策略包、回测请求和用户解释的字典
        """
        # 根据目标和风险偏好选择策略包
        package_key = f"{user_goal}_{risk_tolerance}_risk"
        
        if package_key not in self.strategy_packages:
            # 降级到默认稳健策略
            logger.warning(f"策略包 {package_key} 不存在，使用默认策略")
            package_key = "stable_growth_low_risk"
        
        package = self.strategy_packages[package_key]
        
        # 根据投资期限调整回测周期
        if investment_horizon:
            start_date, end_date = self._calculate_backtest_period(investment_horizon)
        else:
            # 默认使用1年回测
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        return {
            "package": package.to_dict(),
            "backtest_request": {
                "strategy_id": package.strategy_id,
                "symbol": self._select_default_symbol(user_goal),
                "initial_capital": investment_amount,
                "parameters": package.parameters,
                "start_date": start_date,
                "end_date": end_date
            },
            "user_explanation": self._generate_explanation(package, investment_amount)
        }
    
    def _calculate_backtest_period(self, horizon: InvestmentHorizon) -> tuple:
        """根据投资期限计算回测周期"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        if horizon == InvestmentHorizon.SHORT_TERM:
            days = 180  # 6个月
        elif horizon == InvestmentHorizon.MEDIUM_TERM:
            days = 730  # 2年
        else:
            days = 1095  # 3年
        
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return start_date, end_date
    
    def _select_default_symbol(self, user_goal: UserGoal) -> str:
        """根据用户目标选择默认品种"""
        symbol_map = {
            UserGoal.STABLE_GROWTH: "SPY",           # 标普500 - 稳健
            UserGoal.AGGRESSIVE_GROWTH: "QQQ",       # 纳斯达克100 - 成长
            UserGoal.INCOME_FOCUS: "IWM",            # 罗素2000 - 小盘股
            UserGoal.CAPITAL_PRESERVATION: "TLT",    # 长期国债 - 避险
            UserGoal.WEALTH_ACCUMULATION: "SPY"      # 标普500 - 积累
        }
        return symbol_map.get(user_goal, "SPY")
    
    def _generate_explanation(
        self, 
        package: StrategyPackage,
        investment_amount: float
    ) -> Dict[str, Any]:
        """生成白话解释"""
        return {
            "what_it_does": package.description,
            "expected_outcome": (
                f"历史表现：{package.expected_return}，"
                f"最大回撤{package.max_drawdown}"
            ),
            "risk_level": self._translate_risk(package.risk_score),
            "analogy": package.analogy,
            "investment_tip": self._generate_investment_tip(
                package.risk_score,
                investment_amount
            ),
            "next_steps": [
                "系统会每月自动检查市场机会",
                "发现好时机会通过您设置的渠道通知您",
                "您可以随时暂停或调整策略",
                "所有操作都是虚拟交易，不涉及真实资金"
            ]
        }
    
    def _translate_risk(self, risk_score: int) -> str:
        """风险等级翻译"""
        risk_map = {
            1: "极低风险 - 像定期存款，几乎不会亏损",
            2: "低风险 - 像货币基金，偶有小幅波动",
            3: "中风险 - 像股票基金，有起伏但长期向上",
            4: "中高风险 - 像成长股，波动较大但潜力高",
            5: "高风险 - 像创业，可能大赚也可能亏损"
        }
        return risk_map.get(risk_score, "中风险")
    
    def _generate_investment_tip(
        self,
        risk_score: int,
        investment_amount: float
    ) -> str:
        """生成投资建议"""
        if risk_score <= 2:
            return f"建议投入闲钱的50-80%（即 {investment_amount * 0.5:.0f}-{investment_amount * 0.8:.0f}元），其余保留应急资金"
        elif risk_score == 3:
            return f"建议投入闲钱的30-50%（即 {investment_amount * 0.3:.0f}-{investment_amount * 0.5:.0f}元），分散风险"
        else:
            return f"建议仅投入可承受损失的资金（建议不超过 {investment_amount * 0.3:.0f}元），切勿孤注一掷"
    
    def get_all_packages(self) -> List[Dict[str, Any]]:
        """获取所有可用策略包"""
        return [pkg.to_dict() for pkg in self.strategy_packages.values()]
    
    def get_package_by_id(self, package_id: str) -> Optional[StrategyPackage]:
        """根据ID获取策略包"""
        return self.strategy_packages.get(package_id)
    
    def recommend_packages(
        self,
        user_goal: UserGoal,
        risk_tolerance: RiskTolerance
    ) -> List[StrategyPackage]:
        """推荐适合的策略包"""
        recommended = []
        
        for package in self.strategy_packages.values():
            # 匹配目标
            if user_goal.value in package.package_id:
                recommended.append(package)
            # 匹配风险偏好
            elif risk_tolerance.value in package.package_id:
                recommended.append(package)
        
        # 按风险评分排序
        recommended.sort(key=lambda x: x.risk_score)
        
        return recommended[:3]  # 返回最多3个推荐


# 全局单例
intent_service = IntentService()
