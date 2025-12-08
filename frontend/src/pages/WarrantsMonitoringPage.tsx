import React, { useState, useEffect, useRef } from 'react';
import './WarrantsMonitoringPage.css';
import { ApiService } from '../services/api';

interface WarrantData {
  symbol: string;
  underlying_symbol: string;
  warrant_type: 'BULL' | 'BEAR';
  strike_price: number;
  knock_out_price: number;
  current_price: number;
  leverage: number;
  time_to_maturity: number;
  status: string;
  alert_level?: 'danger' | 'warning' | 'normal';
  volume?: number;
  average_volume?: number;
}

interface WarrantMonitoringData {
  symbol: string;
  underlying_symbol: string;
  warrant_type: string;
  current_price: number;
  underlying_price: number;
  distance_to_knock_out: number;
  effective_leverage: number;
  time_to_maturity: number;
  last_updated: string;
  alerts: Array<{
    type: string;
    triggered_at: string | null;
  }>;
}

const WarrantsMonitoringPage: React.FC = () => {
  const [warrants, setWarrants] = useState<WarrantData[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<string>('HK');
  const [timeRange, setTimeRange] = useState<string>('1h');
  const [activeIndicator, setActiveIndicator] = useState<string>('distance');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const ws = useRef<WebSocket | null>(null);

  // 初始化数据加载
  useEffect(() => {
    loadWarrantsData();
    setupWebSocket();
    
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  // 加载牛熊证数据
  const loadWarrantsData = async () => {
    try {
      setLoading(true);
      const response = await ApiService.warrants.getAllWarrants();
      if (response && Array.isArray(response)) {
        setWarrants(response);
        setLastUpdate(new Date().toLocaleTimeString('zh-CN'));
      }
    } catch (error) {
      console.error('Failed to load warrants data:', error);
      // 如果API失败，使用示例数据作为后备
      const sampleResponse = await ApiService.warrants.getSampleWarrants();
      if (sampleResponse && Array.isArray(sampleResponse)) {
        setWarrants(sampleResponse);
      }
    } finally {
      setLoading(false);
    }
  };

  // 设置WebSocket连接 - 使用正确的后端端口
  const setupWebSocket = () => {
    // 开发环境直接连接后端端口8000，生产环境使用相对路径
    const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const wsUrl = isDevelopment 
      ? 'ws://localhost:8000/api/warrants-monitoring/ws'
      : '/api/warrants-monitoring/ws';
    
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      console.log('WebSocket connected to backend');
      setIsConnected(true);
    };
    
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        
        if (data.type === 'warrant_update') {
          setWarrants(prevWarrants => 
            prevWarrants.map(warrant => 
              warrant.symbol === data.data.symbol ? { ...warrant, ...data.data } : warrant
            )
          );
          setLastUpdate(new Date().toLocaleTimeString('zh-CN'));
        } else if (data.type === 'alert_triggered') {
          // 处理预警通知
          console.log('Alert triggered:', data.data);
          showAlertNotification(data.data);
        } else if (data.type === 'trading_signal') {
          // 处理交易信号
          console.log('Trading signal received:', data.data);
          showTradingSignal(data.data);
        } else if (data.type === 'connection_status') {
          console.log('WebSocket status:', data.message);
        }
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // 尝试重新连接
      setTimeout(setupWebSocket, 5000);
    };
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  // 显示预警通知
  const showAlertNotification = (alertData: any) => {
    // 这里可以集成浏览器的通知API或自定义通知组件
    if (Notification.permission === 'granted') {
      new Notification(`牛熊证预警 - ${alertData.symbol}`, {
        body: `${alertData.message} - 距回收价: ${alertData.distance_to_knock_out?.toFixed(2)}%`,
        icon: '/favicon.ico'
      });
    }
    // 也可以在UI中显示通知
    console.log('Alert notification:', alertData);
  };

  // 显示交易信号
  const showTradingSignal = (signalData: any) => {
    if (Notification.permission === 'granted') {
      new Notification(`交易信号 - ${signalData.symbol}`, {
        body: `${signalData.signal} - ${signalData.reason}`,
        icon: '/favicon.ico'
      });
    }
    console.log('Trading signal:', signalData);
  };

  // 刷新数据
  const handleRefresh = () => {
    loadWarrantsData();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'danger': return '#ff4444';
      case 'warning': return '#ffaa00';
      default: return '#00ff88';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'danger': return '高风险';
      case 'warning': return '警告';
      default: return '正常';
    }
  };

  // 计算有效杠杆比率 - 改进版本
  const calculateEffectiveLeverage = (warrant: WarrantData) => {
    // 有效杠杆 = (正股价格 / 牛熊证价格) * 名义杠杆
    // 这里假设正股价格是牛熊证价格的10倍（典型关系）
    const underlyingPriceRatio = 10; // 正股价格与牛熊证价格的典型比例
    const baseLeverage = warrant.leverage || 1;
    const effectiveLeverage = baseLeverage * underlyingPriceRatio;
    return effectiveLeverage;
  };

  // 计算时间价值衰减 - 改进版本
  const calculateTimeValueDecay = (warrant: WarrantData) => {
    // 时间价值衰减 = 剩余天数倒数 * 当前价格 * 衰减因子
    // 衰减因子根据牛熊证类型和剩余天数调整
    const baseDecayFactor = warrant.warrant_type === 'BULL' ? 0.015 : 0.012;
    const timeFactor = Math.max(1 / warrant.time_to_maturity, 0.1); // 最小衰减因子
    const timeDecay = timeFactor * warrant.current_price * baseDecayFactor;
    return timeDecay;
  };

  // 计算距回收价百分比 - 改进版本
  const calculateDistanceToKnockOut = (warrant: WarrantData) => {
    if (warrant.knock_out_price <= 0) return 0;
    
    // 对于牛证：回收价 > 当前价，距离 = (回收价 - 当前价) / 回收价 * 100
    // 对于熊证：回收价 < 当前价，距离 = (当前价 - 回收价) / 回收价 * 100
    let distance;
    if (warrant.warrant_type === 'BULL') {
      distance = ((warrant.knock_out_price - warrant.current_price) / warrant.knock_out_price) * 100;
    } else {
      distance = ((warrant.current_price - warrant.knock_out_price) / warrant.knock_out_price) * 100;
    }
    
    return Math.max(distance, 0); // 确保不为负
  };

  // 计算杠杆预警级别
  const getLeverageAlertLevel = (effectiveLeverage: number) => {
    if (effectiveLeverage >= 15) return 'danger';
    if (effectiveLeverage >= 10) return 'warning';
    return 'normal';
  };

  // 计算时间价值衰减预警级别
  const getTimeDecayAlertLevel = (timeDecay: number, timeToMaturity: number) => {
    // 剩余天数越少，时间价值衰减越严重
    if (timeToMaturity <= 7 && timeDecay >= 0.5) return 'danger';
    if (timeToMaturity <= 14 && timeDecay >= 0.3) return 'warning';
    return 'normal';
  };

  // 计算成交量异常预警级别
  const getVolumeAlertLevel = (warrant: WarrantData) => {
    if (!warrant.volume || !warrant.average_volume) return 'normal';
    
    const volumeRatio = warrant.volume / warrant.average_volume;
    if (volumeRatio >= 3) return 'danger'; // 成交量是平均的3倍以上
    if (volumeRatio >= 2) return 'warning'; // 成交量是平均的2倍以上
    return 'normal';
  };

  // 计算成交量比率
  const calculateVolumeRatio = (warrant: WarrantData) => {
    if (!warrant.volume || !warrant.average_volume) return 0;
    return warrant.volume / warrant.average_volume;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 统一导航键 - 专业金融终端标准 */}
      <div className="bg-[#0a0e17] border-b border-[#2a3a5a] px-6 py-3 flex items-center gap-2 overflow-x-auto">
        {[
          { key: '监控', icon: '📊', active: true },
          { key: '预警', icon: '⚡', active: false },
          { key: '分析', icon: '📈', active: false },
          { key: '信号', icon: '📡', active: false },
          { key: '设置', icon: '⚙️', active: false },
          { key: '历史', icon: '📜', active: false },
          { key: '报告', icon: '📄', active: false }
        ].map(nav => (
          <button 
            key={nav.key}
            className={`px-4 py-2 rounded-lg transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${
              nav.active
                ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold shadow-lg shadow-[#00ccff]/30'
                : 'bg-[#141a2a] text-gray-400 hover:bg-[#1a2332] hover:text-white'
            }`}
          >
            <span className="text-lg">{nav.icon}</span>
            <span>{nav.key}</span>
          </button>
        ))}
      </div>

      {/* 顶部状态栏 */}
      <div className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border-b border-[#2a3a5a] px-6 py-3 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-6">
          <span className="text-xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">牛熊证监控</span>
          <span className="px-3 py-1 rounded-lg text-sm font-semibold bg-[#00ff88]/20 text-[#00ff88]">正常</span>
          <span className="text-sm text-gray-400">延迟: <span className="text-[#00ccff] font-semibold">23ms</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">市场状态: <span className="text-white font-semibold">交易中</span></span>
          <span className="text-sm text-gray-400">活跃品种: <span className="text-[#00ccff] font-semibold">{warrants.length}</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-[#00ccff] font-mono">{new Date().toLocaleString('zh-CN')}</span>
        </div>
      </div>

      <div className="flex gap-6 p-6">
        {/* 左侧控制面板 */}
        <div className="flex-shrink-0 w-80">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl space-y-6">
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>🌏</span>
                <span>市场选择</span>
              </label>
              <select 
                value={selectedMarket} 
                onChange={(e) => setSelectedMarket(e.target.value)}
                className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
              >
                <option value="HK">港股</option>
                <option value="US">美股</option>
                <option value="CN">A股</option>
              </select>
            </div>

            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>⏱️</span>
                <span>时间周期</span>
              </label>
              <select 
                value={timeRange} 
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
              >
                <option value="1m">1分钟</option>
                <option value="5m">5分钟</option>
                <option value="1h">1小时</option>
                <option value="4h">4小时</option>
                <option value="1d">日线</option>
              </select>
            </div>

            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>📊</span>
                <span>监控指标</span>
              </label>
              <select 
                value={activeIndicator} 
                onChange={(e) => setActiveIndicator(e.target.value)}
                className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
              >
                <option value="distance">距回收价</option>
                <option value="leverage">有效杠杆</option>
                <option value="timevalue">时间价值</option>
                <option value="volume">成交量</option>
              </select>
            </div>

            <div>
              <h3 className="flex items-center gap-2 text-lg font-bold text-white mb-3">
                <span>⚠️</span>
                <span>预警设置</span>
              </h3>
              <div className="space-y-2">
                <div className="px-3 py-2 rounded-lg bg-[#ff4444]/20 border border-[#ff4444]/30 text-[#ff4444] text-sm">
                  高风险: ≤ 3% 距回收价
                </div>
                <div className="px-3 py-2 rounded-lg bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 text-sm">
                  警告: ≤ 8% 距回收价
                </div>
                <div className="px-3 py-2 rounded-lg bg-[#00ff88]/20 border border-[#00ff88]/30 text-[#00ff88] text-sm">
                  正常: {'>'} 8% 距回收价
                </div>
              </div>
            </div>

            <div>
              <h3 className="flex items-center gap-2 text-lg font-bold text-white mb-3">
                <span>📡</span>
                <span>交易信号</span>
              </h3>
              <div className="space-y-2">
                <label className="flex items-center gap-2 px-3 py-2 bg-[#1a2332] rounded-lg cursor-pointer hover:bg-[#2a3a5a] transition-colors">
                  <input type="checkbox" defaultChecked className="w-4 h-4" />
                  <span className="text-white text-sm">买入信号</span>
                </label>
                <label className="flex items-center gap-2 px-3 py-2 bg-[#1a2332] rounded-lg cursor-pointer hover:bg-[#2a3a5a] transition-colors">
                  <input type="checkbox" defaultChecked className="w-4 h-4" />
                  <span className="text-white text-sm">卖出信号</span>
                </label>
                <label className="flex items-center gap-2 px-3 py-2 bg-[#1a2332] rounded-lg cursor-pointer hover:bg-[#2a3a5a] transition-colors">
                  <input type="checkbox" defaultChecked className="w-4 h-4" />
                  <span className="text-white text-sm">回收预警</span>
                </label>
              </div>
            </div>

            <button 
              className="w-full px-6 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold rounded-xl hover:scale-105 transition-all duration-300 shadow-lg shadow-[#00ccff]/30 flex items-center justify-center gap-2"
              onClick={handleRefresh}
            >
              <span className="text-xl">🔄</span>
              <span>刷新数据</span>
            </button>
          </div>
        </div>

          {/* 右侧主内容区域 */}
        <div className="flex-1 space-y-6">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">📊</span>
                <span>牛熊证实时监控</span>
              </h2>
              <div className="flex items-center gap-6 text-sm">
                <span className="text-gray-400">活跃: <span className="text-[#00ccff] font-bold text-lg">{warrants.length}</span></span>
                <span className="text-gray-400">高风险: <span className="text-[#ff4444] font-bold text-lg">{warrants.filter(w => {
                  const distanceToKnockOut = w.knock_out_price > 0 
                    ? Math.abs((w.current_price - w.knock_out_price) / w.knock_out_price * 100)
                    : 0;
                  return distanceToKnockOut <= 3;
                }).length}</span></span>
                <span className="text-gray-400">警告: <span className="text-yellow-400 font-bold text-lg">{warrants.filter(w => {
                  const distanceToKnockOut = w.knock_out_price > 0 
                    ? Math.abs((w.current_price - w.knock_out_price) / w.knock_out_price * 100)
                    : 0;
                  return distanceToKnockOut > 3 && distanceToKnockOut <= 8;
                }).length}</span></span>
              </div>
            </div>

          {/* 牛熊证数据表格 */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2a3a5a]">
                  <th className="text-left py-4 px-3 text-gray-400 font-semibold text-sm">代码</th>
                  <th className="text-left py-4 px-3 text-gray-400 font-semibold text-sm">正股</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">现价</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">回收价</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">距回收价</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">有效杠杆</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">时间衰减</th>
                  <th className="text-center py-4 px-3 text-gray-400 font-semibold text-sm">类型</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">名义杠杆</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">剩余天数</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">成交量</th>
                  <th className="text-right py-4 px-3 text-gray-400 font-semibold text-sm">成交量比率</th>
                  <th className="text-center py-4 px-3 text-gray-400 font-semibold text-sm">状态</th>
                </tr>
              </thead>
              <tbody>
                {warrants.map((warrant, index) => {
                  const distanceToKnockOut = warrant.knock_out_price > 0 
                    ? Math.abs((warrant.current_price - warrant.knock_out_price) / warrant.knock_out_price * 100)
                    : 0;
                  
                  const effectiveLeverage = calculateEffectiveLeverage(warrant);
                  const timeValueDecay = calculateTimeValueDecay(warrant);
                  const alertLevel = distanceToKnockOut <= 3 ? 'danger' : distanceToKnockOut <= 8 ? 'warning' : 'normal';
                  const leverageAlertLevel = getLeverageAlertLevel(effectiveLeverage);
                  const timeDecayAlertLevel = getTimeDecayAlertLevel(timeValueDecay, warrant.time_to_maturity);
                  const volumeAlertLevel = getVolumeAlertLevel(warrant);
                  const volumeRatio = calculateVolumeRatio(warrant);
                  
                  return (
                    <tr key={`${warrant.symbol}-${index}`} className={`border-b border-[#2a3a5a]/50 hover:bg-[#1a2332] transition-colors duration-200 ${
                      alertLevel === 'danger' ? 'bg-[#ff4444]/5' : alertLevel === 'warning' ? 'bg-yellow-500/5' : ''
                    }`}>
                      <td className="py-4 px-3 text-white font-semibold font-mono">{warrant.symbol}</td>
                      <td className="py-4 px-3 text-gray-300">{warrant.underlying_symbol}</td>
                      <td className="py-4 px-3 text-right text-white font-bold font-mono">${warrant.current_price.toFixed(2)}</td>
                      <td className="py-4 px-3 text-right text-gray-300 font-mono">${warrant.knock_out_price.toFixed(2)}</td>
                      <td className="py-4 px-3 text-right">
                        <span className={`px-2 py-1 rounded font-bold font-mono ${
                          alertLevel === 'danger' ? 'bg-[#ff4444]/20 text-[#ff4444]' :
                          alertLevel === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-[#00ff88]/20 text-[#00ff88]'
                        }`}>{distanceToKnockOut.toFixed(2)}%</span>
                      </td>
                      <td className="py-4 px-3 text-right">
                        <span className={`px-2 py-1 rounded font-bold font-mono ${
                          leverageAlertLevel === 'danger' ? 'bg-[#ff4444]/20 text-[#ff4444]' :
                          leverageAlertLevel === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-[#00ccff]/20 text-[#00ccff]'
                        }`}>{effectiveLeverage.toFixed(1)}x</span>
                      </td>
                      <td className="py-4 px-3 text-right">
                        <span className={`px-2 py-1 rounded font-bold font-mono ${
                          timeDecayAlertLevel === 'danger' ? 'bg-[#ff4444]/20 text-[#ff4444]' :
                          timeDecayAlertLevel === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>{timeValueDecay.toFixed(3)}</span>
                      </td>
                      <td className="py-4 px-3 text-center">
                        <span className={`px-3 py-1 rounded-lg font-bold ${
                          warrant.warrant_type === 'BULL' ? 'bg-[#00ff88]/20 text-[#00ff88]' : 'bg-[#ff4444]/20 text-[#ff4444]'
                        }`}>
                          {warrant.warrant_type === 'BULL' ? '🐂 牛证' : '🐻 熊证'}
                        </span>
                      </td>
                      <td className="py-4 px-3 text-right text-white font-mono">{warrant.leverage.toFixed(1)}x</td>
                      <td className="py-4 px-3 text-right text-gray-300 font-mono">{warrant.time_to_maturity}天</td>
                      <td className="py-4 px-3 text-right">
                        <span className={`px-2 py-1 rounded font-mono ${
                          volumeAlertLevel === 'danger' ? 'bg-[#ff4444]/20 text-[#ff4444]' :
                          volumeAlertLevel === 'warning' ? 'bg-yellow-500/20 text-yellow-400' : 'text-gray-300'
                        }`}>{warrant.volume ? warrant.volume.toLocaleString() : 'N/A'}</span>
                      </td>
                      <td className="py-4 px-3 text-right">
                        <span className={`px-2 py-1 rounded font-bold font-mono ${
                          volumeAlertLevel === 'danger' ? 'bg-[#ff4444]/20 text-[#ff4444]' :
                          volumeAlertLevel === 'warning' ? 'bg-yellow-500/20 text-yellow-400' : 'text-gray-400'
                        }`}>{volumeRatio > 0 ? volumeRatio.toFixed(2) + 'x' : 'N/A'}</span>
                      </td>
                      <td className="py-4 px-3 text-center">
                        <span className={`px-3 py-1 rounded-lg font-bold ${
                          alertLevel === 'danger' ? 'bg-[#ff4444]/20 text-[#ff4444]' :
                          alertLevel === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-[#00ff88]/20 text-[#00ff88]'
                        }`}>{getStatusText(alertLevel)}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* 底部状态信息 */}
          <div className="mt-6 bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border-t border-[#2a3a5a] px-6 py-4 flex items-center justify-between rounded-lg shadow-lg">
            <div className="flex items-center gap-6">
              <span className="text-sm text-gray-400">数据更新: <span className={`font-semibold ${isConnected ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>{isConnected ? '实时' : '离线'}</span></span>
              <span className="text-gray-500">|</span>
              <span className="text-sm text-gray-400">连接状态: <span className={`font-semibold ${isConnected ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>{isConnected ? '已连接' : '断开'}</span></span>
            </div>
            <span className="text-sm text-gray-400">最后刷新: <span className="text-[#00ccff] font-mono">{lastUpdate || '未刷新'}</span></span>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarrantsMonitoringPage;
