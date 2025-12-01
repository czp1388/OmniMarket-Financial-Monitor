"""
LEAN引擎回测服务
为QuantConnect LEAN引擎提供Python接口，用于策略回测和执行
"""
import asyncio
import json
import logging
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import yfinance as yf
from pydantic import BaseModel
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

logger = logging.getLogger(__name__)


class BacktestRequest(BaseModel):
    """回测请求模型"""
    strategy_id: str
    strategy_code: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    parameters: Dict[str, Any] = {}
    data_source: str = "yfinance"  # yfinance, alpha_vantage, akshare, custom


class BacktestResult(BaseModel):
    """回测结果模型"""
    backtest_id: str
    strategy_id: str
    status: str  # running, completed, failed
    statistics: Dict[str, Any] = {}
    equity_curve: List[Dict[str, float]] = []
    trades: List[Dict[str, Any]] = []
    logs: List[str] = []
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class StrategyPerformance(BaseModel):
    """策略表现统计"""
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profit_factor: float
    calmar_ratio: float


class LeanBacktestService:
    """LEAN回测服务"""
    
    def __init__(self):
        self.active_backtests: Dict[str, BacktestResult] = {}
        self.backtest_history: List[BacktestResult] = []
        self.strategy_templates: Dict[str, str] = self._load_strategy_templates()
        logger.info("LEAN回测服务已初始化")
    
    def _load_strategy_templates(self) -> Dict[str, str]:
        """加载策略模板"""
        return {
            "moving_average_crossover": """
# 移动平均线交叉策略
from datetime import timedelta
from AlgorithmImports import *

class MovingAverageCrossAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate({start_date})
        self.SetEndDate({end_date})
        self.SetCash({initial_capital})
        
        # 添加资产
        self.AddEquity("{symbol}", Resolution.Daily)
        
        # 初始化指标
        self.fast_period = {parameters.get('fast_period', 10)}
        self.slow_period = {parameters.get('slow_period', 30)}
        
        self.fast_ma = self.SMA("{symbol}", self.fast_period, Resolution.Daily)
        self.slow_ma = self.SMA("{symbol}", self.slow_period, Resolution.Daily)
        
        # 设置定时器
        self.Schedule.On(self.DateRules.EveryDay("{symbol}"), 
                        self.TimeRules.AfterMarketOpen("{symbol}", 30),
                        self.Trade)
    
    def Trade(self):
        if not self.fast_ma.IsReady or not self.slow_ma.IsReady:
            return
        
        holdings = self.Portfolio["{symbol}"].Quantity
        
        if self.fast_ma.Current.Value > self.slow_ma.Current.Value and holdings <= 0:
            self.SetHoldings("{symbol}", 1.0)
        elif self.fast_ma.Current.Value < self.slow_ma.Current.Value and holdings > 0:
            self.Liquidate("{symbol}")
""",
            "rsi_strategy": """
# RSI策略
from datetime import timedelta
from AlgorithmImports import *

class RsiAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate({start_date})
        self.SetEndDate({end_date})
        self.SetCash({initial_capital})
        
        # 添加资产
        self.AddEquity("{symbol}", Resolution.Daily)
        
        # 初始化RSI指标
        self.rsi_period = {parameters.get('rsi_period', 14)}
        self.oversold = {parameters.get('oversold', 30)}
        self.overbought = {parameters.get('overbought', 70)}
        
        self.rsi = self.RSI("{symbol}", self.rsi_period, MovingAverageType.Simple, Resolution.Daily)
        
        # 设置定时器
        self.Schedule.On(self.DateRules.EveryDay("{symbol}"), 
                        self.TimeRules.AfterMarketOpen("{symbol}", 30),
                        self.Trade)
    
    def Trade(self):
        if not self.rsi.IsReady:
            return
        
        holdings = self.Portfolio["{symbol}"].Quantity
        current_rsi = self.rsi.Current.Value
        
        if current_rsi < self.oversold and holdings <= 0:
            self.SetHoldings("{symbol}", 1.0)
        elif current_rsi > self.overbought and holdings > 0:
            self.Liquidate("{symbol}")
""",
            "mean_reversion": """
# 均值回归策略
from datetime import timedelta
from AlgorithmImports import *

class MeanReversionAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate({start_date})
        self.SetEndDate({end_date})
        self.SetCash({initial_capital})
        
        # 添加资产
        self.AddEquity("{symbol}", Resolution.Daily)
        
        # 初始化布林带指标
        self.bb_period = {parameters.get('bb_period', 20)}
        self.std_dev = {parameters.get('std_dev', 2.0)}
        
        self.bb = self.BB("{symbol}", self.bb_period, self.std_dev, MovingAverageType.Simple, Resolution.Daily)
        
        # 设置定时器
        self.Schedule.On(self.DateRules.EveryDay("{symbol}"), 
                        self.TimeRules.AfterMarketOpen("{symbol}", 30),
                        self.Trade)
    
    def Trade(self):
        if not self.bb.IsReady:
            return
        
        holdings = self.Portfolio["{symbol}"].Quantity
        price = self.Securities["{symbol}"].Price
        
        lower_band = self.bb.LowerBand.Current.Value
        upper_band = self.bb.UpperBand.Current.Value
        
        if price < lower_band and holdings <= 0:
            self.SetHoldings("{symbol}", 1.0)
        elif price > upper_band and holdings > 0:
            self.Liquidate("{symbol}")
"""
        }
    
    async def start_backtest(self, request: BacktestRequest) -> str:
        """启动回测"""
        backtest_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.strategy_id}"
        
        result = BacktestResult(
            backtest_id=backtest_id,
            strategy_id=request.strategy_id,
            status="running",
            created_at=datetime.now().isoformat(),
            statistics={},
            equity_curve=[],
            trades=[],
            logs=[f"开始回测 {backtest_id}"]
        )
        
        self.active_backtests[backtest_id] = result
        
        # 在后台运行回测
        asyncio.create_task(self._run_backtest(backtest_id, request))
        
        logger.info(f"启动回测: {backtest_id}")
        return backtest_id
    
    async def _run_backtest(self, backtest_id: str, request: BacktestRequest):
        """执行回测"""
        try:
            # 使用backtesting库进行真实回测
            await self._run_backtesting_backtest(backtest_id, request)
            
        except Exception as e:
            logger.error(f"回测执行失败: {backtest_id}, 错误: {e}")
            result = self.active_backtests[backtest_id]
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now().isoformat()
            
            # 移动到历史记录
            self.backtest_history.append(result)
            del self.active_backtests[backtest_id]
    
    async def _run_backtesting_backtest(self, backtest_id: str, request: BacktestRequest):
        """使用backtesting库执行真实回测"""
        result = self.active_backtests[backtest_id]
        result.logs.append("开始下载历史数据...")
        
        try:
            # 根据策略ID选择相应的策略类
            if request.strategy_id == "moving_average_crossover":
                strategy_class = self._create_moving_average_crossover_strategy(request.parameters)
            elif request.strategy_id == "rsi_strategy":
                strategy_class = self._create_rsi_strategy(request.parameters)
            elif request.strategy_id == "mean_reversion":
                strategy_class = self._create_mean_reversion_strategy(request.parameters)
            else:
                # 默认使用移动平均线交叉策略
                strategy_class = self._create_moving_average_crossover_strategy(request.parameters)
            
            # 下载历史数据
            result.logs.append(f"下载数据: {request.symbol} 从 {request.start_date} 到 {request.end_date}")
            data = self._download_historical_data(request.symbol, request.start_date, request.end_date)
            
            if data.empty:
                raise ValueError(f"无法获取 {request.symbol} 的历史数据")
            
            result.logs.append(f"数据下载完成，共 {len(data)} 条记录")
            
            # 运行回测
            bt = Backtest(data, strategy_class, cash=request.initial_capital, commission=.002)
            output = bt.run()
            
            # 提取回测结果
            result.statistics = {
                "total_return": output['Return [%]'],
                "annual_return": output['Return (Ann.) [%]'],
                "sharpe_ratio": output['Sharpe Ratio'],
                "max_drawdown": output['Max. Drawdown [%]'],
                "win_rate": output['Win Rate [%]'],
                "total_trades": output['# Trades'],
                "profit_factor": output['Profit Factor'],
                "calmar_ratio": output['Calmar Ratio'],
                "alpha": 0.0,  # 暂时设为0，后续可计算
                "beta": 1.0,   # 暂时设为1，后续可计算
                "volatility": output['Volatility (Ann.) [%]']
            }
            
            # 生成权益曲线
            equity_curve = output['_equity_curve']
            if equity_curve is not None and not equity_curve.empty:
                # 获取权益曲线的值和索引
                equity_values = equity_curve.Equity if hasattr(equity_curve, 'Equity') else equity_curve
                equity_index = equity_curve.index
                
                # 采样，最多100个点
                step = max(1, len(equity_values) // 100)
                for i in range(0, len(equity_values), step):
                    equity = equity_values.iloc[i] if hasattr(equity_values, 'iloc') else equity_values[i]
                    date_index = equity_index[i] if hasattr(equity_index, '__getitem__') else i
                    
                    result.equity_curve.append({
                        "date": date_index.strftime("%Y-%m-%d") if hasattr(date_index, 'strftime') else str(date_index),
                        "equity": round(float(equity), 2),
                        "return": round((float(equity) / request.initial_capital - 1) * 100, 2) if i > 0 else 0
                    })
            
            # 生成交易记录
            trades = output['_trades']
            if trades is not None and not trades.empty:
                for i, trade in trades.iterrows():
                    result.trades.append({
                        "id": f"trade_{i}",
                        "date": trade['EntryTime'].strftime("%Y-%m-%d") if hasattr(trade['EntryTime'], 'strftime') else str(trade['EntryTime']),
                        "direction": "BUY" if trade['Size'] > 0 else "SELL",
                        "quantity": abs(trade['Size']),
                        "entry_price": trade['EntryPrice'],
                        "exit_price": trade['ExitPrice'],
                        "profit_loss": trade['PnL'],
                        "return_pct": trade['ReturnPct']
                    })
            
            result.logs.append("回测完成")
            result.status = "completed"
            result.completed_at = datetime.now().isoformat()
            
            # 移动到历史记录
            self.backtest_history.append(result)
            del self.active_backtests[backtest_id]
            
            logger.info(f"回测完成: {backtest_id}")
            
        except Exception as e:
            logger.error(f"回测过程中出错: {e}")
            raise
    
    def _download_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """下载历史数据"""
        # 清理符号格式
        clean_symbol = symbol.replace('/', '-').replace('.HK', '').replace('.', '-')
        
        try:
            # 使用yfinance下载数据
            ticker = yf.Ticker(clean_symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            # 确保数据格式正确
            if data.empty:
                # 尝试使用原始符号
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)
            
            # 重命名列以符合backtesting库的期望
            data = data.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            })
            
            return data
            
        except Exception as e:
            logger.error(f"下载历史数据失败: {symbol}, 错误: {e}")
            # 返回空DataFrame
            return pd.DataFrame()
    
    def _create_moving_average_crossover_strategy(self, parameters: Dict[str, Any]) -> type:
        """创建移动平均线交叉策略类"""
        fast_period = parameters.get('fast_period', 10)
        slow_period = parameters.get('slow_period', 30)
        
        class MovingAverageCross(Strategy):
            def init(self):
                # 使用pandas计算移动平均线
                import pandas as pd
                self.fast_ma = self.I(lambda x: pd.Series(x).rolling(fast_period).mean(), self.data.Close)
                self.slow_ma = self.I(lambda x: pd.Series(x).rolling(slow_period).mean(), self.data.Close)
            
            def next(self):
                if crossover(self.fast_ma, self.slow_ma):
                    self.buy()
                elif crossover(self.slow_ma, self.fast_ma):
                    self.sell()
        
        return MovingAverageCross
    
    def _create_rsi_strategy(self, parameters: Dict[str, Any]) -> type:
        """创建RSI策略类"""
        rsi_period = parameters.get('rsi_period', 14)
        oversold = parameters.get('oversold', 30)
        overbought = parameters.get('overbought', 70)
        
        def compute_rsi(prices, period):
            """计算RSI指标"""
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        class RsiStrategy(Strategy):
            rsi_period = rsi_period
            oversold = oversold
            overbought = overbought
            
            def init(self):
                import pandas as pd
                self.rsi = self.I(lambda x: compute_rsi(pd.Series(x), self.rsi_period), self.data.Close)
            
            def next(self):
                if self.rsi[-1] < self.oversold and not self.position:
                    self.buy()
                elif self.rsi[-1] > self.overbought and self.position:
                    self.sell()
        
        return RsiStrategy
    
    def _create_mean_reversion_strategy(self, parameters: Dict[str, Any]) -> type:
        """创建均值回归策略类"""
        bb_period = parameters.get('bb_period', 20)
        std_dev = parameters.get('std_dev', 2.0)
        
        class MeanReversion(Strategy):
            bb_period = bb_period
            std_dev = std_dev
            
            def init(self):
                from backtesting.lib import bollinger_bands
                self.bb_upper, self.bb_mid, self.bb_lower = self.I(bollinger_bands, self.data.Close, self.bb_period, self.std_dev)
            
            def next(self):
                if self.data.Close[-1] < self.bb_lower[-1] and not self.position:
                    self.buy()
                elif self.data.Close[-1] > self.bb_upper[-1] and self.position:
                    self.sell()
        
        return MeanReversion
    
    def get_backtest_status(self, backtest_id: str) -> Optional[BacktestResult]:
        """获取回测状态"""
        if backtest_id in self.active_backtests:
            return self.active_backtests[backtest_id]
        
        # 在历史记录中查找
        for result in self.backtest_history:
            if result.backtest_id == backtest_id:
                return result
        
        return None
    
    def get_all_backtests(self, strategy_id: Optional[str] = None) -> List[BacktestResult]:
        """获取所有回测"""
        if strategy_id:
            return [
                result for result in self.backtest_history
                if result.strategy_id == strategy_id
            ]
        return self.backtest_history
    
    def cancel_backtest(self, backtest_id: str) -> bool:
        """取消回测"""
        if backtest_id in self.active_backtests:
            result = self.active_backtests[backtest_id]
            result.status = "cancelled"
            result.completed_at = datetime.now().isoformat()
            
            self.backtest_history.append(result)
            del self.active_backtests[backtest_id]
            
            logger.info(f"回测已取消: {backtest_id}")
            return True
        
        return False
    
    def get_strategy_templates(self) -> Dict[str, str]:
        """获取可用的策略模板"""
        return self.strategy_templates
    
    def create_strategy_from_template(self, template_id: str, 
                                     symbol: str, 
                                     start_date: str, 
                                     end_date: str, 
                                     initial_capital: float = 10000.0,
                                     parameters: Optional[Dict[str, Any]] = None) -> str:
        """从模板创建策略代码"""
        if template_id not in self.strategy_templates:
            raise ValueError(f"策略模板不存在: {template_id}")
        
        template = self.strategy_templates[template_id]
        
        # 替换模板变量
        strategy_code = template.format(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            parameters=parameters or {}
        )
        
        return strategy_code


# 全局服务实例
lean_service = LeanBacktestService()
