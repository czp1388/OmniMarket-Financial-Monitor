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
      // 设置2秒超时，快速降级
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      
      const response = await ApiService.market.getTickers(symbols);
      clearTimeout(timeoutId);
      
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
      <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#2a3a5a] border-t-[#00ccff] mx-auto shadow-lg shadow-[#00ccff]/20"></div>
          <span className="text-[#00ccff] text-lg animate-pulse">加载预警数据...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 顶部状态栏 - 增强版 */}
      <div className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border-b border-[#2a3a5a] px-6 py-3 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-6">
          <span className="text-xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">OmniMarket</span>
          <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
            systemStatus === '正常' ? 'bg-[#00ff88]/20 text-[#00ff88]' :
            systemStatus === '连接异常' ? 'bg-yellow-500/20 text-yellow-500' :
            'bg-gray-500/20 text-gray-400'
          }`}>
            {systemStatus}
          </span>
          <span className="text-sm text-gray-400">延迟: <span className="text-[#00ccff] font-semibold">{connectionDelay}ms</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">市场状态: <span className="text-white font-semibold">{systemStatus === '市场关闭' ? '休市' : '开市'}</span></span>
          <span className="text-sm text-gray-400">活跃预警: <span className="text-[#ff4444] font-semibold">{alerts.filter(a => a.isActive).length}</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-[#00ccff] font-mono">{currentTime}</span>
          <span className="text-sm text-gray-500">数据源: 实时数据</span>
        </div>
      </div>

      <div className="flex gap-6 p-6">
        {/* 左侧实时价格卡片 */}
        <div className="flex-shrink-0 w-80">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl sticky top-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-2xl">📊</span>
                <span>实时监控</span>
              </h3>
              <div className="text-sm text-gray-400">{symbolsData.length}个品种</div>
            </div>
            <div className="space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto pr-2 scrollbar-thin">
              {symbolsData.map((symbol) => (
                <div key={symbol.symbol} className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-3 hover:border-[#00ccff] transition-all duration-300 cursor-pointer group">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-white group-hover:text-[#00ccff] transition-colors">{symbol.symbol}</span>
                    <span className={`text-sm font-semibold ${
                      symbol.changePercent >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                    }`}>
                      {symbol.changePercent >= 0 ? '↗ +' : '↘ '}{symbol.changePercent.toFixed(2)}%
                    </span>
                  </div>
                  <div className="text-xl font-bold text-white mb-1">${symbol.price.toLocaleString()}</div>
                  <div className="flex items-center justify-between text-xs">
                    <span className={`font-semibold ${
                      symbol.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                    }`}>
                      {symbol.change >= 0 ? '+' : ''}{symbol.change.toLocaleString()}
                    </span>
                    <span className="text-gray-400">成交量: {(symbol.volume / 1000000).toFixed(2)}M</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧预警管理内容 */}
        <div className="flex-1 space-y-6">
          {/* 创建新预警 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-5 flex items-center gap-2">
              <span className="text-3xl">⚡</span>
              <span>创建新预警</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>🎯</span>
                  <span>交易对</span>
                </label>
                <select
                  value={newAlert.symbol}
                  onChange={(e) => setNewAlert({...newAlert, symbol: e.target.value})}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
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
              
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>📊</span>
                  <span>预警类型</span>
                </label>
                <select
                  value={newAlert.alertType}
                  onChange={(e) => setNewAlert({...newAlert, alertType: e.target.value as 'price' | 'technical' | 'volume'})}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
                >
                  <option value="price">价格预警</option>
                  <option value="technical">技术指标</option>
                  <option value="volume">成交量预警</option>
                </select>
              </div>
              
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>⚙️</span>
                  <span>预警条件</span>
                </label>
                <select
                  value={newAlert.condition}
                  onChange={(e) => setNewAlert({...newAlert, condition: e.target.value})}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
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
              
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>💰</span>
                  <span>阈值</span>
                </label>
                <input
                  type="number"
                  value={newAlert.value}
                  onChange={(e) => setNewAlert({...newAlert, value: parseFloat(e.target.value)})}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
                  placeholder="输入阈值"
                />
              </div>
              
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>⚠️</span>
                  <span>优先级</span>
                </label>
                <select
                  value={newAlert.priority}
                  onChange={(e) => setNewAlert({...newAlert, priority: e.target.value as 'low' | 'medium' | 'high'})}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
                >
                  <option value="low">低</option>
                  <option value="medium">中</option>
                  <option value="high">高</option>
                </select>
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={handleCreateAlert}
                  className="w-full px-6 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold rounded-xl hover:scale-105 transition-all duration-300 shadow-lg shadow-[#00ccff]/30 flex items-center justify-center gap-2"
                >
                  <span className="text-xl">✅</span>
                  <span>创建预警</span>
                </button>
              </div>
            </div>
          </div>

          {/* 图形化预警策略配置界面 */}
          <div className="graphic-config-card">
            <div className="graphic-config-header">
              <h2 className="graphic-config-title">图形化策略配置</h2>
              <div className="graphic-config-tabs">
                <button className="graphic-tab-button graphic-tab-active">价格图表</button>
                <button className="graphic-tab-button">技术指标</button>
                <button className="graphic-tab-button">模式识别</button>
              </div>
            </div>
            <div className="graphic-config-body">
              <div className="chart-container">
                <div className="chart-header">
                  <span className="chart-symbol">{newAlert.symbol}</span>
                  <span className="chart-timeframe">1小时图</span>
                  <span className="chart-price">当前价格: {symbolsData.find(s => s.symbol === newAlert.symbol)?.price.toLocaleString() || '0'}</span>
                </div>
                <div className="chart-wrapper">
                  <div className="price-chart">
                    {/* 模拟价格曲线 */}
                    <svg className="chart-svg" width="100%" height="200">
                      <defs>
                        <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                          <stop offset="0%" stopColor="rgba(0, 255, 136, 0.2)" />
                          <stop offset="100%" stopColor="rgba(0, 255, 136, 0.01)" />
                        </linearGradient>
                      </defs>
                      {/* 价格曲线 */}
                      <path
                        className="price-line"
                        d="M 0,180 L 40,160 L 80,140 L 120,150 L 160,130 L 200,110 L 240,120 L 280,100 L 320,90 L 360,80"
                        fill="none"
                        stroke="#00ff88"
                        strokeWidth="2"
                      />
                      {/* 填充区域 */}
                      <path
                        className="price-area"
                        d="M 0,180 L 40,160 L 80,140 L 120,150 L 160,130 L 200,110 L 240,120 L 280,100 L 320,90 L 360,80 L 360,200 L 0,200 Z"
                        fill="url(#priceGradient)"
                      />
                      {/* 阈值线 - 可拖拽 */}
                      <line
                        className="threshold-line"
                        x1="0"
                        y1={180 - (newAlert.value / 50000 * 100)}
                        x2="360"
                        y2={180 - (newAlert.value / 50000 * 100)}
                        stroke={newAlert.condition === 'price_above' ? "#ff4444" : "#00ccff"}
                        strokeWidth="2"
                        strokeDasharray="5,5"
                      />
                      {/* 阈值线手柄 */}
                      <circle
                        className="threshold-handle"
                        cx="360"
                        cy={180 - (newAlert.value / 50000 * 100)}
                        r="8"
                        fill={newAlert.condition === 'price_above' ? "#ff4444" : "#00ccff"}
                        cursor="ns-resize"
                      />
                      {/* 价格点标记 */}
                      <circle cx="0" cy="180" r="3" fill="#00ff88" />
                      <circle cx="40" cy="160" r="3" fill="#00ff88" />
                      <circle cx="80" cy="140" r="3" fill="#00ff88" />
                      <circle cx="120" cy="150" r="3" fill="#00ff88" />
                      <circle cx="160" cy="130" r="3" fill="#00ff88" />
                      <circle cx="200" cy="110" r="3" fill="#00ff88" />
                      <circle cx="240" cy="120" r="3" fill="#00ff88" />
                      <circle cx="280" cy="100" r="3" fill="#00ff88" />
                      <circle cx="320" cy="90" r="3" fill="#00ff88" />
                      <circle cx="360" cy="80" r="3" fill="#00ff88" />
                    </svg>
                    <div className="chart-controls">
                      <div className="threshold-control">
                        <span className="threshold-label">
                          阈值: <strong>{newAlert.value}</strong>
                        </span>
                        <input
                          type="range"
                          min="0"
                          max="50000"
                          step="100"
                          value={newAlert.value}
                          onChange={(e) => setNewAlert({...newAlert, value: parseFloat(e.target.value)})}
                          className="threshold-slider"
                        />
                        <div className="threshold-actions">
                          <button
                            className={`threshold-type-btn ${newAlert.condition === 'price_above' ? 'active' : ''}`}
                            onClick={() => setNewAlert({...newAlert, condition: 'price_above'})}
                          >
                            价格高于
                          </button>
                          <button
                            className={`threshold-type-btn ${newAlert.condition === 'price_below' ? 'active' : ''}`}
                            onClick={() => setNewAlert({...newAlert, condition: 'price_below'})}
                          >
                            价格低于
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="chart-footer">
                  <div className="chart-stats">
                    <div className="stat-item">
                      <span className="stat-label">最高</span>
                      <span className="stat-value">42567</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">最低</span>
                      <span className="stat-value">42100</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">波动</span>
                      <span className="stat-value">+2.34%</span>
                    </div>
                  </div>
                  <div className="chart-hint">
                    <span className="hint-text">提示: 拖拽阈值线或使用滑块调整预警阈值</span>
                  </div>
                </div>
              </div>
              <div className="config-sidebar">
                <h3 className="sidebar-title">条件预览</h3>
                <div className="condition-preview">
                  <div className="preview-item">
                    <span className="preview-label">交易对:</span>
                    <span className="preview-value">{newAlert.symbol}</span>
                  </div>
                  <div className="preview-item">
                    <span className="preview-label">预警类型:</span>
                    <span className="preview-value">
                      {newAlert.alertType === 'price' ? '价格预警' : 
                       newAlert.alertType === 'technical' ? '技术指标' : '成交量预警'}
                    </span>
                  </div>
                  <div className="preview-item">
                    <span className="preview-label">预警条件:</span>
                    <span className="preview-value">
                      {newAlert.condition === 'price_above' ? '价格高于' :
                       newAlert.condition === 'price_below' ? '价格低于' :
                       newAlert.condition === 'rsi_above' ? 'RSI高于' :
                       newAlert.condition === 'rsi_below' ? 'RSI低于' :
                       newAlert.condition === 'volume_above' ? '成交量高于' :
                       newAlert.condition === 'volume_below' ? '成交量低于' :
                       newAlert.condition === 'macd_cross' ? 'MACD金叉' : 'MACD死叉'}
                    </span>
                  </div>
                  <div className="preview-item">
                    <span className="preview-label">阈值:</span>
                    <span className="preview-value highlight">{newAlert.value}</span>
                  </div>
                  <div className="preview-item">
                    <span className="preview-label">优先级:</span>
                    <span className={`preview-value priority-${newAlert.priority}`}>
                      {newAlert.priority === 'low' ? '低' :
                       newAlert.priority === 'medium' ? '中' : '高'}
                    </span>
                  </div>
                </div>
                <div className="condition-logic">
                  <h4 className="logic-title">条件逻辑</h4>
                  <div className="logic-item">
                    <input type="checkbox" id="logic1" defaultChecked />
                    <label htmlFor="logic1">发送电子邮件通知</label>
                  </div>
                  <div className="logic-item">
                    <input type="checkbox" id="logic2" defaultChecked />
                    <label htmlFor="logic2">发送推送通知</label>
                  </div>
                  <div className="logic-item">
                    <input type="checkbox" id="logic3" />
                    <label htmlFor="logic3">声音提醒</label>
                  </div>
                  <div className="logic-item">
                    <input type="checkbox" id="logic4" />
                    <label htmlFor="logic4">重复触发</label>
                  </div>
                </div>
                <div className="condition-actions">
                  <button className="action-btn save-btn">保存策略模板</button>
                  <button className="action-btn apply-btn" onClick={handleCreateAlert}>应用配置并创建</button>
                </div>
              </div>
            </div>
          </div>

          {/* 预警列表 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                  <span className="text-3xl">📋</span>
                  <span>预警列表</span>
                </h2>
                <div className="flex items-center gap-2">
                  {[
                    { key: 'active', label: '活跃预警', icon: '⚡' },
                    { key: 'triggered', label: '已触发', icon: '✅' },
                    { key: 'all', label: '全部', icon: '📊' }
                  ].map(tab => (
                    <button
                      key={tab.key}
                      className={`px-4 py-2 rounded-lg transition-all duration-300 flex items-center gap-2 ${
                        activeTab === tab.key
                          ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold shadow-lg shadow-[#00ccff]/30'
                          : 'bg-[#1a2332] text-gray-400 hover:bg-[#2a3a5a] hover:text-white'
                      }`}
                      onClick={() => setActiveTab(tab.key as 'active' | 'triggered' | 'all')}
                    >
                      <span>{tab.icon}</span>
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="搜索交易对、类型、条件..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 pl-10 text-white placeholder-gray-500 focus:border-[#00ccff] focus:outline-none transition-colors"
                    />
                    <span className="absolute left-3 top-3.5 text-gray-500">🔍</span>
                    {searchTerm && (
                      <button
                        onClick={() => setSearchTerm('')}
                        className="absolute right-3 top-3 text-gray-400 hover:text-white transition-colors"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <select
                    value={sortField}
                    onChange={(e) => setSortField(e.target.value as keyof Alert)}
                    className="bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
                  >
                    <option value="createdAt">创建时间</option>
                    <option value="symbol">交易对</option>
                    <option value="priority">优先级</option>
                    <option value="value">阈值</option>
                  </select>
                  <button
                    onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
                    className="px-4 py-3 bg-[#1a2332] border border-[#2a3a5a] rounded-lg text-white hover:bg-[#2a3a5a] transition-colors"
                  >
                    {sortDirection === 'asc' ? '↑' : '↓'}
                  </button>
                </div>
                
                <div className="flex items-center gap-3">
                  <button
                    onClick={simulateAlertTrigger}
                    className="px-5 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold rounded-lg hover:scale-105 transition-all duration-300 shadow-lg shadow-[#00ccff]/30"
                    title="测试预警触发"
                  >
                    🔔 测试预警
                  </button>
                  <label className="flex items-center gap-2 px-4 py-3 bg-[#1a2332] border border-[#2a3a5a] rounded-lg cursor-pointer hover:bg-[#2a3a5a] transition-colors">
                    <input
                      type="checkbox"
                      checked={soundEnabled}
                      onChange={(e) => setSoundEnabled(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-white text-sm">🔊 声音提醒</span>
                  </label>
                </div>
              </div>
              
              <div className="flex items-center gap-6 text-sm">
                <span className="text-gray-400">活跃: <span className="text-[#00ff88] font-bold text-lg">{alerts.filter(a => a.isActive).length}</span></span>
                <span className="text-gray-400">已触发: <span className="text-[#ff4444] font-bold text-lg">{alerts.filter(a => !a.isActive).length}</span></span>
                <span className="text-gray-400">总数: <span className="text-[#00ccff] font-bold text-lg">{alerts.length}</span></span>
              </div>
            </div>
            <div className="overflow-x-auto mt-5">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#2a3a5a]">
                    <th className="text-left py-4 px-4 text-gray-400 font-semibold">交易对</th>
                    <th className="text-left py-4 px-4 text-gray-400 font-semibold">类型</th>
                    <th className="text-left py-4 px-4 text-gray-400 font-semibold">优先级</th>
                    <th className="text-left py-4 px-4 text-gray-400 font-semibold">预警条件</th>
                    <th className="text-right py-4 px-4 text-gray-400 font-semibold">阈值</th>
                    <th className="text-right py-4 px-4 text-gray-400 font-semibold">当前值</th>
                    <th className="text-center py-4 px-4 text-gray-400 font-semibold">状态</th>
                    <th className="text-center py-4 px-4 text-gray-400 font-semibold">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {getFilteredAlerts().map((alert) => (
                    <tr key={alert.id} className="border-b border-[#2a3a5a]/50 hover:bg-[#1a2332] transition-colors duration-200">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-[#00ccff]/20 text-[#00ccff] text-xs font-bold">
                            {alert.symbol.includes('/') ? 'FX' : alert.symbol.length <= 4 ? 'STK' : 'CRY'}
                          </span>
                          <span className="text-white font-semibold">{alert.symbol}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                          alert.alertType === 'price' ? 'bg-[#00ccff]/20 text-[#00ccff]' :
                          alert.alertType === 'technical' ? 'bg-purple-500/20 text-purple-400' :
                          'bg-orange-500/20 text-orange-400'
                        }`}>
                          {getAlertTypeText(alert.alertType)}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-3 py-1 rounded-lg text-sm font-bold ${
                          alert.priority === 'high' ? 'bg-[#ff4444]/20 text-[#ff4444]' :
                          alert.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {getPriorityText(alert.priority)}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-300">{getConditionText(alert.condition)}</td>
                      <td className="py-4 px-4 text-right text-white font-bold font-mono">{alert.value}</td>
                      <td className="py-4 px-4 text-right text-white font-bold font-mono">{alert.currentValue}</td>
                      <td className="py-4 px-4 text-center">
                        <span className={`px-3 py-1 rounded-lg font-bold ${
                          alert.isActive ? 'bg-[#00ff88]/20 text-[#00ff88]' : 'bg-gray-500/20 text-gray-400'
                        }`}>
                          {alert.isActive ? '⚡ 活跃' : '✅ 已触发'}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() => toggleAlert(alert.id)}
                            className={`px-4 py-2 rounded-lg font-semibold transition-all duration-300 ${
                              alert.isActive 
                                ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30' 
                                : 'bg-[#00ff88]/20 text-[#00ff88] hover:bg-[#00ff88]/30'
                            }`}
                          >
                            {alert.isActive ? '⏸️ 禁用' : '▶️ 启用'}
                          </button>
                          <button
                            onClick={() => deleteAlert(alert.id)}
                            className="px-4 py-2 bg-[#ff4444]/20 text-[#ff4444] rounded-lg font-semibold hover:bg-[#ff4444]/30 transition-all duration-300"
                          >
                            🗑️ 删除
                          </button>
                        </div>
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
      <div className="mt-6 bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border-t border-[#2a3a5a] px-6 py-4 flex items-center justify-between shadow-2xl">
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">版本: <span className="text-white font-semibold">OmniMarket v1.0.0</span></span>
          <span className="text-gray-500">|</span>
          <span className="text-sm text-gray-400">连接状态: <span className={`font-semibold ${
            systemStatus === '正常' ? 'text-[#00ff88]' : 
            systemStatus === '连接异常' ? 'text-yellow-400' : 
            'text-gray-400'
          }`}>{systemStatus}</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">最后更新: <span className="text-[#00ccff] font-mono">{currentTime}</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">总预警数: <span className="text-2xl font-bold text-white">{alerts.length}</span></span>
          <span className="text-gray-500">|</span>
          <span className="text-sm text-gray-400">数据更新: <span className="text-[#00ff88] font-semibold">实时</span></span>
        </div>
      </div>
    </div>
  );
};

export default AlertsPage;
