import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

class TradingAnalyticsService:
    """交易分析服务 - 提供交易统计和风险指标计算"""
    
    def __init__(self):
        self.trading_records: List[Dict] = []
        self.portfolio_values: List[Tuple[datetime, float]] = []
        self.risk_metrics_cache: Dict[str, float] = {}
        
    async def record_trade(self, trade_data: Dict):
        """记录交易数据"""
        trade_data['timestamp'] = datetime.now()
        self.trading_records.append(trade_data)
        logger.info(f"记录交易: {trade_data.get('symbol')} - {trade_data.get('side')}")
        
    async def update_portfolio_value(self, value: float):
        """更新投资组合价值"""
        self.portfolio_values.append((datetime.now(), value))
        # 保持最近1000个记录
        if len(self.portfolio_values) > 1000:
            self.portfolio_values = self.portfolio_values[-1000:]
            
    async def get_trading_statistics(self, days: int = 30) -> Dict:
        """获取交易统计数据"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 过滤指定时间段内的交易
        recent_trades = [
            trade for trade in self.trading_records 
            if trade['timestamp'] >= cutoff_time
        ]
        
        if not recent_trades:
            return {
                'total_trades': 0,
                'successful_trades': 0,
                'failed_trades': 0,
                'total_profit_loss': 0.0,
                'average_profit_loss': 0.0,
                'win_rate': 0.0,
                'current_positions': [],
                'daily_trades_count': 0,
                'daily_profit_loss': 0.0
            }
            
        # 计算基本统计
        total_trades = len(recent_trades)
        successful_trades = len([t for t in recent_trades if t.get('profit_loss', 0) > 0])
        failed_trades = total_trades - successful_trades
        total_profit_loss = sum(t.get('profit_loss', 0) for t in recent_trades)
        average_profit_loss = total_profit_loss / total_trades if total_trades > 0 else 0
        win_rate = successful_trades / total_trades if total_trades > 0 else 0
        
        # 当日交易统计
        today = datetime.now().date()
        daily_trades = [
            t for t in recent_trades 
            if t['timestamp'].date() == today
        ]
        daily_trades_count = len(daily_trades)
        daily_profit_loss = sum(t.get('profit_loss', 0) for t in daily_trades)
        
        # 当前持仓
        current_positions = [
            t for t in recent_trades 
            if t.get('status') == 'open' or t.get('position_status') == 'active'
        ]
        
        return {
            'total_trades': total_trades,
            'successful_trades': successful_trades,
            'failed_trades': failed_trades,
            'total_profit_loss': total_profit_loss,
            'average_profit_loss': average_profit_loss,
            'win_rate': win_rate,
            'current_positions': [t.get('symbol') for t in current_positions],
            'daily_trades_count': daily_trades_count,
            'daily_profit_loss': daily_profit_loss
        }
        
    async def calculate_risk_metrics(self) -> Dict:
        """计算风险指标"""
        if not self.portfolio_values:
            return {
                'current_drawdown': 0.0,
                'max_drawdown': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'var_95': 0.0,
                'expected_shortfall': 0.0
            }
            
        # 提取投资组合价值序列
        values = [value for _, value in self.portfolio_values]
        
        # 计算回撤
        current_drawdown = self._calculate_current_drawdown(values)
        max_drawdown = self._calculate_max_drawdown(values)
        
        # 计算波动率（年化）
        volatility = self._calculate_volatility(values)
        
        # 计算夏普比率（假设无风险利率为2%）
        sharpe_ratio = self._calculate_sharpe_ratio(values, risk_free_rate=0.02)
        
        # 计算VaR（95%置信水平）
        var_95 = self._calculate_var(values, confidence_level=0.95)
        
        # 计算期望损失（ES）
        expected_shortfall = self._calculate_expected_shortfall(values, confidence_level=0.95)
        
        return {
            'current_drawdown': current_drawdown,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'var_95': var_95,
            'expected_shortfall': expected_shortfall
        }
        
    def _calculate_current_drawdown(self, values: List[float]) -> float:
        """计算当前回撤"""
        if not values:
            return 0.0
        current_value = values[-1]
        peak_value = max(values)
        return (current_value - peak_value) / peak_value if peak_value > 0 else 0.0
        
    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """计算最大回撤"""
        if len(values) < 2:
            return 0.0
            
        peak = values[0]
        max_drawdown = 0.0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0.0
            max_drawdown = max(max_drawdown, drawdown)
            
        return max_drawdown
        
    def _calculate_volatility(self, values: List[float]) -> float:
        """计算年化波动率"""
        if len(values) < 2:
            return 0.0
            
        returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                returns.append((values[i] - values[i-1]) / values[i-1])
                
        if not returns:
            return 0.0
            
        # 年化波动率（假设每日数据）
        daily_volatility = np.std(returns)
        annual_volatility = daily_volatility * np.sqrt(252)
        
        return annual_volatility
        
    def _calculate_sharpe_ratio(self, values: List[float], risk_free_rate: float = 0.02) -> float:
        """计算夏普比率"""
        if len(values) < 2:
            return 0.0
            
        returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                returns.append((values[i] - values[i-1]) / values[i-1])
                
        if not returns:
            return 0.0
            
        # 年化收益率
        total_return = (values[-1] - values[0]) / values[0] if values[0] != 0 else 0
        annual_return = (1 + total_return) ** (252 / len(values)) - 1
        
        # 年化波动率
        daily_volatility = np.std(returns)
        annual_volatility = daily_volatility * np.sqrt(252)
        
        if annual_volatility == 0:
            return 0.0
            
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        return sharpe_ratio
        
    def _calculate_var(self, values: List[float], confidence_level: float = 0.95) -> float:
        """计算在险价值（VaR）"""
        if len(values) < 2:
            return 0.0
            
        returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                returns.append((values[i] - values[i-1]) / values[i-1])
                
        if not returns:
            return 0.0
            
        # 使用历史模拟法计算VaR
        var = -np.percentile(returns, (1 - confidence_level) * 100)
        current_value = values[-1] if values else 0
        var_amount = var * current_value
        
        return var_amount
        
    def _calculate_expected_shortfall(self, values: List[float], confidence_level: float = 0.95) -> float:
        """计算期望损失（ES）"""
        if len(values) < 2:
            return 0.0
            
        returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                returns.append((values[i] - values[i-1]) / values[i-1])
                
        if not returns:
            return 0.0
            
        # 计算VaR阈值
        var_threshold = np.percentile(returns, (1 - confidence_level) * 100)
        
        # 计算超过VaR的损失平均值
        tail_losses = [r for r in returns if r <= var_threshold]
        
        if not tail_losses:
            return 0.0
            
        es = -np.mean(tail_losses)
        current_value = values[-1] if values else 0
        es_amount = es * current_value
        
        return es_amount
        
    async def get_performance_analysis(self, benchmark_return: float = 0.08) -> Dict:
        """获取绩效分析"""
        trading_stats = await self.get_trading_statistics()
        risk_metrics = await self.calculate_risk_metrics()
        
        # 计算信息比率（相对于基准）
        excess_return = trading_stats.get('total_profit_loss', 0) - benchmark_return
        tracking_error = risk_metrics.get('volatility', 0.01)  # 简化处理
        information_ratio = excess_return / tracking_error if tracking_error != 0 else 0
        
        # 计算索提诺比率（只考虑下行风险）
        downside_risk = self._calculate_downside_risk()
        sortino_ratio = excess_return / downside_risk if downside_risk != 0 else 0
        
        # 计算卡玛比率（回撤调整收益）
        calmar_ratio = excess_return / abs(risk_metrics.get('max_drawdown', 0.01)) if risk_metrics.get('max_drawdown', 0) != 0 else 0
        
        return {
            'trading_statistics': trading_stats,
            'risk_metrics': risk_metrics,
            'performance_ratios': {
                'information_ratio': information_ratio,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio
            },
            'risk_adjusted_returns': {
                'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0),
                'var_95': risk_metrics.get('var_95', 0),
                'expected_shortfall': risk_metrics.get('expected_shortfall', 0)
            }
        }
        
    def _calculate_downside_risk(self) -> float:
        """计算下行风险"""
        if not self.portfolio_values:
            return 0.0
            
        values = [value for _, value in self.portfolio_values]
        if len(values) < 2:
            return 0.0
            
        # 计算负收益的标准差
        negative_returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                return_val = (values[i] - values[i-1]) / values[i-1]
                if return_val < 0:
                    negative_returns.append(return_val)
                    
        if not negative_returns:
            return 0.0
            
        downside_risk = np.std(negative_returns) * np.sqrt(252)  # 年化
        return downside_risk
        
    async def generate_trading_report(self, period: str = "monthly") -> Dict:
        """生成交易报告"""
        analysis = await self.get_performance_analysis()
        
        report = {
            'report_period': period,
            'generated_at': datetime.now().isoformat(),
            'executive_summary': {
                'total_trades': analysis['trading_statistics']['total_trades'],
                'total_profit_loss': analysis['trading_statistics']['total_profit_loss'],
                'win_rate': analysis['trading_statistics']['win_rate'],
                'max_drawdown': analysis['risk_metrics']['max_drawdown'],
                'sharpe_ratio': analysis['risk_metrics']['sharpe_ratio']
            },
            'detailed_analysis': analysis,
            'recommendations': self._generate_recommendations(analysis)
        }
        
        return report
        
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        stats = analysis['trading_statistics']
        risk_metrics = analysis['risk_metrics']
        performance_ratios = analysis['performance_ratios']
        
        # 基于交易统计的建议
        if stats['win_rate'] < 0.5:
            recommendations.append("考虑优化交易策略，当前胜率较低")
            
        if stats['daily_trades_count'] > 20:
            recommendations.append("交易频率较高，建议控制交易次数以降低交易成本")
            
        # 基于风险指标的建议
        if risk_metrics['max_drawdown'] > 0.1:
            recommendations.append("最大回撤较大，建议加强风险控制")
            
        if risk_metrics['sharpe_ratio'] < 1.0:
            recommendations.append("夏普比率偏低，建议优化风险调整后收益")
            
        if risk_metrics['volatility'] > 0.3:
            recommendations.append("投资组合波动率较高，建议分散投资")
            
        return recommendations

    async def get_trade_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """获取交易历史记录"""
        filtered_trades = self.trading_records.copy()
        
        # 按日期过滤
        if start_date:
            filtered_trades = [t for t in filtered_trades if t['timestamp'] >= start_date]
        if end_date:
            filtered_trades = [t for t in filtered_trades if t['timestamp'] <= end_date]
            
        # 按交易品种过滤
        if symbol:
            filtered_trades = [t for t in filtered_trades if t.get('symbol') == symbol]
            
        # 按策略过滤
        if strategy:
            filtered_trades = [t for t in filtered_trades if t.get('strategy') == strategy]
            
        # 按时间倒序排序并限制数量
        filtered_trades.sort(key=lambda x: x['timestamp'], reverse=True)
        return filtered_trades[:limit]

    async def get_portfolio_value_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 30
    ) -> List[Dict]:
        """获取投资组合价值历史"""
        if not self.portfolio_values:
            return []
            
        # 如果没有指定日期范围，使用days参数
        if not start_date and not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
        # 过滤指定时间段内的记录
        filtered_values = [
            {'timestamp': timestamp.isoformat(), 'value': value}
            for timestamp, value in self.portfolio_values
            if (not start_date or timestamp >= start_date) and 
               (not end_date or timestamp <= end_date)
        ]
        
        return filtered_values

    async def reset_data(self):
        """重置交易数据（用于测试）"""
        self.trading_records.clear()
        self.portfolio_values.clear()
        self.risk_metrics_cache.clear()
        logger.info("交易数据已重置")

    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """获取投资组合摘要信息"""
        if not self.portfolio_values:
            # 返回默认投资组合数据
            return {
                'current_value': 100000.0,  # 默认初始资金
                'initial_value': 100000.0,
                'total_return': 0.0,
                'daily_return': 0.0,
                'positions': [],
                'cash_balance': 100000.0,
                'total_assets': 100000.0,
                'update_time': datetime.now().isoformat()
            }
        
        current_value = self.portfolio_values[-1][1] if self.portfolio_values else 100000.0
        initial_value = self.portfolio_values[0][1] if self.portfolio_values else 100000.0
        
        return {
            'current_value': current_value,
            'initial_value': initial_value,
            'total_return': (current_value - initial_value) / initial_value if initial_value > 0 else 0.0,
            'daily_return': self._calculate_daily_return(),
            'positions': self._get_current_positions(),
            'cash_balance': current_value * 0.3,  # 假设30%为现金
            'total_assets': current_value,
            'update_time': datetime.now().isoformat()
        }

    async def get_recent_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近的交易记录"""
        # 返回最近的交易记录，按时间倒序
        recent_trades = sorted(
            self.trading_records, 
            key=lambda x: x.get('timestamp', datetime.min), 
            reverse=True
        )[:limit]
        
        # 确保每个交易记录都有必要的字段
        for trade in recent_trades:
            if 'profit_loss' not in trade:
                trade['profit_loss'] = 0.0
            if 'success' not in trade:
                trade['success'] = trade.get('profit_loss', 0) > 0
        
        return recent_trades

    def _calculate_daily_return(self) -> float:
        """计算当日收益率"""
        if len(self.portfolio_values) < 2:
            return 0.0
        
        today = datetime.now().date()
        today_values = [
            value for timestamp, value in self.portfolio_values 
            if timestamp.date() == today
        ]
        
        if len(today_values) < 2:
            return 0.0
        
        start_value = today_values[0]
        end_value = today_values[-1]
        
        return (end_value - start_value) / start_value if start_value > 0 else 0.0

    def _get_current_positions(self) -> List[Dict[str, Any]]:
        """获取当前持仓信息"""
        # 从交易记录中提取当前持仓
        current_positions = []
        
        # 假设持仓为最近的成功交易且状态为活跃
        for trade in reversed(self.trading_records):
            if (trade.get('success', False) and 
                trade.get('status') in ['open', 'active', None] and
                trade.get('symbol') not in [pos.get('symbol') for pos in current_positions]):
                
                position = {
                    'symbol': trade.get('symbol', 'Unknown'),
                    'quantity': trade.get('quantity', 100),
                    'avg_price': trade.get('price', 0.0),
                    'market_value': trade.get('price', 0.0) * trade.get('quantity', 100),
                    'profit_loss': trade.get('profit_loss', 0.0),
                    'side': trade.get('side', 'BUY')
                }
                current_positions.append(position)
        
        return current_positions


# 全局交易分析服务实例
trading_analytics_service = TradingAnalyticsService()
