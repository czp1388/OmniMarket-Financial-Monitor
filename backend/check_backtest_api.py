import backtesting
from backtesting import Backtest, Strategy
import pandas as pd

print(f"Backtesting version: {backtesting.__version__}")

# 创建测试数据
data = pd.DataFrame({
    'Open': [1, 2, 3],
    'High': [2, 3, 4],
    'Low': [0.5, 1.5, 2.5],
    'Close': [1.5, 2.5, 3.5],
    'Volume': [100, 200, 300]
})

class TestStrategy(Strategy):
    def init(self):
        # 初始化指标（可选）
        pass
    
    def next(self):
        # 简单的买入持有策略
        if len(self.data.Close) > 1 and not self.position:
            self.buy()
        elif len(self.data.Close) > 2 and self.position:
            self.sell()

# 运行回测
bt = Backtest(data, TestStrategy, cash=10000)
output = bt.run()

print(f"\nOutput type: {type(output)}")
print(f"Output:\n{output}")

print("\n=== Checking Backtest object attributes ===")
print(f"Has '_equity_curve'? {hasattr(bt, '_equity_curve')}")
print(f"Has '_trades'? {hasattr(bt, '_trades')}")

print("\n=== Checking output keys ===")
if isinstance(output, pd.Series):
    print(f"Output keys: {output.index.tolist()}")
    
    # 检查'_equity_curve'和'_trades'
    if '_equity_curve' in output:
        equity_curve = output['_equity_curve']
        print(f"\n_equity_curve type: {type(equity_curve)}")
        print(f"_equity_curve value: {equity_curve}")
        if hasattr(equity_curve, '__len__'):
            print(f"_equity_curve length: {len(equity_curve)}")
        if hasattr(equity_curve, 'shape'):
            print(f"_equity_curve shape: {equity_curve.shape}")
        if isinstance(equity_curve, pd.DataFrame):
            print(f"_equity_curve columns: {equity_curve.columns.tolist()}")
            print(f"_equity_curve head:\n{equity_curve.head()}")
        elif isinstance(equity_curve, pd.Series):
            print(f"_equity_curve head:\n{equity_curve.head()}")
        elif isinstance(equity_curve, str):
            print("_equity_curve is a string, might be a DataFrame representation")
    
    if '_trades' in output:
        trades = output['_trades']
        print(f"\n_trades type: {type(trades)}")
        print(f"_trades value: {trades}")
        if hasattr(trades, '__len__'):
            print(f"_trades length: {len(trades)}")
        if hasattr(trades, 'shape'):
            print(f"_trades shape: {trades.shape}")
        if isinstance(trades, pd.DataFrame):
            print(f"_trades columns: {trades.columns.tolist()}")
            print(f"_trades head:\n{trades.head()}")
        elif isinstance(trades, pd.Series):
            print(f"_trades head:\n{trades.head()}")
        elif isinstance(trades, str):
            print("_trades is a string, might be a DataFrame representation")

print("\n=== Exploring backtesting library methods ===")
# 尝试使用Backtest对象的方法获取更多数据
try:
    # 获取权益曲线
    equity_data = bt.optimize()
    print(f"Optimize method exists, returns: {type(equity_data)}")
except Exception as e:
    print(f"Optimize error: {e}")

# 检查是否有获取权益曲线的方法
print("\n=== Checking for equity curve extraction ===")
# 根据backtesting文档，我们可以通过Backtest.run()返回的Series获取权益曲线
# 但权益曲线数据可能存储在Backtest对象内部
# 让我们尝试检查Backtest对象的_data属性
if hasattr(bt, '_data'):
    print("Has '_data' attribute")
    
# 尝试使用get_all_metrics或类似方法
print("\n=== Checking for additional data access ===")
# 查看backtesting库的源代码或文档，寻找获取交易明细和权益曲线的方法
# 对于现在，我们先运行一个简单的回测来查看输出中包含什么
