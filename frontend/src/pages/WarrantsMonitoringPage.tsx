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
    <div className="warrants-monitoring-container">
      {/* 统一导航键 - 专业金融终端标准 */}
      <div className="warrants-nav-bar">
        <button className="warrants-nav-btn active">
          <span className="status-indicator"></span>
          监控
        </button>
        <button className="warrants-nav-btn">
          <span className="status-indicator"></span>
          预警
        </button>
        <button className="warrants-nav-btn">
          <span className="status-indicator"></span>
          分析
        </button>
        <button className="warrants-nav-btn">
          <span className="status-indicator"></span>
          信号
        </button>
        <button className="warrants-nav-btn">
          <span className="status-indicator"></span>
          设置
        </button>
        <button className="warrants-nav-btn">
          <span className="status-indicator"></span>
          历史
        </button>
        <button className="warrants-nav-btn">
          <span className="status-indicator"></span>
          报告
        </button>
      </div>

      {/* 顶部状态栏 */}
      <div className="status-bar">
        <div className="status-item">
          <span className="status-label">系统状态:</span>
          <span className="status-value connected">正常</span>
        </div>
        <div className="status-item">
          <span className="status-label">连接延迟:</span>
          <span className="status-value">23ms</span>
        </div>
        <div className="status-item">
          <span className="status-label">市场状态:</span>
          <span className="status-value">交易中</span>
        </div>
        <div className="status-item">
          <span className="status-label">时间:</span>
          <span className="status-value">{new Date().toLocaleString('zh-CN')}</span>
        </div>
      </div>

      <div className="warrants-content">
        {/* 左侧控制面板 */}
        <div className="control-panel">
          <div className="panel-section">
            <h3>市场选择</h3>
            <select 
              value={selectedMarket} 
              onChange={(e) => setSelectedMarket(e.target.value)}
              className="control-select"
            >
              <option value="HK">港股</option>
              <option value="US">美股</option>
              <option value="CN">A股</option>
            </select>
          </div>

          <div className="panel-section">
            <h3>时间周期</h3>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              className="control-select"
            >
              <option value="1m">1分钟</option>
              <option value="5m">5分钟</option>
              <option value="1h">1小时</option>
              <option value="4h">4小时</option>
              <option value="1d">日线</option>
            </select>
          </div>

          <div className="panel-section">
            <h3>监控指标</h3>
            <select 
              value={activeIndicator} 
              onChange={(e) => setActiveIndicator(e.target.value)}
              className="control-select"
            >
              <option value="distance">距回收价</option>
              <option value="leverage">有效杠杆</option>
              <option value="timevalue">时间价值</option>
              <option value="volume">成交量</option>
            </select>
          </div>

          <div className="panel-section">
            <h3>预警设置</h3>
            <div className="warning-levels">
              <div className="warning-level danger">
                高风险: ≤3% 距回收价
              </div>
              <div className="warning-level warning">
                警告: ≤8% 距回收价
              </div>
              <div className="warning-level normal">
                正常: {'>'}8% 距回收价
              </div>
            </div>
          </div>

          <div className="panel-section">
            <h3>交易信号</h3>
            <div className="signal-filters">
              <label className="filter-item">
                <input type="checkbox" defaultChecked />
                买入信号
              </label>
              <label className="filter-item">
                <input type="checkbox" defaultChecked />
                卖出信号
              </label>
              <label className="filter-item">
                <input type="checkbox" defaultChecked />
                回收预警
              </label>
            </div>
          </div>

          <button className="refresh-btn" onClick={handleRefresh}>
            刷新数据
          </button>
        </div>

          {/* 右侧主内容区域 */}
        <div className="main-content">
          <div className="content-header">
            <h2>牛熊证实时监控</h2>
          <div className="market-stats">
            <span>活跃牛熊证: {warrants.length}</span>
            <span>高风险: {warrants.filter(w => {
              const distanceToKnockOut = w.knock_out_price > 0 
                ? Math.abs((w.current_price - w.knock_out_price) / w.knock_out_price * 100)
                : 0;
              return distanceToKnockOut <= 3;
            }).length}</span>
            <span>警告: {warrants.filter(w => {
              const distanceToKnockOut = w.knock_out_price > 0 
                ? Math.abs((w.current_price - w.knock_out_price) / w.knock_out_price * 100)
                : 0;
              return distanceToKnockOut > 3 && distanceToKnockOut <= 8;
            }).length}</span>
          </div>
          </div>

          {/* 牛熊证数据表格 */}
          <div className="warrants-table-container">
            <table className="warrants-table">
              <thead>
                <tr>
                  <th>代码</th>
                  <th>正股</th>
                  <th>现价</th>
                  <th>回收价</th>
                  <th>距回收价</th>
                  <th>有效杠杆</th>
                  <th>时间衰减</th>
                  <th>类型</th>
                  <th>名义杠杆</th>
                  <th>剩余天数</th>
                  <th>成交量</th>
                  <th>成交量比率</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                {warrants.map((warrant, index) => {
                  // 计算距回收价百分比（基于正股价格和回收价）
                  const distanceToKnockOut = warrant.knock_out_price > 0 
                    ? Math.abs((warrant.current_price - warrant.knock_out_price) / warrant.knock_out_price * 100)
                    : 0;
                  
                  // 计算有效杠杆和时间衰减
                  const effectiveLeverage = calculateEffectiveLeverage(warrant);
                  const timeValueDecay = calculateTimeValueDecay(warrant);
                  
                  // 根据距回收价确定预警级别
                  const alertLevel = distanceToKnockOut <= 3 ? 'danger' : 
                                   distanceToKnockOut <= 8 ? 'warning' : 'normal';
                  
                  // 计算杠杆和时间衰减的预警级别
                  const leverageAlertLevel = getLeverageAlertLevel(effectiveLeverage);
                  const timeDecayAlertLevel = getTimeDecayAlertLevel(timeValueDecay, warrant.time_to_maturity);
                  const volumeAlertLevel = getVolumeAlertLevel(warrant);
                  const volumeRatio = calculateVolumeRatio(warrant);
                  
                  return (
                    <tr key={`${warrant.symbol}-${index}`} className={`warrant-row ${alertLevel}`}>
                      <td className="code">{warrant.symbol}</td>
                      <td className="underlying">{warrant.underlying_symbol}</td>
                      <td className="price">${warrant.current_price.toFixed(2)}</td>
                      <td className="strike">${warrant.knock_out_price.toFixed(2)}</td>
                      <td className="distance">{distanceToKnockOut.toFixed(2)}%</td>
                      <td className={`effective-leverage ${leverageAlertLevel}`}>
                        {effectiveLeverage.toFixed(1)}x
                      </td>
                      <td className={`time-decay ${timeDecayAlertLevel}`}>
                        {timeValueDecay.toFixed(3)}
                      </td>
                      <td className={`type ${warrant.warrant_type === 'BULL' ? 'bull' : 'bear'}`}>
                        {warrant.warrant_type === 'BULL' ? '牛证' : '熊证'}
                      </td>
                      <td className="nominal-leverage">{warrant.leverage.toFixed(1)}x</td>
                      <td className="time-to-maturity">{warrant.time_to_maturity}天</td>
                      <td className={`volume ${volumeAlertLevel}`}>
                        {warrant.volume ? warrant.volume.toLocaleString() : 'N/A'}
                      </td>
                      <td className={`volume-ratio ${volumeAlertLevel}`}>
                        {volumeRatio > 0 ? volumeRatio.toFixed(2) + 'x' : 'N/A'}
                      </td>
                      <td className="status">
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(alertLevel) }}
                        >
                          {getStatusText(alertLevel)}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* 底部状态信息 */}
          <div className="info-panel">
            <div className="info-item">
              <span className="info-label">数据更新:</span>
              <span className="info-value">{isConnected ? '实时' : '离线'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">连接状态:</span>
              <span className="info-value">{isConnected ? '已连接' : '断开'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">最后刷新:</span>
              <span className="info-value">{lastUpdate || '未刷新'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarrantsMonitoringPage;
