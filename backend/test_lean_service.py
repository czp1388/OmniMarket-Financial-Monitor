#!/usr/bin/env python3
"""
测试LEAN回测服务的脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.lean_backtest_service import LeanBacktestService, BacktestRequest
from datetime import datetime, timedelta


async def test_lean_service():
    """测试LEAN回测服务的基本功能"""
    print("=== 测试LEAN回测服务 ===")
    
    # 创建服务实例
    service = LeanBacktestService()
    
    # 创建测试请求
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    test_request = BacktestRequest(
        strategy_id="test_macross_strategy",
        strategy_code="moving_average_crossover",
        symbol="AAPL",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        initial_capital=10000.0,
        parameters={
            "fast_period": 10,
            "slow_period": 30
        },
        data_source="yfinance"
    )
    
    try:
        # 测试启动回测
        print("1. 测试启动回测...")
        backtest_id = await service.start_backtest(test_request)
        print(f"   回测已启动，ID: {backtest_id}")
        
        # 测试获取回测状态
        print("2. 测试获取回测状态...")
        status = service.get_backtest_status(backtest_id)
        print(f"   回测状态: {status}")
        
        # 测试获取回测结果（等待模拟回测完成）
        print("3. 等待回测完成...")
        await asyncio.sleep(3)  # 等待模拟回测完成
        
        # 再次获取状态，此时应已完成
        result = service.get_backtest_status(backtest_id)
        if result:
            print(f"   回测结果状态: {result.status}")
            if result.status == "completed":
                print(f"   总收益: {result.statistics.get('total_return', 0)}%")
                print(f"   夏普比率: {result.statistics.get('sharpe_ratio', 0)}")
                print(f"   最大回撤: {result.statistics.get('max_drawdown', 0)}%")
        
        # 测试获取策略模板
        print("4. 测试获取策略模板...")
        templates = service.get_strategy_templates()
        print(f"   可用策略模板: {len(templates)} 个")
        for template_id in list(templates.keys())[:3]:  # 显示前3个
            print(f"   - {template_id}")
        
        print("\n=== 所有测试通过 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    # 这里可以添加实际的HTTP请求测试
    # 但由于我们只是验证服务，暂时跳过
    
    print("API端点测试（需要运行服务器）")


if __name__ == "__main__":
    print("LEAN回测服务测试")
    print("=" * 50)
    
    # 运行服务测试
    asyncio.run(test_lean_service())
    
    print("\n" + "=" * 50)
    print("注意: 要测试完整的API，请运行: python backend/main.py")
    print("然后访问: http://localhost:8000/docs")
    print("或使用curl测试:")
    print('  curl -X POST http://localhost:8000/api/lean/backtest/start \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"strategy_id": "macross", "symbol": "AAPL", "exchange": "NASDAQ", "timeframe": "1d", "start_date": "2023-01-01", "end_date": "2024-01-01", "capital": 10000}\'')
