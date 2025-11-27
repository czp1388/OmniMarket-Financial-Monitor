import React, { useState, useEffect } from 'react';
import { realTimeDataService } from '../services/realTimeDataService';
import './SettingsPage.css';

interface SymbolData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  last: number;
  open: number;
  high: number;
  low: number;
  close: number;
  timestamp: string;
  type: string;
  source: string;
  lastUpdate: string;
}

const SettingsPage: React.FC = () => {
  const [symbolsData, setSymbolsData] = useState<SymbolData[]>([]);
  const [systemStatus, setSystemStatus] = useState({
    connection: '正常',
    latency: '25ms',
    marketStatus: '交易中',
    lastUpdate: new Date().toLocaleString('zh-CN')
  });
  const [activeNav, setActiveNav] = useState('常规设置');
  const [settings, setSettings] = useState({
    // 数据源设置
    dataSources: {
      crypto: true,
      stocks: true,
      forex: false,
      futures: false
    },
    // 通知设置
    notifications: {
      email: true,
      push: true,
      sound: false,
      telegram: false
    },
    // 图表设置
    chart: {
      theme: 'dark',
      timezone: 'Asia/Shanghai',
      defaultTimeframe: '1h'
    },
    // 风险设置
    risk: {
      maxDrawdown: 10,
      maxPositionSize: 25,
      stopLossEnabled: true
    },
    // 系统设置
    system: {
      autoRefresh: true,
      dataQualityMonitor: true,
      alertStrategyEngine: false
    },
    // 数据质量监控设置
    dataQuality: {
      integrityCheck: true,
      anomalyDetection: true,
      sourceHealthMonitor: true,
      latencyAlert: true,
      dataDriftMonitor: false,
      crossValidation: true,
      completenessThreshold: 95,
      accuracyThreshold: 98,
      latencyThreshold: 1000
    },
    // 预警策略引擎设置
    alertEngine: {
      graphicalConfig: true,
      multiCondition: true,
      technicalCross: true,
      andOrLogic: true,
      webhookIntegration: false,
      autoResponse: false,
      reportGeneration: true,
      notificationTemplates: true
    }
  });

  const handleDataSourceChange = (source: string, value: boolean) => {
    setSettings({
      ...settings,
      dataSources: {
        ...settings.dataSources,
        [source]: value
      }
    });
  };

  const handleNotificationChange = (type: string, value: boolean) => {
    setSettings({
      ...settings,
      notifications: {
        ...settings.notifications,
        [type]: value
      }
    });
  };

  const handleChartSettingChange = (setting: string, value: string) => {
    setSettings({
      ...settings,
      chart: {
        ...settings.chart,
        [setting]: value
      }
    });
  };

  const handleRiskSettingChange = (setting: string, value: number | boolean) => {
    setSettings({
      ...settings,
      risk: {
        ...settings.risk,
        [setting]: value
      }
    });
  };

  const handleSystemSettingChange = (setting: string, value: boolean) => {
    setSettings({
      ...settings,
      system: {
        ...settings.system,
        [setting]: value
      }
    });
  };

  const handleDataQualityChange = (setting: string, value: boolean | number) => {
    setSettings({
      ...settings,
      dataQuality: {
        ...settings.dataQuality,
        [setting]: value
      }
    });
  };

  const handleAlertEngineChange = (setting: string, value: boolean) => {
    setSettings({
      ...settings,
      alertEngine: {
        ...settings.alertEngine,
        [setting]: value
      }
    });
  };

  // 使用realTimeDataService获取实时数据
  useEffect(() => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
    
    const stopUpdates = realTimeDataService.startRealTimeUpdates(
      (data: any[]) => {
        const updatedSymbols = data.map(item => ({
          symbol: item.symbol,
          price: item.price,
          change: item.change,
          changePercent: item.changePercent,
          volume: item.volume || 0,
          last: item.price,
          open: item.open || item.price,
          high: item.high || item.price,
          low: item.low || item.price,
          close: item.close || item.price,
          timestamp: item.lastUpdate || new Date().toISOString(),
          type: item.type || 'crypto',
          source: item.source || 'realTimeDataService',
          lastUpdate: item.lastUpdate || new Date().toLocaleTimeString('zh-CN', { hour12: false })
        }));
        setSymbolsData(updatedSymbols);
        setSystemStatus(prev => ({
          ...prev,
          lastUpdate: new Date().toLocaleString('zh-CN')
        }));
      },
      symbols,
      5000 // 5秒更新间隔
    );

    return stopUpdates;
  }, []);

  const saveSettings = async () => {
    try {
      // 调用API保存设置
      console.log('保存设置:', settings);
      // 这里可以添加实际的API调用
      // await ApiService.users.updateProfile({ settings });
      alert('设置已保存！');
    } catch (error) {
      console.error('保存设置失败:', error);
      alert('保存设置失败，请重试！');
    }
  };

  const formatNumber = (num: number): string => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const formatPercent = (num: number): string => {
    return `${num > 0 ? '+' : ''}${num.toFixed(2)}%`;
  };

  return (
    <div className="settings-main">
      {/* 左侧实时监控面板 */}
        <div className="symbols-sidebar">
          <div className="sidebar-header">
            <h3>实时监控</h3>
            <span className="update-indicator">实时数据</span>
          </div>
          <div className="symbols-list">
            {symbolsData.map((symbol) => (
              <div key={symbol.symbol} className="symbol-card">
                <div className="symbol-header">
                  <span className="symbol-name">{symbol.symbol}</span>
                  <span className={`symbol-change ${symbol.changePercent >= 0 ? 'positive' : 'negative'}`}>
                    {formatPercent(symbol.changePercent)}
                  </span>
                </div>
                <div className="symbol-details">
                  <span className="symbol-price">
                    {symbol.symbol.includes('/') ? '$' : ''}{formatNumber(symbol.price)}
                  </span>
                  <span className={`symbol-absolute ${symbol.change >= 0 ? 'positive' : 'negative'}`}>
                    {symbol.change >= 0 ? '+' : ''}{formatNumber(symbol.change)}
                  </span>
                </div>
                <div className="symbol-volume">
                  成交量: {symbol.volume.toLocaleString()}
                </div>
                <div className="symbol-range">
                  H: {formatNumber(symbol.high)} L: {formatNumber(symbol.low)}
                </div>
              </div>
            ))}
          </div>
        </div>

      {/* 右侧设置内容 */}
      <div className="settings-content">
        {/* 功能导航栏 - 彭博终端风格 */}
        <div className="settings-nav-bar">
          <button 
            className={`settings-nav-btn ${activeNav === '常规设置' ? 'active' : ''}`}
            onClick={() => setActiveNav('常规设置')}
          >
            常规设置
          </button>
          <button 
            className={`settings-nav-btn ${activeNav === '数据源' ? 'active' : ''}`}
            onClick={() => setActiveNav('数据源')}
          >
            数据源
          </button>
          <button 
            className={`settings-nav-btn ${activeNav === '通知' ? 'active' : ''}`}
            onClick={() => setActiveNav('通知')}
          >
            通知
          </button>
          <button 
            className={`settings-nav-btn ${activeNav === '图表' ? 'active' : ''}`}
            onClick={() => setActiveNav('图表')}
          >
            图表
          </button>
          <button 
            className={`settings-nav-btn ${activeNav === '风险' ? 'active' : ''}`}
            onClick={() => setActiveNav('风险')}
          >
            风险
          </button>
          <button 
            className={`settings-nav-btn ${activeNav === '数据质量' ? 'active' : ''}`}
            onClick={() => setActiveNav('数据质量')}
          >
            数据质量
          </button>
          <button 
            className={`settings-nav-btn ${activeNav === '预警策略' ? 'active' : ''}`}
            onClick={() => setActiveNav('预警策略')}
          >
            预警策略
          </button>
        </div>

        <div className="settings-header">
          <h1>系统设置</h1>
          <p>配置您的监控系统偏好</p>
        </div>

        <div className="settings-grid">
          {/* 数据源设置 */}
          <div className="settings-card">
            <h2>数据源设置</h2>
            <div className="checkbox-grid">
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="crypto"
                  checked={settings.dataSources.crypto}
                  onChange={(e) => handleDataSourceChange('crypto', e.target.checked)}
                />
                <label htmlFor="crypto">
                  <span className={`status-indicator ${settings.dataSources.crypto ? 'status-active' : 'status-inactive'}`}></span>
                  加密货币数据
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="stocks"
                  checked={settings.dataSources.stocks}
                  onChange={(e) => handleDataSourceChange('stocks', e.target.checked)}
                />
                <label htmlFor="stocks">
                  <span className={`status-indicator ${settings.dataSources.stocks ? 'status-active' : 'status-inactive'}`}></span>
                  股票数据
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="forex"
                  checked={settings.dataSources.forex}
                  onChange={(e) => handleDataSourceChange('forex', e.target.checked)}
                />
                <label htmlFor="forex">
                  <span className={`status-indicator ${settings.dataSources.forex ? 'status-active' : 'status-inactive'}`}></span>
                  外汇数据
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="futures"
                  checked={settings.dataSources.futures}
                  onChange={(e) => handleDataSourceChange('futures', e.target.checked)}
                />
                <label htmlFor="futures">
                  <span className={`status-indicator ${settings.dataSources.futures ? 'status-active' : 'status-inactive'}`}></span>
                  期货数据
                </label>
              </div>
            </div>
          </div>

          {/* 通知设置 */}
          <div className="settings-card">
            <h2>通知设置</h2>
            <div className="checkbox-grid">
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="email"
                  checked={settings.notifications.email}
                  onChange={(e) => handleNotificationChange('email', e.target.checked)}
                />
                <label htmlFor="email">
                  <span className={`status-indicator ${settings.notifications.email ? 'status-active' : 'status-inactive'}`}></span>
                  邮件通知
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="push"
                  checked={settings.notifications.push}
                  onChange={(e) => handleNotificationChange('push', e.target.checked)}
                />
                <label htmlFor="push">
                  <span className={`status-indicator ${settings.notifications.push ? 'status-active' : 'status-inactive'}`}></span>
                  推送通知
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="sound"
                  checked={settings.notifications.sound}
                  onChange={(e) => handleNotificationChange('sound', e.target.checked)}
                />
                <label htmlFor="sound">
                  <span className={`status-indicator ${settings.notifications.sound ? 'status-active' : 'status-inactive'}`}></span>
                  声音提示
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="telegram"
                  checked={settings.notifications.telegram}
                  onChange={(e) => handleNotificationChange('telegram', e.target.checked)}
                />
                <label htmlFor="telegram">
                  <span className={`status-indicator ${settings.notifications.telegram ? 'status-active' : 'status-inactive'}`}></span>
                  Telegram通知
                </label>
              </div>
            </div>
          </div>

          {/* 图表设置 */}
          <div className="settings-card">
            <h2>图表设置</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="theme">主题</label>
                <select
                  id="theme"
                  value={settings.chart.theme}
                  onChange={(e) => handleChartSettingChange('theme', e.target.value)}
                  className="form-control"
                >
                  <option value="light">浅色</option>
                  <option value="dark">深色</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="timezone">时区</label>
                <select
                  id="timezone"
                  value={settings.chart.timezone}
                  onChange={(e) => handleChartSettingChange('timezone', e.target.value)}
                  className="form-control"
                >
                  <option value="Asia/Shanghai">北京时间</option>
                  <option value="America/New_York">纽约时间</option>
                  <option value="Europe/London">伦敦时间</option>
                  <option value="UTC">UTC</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="timeframe">默认时间周期</label>
                <select
                  id="timeframe"
                  value={settings.chart.defaultTimeframe}
                  onChange={(e) => handleChartSettingChange('defaultTimeframe', e.target.value)}
                  className="form-control"
                >
                  <option value="1m">1分钟</option>
                  <option value="5m">5分钟</option>
                  <option value="15m">15分钟</option>
                  <option value="1h">1小时</option>
                  <option value="4h">4小时</option>
                  <option value="1d">日线</option>
                </select>
              </div>
            </div>
          </div>

          {/* 风险管理设置 */}
          <div className="settings-card">
            <h2>风险管理设置</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="maxDrawdown">最大回撤 (%)</label>
                <input
                  type="number"
                  id="maxDrawdown"
                  value={settings.risk.maxDrawdown}
                  onChange={(e) => handleRiskSettingChange('maxDrawdown', parseFloat(e.target.value))}
                  className="form-control"
                  min="0"
                  max="100"
                />
              </div>
              <div className="form-group">
                <label htmlFor="maxPositionSize">最大仓位规模 (%)</label>
                <input
                  type="number"
                  id="maxPositionSize"
                  value={settings.risk.maxPositionSize}
                  onChange={(e) => handleRiskSettingChange('maxPositionSize', parseFloat(e.target.value))}
                  className="form-control"
                  min="0"
                  max="100"
                />
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="stopLossEnabled"
                  checked={settings.risk.stopLossEnabled}
                  onChange={(e) => handleRiskSettingChange('stopLossEnabled', e.target.checked)}
                />
                <label htmlFor="stopLossEnabled">
                  <span className={`status-indicator ${settings.risk.stopLossEnabled ? 'status-active' : 'status-inactive'}`}></span>
                  启用止损
                </label>
              </div>
            </div>
          </div>

          {/* 数据质量监控设置 */}
          <div className="settings-card">
            <h2>数据质量监控</h2>
            <div className="checkbox-grid">
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="integrityCheck"
                  checked={settings.dataQuality.integrityCheck}
                  onChange={(e) => handleDataQualityChange('integrityCheck', e.target.checked)}
                />
                <label htmlFor="integrityCheck">
                  <span className={`status-indicator ${settings.dataQuality.integrityCheck ? 'status-active' : 'status-inactive'}`}></span>
                  数据完整性检查
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="anomalyDetection"
                  checked={settings.dataQuality.anomalyDetection}
                  onChange={(e) => handleDataQualityChange('anomalyDetection', e.target.checked)}
                />
                <label htmlFor="anomalyDetection">
                  <span className={`status-indicator ${settings.dataQuality.anomalyDetection ? 'status-active' : 'status-inactive'}`}></span>
                  异常数据检测
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="sourceHealthMonitor"
                  checked={settings.dataQuality.sourceHealthMonitor}
                  onChange={(e) => handleDataQualityChange('sourceHealthMonitor', e.target.checked)}
                />
                <label htmlFor="sourceHealthMonitor">
                  <span className={`status-indicator ${settings.dataQuality.sourceHealthMonitor ? 'status-active' : 'status-inactive'}`}></span>
                  数据源健康监控
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="latencyAlert"
                  checked={settings.dataQuality.latencyAlert}
                  onChange={(e) => handleDataQualityChange('latencyAlert', e.target.checked)}
                />
                <label htmlFor="latencyAlert">
                  <span className={`status-indicator ${settings.dataQuality.latencyAlert ? 'status-active' : 'status-inactive'}`}></span>
                  延迟报警
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="dataDriftMonitor"
                  checked={settings.dataQuality.dataDriftMonitor}
                  onChange={(e) => handleDataQualityChange('dataDriftMonitor', e.target.checked)}
                />
                <label htmlFor="dataDriftMonitor">
                  <span className={`status-indicator ${settings.dataQuality.dataDriftMonitor ? 'status-active' : 'status-inactive'}`}></span>
                  数据漂移监控
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="crossValidation"
                  checked={settings.dataQuality.crossValidation}
                  onChange={(e) => handleDataQualityChange('crossValidation', e.target.checked)}
                />
                <label htmlFor="crossValidation">
                  <span className={`status-indicator ${settings.dataQuality.crossValidation ? 'status-active' : 'status-inactive'}`}></span>
                  交叉验证
                </label>
              </div>
            </div>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="completenessThreshold">完整性阈值 (%)</label>
                <input
                  type="number"
                  id="completenessThreshold"
                  value={settings.dataQuality.completenessThreshold}
                  onChange={(e) => handleDataQualityChange('completenessThreshold', parseFloat(e.target.value))}
                  className="form-control"
                  min="0"
                  max="100"
                />
              </div>
              <div className="form-group">
                <label htmlFor="accuracyThreshold">准确性阈值 (%)</label>
                <input
                  type="number"
                  id="accuracyThreshold"
                  value={settings.dataQuality.accuracyThreshold}
                  onChange={(e) => handleDataQualityChange('accuracyThreshold', parseFloat(e.target.value))}
                  className="form-control"
                  min="0"
                  max="100"
                />
              </div>
              <div className="form-group">
                <label htmlFor="latencyThreshold">延迟阈值 (ms)</label>
                <input
                  type="number"
                  id="latencyThreshold"
                  value={settings.dataQuality.latencyThreshold}
                  onChange={(e) => handleDataQualityChange('latencyThreshold', parseFloat(e.target.value))}
                  className="form-control"
                  min="0"
                  max="10000"
                />
              </div>
            </div>
          </div>

          {/* 预警策略引擎设置 */}
          <div className="settings-card">
            <h2>预警策略引擎</h2>
            <div className="checkbox-grid">
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="graphicalConfig"
                  checked={settings.alertEngine.graphicalConfig}
                  onChange={(e) => handleAlertEngineChange('graphicalConfig', e.target.checked)}
                />
                <label htmlFor="graphicalConfig">
                  <span className={`status-indicator ${settings.alertEngine.graphicalConfig ? 'status-active' : 'status-inactive'}`}></span>
                  图形化策略配置
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="multiCondition"
                  checked={settings.alertEngine.multiCondition}
                  onChange={(e) => handleAlertEngineChange('multiCondition', e.target.checked)}
                />
                <label htmlFor="multiCondition">
                  <span className={`status-indicator ${settings.alertEngine.multiCondition ? 'status-active' : 'status-inactive'}`}></span>
                  多条件组合预警
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="technicalCross"
                  checked={settings.alertEngine.technicalCross}
                  onChange={(e) => handleAlertEngineChange('technicalCross', e.target.checked)}
                />
                <label htmlFor="technicalCross">
                  <span className={`status-indicator ${settings.alertEngine.technicalCross ? 'status-active' : 'status-inactive'}`}></span>
                  技术指标交叉预警
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="andOrLogic"
                  checked={settings.alertEngine.andOrLogic}
                  onChange={(e) => handleAlertEngineChange('andOrLogic', e.target.checked)}
                />
                <label htmlFor="andOrLogic">
                  <span className={`status-indicator ${settings.alertEngine.andOrLogic ? 'status-active' : 'status-inactive'}`}></span>
                  AND/OR逻辑支持
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="webhookIntegration"
                  checked={settings.alertEngine.webhookIntegration}
                  onChange={(e) => handleAlertEngineChange('webhookIntegration', e.target.checked)}
                />
                <label htmlFor="webhookIntegration">
                  <span className={`status-indicator ${settings.alertEngine.webhookIntegration ? 'status-active' : 'status-inactive'}`}></span>
                  Webhook集成
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="autoResponse"
                  checked={settings.alertEngine.autoResponse}
                  onChange={(e) => handleAlertEngineChange('autoResponse', e.target.checked)}
                />
                <label htmlFor="autoResponse">
                  <span className={`status-indicator ${settings.alertEngine.autoResponse ? 'status-active' : 'status-inactive'}`}></span>
                  自动响应动作
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="reportGeneration"
                  checked={settings.alertEngine.reportGeneration}
                  onChange={(e) => handleAlertEngineChange('reportGeneration', e.target.checked)}
                />
                <label htmlFor="reportGeneration">
                  <span className={`status-indicator ${settings.alertEngine.reportGeneration ? 'status-active' : 'status-inactive'}`}></span>
                  自动报告生成
                </label>
              </div>
              <div className="checkbox-item">
                <input
                  type="checkbox"
                  id="notificationTemplates"
                  checked={settings.alertEngine.notificationTemplates}
                  onChange={(e) => handleAlertEngineChange('notificationTemplates', e.target.checked)}
                />
                <label htmlFor="notificationTemplates">
                  <span className={`status-indicator ${settings.alertEngine.notificationTemplates ? 'status-active' : 'status-inactive'}`}></span>
                  通知模板自定义
                </label>
              </div>
            </div>
          </div>

          {/* API 配置 */}
          <div className="settings-card">
            <h2>API 配置</h2>
            <div className="api-config">
              <label htmlFor="binanceApi">Binance API Key</label>
              <input
                type="password"
                id="binanceApi"
                placeholder="输入您的Binance API Key"
                className="form-control"
              />
            </div>
            <div className="api-config">
              <label htmlFor="telegramBot">Telegram Bot Token</label>
              <input
                type="password"
                id="telegramBot"
                placeholder="输入您的Telegram Bot Token"
                className="form-control"
              />
            </div>
          </div>
        </div>

        {/* 保存按钮 */}
        <div className="save-section">
          <button
            onClick={saveSettings}
            className="save-button"
          >
            保存设置
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
