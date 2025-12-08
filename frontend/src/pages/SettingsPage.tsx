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
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white p-6">
      <div className="flex gap-4">
        {/* 左侧实时监控面板 */}
        <div className="w-full md:w-[25%] bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-4 shadow-2xl">
          <div className="mb-4">
            <h3 className="text-xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-2xl">📊</span>
              <span>实时监控</span>
            </h3>
            <div className="flex items-center gap-2 mt-2">
              <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
              <span className="text-[#00ff88] text-sm font-semibold">实时数据</span>
            </div>
          </div>
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {symbolsData.map((symbol) => (
              <div key={symbol.symbol} className="bg-[#1a2332] border border-[#2a3a5a] rounded-xl p-3 hover:scale-[1.02] transition-all">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-white font-bold">{symbol.symbol}</span>
                  <span className={`font-semibold text-sm ${symbol.changePercent >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                    {formatPercent(symbol.changePercent)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-lg font-mono text-white">
                    {symbol.symbol.includes('/') ? '$' : ''}{formatNumber(symbol.price)}
                  </span>
                  <span className={`text-sm ${symbol.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                    {symbol.change >= 0 ? '↗ +' : '↘ '}{formatNumber(symbol.change)}
                  </span>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  成交量: {symbol.volume.toLocaleString()}
                </div>
                <div className="text-xs text-gray-400">
                  H: {formatNumber(symbol.high)} L: {formatNumber(symbol.low)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧设置内容 */}
        <div className="w-full md:w-[75%] space-y-4">
          {/* 功能导航栏 */}
          <div className="bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-2xl p-3 shadow-2xl">
            <div className="flex items-center gap-2 overflow-x-auto">
              {['常规设置', '数据源', '通知', '图表', '风险', '数据质量', '预警策略'].map((nav) => (
                <button
                  key={nav}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all whitespace-nowrap ${
                    activeNav === nav
                      ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black'
                      : 'bg-[#1a2332] text-gray-400 hover:bg-[#222b3d] hover:text-white'
                  }`}
                  onClick={() => setActiveNav(nav)}
                >
                  {nav}
                </button>
              ))}
            </div>
          </div>

          {/* 标题区 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-3">
              <span className="text-5xl">⚙️</span>
              <span>系统设置</span>
            </h1>
            <p className="text-gray-400 mt-2">配置您的监控系统偏好</p>
          </div>

          {/* 设置卡片网格 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 数据源设置 */}
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
              <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">🌐</span>
                <span>数据源设置</span>
              </h2>
              <div className="space-y-3">
                {[
                  { id: 'crypto', label: '加密货币数据', value: settings.dataSources.crypto },
                  { id: 'stocks', label: '股票数据', value: settings.dataSources.stocks },
                  { id: 'forex', label: '外汇数据', value: settings.dataSources.forex },
                  { id: 'futures', label: '期货数据', value: settings.dataSources.futures }
                ].map((item) => (
                  <div key={item.id} className="flex items-center gap-3 p-3 bg-[#1a2332] rounded-lg">
                    <input
                      type="checkbox"
                      id={item.id}
                      checked={item.value}
                      onChange={(e) => handleDataSourceChange(item.id, e.target.checked)}
                      className="w-5 h-5 accent-[#00ccff]"
                    />
                    <label htmlFor={item.id} className="flex items-center gap-2 cursor-pointer flex-1">
                      <div className={`w-3 h-3 rounded-full ${item.value ? 'bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50' : 'bg-gray-500'}`}></div>
                      <span className="text-white">{item.label}</span>
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* 通知设置 */}
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
              <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">🔔</span>
                <span>通知设置</span>
              </h2>
              <div className="space-y-3">
                {[
                  { id: 'email', label: '邮件通知', value: settings.notifications.email },
                  { id: 'push', label: '推送通知', value: settings.notifications.push },
                  { id: 'sound', label: '声音提示', value: settings.notifications.sound },
                  { id: 'telegram', label: 'Telegram通知', value: settings.notifications.telegram }
                ].map((item) => (
                  <div key={item.id} className="flex items-center gap-3 p-3 bg-[#1a2332] rounded-lg">
                    <input
                      type="checkbox"
                      id={item.id}
                      checked={item.value}
                      onChange={(e) => handleNotificationChange(item.id, e.target.checked)}
                      className="w-5 h-5 accent-[#00ccff]"
                    />
                    <label htmlFor={item.id} className="flex items-center gap-2 cursor-pointer flex-1">
                      <div className={`w-3 h-3 rounded-full ${item.value ? 'bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50' : 'bg-gray-500'}`}></div>
                      <span className="text-white">{item.label}</span>
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* 图表设置 */}
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
              <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">📈</span>
                <span>图表设置</span>
              </h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="theme" className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <span>🎨</span><span>主题</span>
                  </label>
                  <select
                    id="theme"
                    value={settings.chart.theme}
                    onChange={(e) => handleChartSettingChange('theme', e.target.value)}
                    className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none"
                  >
                    <option value="light">浅色</option>
                    <option value="dark">深色</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="timezone" className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <span>🌍</span><span>时区</span>
                  </label>
                  <select
                    id="timezone"
                    value={settings.chart.timezone}
                    onChange={(e) => handleChartSettingChange('timezone', e.target.value)}
                    className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none"
                  >
                    <option value="Asia/Shanghai">北京时间</option>
                    <option value="America/New_York">纽约时间</option>
                    <option value="Europe/London">伦敦时间</option>
                    <option value="UTC">UTC</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="timeframe" className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <span>⏱️</span><span>默认时间周期</span>
                  </label>
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
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
              <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">🔑</span>
                <span>API 配置</span>
              </h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="binanceApi" className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <span>🪙</span><span>Binance API Key</span>
                  </label>
                  <input
                    type="password"
                    id="binanceApi"
                    placeholder="输入您的Binance API Key"
                    className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none"
                  />
                </div>
                <div>
                  <label htmlFor="telegramBot" className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <span>✈️</span><span>Telegram Bot Token</span>
                  </label>
                  <input
                    type="password"
                    id="telegramBot"
                    placeholder="输入您的Telegram Bot Token"
                    className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* 保存按钮 */}
          <div className="mt-6">
            <button
              onClick={saveSettings}
              className="w-full bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold text-lg px-8 py-4 rounded-xl hover:scale-[1.02] transition-all duration-300 shadow-2xl flex items-center justify-center gap-3"
            >
              <span className="text-2xl">💾</span>
              <span>保存设置</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
