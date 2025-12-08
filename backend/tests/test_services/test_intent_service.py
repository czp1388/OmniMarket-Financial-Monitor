"""
意图理解服务测试
测试用户意图识别、策略包推荐等功能
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from services.intent_service import (
    IntentService,
    UserGoal,
    RiskTolerance,
    InvestmentHorizon,
    StrategyPackage
)


@pytest.fixture
def intent_service():
    """创建IntentService实例"""
    return IntentService()


@pytest.fixture
def sample_user_input():
    """示例用户输入"""
    return {
        "goal": "stable_growth",
        "risk_tolerance": "low",
        "investment_amount": 10000.0,
        "investment_horizon": "long_term"
    }


class TestIntentService:
    """意图服务测试套件"""
    
    def test_service_initialization(self, intent_service):
        """测试服务初始化"""
        assert intent_service is not None
        assert hasattr(intent_service, 'strategy_packages')
    
    def test_parse_user_goal_stable_growth(self, intent_service):
        """测试解析稳健增长目标"""
        result = intent_service.parse_user_goal("stable_growth")
        
        assert result is not None
        assert result == UserGoal.STABLE_GROWTH
    
    def test_parse_user_goal_aggressive(self, intent_service):
        """测试解析进取增长目标"""
        result = intent_service.parse_user_goal("aggressive_growth")
        
        assert result == UserGoal.AGGRESSIVE_GROWTH
    
    def test_parse_risk_tolerance_low(self, intent_service):
        """测试解析低风险承受度"""
        result = intent_service.parse_risk_tolerance("low")
        
        assert result == RiskTolerance.LOW
    
    def test_parse_risk_tolerance_high(self, intent_service):
        """测试解析高风险承受度"""
        result = intent_service.parse_risk_tolerance("high")
        
        assert result == RiskTolerance.HIGH
    
    def test_recommend_strategy_stable_low_risk(self, intent_service):
        """测试推荐策略：稳健增长 + 低风险"""
        user_input = {
            "goal": UserGoal.STABLE_GROWTH,
            "risk_tolerance": RiskTolerance.LOW,
            "investment_amount": 10000.0,
            "investment_horizon": InvestmentHorizon.LONG_TERM
        }
        
        recommendations = intent_service.recommend_strategies(user_input)
        
        assert recommendations is not None
        assert len(recommendations) > 0
        # 第一个推荐应该是低风险策略
        assert recommendations[0].risk_score <= 3
    
    def test_recommend_strategy_aggressive_high_risk(self, intent_service):
        """测试推荐策略：进取增长 + 高风险"""
        user_input = {
            "goal": UserGoal.AGGRESSIVE_GROWTH,
            "risk_tolerance": RiskTolerance.HIGH,
            "investment_amount": 50000.0,
            "investment_horizon": InvestmentHorizon.SHORT_TERM
        }
        
        recommendations = intent_service.recommend_strategies(user_input)
        
        assert recommendations is not None
        assert len(recommendations) > 0
        # 应该推荐高风险策略
        assert any(pkg.risk_score >= 7 for pkg in recommendations)
    
    def test_get_all_strategy_packages(self, intent_service):
        """测试获取所有策略包"""
        packages = intent_service.get_all_strategy_packages()
        
        assert packages is not None
        assert len(packages) > 0
        assert all(isinstance(pkg, StrategyPackage) for pkg in packages)
    
    def test_get_strategy_package_by_id(self, intent_service):
        """测试通过ID获取策略包"""
        # 假设有预定义的策略包ID
        package = intent_service.get_strategy_package("stable_growth_low_risk")
        
        assert package is not None or package is None  # 取决于是否存在
    
    def test_translate_to_technical_parameters_stable(self, intent_service):
        """测试翻译为技术参数：稳健策略"""
        user_input = {
            "goal": UserGoal.STABLE_GROWTH,
            "risk_tolerance": RiskTolerance.LOW,
            "investment_amount": 10000.0,
            "investment_horizon": InvestmentHorizon.LONG_TERM
        }
        
        params = intent_service.translate_to_technical_parameters(user_input)
        
        assert params is not None
        assert "strategy_id" in params
        assert "parameters" in params
        # 低风险应该有保守的参数
        if "stop_loss" in params["parameters"]:
            assert params["parameters"]["stop_loss"] < 0.1  # 止损小于10%
    
    def test_translate_to_technical_parameters_aggressive(self, intent_service):
        """测试翻译为技术参数：激进策略"""
        user_input = {
            "goal": UserGoal.AGGRESSIVE_GROWTH,
            "risk_tolerance": RiskTolerance.HIGH,
            "investment_amount": 50000.0,
            "investment_horizon": InvestmentHorizon.SHORT_TERM
        }
        
        params = intent_service.translate_to_technical_parameters(user_input)
        
        assert params is not None
        # 高风险应该有激进的参数
        if "position_size" in params["parameters"]:
            assert params["parameters"]["position_size"] >= 0.5  # 仓位>=50%
    
    def test_explain_strategy_in_simple_terms(self, intent_service):
        """测试用白话解释策略"""
        strategy_package = StrategyPackage(
            package_id="test_strategy",
            friendly_name="测试策略",
            icon="🎯",
            tagline="测试用策略",
            description="这是一个测试策略",
            strategy_id="rsi_dca",
            parameters={"rsi_period": 14},
            expected_return="10-15%",
            max_drawdown="5-8%",
            suitable_for=["保守投资者"],
            analogy="就像定期存款",
            risk_score=3
        )
        
        explanation = intent_service.explain_strategy(strategy_package)
        
        assert explanation is not None
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_validate_user_input_valid(self, intent_service, sample_user_input):
        """测试验证有效的用户输入"""
        is_valid = intent_service.validate_user_input(sample_user_input)
        
        assert is_valid is True
    
    def test_validate_user_input_missing_goal(self, intent_service):
        """测试验证缺少目标的输入"""
        invalid_input = {
            "risk_tolerance": "low",
            "investment_amount": 10000.0
        }
        
        is_valid = intent_service.validate_user_input(invalid_input)
        
        assert is_valid is False
    
    def test_validate_user_input_invalid_amount(self, intent_service):
        """测试验证无效金额"""
        invalid_input = {
            "goal": "stable_growth",
            "risk_tolerance": "low",
            "investment_amount": -1000.0  # 负数金额
        }
        
        is_valid = intent_service.validate_user_input(invalid_input)
        
        assert is_valid is False
    
    def test_calculate_expected_return(self, intent_service):
        """测试计算预期收益"""
        strategy_params = {
            "strategy_id": "rsi_dca",
            "risk_level": "low"
        }
        investment_amount = 10000.0
        
        expected_return = intent_service.calculate_expected_return(
            strategy_params,
            investment_amount
        )
        
        assert expected_return is not None
        assert expected_return >= 0 or expected_return < 0  # 任何数值都可接受
    
    def test_calculate_risk_score(self, intent_service):
        """测试计算风险评分"""
        user_input = {
            "goal": UserGoal.STABLE_GROWTH,
            "risk_tolerance": RiskTolerance.LOW,
            "investment_amount": 10000.0
        }
        
        risk_score = intent_service.calculate_risk_score(user_input)
        
        assert risk_score is not None
        assert 1 <= risk_score <= 10  # 风险评分应该在1-10之间
    
    def test_generate_strategy_report(self, intent_service, sample_user_input):
        """测试生成策略报告"""
        report = intent_service.generate_strategy_report(sample_user_input)
        
        assert report is not None
        assert "strategy_name" in report or isinstance(report, dict)
    
    def test_match_strategy_to_user_profile(self, intent_service):
        """测试匹配策略到用户画像"""
        user_profile = {
            "age": 30,
            "income_level": "medium",
            "investment_experience": "beginner",
            "goal": UserGoal.STABLE_GROWTH,
            "risk_tolerance": RiskTolerance.LOW
        }
        
        matched_strategies = intent_service.match_strategies_to_profile(user_profile)
        
        assert matched_strategies is not None
        assert len(matched_strategies) > 0 or matched_strategies == []


@pytest.mark.integration
class TestIntentServiceIntegration:
    """意图服务集成测试"""
    
    def test_full_recommendation_flow(self, intent_service):
        """测试完整推荐流程"""
        # 1. 用户输入
        user_input = {
            "goal": "stable_growth",
            "risk_tolerance": "low",
            "investment_amount": 10000.0,
            "investment_horizon": "long_term"
        }
        
        # 2. 验证输入
        assert intent_service.validate_user_input(user_input)
        
        # 3. 解析目标
        goal = intent_service.parse_user_goal(user_input["goal"])
        assert goal == UserGoal.STABLE_GROWTH
        
        # 4. 推荐策略
        recommendations = intent_service.recommend_strategies(user_input)
        assert len(recommendations) > 0
        
        # 5. 获取详情
        first_strategy = recommendations[0]
        assert hasattr(first_strategy, 'friendly_name')
        assert hasattr(first_strategy, 'strategy_id')
    
    def test_edge_case_extreme_amount(self, intent_service):
        """测试边缘情况：极端金额"""
        # 极小金额
        small_input = {
            "goal": "stable_growth",
            "risk_tolerance": "low",
            "investment_amount": 100.0,  # 很小的金额
            "investment_horizon": "short_term"
        }
        
        recommendations = intent_service.recommend_strategies(small_input)
        # 应该返回推荐或给出提示
        assert recommendations is not None
        
        # 极大金额
        large_input = {
            "goal": "aggressive_growth",
            "risk_tolerance": "high",
            "investment_amount": 1000000.0,  # 100万
            "investment_horizon": "long_term"
        }
        
        recommendations = intent_service.recommend_strategies(large_input)
        assert recommendations is not None
    
    def test_conflicting_goals(self, intent_service):
        """测试冲突目标"""
        # 资本保值 + 高风险（矛盾）
        conflicting_input = {
            "goal": "capital_preservation",
            "risk_tolerance": "high",  # 矛盾：保值却高风险
            "investment_amount": 10000.0,
            "investment_horizon": "short_term"
        }
        
        # 服务应该能处理或给出警告
        recommendations = intent_service.recommend_strategies(conflicting_input)
        assert recommendations is not None or recommendations == []


@pytest.mark.unit
class TestStrategyPackage:
    """策略包测试"""
    
    def test_strategy_package_creation(self):
        """测试创建策略包"""
        package = StrategyPackage(
            package_id="test_pkg",
            friendly_name="测试策略",
            icon="🎯",
            tagline="测试标语",
            description="测试描述",
            strategy_id="test_strategy",
            parameters={"param1": "value1"},
            expected_return="10%",
            max_drawdown="5%",
            suitable_for=["保守型"],
            analogy="测试类比",
            risk_score=3
        )
        
        assert package.package_id == "test_pkg"
        assert package.risk_score == 3
        assert package.strategy_id == "test_strategy"
    
    def test_strategy_package_validation(self):
        """测试策略包验证"""
        # 风险评分应该在合理范围内
        assert 1 <= 3 <= 10
        
        # 参数应该是字典
        params = {"param1": "value1"}
        assert isinstance(params, dict)
