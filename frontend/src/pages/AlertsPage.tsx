import React, { useState, useEffect } from 'react';
import './AlertsPage.css';
import { ApiService } from '../services/api';

interface Alert {
  id: string;
  symbol: string;
  condition: string;
  value: number;
  currentValue: number;
  isActive: boolean;
  createdAt: string;
  triggeredAt?: string;
  alertType: 'price' | 'technical' | 'volume';
  priority: 'low' | 'medium' | 'high';
}

interface SymbolData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high24h: number;
  low24h: number;
}

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [symbolsData, setSymbolsData] = useState<SymbolData[]>([]);
  const [newAlert, setNewAlert] = useState({
    symbol: 'BTC/USDT',
    condition: 'price_above',
    value: 0,
    alertType: 'price' as 'price' | 'technical' | 'volume',
    priority: 'medium' as 'low' | 'medium' | 'high'
  });
  const [activeTab, setActiveTab] = useState<'active' | 'triggered' | 'all'>('active');
  const [currentTime, setCurrentTime] = useState<string>('');
  const [systemStatus, setSystemStatus] = useState<'正常' | '连接异常' | '市场关闭'>('正常');
  const [connectionDelay, setConnectionDelay] = useState<number>(0);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortField, setSortField] = useState<keyof Alert>('createdAt');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [notifications, setNotifications] = useState<string[]>([]);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);

  // 从后端API获取实时价格数据
  const fetchRealTimeData = async (): Promise<SymbolData[]> => {
    try {
      const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
      const response = await ApiService.market.getTickers(symbols);
      
      // 安全的类型检查和处理
      if (Array.isArray(response)) {
        return response.map((ticker: any) => ({
          symbol: ticker.symbol,
          price: ticker.last || ticker.close || 0,
          change: ticker.change || 0,
          changePercent: ticker.change_percent || 0,
          volume: ticker.baseVolume || ticker.volume || 0,
          high24h: ticker.high || 0,
          low24h: ticker.low || 0
        }));
      } else {
        console.warn('Invalid response format from API, using fallback data');
        return generateFallbackData();
      }
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
      return generateFallbackData();
    }
  };

  // 生成备用数据（当API调用失败时使用）
  const generateFallbackData = (): SymbolData[] => {
    return [
      { symbol: 'BTC/USDT', price: 42567.39, change: 975.42, changePercent: 2.34, volume: 28456789, high24h: 42800.50, low24h: 42100.25 },
      { symbol: 'ETH/USDT', price: 2345.67, change: 28.51, changePercent: 1.23, volume: 15678923, high24h: 2360.80, low24h: 2300.45 },
      { symbol: 'AAPL', price: 182.45, change: -1.03, changePercent: -0.56, volume: 4567890, high24h: 184.20, low24h: 180.80 },
      { symbol: 'TSLA', price: 245.67, change: 3.21, changePercent: 1.32, volume: 2345678, high24h: 248.90, low24h: 240.15 },
      { symbol: 'USD/CNY', price: 7.1987, change: 0.0086, changePercent: 0.12, volume: 123456789, high24h: 7.2050, low24h: 7.1850 },
      { symbol: 'EUR/USD', price: 1.0856, change: -0.0023, changePercent: -0.21, volume: 98765432, high24h: 1.0880, low24h: 1.0820 },
      { symbol: 'XAU/USD', price: 1987.45, change: 12.34, changePercent: 0.62, volume: 345678, high24h: 1995.60, low24h: 1970.80 },
      { symbol: 'SPY', price: 456.78, change: 2.34, changePercent: 0.51, volume: 1234567, high24h: 458.20, low24h: 452.40 }
    ];
  };

  useEffect(() => {
    // 更新时间
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }));
    };

    // 模拟系统状态
    const updateSystemStatus = () => {
      const randomStatus = Math.random();
      if (randomStatus < 0.9) {
        setSystemStatus('正常');
        setConnectionDelay(Math.floor(Math.random() * 50) + 10);
      } else if (randomStatus < 0.95) {
        setSystemStatus('连接异常');
        setConnectionDelay(Math.floor(Math.random() * 200) + 100);
      } else {
        setSystemStatus('市场关闭');
        setConnectionDelay(0);
      }
    };

    // 模拟预警数据
    const mockAlerts: Alert[] = [
      {
        id: '1',
        symbol: 'BTC/USDT',
        condition: 'price_above',
        value: 43000,
        currentValue: 42567.39,
        isActive: true,
        createdAt: new Date().toISOString(),
        alertType: 'price',
        priority: 'high'
      },
      {
        id: '2',
        symbol: 'ETH/USDT',
        condition: 'rsi_below',
        value: 30,
        currentValue: 45.8,
        isActive: true,
        createdAt: new Date().toISOString(),
        alertType: 'technical',
        priority: 'medium'
      },
      {
        id: '3',
        symbol: 'AAPL',
        condition: 'price_below',
        value: 180,
        currentValue: 182.45,
        isActive: false,
        createdAt: new Date().toISOString(),
        triggeredAt: new Date().toISOString(),
        alertType: 'price',
        priority: 'low'
      },
      {
        id: '4',
        symbol: 'TSLA',
        condition: 'volume_above',
        value: 2000000,
        currentValue: 2345678,
        isActive: true,
        createdAt: new Date().toISOString(),
        alertType: 'volume',
        priority: 'medium'
      },
      {
        id: '5',
        symbol: 'XAU/USD',
        condition: 'macd_cross',
        value: 0,
        currentValue: 1987.45,
        isActive: true,
        createdAt: new Date().toISOString(),
        alertType: 'technical',
        priority: 'high'
      }
    ];
    
    // 初始化数据
    const initializeData = async () => {
      try {
        const realTimeData = await fetchRealTimeData();
        setSymbolsData(realTimeData);
        setAlerts(mockAlerts);
        setLoading(false);
      } catch (error) {
        console.error('Failed to initialize data:', error);
        setSymbolsData(generateFallbackData());
        setAlerts(mockAlerts);
        setLoading(false);
      }
    };

    initializeData();
    updateTime();
    updateSystemStatus();

    // 实时数据更新
    const dataInterval = setInterval(async () => {
      try {
        const realTimeData = await fetchRealTimeData();
        setSymbolsData(realTimeData);
      } catch (error) {
        console.error('Failed to update real-time data:', error);
        setSymbolsData(generateFallbackData());
      }
    }, 2000);

    // 时间更新
    const timeInterval = setInterval(updateTime, 1000);

    // 系统状态更新
    const statusInterval = setInterval(updateSystemStatus, 5000);

    return () => {
      clearInterval(dataInterval);
      clearInterval(timeInterval);
      clearInterval(statusInterval);
    };
  }, []);

  const handleCreateAlert = () => {
    const alert: Alert = {
      id: Date.now().toString(),
      symbol: newAlert.symbol,
      condition: newAlert.condition,
      value: newAlert.value,
      currentValue: 0, // 这应该从实时数据获取
      isActive: true,
      createdAt: new Date().toISOString(),
      alertType: newAlert.alertType,
      priority: newAlert.priority
    };
    
    setAlerts([...alerts, alert]);
    setNewAlert({ 
      symbol: 'BTC/USDT', 
      condition: 'price_above', 
      value: 0,
      alertType: 'price' as 'price' | 'technical' | 'volume',
      priority: 'medium' as 'low' | 'medium' | 'high'
    });
  };

  const toggleAlert = (id: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, isActive: !alert.isActive } : alert
    ));
  };

  const deleteAlert = (id: string) => {
    setAlerts(alerts.filter(alert => alert.id !== id));
  };

  const getConditionText = (condition: string) => {
    const conditions: { [key: string]: string } = {
      'price_above': '价格高于',
      'price_below': '价格低于',
      'rsi_above': 'RSI高于',
      'rsi_below': 'RSI低于',
      'volume_above': '成交量高于',
      'volume_below': '成交量低于',
      'macd_cross': 'MACD金叉',
      'macd_death': 'MACD死叉'
    };
    return conditions[condition] || condition;
  };

  const getAlertTypeText = (alertType: string) => {
    const types: { [key: string]: string } = {
      'price': '价格',
      'technical': '技术',
      'volume': '成交量'
    };
    return types[alertType] || alertType;
  };

  const getPriorityText = (priority: string) => {
    const priorities: { [key: string]: string } = {
      'low': '低',
      'medium': '中',
      'high': '高'
    };
    return priorities[priority] || priority;
  };

  const getFilteredAlerts = () => {
    let filtered = alerts;
    
    // 按标签过滤
    switch (activeTab) {
      case 'active':
        filtered = filtered.filter(alert => alert.isActive);
        break;
      case 'triggered':
        filtered = filtered.filter(alert => !alert.isActive);
        break;
      case 'all':
      default:
        break;
    }
    
    // 按搜索词过滤
    if (searchTerm) {
      filtered = filtered.filter(alert => 
        alert.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        getAlertTypeText(alert.alertType).toLowerCase().includes(searchTerm.toLowerCase()) ||
        getConditionText(alert.condition).toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // 排序
    filtered.sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (aValue === undefined || bValue === undefined) return 0;
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      } else if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' 
          ? aValue - bValue
          : bValue - aValue;
      } else if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
        return sortDirection === 'asc' 
          ? (aValue === bValue ? 0 : aValue ? 1 : -1)
          : (aValue === bValue ? 0 : aValue ? -1 : 1);
      }
      
      return 0;
    });
    
    return filtered;
  };

  // 添加通知
  const addNotification = (message: string) => {
    const newNotification = `${new Date().toLocaleTimeString('zh-CN')} - ${message}`;
    setNotifications(prev => [newNotification, ...prev].slice(0, 10)); // 只保留最近10条
  };

  // 模拟预警触发
  const simulateAlertTrigger = () => {
    const activeAlerts = alerts.filter(alert => alert.isActive);
    if (activeAlerts.length > 0) {
      const randomAlert = activeAlerts[Math.floor(Math.random() * activeAlerts.length)];
      const message = `预警触发: ${randomAlert.symbol} ${getConditionText(randomAlert.condition)} ${randomAlert.value}`;
      addNotification(message);
      
      if (soundEnabled) {
        // 在实际应用中，这里会播放声音
        console.log('播放预警声音');
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <span className="loading-text">加载预警数据...</span>
      </div>
    );
  }

  return (
    <div className="alerts-container">
      {/* 顶部状态栏 - 专业金融终端标准 */}
      <div className="status-bar top-status-bar">
        <div className="status-left">
          <span className="system-name">OmniMarket</span>
          <span className={`status-indicator ${systemStatus === '正常' ? 'status-normal' : systemStatus === '连接异常' ? 'status-warning' : 'status-closed'}`}>
            {systemStatus}
          </span>
          <span className="delay-info">延迟: {connectionDelay}ms</span>
        </div>
        <div className="status-center">
          <span className="market-status">市场状态: {systemStatus === '市场关闭' ? '休市' : '开市'}</span>
          <span className="active-alerts-count">活跃预警: {alerts.filter(a => a.isActive).length}</span>
        </div>
        <div className="status-right">
          <span className="current-time">{currentTime}</span>
          <span className="data-source">数据源: 实时数据</span>
        </div>
      </div>

      <div className="alerts-main">
        {/* 左侧实时价格卡片 */}
        <div className="symbols-sidebar">
          <div className="symbols-header">
            <h3>实时监控</h3>
            <span className="symbols-count">{symbolsData.length} 品种</span>
          </div>
          <div className="symbols-list">
            {symbolsData.map((symbol) => (
              <div key={symbol.symbol} className="symbol-card">
                <div className="symbol-info">
                  <div className="symbol-name">{symbol.symbol}</div>
                  <div className={`symbol-price ${
                    symbol.change >= 0 ? 'price-up' : 'price-down'
                  }`}>
                    {symbol.price.toLocaleString()}
                  </div>
                </div>
                <div className="symbol-details">
                  <div className={`symbol-change ${
                    symbol.change >= 0 ? 'change-up' : 'change-down'
                  }`}>
                    {symbol.change >= 0 ? '+' : ''}{symbol.change.toFixed(2)} ({symbol.changePercent.toFixed(2)}%)
                  </div>
                  <div className="symbol-volume">
                    成交量: {(symbol.volume / 1000000).toFixed(2)}M
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧预警管理内容 */}
        <div className="alerts-content">
          {/* 创建新预警 */}
          <div className="create-alert-card">
            <h2 className="create-alert-title">创建新预警</h2>
            <div className="create-alert-form">
              <div className="form-group">
                <label className="form-label">交易对</label>
                <select
                  value={newAlert.symbol}
                  onChange={(e) => setNewAlert({...newAlert, symbol: e.target.value})}
                  className="form-select"
                >
                  <option value="BTC/USDT">BTC/USDT</option>
                  <option value="ETH/USDT">ETH/USDT</option>
                  <option value="AAPL">AAPL</option>
                  <option value="TSLA">TSLA</option>
                  <option value="USD/CNY">USD/CNY</option>
                  <option value="EUR/USD">EUR/USD</option>
                  <option value="XAU/USD">XAU/USD</option>
                  <option value="SPY">SPY</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">预警类型</label>
                <select
                  value={newAlert.alertType}
                  onChange={(e) => setNewAlert({...newAlert, alertType: e.target.value as 'price' | 'technical' | 'volume'})}
                  className="form-select"
                >
                  <option value="price">价格预警</option>
                  <option value="technical">技术指标</option>
                  <option value="volume">成交量预警</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">预警条件</label>
                <select
                  value={newAlert.condition}
                  onChange={(e) => setNewAlert({...newAlert, condition: e.target.value})}
                  className="form-select"
                >
                  <option value="price_above">价格高于</option>
                  <option value="price_below">价格低于</option>
                  <option value="rsi_above">RSI高于</option>
                  <option value="rsi_below">RSI低于</option>
                  <option value="volume_above">成交量高于</option>
                  <option value="volume_below">成交量低于</option>
                  <option value="macd_cross">MACD金叉</option>
                  <option value="macd_death">MACD死叉</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">阈值</label>
                <input
                  type="number"
                  value={newAlert.value}
                  onChange={(e) => setNewAlert({...newAlert, value: parseFloat(e.target.value)})}
                  className="form-input"
                  placeholder="输入阈值"
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">优先级</label>
                <select
                  value={newAlert.priority}
                  onChange={(e) => setNewAlert({...newAlert, priority: e.target.value as 'low' | 'medium' | 'high'})}
                  className="form-select"
                >
                  <option value="low">低</option>
                  <option value="medium">中</option>
                  <option value="high">高</option>
                </select>
              </div>
              
              <div className="form-group">
                <button
                  onClick={handleCreateAlert}
                  className="create-button"
                >
                  创建预警
                </button>
              </div>
            </div>
          </div>

          {/* 预警列表 */}
          <div className="alerts-list-card">
            <div className="alerts-list-header">
              <h2 className="alerts-list-title">预警列表</h2>
              <div className="alerts-tabs">
                <button
                  className={`tab-button ${activeTab === 'active' ? 'tab-active' : ''}`}
                  onClick={() => setActiveTab('active')}
                >
                  活跃预警
                </button>
                <button
                  className={`tab-button ${activeTab === 'triggered' ? 'tab-active' : ''}`}
                  onClick={() => setActiveTab('triggered')}
                >
                  已触发
                </button>
                <button
                  className={`tab-button ${activeTab === 'all' ? 'tab-active' : ''}`}
                  onClick={() => setActiveTab('all')}
                >
                  全部
                </button>
              </div>
              <div className="alerts-controls">
                <div className="search-control">
                  <input
                    type="text"
                    placeholder="搜索交易对、类型、条件..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="search-input"
                  />
                  {searchTerm && (
                    <button
                      onClick={() => setSearchTerm('')}
                      className="clear-search"
                    >
                      ✕
                    </button>
                  )}
                </div>
                <div className="sort-control">
                  <select
                    value={sortField}
                    onChange={(e) => setSortField(e.target.value as keyof Alert)}
                    className="sort-select"
                  >
                    <option value="createdAt">创建时间</option>
                    <option value="symbol">交易对</option>
                    <option value="priority">优先级</option>
                    <option value="value">阈值</option>
                  </select>
                  <button
                    onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
                    className="sort-direction"
                  >
                    {sortDirection === 'asc' ? '↑' : '↓'}
                  </button>
                </div>
                <div className="notification-controls">
                  <button
                    onClick={simulateAlertTrigger}
                    className="test-alert-button"
                    title="测试预警触发"
                  >
                    测试预警
                  </button>
                  <label className="sound-toggle">
                    <input
                      type="checkbox"
                      checked={soundEnabled}
                      onChange={(e) => setSoundEnabled(e.target.checked)}
                    />
                    声音提醒
                  </label>
                </div>
              </div>
              <div className="alerts-stats">
                <span className="active-alerts">活跃: {alerts.filter(a => a.isActive).length}</span>
                <span className="triggered-alerts">已触发: {alerts.filter(a => !a.isActive).length}</span>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="alerts-table">
                <thead>
                  <tr>
                    <th>交易对</th>
                    <th>类型</th>
                    <th>优先级</th>
                    <th>预警条件</th>
                    <th>阈值</th>
                    <th>当前值</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {getFilteredAlerts().map((alert) => (
                    <tr key={alert.id}>
                      <td className="symbol-cell">
                        <div className="symbol-name">{alert.symbol}</div>
                      </td>
                      <td>
                        <span className={`type-badge type-${alert.alertType}`}>
                          {getAlertTypeText(alert.alertType)}
                        </span>
                      </td>
                      <td>
                        <span className={`priority-badge priority-${alert.priority}`}>
                          {getPriorityText(alert.priority)}
                        </span>
                      </td>
                      <td>{getConditionText(alert.condition)}</td>
                      <td>{alert.value}</td>
                      <td>{alert.currentValue}</td>
                      <td>
                        <span className={`status-badge ${
                          alert.isActive ? 'status-active' : 'status-triggered'
                        }`}>
                          {alert.isActive ? '活跃' : '已触发'}
                        </span>
                      </td>
                      <td>
                        <button
                          onClick={() => toggleAlert(alert.id)}
                          className={`action-button ${
                            alert.isActive ? 'button-disable' : 'button-enable'
                          }`}
                        >
                          {alert.isActive ? '禁用' : '启用'}
                        </button>
                        <button
                          onClick={() => deleteAlert(alert.id)}
                          className="action-button button-delete"
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* 底部状态栏 - 专业金融终端标准 */}
      <div className="status-bar bottom-status-bar">
        <div className="status-left">
          <span className="version-info">OmniMarket v1.0.0</span>
          <span className="connection-status">连接状态: {systemStatus}</span>
        </div>
        <div className="status-center">
          <span className="last-update">最后更新: {currentTime}</span>
        </div>
        <div className="status-right">
          <span className="total-alerts">总预警数: {alerts.length}</span>
          <span className="data-update-status">数据更新: 实时</span>
        </div>
      </div>
    </div>
  );
};

export default AlertsPage;
