import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import './AutoTradingPage.css';

interface TradingStrategy {
  value: string;
  name: string;
  description: string;
  risk_level: string;
  recommended_market: string;
}

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

interface TradingPerformance {
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
}

const AutoTradingPage: React.FC = () => {
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>([]);
  const [availableStrategies, setAvailableStrategies] = useState<TradingStrategy[]>([]);
  const [tradingStatus, setTradingStatus] = useState<TradingStatus | null>(null);
  const [performance, setPerformance] = useState<TradingPerformance | null>(null);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [config, setConfig] = useState({
    max_daily_trades: 50,
    max_daily_loss: 10000,
    max_position_size: 5000,
    volatility_threshold: 0.3
  });

  // 获取可用策略
  const fetchStrategies = async () => {
    try {
      const response = await ApiService.autoTrading.getStrategies();
      // 处理API响应类型
      const strategies = (response as any).data || response;
      if (Array.isArray(strategies)) {
        setAvailableStrategies(strategies);
      } else {
        console.warn('策略数据格式异常:', strategies);
        setAvailableStrategies([]);
      }
    } catch (error) {
      console.error('获取策略失败:', error);
      addLog('获取策略失败: ' + (error as Error).message);
    }
  };

  // 获取交易状态
  const fetchTradingStatus = async () => {
    try {
      const response = await ApiService.autoTrading.getStatus();
      // 处理API响应类型
      const status = (response as any).data || response;
      if (status && typeof status === 'object') {
        setTradingStatus(status);
      }
    } catch (error) {
      console.error('获取交易状态失败:', error);
      addLog('获取交易状态失败: ' + (error as Error).message);
    }
  };

  // 获取交易绩效
  const fetchPerformance = async () => {
    try {
      const response = await ApiService.autoTrading.getPerformance();
      // 处理API响应类型
      const performanceData = (response as any).data || response;
      if (performanceData && typeof performanceData === 'object') {
        setPerformance(performanceData);
      }
    } catch (error) {
      console.error('获取交易绩效失败:', error);
      addLog('获取交易绩效失败: ' + (error as Error).message);
    }
  };

  // 获取风险指标
  const fetchRiskMetrics = async () => {
    try {
      const response = await ApiService.autoTrading.getRiskMetrics();
      // 处理API响应类型
      const riskData = (response as any).data || response;
      if (riskData && typeof riskData === 'object') {
        setRiskMetrics(riskData);
      }
    } catch (error) {
      console.error('获取风险指标失败:', error);
      addLog('获取风险指标失败: ' + (error as Error).message);
    }
  };

  // 添加日志
  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 50));
  };

  // 启动交易
  const startTrading = async () => {
    if (selectedStrategies.length === 0) {
      addLog('请至少选择一个交易策略');
      return;
    }

    setIsLoading(true);
    try {
      // 只使用第一个选中的策略
      const strategyId = selectedStrategies[0];
      await ApiService.autoTrading.start(strategyId, config);
      addLog(`交易启动成功: ${strategyId}`);
      fetchTradingStatus();
    } catch (error: any) {
      addLog(`交易启动失败: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 停止交易
  const stopTrading = async () => {
    setIsLoading(true);
    try {
      await ApiService.autoTrading.stop();
      addLog('交易停止成功');
      fetchTradingStatus();
    } catch (error: any) {
      addLog(`交易停止失败: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 暂停交易
  const pauseTrading = async () => {
    setIsLoading(true);
    try {
      await ApiService.autoTrading.pause();
      addLog('交易暂停成功');
      fetchTradingStatus();
    } catch (error: any) {
      addLog(`交易暂停失败: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 恢复交易
  const resumeTrading = async () => {
    setIsLoading(true);
    try {
      await ApiService.autoTrading.resume();
      addLog('交易恢复成功');
      fetchTradingStatus();
    } catch (error: any) {
      addLog(`交易恢复失败: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 紧急停止
  const emergencyStop = async () => {
    if (!window.confirm('确定要执行紧急停止吗？这将触发所有熔断机制并立即停止所有交易。')) {
      return;
    }

    setIsLoading(true);
    try {
      await ApiService.autoTrading.emergencyStop();
      addLog('紧急停止已执行');
      fetchTradingStatus();
      fetchRiskMetrics();
    } catch (error: any) {
      addLog(`紧急停止失败: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 重置熔断
  const resetBrakes = async () => {
    setIsLoading(true);
    try {
      await ApiService.autoTrading.resetBrakes();
      addLog('紧急熔断已重置');
      fetchTradingStatus();
      fetchRiskMetrics();
    } catch (error: any) {
      addLog(`重置熔断失败: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 配置交易参数
  const configureTrading = async () => {
    setIsLoading(true);
    try {
      await ApiService.autoTrading.configure(config);
      addLog('交易配置更新成功');
    } catch (error: any) {
      addLog(`交易配置更新失败: ${error.message || error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 初始化数据
  useEffect(() => {
    fetchStrategies();
    fetchTradingStatus();
    fetchPerformance();
    fetchRiskMetrics();
  }, []);

  // 设置定时更新
  useEffect(() => {
    const interval = setInterval(() => {
      if (tradingStatus?.status === 'running') {
        fetchTradingStatus();
        fetchPerformance();
        fetchRiskMetrics();
      }
    }, 3000); // 每3秒更新一次

    return () => clearInterval(interval);
  }, [tradingStatus?.status]);

  // 策略选择处理
  const handleStrategyToggle = (strategyValue: string) => {
    setSelectedStrategies(prev => 
      prev.includes(strategyValue)
        ? prev.filter(s => s !== strategyValue)
        : [...prev, strategyValue]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return '#00ff88';
      case 'stopped': return '#ff4444';
      case 'paused': return '#ffaa00';
      case 'emergency_stop': return '#ff0000';
      default: return '#cccccc';
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case '低风险': return '#00ff88';
      case '中等风险': return '#ffaa00';
      case '高风险': return '#ff4444';
      case '极高风险': return '#ff0000';
      default: return '#cccccc';
    }
  };

  return (
    <div className="auto-trading-page">
      <div className="container">
        <div className="header">
          <h1>全自动交易系统</h1>
          <p>智能策略调度 · 实时风险控制 · 专业交易执行</p>
        </div>

        {/* 状态栏 */}
        <div className="status-bar">
          <div className="status-indicator">
            <div 
              className="status-dot" 
              style={{ backgroundColor: getStatusColor(tradingStatus?.status || 'stopped') }}
            ></div>
            <span>交易状态: {tradingStatus?.status === 'running' ? '运行中' : 
                           tradingStatus?.status === 'stopped' ? '已停止' :
                           tradingStatus?.status === 'paused' ? '已暂停' : '紧急停止'}</span>
          </div>
          <div className="status-info">
            <span>活跃策略: {tradingStatus?.active_strategies.length || 0}</span>
            <span>总交易次数: {tradingStatus?.trading_stats.total_trades || 0}</span>
            <span>运行时间: {tradingStatus?.uptime ? Math.round(tradingStatus.uptime / 60) + '分钟' : 'N/A'}</span>
          </div>
        </div>

        <div className="main-content">
          {/* 左侧控制面板 */}
          <div className="control-panel">
            <div className="panel-section">
              <h3>交易策略选择</h3>
              <div className="strategy-list">
                {availableStrategies.map(strategy => (
                  <div key={strategy.value} className="strategy-item">
                    <label className="strategy-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedStrategies.includes(strategy.value)}
                        onChange={() => handleStrategyToggle(strategy.value)}
                        disabled={tradingStatus?.status === 'running'}
                      />
                      <span className="checkmark"></span>
                      <div className="strategy-info">
                        <div className="strategy-name">{strategy.name}</div>
                        <div className="strategy-desc">{strategy.description}</div>
                        <div className="strategy-meta">
                          <span className={`risk-level risk-${strategy.risk_level}`}>
                            {strategy.risk_level}风险
                          </span>
                          <span className="market">{strategy.recommended_market}</span>
                        </div>
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel-section">
              <h3>交易控制</h3>
              <div className="control-buttons">
                <button 
                  className="btn btn-start"
                  onClick={startTrading}
                  disabled={isLoading || tradingStatus?.status === 'running' || selectedStrategies.length === 0}
                >
                  启动交易
                </button>
                <button 
                  className="btn btn-stop"
                  onClick={stopTrading}
                  disabled={isLoading || tradingStatus?.status === 'stopped'}
                >
                  停止交易
                </button>
                <button 
                  className="btn btn-pause"
                  onClick={pauseTrading}
                  disabled={isLoading || tradingStatus?.status !== 'running'}
                >
                  暂停交易
                </button>
                <button 
                  className="btn btn-resume"
                  onClick={resumeTrading}
                  disabled={isLoading || tradingStatus?.status !== 'paused'}
                >
                  恢复交易
                </button>
              </div>
            </div>

            <div className="panel-section">
              <h3>紧急控制</h3>
              <div className="emergency-controls">
                <button 
                  className="btn btn-emergency"
                  onClick={emergencyStop}
                  disabled={isLoading || tradingStatus?.status === 'stopped'}
                >
                  紧急停止
                </button>
                <button 
                  className="btn btn-reset"
                  onClick={resetBrakes}
                  disabled={isLoading}
                >
                  重置熔断
                </button>
              </div>
            </div>

            <div className="panel-section">
              <h3>交易配置</h3>
              <div className="config-form">
                <div className="config-item">
                  <label>单日最大交易次数:</label>
                  <input
                    type="number"
                    value={config.max_daily_trades}
                    onChange={(e) => setConfig(prev => ({...prev, max_daily_trades: parseInt(e.target.value)}))}
                  />
                </div>
                <div className="config-item">
                  <label>单日最大亏损:</label>
                  <input
                    type="number"
                    value={config.max_daily_loss}
                    onChange={(e) => setConfig(prev => ({...prev, max_daily_loss: parseFloat(e.target.value)}))}
                  />
                </div>
                <div className="config-item">
                  <label>最大仓位大小:</label>
                  <input
                    type="number"
                    value={config.max_position_size}
                    onChange={(e) => setConfig(prev => ({...prev, max_position_size: parseFloat(e.target.value)}))}
                  />
                </div>
                <div className="config-item">
                  <label>波动率阈值:</label>
                  <input
                    type="number"
                    step="0.01"
                    value={config.volatility_threshold}
                    onChange={(e) => setConfig(prev => ({...prev, volatility_threshold: parseFloat(e.target.value)}))}
                  />
                </div>
                <button 
                  className="btn btn-configure"
                  onClick={configureTrading}
                  disabled={isLoading}
                >
                  更新配置
                </button>
              </div>
            </div>
          </div>

          {/* 右侧信息面板 */}
          <div className="info-panel">
            <div className="panel-section">
              <h3>交易绩效</h3>
              {performance && (
                <div className="performance-grid">
                  <div className="metric-card">
                    <div className="metric-value">{performance.total_trades}</div>
                    <div className="metric-label">总交易次数</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{(performance.success_rate * 100).toFixed(1)}%</div>
                    <div className="metric-label">成功率</div>
                  </div>
                  <div className="metric-card">
                    <div className={`metric-value ${performance.total_profit_loss >= 0 ? 'positive' : 'negative'}`}>
                      ${performance.total_profit_loss.toFixed(2)}
                    </div>
                    <div className="metric-label">总盈亏</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{performance.current_positions}</div>
                    <div className="metric-label">当前持仓</div>
                  </div>
                </div>
              )}
            </div>

            <div className="panel-section">
              <h3>风险指标</h3>
              {riskMetrics && (
                <div className="risk-grid">
                  <div className="risk-item">
                    <span className="risk-label">当前回撤:</span>
                    <span className="risk-value">{(riskMetrics.current_drawdown * 100).toFixed(2)}%</span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-label">最大回撤:</span>
                    <span className="risk-value">{(riskMetrics.max_drawdown * 100).toFixed(2)}%</span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-label">波动率:</span>
                    <span className="risk-value">{(riskMetrics.volatility * 100).toFixed(2)}%</span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-label">夏普比率:</span>
                    <span className="risk-value">{riskMetrics.sharpe_ratio.toFixed(2)}</span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-label">活跃熔断:</span>
                    <span className="risk-value">{riskMetrics.active_brakes}</span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-label">风险等级:</span>
                    <span 
                      className="risk-level" 
                      style={{ color: getRiskLevelColor(riskMetrics.risk_level) }}
                    >
                      {riskMetrics.risk_level}
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div className="panel-section">
              <h3>系统日志</h3>
              <div className="log-container">
                {logs.map((log, index) => (
                  <div key={index} className="log-entry">
                    {log}
                  </div>
                ))}
                {logs.length === 0 && (
                  <div className="no-logs">暂无日志记录</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoTradingPage;
