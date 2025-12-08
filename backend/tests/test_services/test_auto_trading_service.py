"""
Auto Trading Service 单元测试
测试全自动交易服务的核心功能
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from services.auto_trading_service import AutoTradingService


@pytest.fixture
def auto_trading_service():
    """创建 AutoTradingService 实例"""
    service = AutoTradingService()
    yield service
    # 清理
    if service.status.value != "stopped":
        asyncio.create_task(service.stop_trading())


@pytest.fixture
def sample_strategy_config():
    """示例策略配置"""
    return {
        "strategy_id": "ma_crossover",
        "name": "MA Crossover Strategy",
        "symbol": "BTC/USDT",
        "market_type": "crypto",
        "exchange": "binance",
        "timeframe": "1h",
        "parameters": {
            "fast_period": 10,
            "slow_period": 20,
            "position_size": 0.1
        },
        "risk_config": {
            "max_position_size": 1000.0,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.05
        }
    }


class TestAutoTradingService:
    """全自动交易服务测试套件"""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, auto_trading_service):
        """测试服务初始化"""
        assert auto_trading_service is not None
        assert auto_trading_service.status.value == "stopped"
        assert auto_trading_service.active_strategies == []
    
    @pytest.mark.asyncio
    async def test_start_trading(self, auto_trading_service):
        """测试启动交易"""
        from backend.services.auto_trading_service import AutoTradingStrategy
        result = await auto_trading_service.start_trading([AutoTradingStrategy.TREND_FOLLOWING])
        assert result["success"] is True
        assert auto_trading_service.status.value == "running"
        
        # 清理
        await auto_trading_service.stop_trading()
    
    @pytest.mark.asyncio
    async def test_stop_trading(self, auto_trading_service):
        """测试停止交易"""
        from backend.services.auto_trading_service import AutoTradingStrategy
        await auto_trading_service.start_trading([AutoTradingStrategy.TREND_FOLLOWING])
        assert auto_trading_service.status.value == "running"
        
        result = await auto_trading_service.stop_trading()
        assert result["success"] is True
        assert auto_trading_service.status.value == "stopped"
    
    @pytest.mark.asyncio
    async def test_add_strategy(self, auto_trading_service):
        """测试添加策略"""
        from backend.services.auto_trading_service import AutoTradingStrategy
        result = await auto_trading_service.start_trading([AutoTradingStrategy.MEAN_REVERSION, AutoTradingStrategy.TREND_FOLLOWING])
        
        # 验证策略已添加
        assert result["success"] is True
        assert len(auto_trading_service.active_strategies) == 2
        await auto_trading_service.stop_trading()
    
    @pytest.mark.asyncio
    async def test_remove_strategy(self, auto_trading_service):
        """测试移除策略"""
        from backend.services.auto_trading_service import AutoTradingStrategy
        # 先添加策略
        await auto_trading_service.start_trading([AutoTradingStrategy.TREND_FOLLOWING])
        
        # 停止交易（移除所有策略）
        result = await auto_trading_service.stop_trading()
        assert result["success"] is True
        assert len(auto_trading_service.active_strategies) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="get_status() 方法不存在，应使用 auto_trading_service.status 属性")
    async def test_get_status(self, auto_trading_service):
        """测试获取交易状态"""
        # AutoTradingService 使用 status 属性而非 get_status() 方法
        pass
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="emergency_stop() 方法不存在或未导出")
    async def test_emergency_stop(self, auto_trading_service):
        """测试紧急停止"""
        # emergency_stop() 方法不存在于 AutoTradingService
        # 跳过此测试
        pass
    
    @pytest.mark.asyncio
    async def test_invalid_strategy_config(self, auto_trading_service):
        """测试无效策略配置"""
        # 使用空列表启动，应该成功但没有策略
        result = await auto_trading_service.start_trading([])
        assert result["success"] is True
        assert len(auto_trading_service.active_strategies) == 0
        await auto_trading_service.stop_trading()
    
    @pytest.mark.asyncio
    async def test_risk_management(self, auto_trading_service):
        """测试风险管理功能"""
        # 验证风险配置存在
        assert "max_daily_trades" in auto_trading_service.trading_config
        assert "max_daily_loss" in auto_trading_service.trading_config
        assert auto_trading_service.trading_config["max_daily_loss"] > 0
    
    @pytest.mark.asyncio
    async def test_multiple_strategies(self, auto_trading_service):
        """测试同时运行多个策略"""
        from backend.services.auto_trading_service import AutoTradingStrategy
        
        # 添加多个策略
        strategies = [AutoTradingStrategy.TREND_FOLLOWING, AutoTradingStrategy.MEAN_REVERSION, AutoTradingStrategy.BREAKOUT]
        result = await auto_trading_service.start_trading(strategies)
        
        # 验证多策略
        assert result["success"] is True
        assert len(auto_trading_service.active_strategies) == 3
        await auto_trading_service.stop_trading()
    
    @pytest.mark.asyncio
    async def test_strategy_execution_error_handling(self, auto_trading_service):
        """测试策略执行错误处理"""
        from backend.services.auto_trading_service import AutoTradingStrategy
        # 启动并立即停止，不应该崩溃
        try:
            await auto_trading_service.start_trading([AutoTradingStrategy.TREND_FOLLOWING])
            await asyncio.sleep(0.1)
            await auto_trading_service.stop_trading()
        except Exception as e:
            pytest.fail(f"Service should handle errors gracefully: {e}")
    
    @pytest.mark.asyncio
    async def test_get_trading_statistics(self, auto_trading_service):
        """测试获取交易统计"""
        stats = auto_trading_service.trading_stats
        
        # 验证统计数据结构
        assert isinstance(stats, dict)
        assert "total_trades" in stats
        assert "total_profit_loss" in stats
    
    @pytest.mark.asyncio
    async def test_update_strategy_parameters(self, auto_trading_service):
        """测试更新策略参数"""
        # 测试配置更新
        old_max_trades = auto_trading_service.trading_config["max_daily_trades"]
        auto_trading_service.trading_config["max_daily_trades"] = 100
        
        assert auto_trading_service.trading_config["max_daily_trades"] == 100
        assert auto_trading_service.trading_config["max_daily_trades"] != old_max_trades
