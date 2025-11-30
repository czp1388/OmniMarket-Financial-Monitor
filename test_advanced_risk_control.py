"""
测试全自动交易系统的高级风控功能
"""

import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.auto_trading_service import AutoTradingService, AutoTradingStrategy, TradingStatus


async def test_advanced_risk_control():
    """测试高级风控功能"""
    print("=== 测试全自动交易系统高级风控功能 ===\n")
    
    # 创建自动交易服务实例
    trading_service = AutoTradingService()
    
    print("1. 测试交易状态管理...")
    # 测试启动交易
    start_result = await trading_service.start_trading([
        AutoTradingStrategy.TREND_FOLLOWING,
        AutoTradingStrategy.MEAN_REVERSION
    ])
    print(f"启动结果: {start_result}")
    
    # 获取交易状态
    status = trading_service.get_trading_status()
    print(f"交易状态: {status['status']}")
    print(f"活跃策略: {status['active_strategies']}")
    
    print("\n2. 测试高级风控检查...")
    # 手动调用高级风控检查
    await trading_service._advanced_risk_control()
    print("高级风控检查完成")
    
    print("\n3. 测试具体风控功能...")
    
    # 测试实时资金监控
    print("测试实时资金监控...")
    await trading_service._real_time_capital_monitoring()
    
    # 测试波动率自适应调整
    print("测试波动率自适应调整...")
    await trading_service._volatility_adaptive_adjustment()
    print(f"当前仓位规模: {trading_service.trading_config['max_position_size']}")
    
    # 测试异常交易检测
    print("测试异常交易检测...")
    await trading_service._anomaly_trading_detection()
    
    # 测试流动性风险检查
    print("测试流动性风险检查...")
    await trading_service._liquidity_risk_check()
    
    # 测试集中度风险监控
    print("测试集中度风险监控...")
    await trading_service._concentration_risk_monitoring()
    
    print("\n4. 测试紧急熔断机制...")
    # 模拟触发市场波动率熔断
    trading_service.risk_metrics["volatility"] = 0.4  # 设置高波动率
    await trading_service._volatility_adaptive_adjustment()
    print(f"市场波动率熔断状态: {trading_service.emergency_brakes['market_volatility_brake']}")
    
    # 检查紧急熔断
    emergency_triggered = trading_service._check_emergency_brakes()
    print(f"紧急熔断触发: {emergency_triggered}")
    
    print("\n5. 测试交易统计和风险指标...")
    # 模拟一些交易数据
    trading_service.trading_stats["total_trades"] = 15
    trading_service.trading_stats["successful_trades"] = 12
    trading_service.trading_stats["daily_profit_loss"] = -5000.0
    
    # 更新风险指标
    trading_service._update_risk_metrics()
    
    status = trading_service.get_trading_status()
    print(f"交易统计: {status['trading_stats']}")
    print(f"风险指标: {status['risk_metrics']}")
    print(f"紧急熔断状态: {status['emergency_brakes']}")
    
    print("\n6. 测试停止交易...")
    stop_result = await trading_service.stop_trading()
    print(f"停止结果: {stop_result}")
    
    print("\n=== 高级风控功能测试完成 ===")


async def test_risk_scenarios():
    """测试风险场景"""
    print("\n=== 测试风险场景 ===")
    
    trading_service = AutoTradingService()
    
    # 场景1: 高波动率环境
    print("\n场景1: 高波动率环境")
    trading_service.risk_metrics["volatility"] = 0.35
    await trading_service._volatility_adaptive_adjustment()
    print(f"仓位规模调整: {trading_service.trading_config['max_position_size']}")
    print(f"波动率熔断: {trading_service.emergency_brakes['market_volatility_brake']}")
    
    # 场景2: 大额亏损
    print("\n场景2: 大额亏损")
    trading_service.trading_stats["daily_profit_loss"] = -15000.0
    await trading_service._execute_trade(
        AutoTradingStrategy.TREND_FOLLOWING,
        {"action": "buy", "symbol": "TEST", "price": 100, "quantity": 1, "confidence": 0.8, "strategy": "trend_following"},
        {"price": 100, "volume": 1000, "change": 0.01, "timestamp": "2023-01-01"}
    )
    print(f"每日亏损熔断: {trading_service.emergency_brakes['max_daily_loss_brake']}")
    
    # 场景3: 高频交易异常
    print("\n场景3: 高频交易异常检测")
    await trading_service._anomaly_trading_detection()
    
    # 重置熔断
    trading_service.reset_emergency_brakes()
    print(f"熔断重置后状态: {trading_service.emergency_brakes}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_advanced_risk_control())
    asyncio.run(test_risk_scenarios())
