"""
快速测试诊断脚本
检查测试环境和关键功能
"""
import sys
from pathlib import Path

# 添加backend到路径
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

print("=" * 60)
print("测试环境诊断")
print("=" * 60)

# 1. 检查Timeframe枚举
try:
    from models.market_data import Timeframe
    print("\n✅ Timeframe 导入成功")
    print(f"   可用值: {[e.name for e in Timeframe]}")
    print(f"   HOUR_1 存在: {hasattr(Timeframe, 'HOUR_1')}")
    print(f"   H1 存在: {hasattr(Timeframe, 'H1')}")
except Exception as e:
    print(f"\n❌ Timeframe 导入失败: {e}")

# 2. 检查DataService
try:
    from services.data_service import DataService
    print("\n✅ DataService 导入成功")
    service = DataService()
    print(f"   实例创建成功: {type(service).__name__}")
except Exception as e:
    print(f"\n❌ DataService 导入失败: {e}")

# 3. 检查 VirtualTradingEngine
try:
    from services.virtual_trading_engine import VirtualTradingEngine, OrderType, OrderSide
    print("\n✅ VirtualTradingEngine 导入成功")
    engine = VirtualTradingEngine(initial_balance=10000.0)
    print(f"   初始余额: {engine.get_balance()}")
    
    # 测试订单创建
    order = engine.create_order(
        symbol="BTC/USDT",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=0.1,
        price=42000.0
    )
    print(f"   订单状态: {order.status}")
    print(f"   订单ID: {order.id}")
except Exception as e:
    print(f"\n❌ VirtualTradingEngine 测试失败: {e}")

# 4. 检查异步支持
try:
    import asyncio
    
    async def test_async():
        from services.data_service import DataService
        from models.market_data import MarketType, Timeframe
        
        service = DataService()
        # 尝试获取mock数据
        result = await service.get_klines(
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            exchange="binance",
            timeframe=Timeframe.HOUR_1,
            limit=10
        )
        return result
    
    result = asyncio.run(test_async())
    print(f"\n✅ 异步测试成功")
    print(f"   获取K线数量: {len(result)}")
    if result:
        print(f"   第一条数据时间: {result[0].timestamp}")
except Exception as e:
    print(f"\n❌ 异步测试失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
