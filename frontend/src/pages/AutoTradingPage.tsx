/**
 * 全自动交易系统页面
 * 实现完整的自动化交易功能，包括策略调度、订单管理、风险控制和状态监控
 * 遵循PROJECT_UI_STANDARDS.md的彭博终端风格标准
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ApiService } from '../services/api';
import './AutoTradingPage.css';

interface TradingStatus {
  status: string;
  active_strategies: string[];
  trading_stats: {
    total_trades: number;
    successful_trades: number;
    total_profit_loss: number;
    current_positions: any[];
    daily_trades_count: number;
    daily_profit_loss: number;
  };
  risk_metrics: {
    current_drawdown: number;
    max_drawdown: number;
    volatility: number;
    sharpe_ratio: number;
    var_95: number;
  };
  emergency_brakes: {
    market_volatility_brake: boolean;
    max_daily_loss_brake: boolean;
    system_error_brake: boolean;
    network_disruption_brake: boolean;
  };
  trading_config: {
    max_daily_trades: number;
    max_daily_loss: number;
    max_position_size: number;
    volatility_threshold: number;
  };
  last_trade_time: string | null;
  uptime: number | null;
}

interface StrategyInfo {
  value: string;
  name: string;
  description: string;
  risk_level: string;
  recommended_market: string;
}

interface PerformanceData {
  total_trades: number;
  success_rate: number;
  total_profit_loss: number;
  current_positions: number;
  current_drawdown: number;
  max_drawdown: number;
  sharpe_ratio: number;
  volatility: number;
}

interface RiskMetrics {
  current_drawdown: number;
  max_drawdown: number;
  volatility: number;
  sharpe_ratio: number;
  active_brakes: number;
  brake_details: Record<string, boolean>;
  risk_level: string;
  liquidity_risk: number;
  concentration_risk: number;
  market_risk: number;
  credit_risk: number;
}

interface TradeLog {
  id: string;
  timestamp: string;
  symbol: string;
  action: string;
  quantity: number;
  price: number;
  profit_loss: number;
  strategy: string;
  status: string;
}

interface TradingHistory {
  date: string;
  total_trades: number;
  successful_trades: number;
  profit_loss: number;
  volume: number;
  win_rate: number;
}

interface RealTimeMonitor {
  active_positions: Position[];
  account_balance: number;
  available_balance: number;
  total_equity: number;
  unrealized_pnl: number;
  realized_pnl: number;
  margin_used: number;
  margin_available: number;
  leverage: number;
  risk_score: number;
}

interface Position {
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  realized_pnl: number;
  margin_used: number;
  leverage: number;
  position_type: 'LONG' | 'SHORT';
  open_time: string;
}

interface RiskAnalysis {
  portfolio_risk: number;
  position_concentration: number;
  correlation_matrix: Record<string, number>;
  stress_test_results: {
    scenario: string;
    potential_loss: number;
    probability: number;
  }[];
  var_metrics: {
    var_95: number;
    var_99: number;
    expected_shortfall: number;
  };
  liquidity_metrics: {
    bid_ask_spread: number;
    market_depth: number;
    liquidation_time: number;
  };
}

interface StrategyComparison {
  strategy_name: string;
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  avg_profit_per_trade: number;
  risk_adjusted_return: number;
}

// API响应类型定义
interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

interface StatusResponse {
  success: boolean;
  status: TradingStatus;
  timestamp: string;
}

interface StrategiesResponse {
  success: boolean;
  strategies: StrategyInfo[];
}

interface PerformanceResponse {
  success: boolean;
  performance: PerformanceData;
  timestamp: string;
}

interface RiskMetricsResponse {
  success: boolean;
  risk_assessment: RiskMetrics;
  timestamp: string;
}

interface OperationResponse {
  success: boolean;
  message?: string;
}

const AutoTradingPage: React.FC = () => {
  const [tradingStatus, setTradingStatus] = useState<TradingStatus | null>(null);
  const [strategies, setStrategies] = useState<StrategyInfo[]>([]);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [tradeLogs, setTradeLogs] = useState<TradeLog[]>([]);
  const [tradingHistory, setTradingHistory] = useState<TradingHistory[]>([]);
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>(['trend_following']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [configForm, setConfigForm] = useState({
    max_daily_trades: 50,
    max_daily_loss: 10000,
    max_position_size: 5000,
    volatility_threshold: 0.3
  });

  // 从本地存储加载配置
  useEffect(() => {
    const savedConfig = localStorage.getItem('auto_trading_config');
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig);
        setConfigForm(prev => ({ ...prev, ...parsedConfig }));
      } catch (err) {
        console.error('加载保存的配置失败:', err);
      }
    }
  }, []);

  // 保存配置到本地存储
  const saveConfigToStorage = (config: typeof configForm) => {
    try {
      localStorage.setItem('auto_trading_config', JSON.stringify(config));
    } catch (err) {
      console.error('保存配置到本地存储失败:', err);
    }
  };

  // 加载数据
  const loadData = useCallback(async () => {
    try {
      setError(null);
      
      // 加载交易状态
      const statusResponse = await ApiService.autoTrading.getStatus();
      if (statusResponse && statusResponse.success && statusResponse.status) {
        setTradingStatus(statusResponse.status);
      }

      // 加载策略列表
      const strategiesResponse = await ApiService.autoTrading.getStrategies();
      if (strategiesResponse && strategiesResponse.success && strategiesResponse.strategies) {
        setStrategies(strategiesResponse.strategies);
      }

      // 加载绩效数据
      const performanceResponse = await ApiService.autoTrading.getPerformance();
      if (performanceResponse && performanceResponse.success && performanceResponse.performance) {
        setPerformance(performanceResponse.performance);
      }

      // 加载风险指标
      const riskResponse = await ApiService.autoTrading.getRiskMetrics();
      if (riskResponse && riskResponse.success && riskResponse.risk_assessment) {
        setRiskMetrics(riskResponse.risk_assessment);
      }

      // 加载交易日志
      const logsResponse = await ApiService.autoTrading.getTradeLogs();
      if (logsResponse && logsResponse.success && logsResponse.logs) {
        setTradeLogs(logsResponse.logs);
      }

      // 加载交易历史
      const historyResponse = await ApiService.autoTrading.getTradingHistory();
      if (historyResponse && historyResponse.success && historyResponse.history) {
        setTradingHistory(historyResponse.history);
      }

    } catch (err) {
      console.error('加载数据失败:', err);
      setError('加载数据失败，请检查后端服务是否正常运行');
    }
  }, []);

  // 初始化加载
  useEffect(() => {
    loadData();
    
    // 设置定时刷新
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [loadData]);

  // 启动交易
  const handleStartTrading = async () => {
    if (selectedStrategies.length === 0) {
      setError('请至少选择一个交易策略');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.autoTrading.start(selectedStrategies);
      if (response.success) {
        await loadData(); // 重新加载数据
      } else {
        setError(response.message || '启动交易失败');
      }
    } catch (err) {
      console.error('启动交易失败:', err);
      setError('启动交易失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  // 停止交易
  const handleStopTrading = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.autoTrading.stop();
      if (response.success) {
        await loadData(); // 重新加载数据
      } else {
        setError(response.message || '停止交易失败');
      }
    } catch (err) {
      console.error('停止交易失败:', err);
      setError('停止交易失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  // 暂停交易
  const handlePauseTrading = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.autoTrading.pause();
      if (response.success) {
        await loadData(); // 重新加载数据
      } else {
        setError(response.message || '暂停交易失败');
      }
    } catch (err) {
      console.error('暂停交易失败:', err);
      setError('暂停交易失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  // 恢复交易
  const handleResumeTrading = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.autoTrading.resume();
      if (response.success) {
        await loadData(); // 重新加载数据
      } else {
        setError(response.message || '恢复交易失败');
      }
    } catch (err) {
      console.error('恢复交易失败:', err);
      setError('恢复交易失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  // 紧急停止
  const handleEmergencyStop = async () => {
    if (!window.confirm('确定要执行紧急停止吗？这将触发所有熔断机制并立即停止所有交易。')) {
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.autoTrading.emergencyStop();
      if (response.success) {
        await loadData(); // 重新加载数据
      } else {
        setError(response.message || '紧急停止失败');
      }
    } catch (err) {
      console.error('紧急停止失败:', err);
      setError('紧急停止失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  // 重置熔断
  const handleResetBrakes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.autoTrading.resetBrakes();
      if (response.success) {
        await loadData(); // 重新加载数据
      } else {
        setError(response.message || '重置熔断失败');
      }
    } catch (err) {
      console.error('重置熔断失败:', err);
      setError('重置熔断失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  // 更新配置
  const handleUpdateConfig = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.autoTrading.configure(configForm) as OperationResponse;
      if (response.success) {
        saveConfigToStorage(configForm); // 保存配置到本地存储
        await loadData(); // 重新加载数据
      } else {
        setError(response.message || '更新配置失败');
      }
    } catch (err) {
      console.error('更新配置失败:', err);
      setError('更新配置失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  };

  // 策略选择切换
  const handleStrategyToggle = (strategyValue: string) => {
    setSelectedStrategies(prev => 
      prev.includes(strategyValue)
        ? prev.filter(s => s !== strategyValue)
        : [...prev, strategyValue]
    );
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return '#00ff88';
      case 'stopped': return '#ff4444';
      case 'paused': return '#ffaa00';
      case 'emergency_stop': return '#ff0066';
      default: return '#8a94a6';
    }
  };

  // 获取风险等级颜色
  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case '低风险': return '#00ff88';
      case '中等风险': return '#ffaa00';
      case '高风险': return '#ff4444';
      case '极高风险': return '#ff0066';
      default: return '#8a94a6';
    }
  };

  // 格式化数字
  const formatNumber = (num: number, decimals: number = 2) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  };

  // 格式化百分比
  const formatPercent = (num: number) => {
    return `${num >= 0 ? '+' : ''}${formatNumber(num * 100)}%`;
  };

  return (
    <div className="auto-trading-container">
      {/* 顶部状态栏 */}
      <div className="status-bar">
        <div className="status-item">
          <span className="status-label">系统状态:</span>
          <span 
            className="status-value" 
            style={{ color: tradingStatus ? getStatusColor(tradingStatus.status) : '#8a94a6' }}
          >
            {tradingStatus ? tradingStatus.status.toUpperCase() : '加载中...'}
          </span>
        </div>
        <div className="status-item">
          <span className="status-label">运行时间:</span>
          <span className="status-value">
            {tradingStatus?.uptime ? `${Math.floor(tradingStatus.uptime / 60)}分钟` : '--'}
          </span>
        </div>
        <div className="status-item">
          <span className="status-label">最后交易:</span>
          <span className="status-value">
            {tradingStatus?.last_trade_time 
              ? new Date(tradingStatus.last_trade_time).toLocaleTimeString()
              : '--'
            }
          </span>
        </div>
        <div className="status-item">
          <span className="status-label">风险等级:</span>
          <span 
            className="status-value"
            style={{ color: riskMetrics ? getRiskColor(riskMetrics.risk_level) : '#8a94a6' }}
          >
            {riskMetrics?.risk_level || '--'}
          </span>
        </div>
      </div>

      {/* 主内容区域 - 两栏布局 */}
      <div className="main-content">
        {/* 左侧面板 - 控制区 */}
        <div className="left-panel">
          {/* 交易控制 */}
          <div className="control-section">
            <h3 className="section-title">交易控制</h3>
            <div className="control-buttons">
              <button 
                className={`control-btn ${tradingStatus?.status === 'running' ? 'active' : ''}`}
                onClick={handleStartTrading}
                disabled={loading || tradingStatus?.status === 'running'}
              >
                启动交易
              </button>
              <button 
                className={`control-btn ${tradingStatus?.status === 'stopped' ? 'active' : ''}`}
                onClick={handleStopTrading}
                disabled={loading || tradingStatus?.status === 'stopped'}
              >
                停止交易
              </button>
              <button 
                className={`control-btn ${tradingStatus?.status === 'paused' ? 'active' : ''}`}
                onClick={handlePauseTrading}
                disabled={loading || tradingStatus?.status !== 'running'}
              >
                暂停交易
              </button>
              <button 
                className={`control-btn ${tradingStatus?.status === 'running' ? 'active' : ''}`}
                onClick={handleResumeTrading}
                disabled={loading || tradingStatus?.status !== 'paused'}
              >
                恢复交易
              </button>
            </div>
          </div>

          {/* 策略选择 */}
          <div className="control-section">
            <h3 className="section-title">交易策略</h3>
            <div className="strategies-list">
              {strategies.map(strategy => (
                <div key={strategy.value} className="strategy-item">
                  <label className="strategy-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedStrategies.includes(strategy.value)}
                      onChange={() => handleStrategyToggle(strategy.value)}
                      disabled={loading || tradingStatus?.status === 'running'}
                    />
                    <span className="strategy-name">{strategy.name}</span>
                  </label>
                  <div className="strategy-info">
                    <span className="strategy-risk" style={{ color: getRiskColor(strategy.risk_level) }}>
                      {strategy.risk_level}
                    </span>
                    <div className="strategy-desc">{strategy.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 风险控制 */}
          <div className="control-section">
            <h3 className="section-title">风险控制</h3>
            <div className="emergency-controls">
              <button 
                className="emergency-btn"
                onClick={handleEmergencyStop}
                disabled={loading || tradingStatus?.status === 'stopped'}
              >
                紧急停止
              </button>
              <button 
                className="reset-btn"
                onClick={handleResetBrakes}
                disabled={loading}
              >
                重置熔断
              </button>
            </div>
            
            {/* 熔断状态 */}
            <div className="brakes-status">
              <h4>熔断状态</h4>
              {tradingStatus && Object.entries(tradingStatus.emergency_brakes).map(([brake, active]) => (
                <div key={brake} className="brake-item">
                  <span className="brake-name">{brake.replace(/_/g, ' ')}</span>
                  <span 
                    className={`brake-status ${active ? 'active' : ''}`}
                    style={{ color: active ? '#ff4444' : '#00ff88' }}
                  >
                    {active ? '触发' : '正常'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧面板 - 数据显示区 */}
        <div className="right-panel">
          {/* 绩效数据 */}
          <div className="data-section">
            <h3 className="section-title">交易绩效</h3>
            <div className="performance-grid">
              <div className="metric-card">
                <div className="metric-label">总交易次数</div>
                <div className="metric-value">
                  {performance?.total_trades || 0}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">成功率</div>
                <div className="metric-value" style={{ 
                  color: performance && performance.success_rate >= 0.5 ? '#00ff88' : '#ff4444'
                }}>
                  {performance ? formatNumber(performance.success_rate * 100, 1) + '%' : '--'}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">总盈亏</div>
                <div className="metric-value" style={{ 
                  color: performance && performance.total_profit_loss >= 0 ? '#00ff88' : '#ff4444'
                }}>
                  {performance ? formatNumber(performance.total_profit_loss) : '--'}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">当前持仓</div>
                <div className="metric-value">
                  {performance?.current_positions || 0}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">当前回撤</div>
                <div className="metric-value" style={{ 
                  color: performance && performance.current_drawdown >= 0 ? '#00ff88' : '#ff4444'
                }}>
                  {performance ? formatPercent(performance.current_drawdown) : '--'}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">最大回撤</div>
                <div className="metric-value" style={{ 
                  color: performance && performance.max_drawdown >= 0 ? '#00ff88' : '#ff4444'
                }}>
                  {performance ? formatPercent(performance.max_drawdown) : '--'}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">夏普比率</div>
                <div className="metric-value" style={{ 
                  color: performance && performance.sharpe_ratio >= 0 ? '#00ff88' : '#ff4444'
                }}>
                  {performance ? formatNumber(performance.sharpe_ratio, 3) : '--'}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">波动率</div>
                <div className="metric-value">
                  {performance ? formatPercent(performance.volatility) : '--'}
                </div>
              </div>
            </div>
          </div>

          {/* 交易配置 */}
          <div className="data-section">
            <h3 className="section-title">交易配置</h3>
            <div className="config-form">
              <div className="config-row">
                <label className="config-label">单日最大交易次数</label>
                <input
                  type="number"
                  className="config-input"
                  value={configForm.max_daily_trades}
                  onChange={(e) => setConfigForm(prev => ({
                    ...prev,
                    max_daily_trades: parseInt(e.target.value) || 0
                  }))}
                  disabled={loading}
                />
              </div>
              <div className="config-row">
                <label className="config-label">单日最大亏损</label>
                <input
                  type="number"
                  className="config-input"
                  value={configForm.max_daily_loss}
                  onChange={(e) => setConfigForm(prev => ({
                    ...prev,
                    max_daily_loss: parseFloat(e.target.value) || 0
                  }))}
                  disabled={loading}
                />
              </div>
              <div className="config-row">
                <label className="config-label">最大仓位大小</label>
                <input
                  type="number"
                  className="config-input"
                  value={configForm.max_position_size}
                  onChange={(e) => setConfigForm(prev => ({
                    ...prev,
                    max_position_size: parseFloat(e.target.value) || 0
                  }))}
                  disabled={loading}
                />
              </div>
              <div className="config-row">
                <label className="config-label">波动率阈值</label>
                <input
                  type="number"
                  step="0.01"
                  className="config-input"
                  value={configForm.volatility_threshold}
                  onChange={(e) => setConfigForm(prev => ({
                    ...prev,
                    volatility_threshold: parseFloat(e.target.value) || 0
                  }))}
                  disabled={loading}
                />
              </div>
              <button 
                className="update-config-btn"
                onClick={handleUpdateConfig}
                disabled={loading}
              >
                更新配置
              </button>
            </div>
          </div>

          {/* 活跃策略 */}
          <div className="data-section">
            <h3 className="section-title">活跃策略</h3>
            <div className="active-strategies">
              {tradingStatus?.active_strategies && tradingStatus.active_strategies.length > 0 ? (
                tradingStatus.active_strategies.map(strategy => {
                  const strategyInfo = strategies.find(s => s.value === strategy);
                  return (
                    <div key={strategy} className="active-strategy">
                      <span className="strategy-badge">{strategyInfo?.name || strategy}</span>
                      <span className="strategy-market">{strategyInfo?.recommended_market}</span>
                    </div>
                  );
                })
              ) : (
                <div className="no-strategies">暂无活跃策略</div>
              )}
            </div>
          </div>

          {/* 交易日志面板 */}
          <div className="data-section">
            <h3 className="section-title">实时交易日志</h3>
            <div className="trade-logs-panel">
              <div className="logs-header">
                <span>时间</span>
                <span>品种</span>
                <span>操作</span>
                <span>数量</span>
                <span>价格</span>
                <span>盈亏</span>
                <span>策略</span>
                <span>状态</span>
              </div>
              <div className="logs-content">
                {tradeLogs.length > 0 ? (
                  tradeLogs.slice(0, 10).map(log => (
                    <div key={log.id} className="log-entry">
                      <span className="log-time">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className="log-symbol">{log.symbol}</span>
                      <span 
                        className={`log-action ${log.action.toLowerCase()}`}
                        style={{ 
                          color: log.action === 'BUY' ? '#00ff88' : 
                                 log.action === 'SELL' ? '#ff4444' : '#8a94a6'
                        }}
                      >
                        {log.action}
                      </span>
                      <span className="log-quantity">{log.quantity}</span>
                      <span className="log-price">${log.price.toFixed(2)}</span>
                      <span 
                        className="log-profit-loss"
                        style={{ color: log.profit_loss >= 0 ? '#00ff88' : '#ff4444' }}
                      >
                        {log.profit_loss >= 0 ? '+' : ''}{log.profit_loss.toFixed(2)}
                      </span>
                      <span className="log-strategy">
                        {log.strategy.replace('_', ' ').toUpperCase()}
                      </span>
                      <span 
                        className={`log-status ${log.status.toLowerCase()}`}
                        style={{ 
                          color: log.status === 'EXECUTED' ? '#00ff88' : 
                                 log.status === 'FAILED' ? '#ff4444' : '#ffaa00'
                        }}
                      >
                        {log.status}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="no-logs">暂无交易记录</div>
                )}
              </div>
              {tradeLogs.length > 10 && (
                <div className="logs-footer">
                  显示最近 10 条记录，共 {tradeLogs.length} 条
                </div>
              )}
            </div>
          </div>

          {/* 交易历史图表 */}
          <div className="data-section">
            <h3 className="section-title">交易历史统计</h3>
            <div className="trading-history-chart">
              <div className="history-stats">
                <div className="history-stat">
                  <span className="stat-label">总交易天数</span>
                  <span className="stat-value">{tradingHistory.length}</span>
                </div>
                <div className="history-stat">
                  <span className="stat-label">平均胜率</span>
                  <span className="stat-value">
                    {tradingHistory.length > 0 
                      ? ((tradingHistory.reduce((sum, day) => sum + day.win_rate, 0) / tradingHistory.length) * 100).toFixed(1) + '%'
                      : '--'
                    }
                  </span>
                </div>
                <div className="history-stat">
                  <span className="stat-label">日均交易</span>
                  <span className="stat-value">
                    {tradingHistory.length > 0 
                      ? (tradingHistory.reduce((sum, day) => sum + day.total_trades, 0) / tradingHistory.length).toFixed(1)
                      : '--'
                    }
                  </span>
                </div>
              </div>
              <div className="history-grid">
                {tradingHistory.slice(0, 7).map(day => (
                  <div key={day.date} className="history-day">
                    <div className="day-date">{day.date}</div>
                    <div className="day-stats">
                      <div className="day-stat">
                        <span>交易次数</span>
                        <span>{day.total_trades}</span>
                      </div>
                      <div className="day-stat">
                        <span>胜率</span>
                        <span style={{ color: day.win_rate >= 0.5 ? '#00ff88' : '#ff4444' }}>
                          {(day.win_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="day-stat">
                        <span>盈亏</span>
                        <span style={{ color: day.profit_loss >= 0 ? '#00ff88' : '#ff4444' }}>
                          {day.profit_loss >= 0 ? '+' : ''}{day.profit_loss.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 错误显示 */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 加载状态 */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <span>处理中...</span>
        </div>
      )}
    </div>
  );
};

export default AutoTradingPage;
