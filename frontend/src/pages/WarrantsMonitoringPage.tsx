import React, { useState, useEffect } from 'react';
import './WarrantsMonitoringPage.css';

interface WarrantData {
  id: string;
  code: string;
  name: string;
  underlying: string;
  currentPrice: number;
  changePercent: number;
  strikePrice: number;
  callPut: 'C' | 'P';
  leverage: number;
  distanceToStrike: number;
  volume: number;
  timeValue: number;
  status: 'normal' | 'warning' | 'danger';
}

const WarrantsMonitoringPage: React.FC = () => {
  const [warrants, setWarrants] = useState<WarrantData[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<string>('HK');
  const [timeRange, setTimeRange] = useState<string>('1h');
  const [activeIndicator, setActiveIndicator] = useState<string>('distance');

  // 模拟牛熊证数据
  useEffect(() => {
    const mockWarrants: WarrantData[] = [
      {
        id: '1',
        code: '12345',
        name: '腾讯牛证',
        underlying: '00700',
        currentPrice: 0.85,
        changePercent: 2.41,
        strikePrice: 320,
        callPut: 'C',
        leverage: 8.5,
        distanceToStrike: 12.3,
        volume: 1500000,
        timeValue: 0.15,
        status: 'normal'
      },
      {
        id: '2',
        code: '12346',
        name: '腾讯熊证',
        underlying: '00700',
        currentPrice: 0.92,
        changePercent: -1.07,
        strikePrice: 380,
        callPut: 'P',
        leverage: 7.2,
        distanceToStrike: 8.7,
        volume: 890000,
        timeValue: 0.22,
        status: 'warning'
      },
      {
        id: '3',
        code: '12347',
        name: '阿里牛证',
        underlying: '09988',
        currentPrice: 1.23,
        changePercent: 3.36,
        strikePrice: 85,
        callPut: 'C',
        leverage: 6.8,
        distanceToStrike: 15.2,
        volume: 1200000,
        timeValue: 0.18,
        status: 'normal'
      },
      {
        id: '4',
        code: '12348',
        name: '美团熊证',
        underlying: '03690',
        currentPrice: 0.78,
        changePercent: -2.50,
        strikePrice: 120,
        callPut: 'P',
        leverage: 9.1,
        distanceToStrike: 5.8,
        volume: 650000,
        timeValue: 0.25,
        status: 'danger'
      },
      {
        id: '5',
        code: '12349',
        name: '平安牛证',
        underlying: '02318',
        currentPrice: 0.95,
        changePercent: 1.06,
        strikePrice: 48,
        callPut: 'C',
        leverage: 5.4,
        distanceToStrike: 18.9,
        volume: 980000,
        timeValue: 0.12,
        status: 'normal'
      },
      {
        id: '6',
        code: '12350',
        name: '港交所熊证',
        underlying: '00388',
        currentPrice: 1.15,
        changePercent: -0.86,
        strikePrice: 280,
        callPut: 'P',
        leverage: 7.8,
        distanceToStrike: 7.3,
        volume: 720000,
        timeValue: 0.19,
        status: 'warning'
      }
    ];

    setWarrants(mockWarrants);

    // 模拟实时数据更新
    const interval = setInterval(() => {
      setWarrants(prev => prev.map(warrant => ({
        ...warrant,
        currentPrice: warrant.currentPrice * (1 + (Math.random() - 0.5) * 0.02),
        changePercent: warrant.changePercent + (Math.random() - 0.5) * 0.5,
        volume: warrant.volume + Math.floor(Math.random() * 10000),
        distanceToStrike: Math.max(0.1, warrant.distanceToStrike + (Math.random() - 0.5) * 0.3),
        status: warrant.distanceToStrike < 3 ? 'danger' : 
                warrant.distanceToStrike < 8 ? 'warning' : 'normal'
      })));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

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

  return (
    <div className="warrants-monitoring-container">
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

          <button className="refresh-btn">
            刷新数据
          </button>
        </div>

        {/* 右侧主内容区域 */}
        <div className="main-content">
          <div className="content-header">
            <h2>牛熊证实时监控</h2>
            <div className="market-stats">
              <span>活跃牛熊证: {warrants.length}</span>
              <span>高风险: {warrants.filter(w => w.status === 'danger').length}</span>
              <span>警告: {warrants.filter(w => w.status === 'warning').length}</span>
            </div>
          </div>

          {/* 牛熊证数据表格 */}
          <div className="warrants-table-container">
            <table className="warrants-table">
              <thead>
                <tr>
                  <th>代码</th>
                  <th>名称</th>
                  <th>正股</th>
                  <th>现价</th>
                  <th>涨跌幅</th>
                  <th>回收价</th>
                  <th>类型</th>
                  <th>杠杆</th>
                  <th>距回收</th>
                  <th>成交量</th>
                  <th>时间价值</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                {warrants.map((warrant) => (
                  <tr key={warrant.id} className={`warrant-row ${warrant.status}`}>
                    <td className="code">{warrant.code}</td>
                    <td className="name">{warrant.name}</td>
                    <td className="underlying">{warrant.underlying}</td>
                    <td className="price">${warrant.currentPrice.toFixed(2)}</td>
                    <td className={`change ${warrant.changePercent >= 0 ? 'positive' : 'negative'}`}>
                      {warrant.changePercent >= 0 ? '+' : ''}{warrant.changePercent.toFixed(2)}%
                    </td>
                    <td className="strike">${warrant.strikePrice}</td>
                    <td className={`type ${warrant.callPut === 'C' ? 'bull' : 'bear'}`}>
                      {warrant.callPut === 'C' ? '牛证' : '熊证'}
                    </td>
                    <td className="leverage">{warrant.leverage.toFixed(1)}x</td>
                    <td className="distance">{warrant.distanceToStrike.toFixed(1)}%</td>
                    <td className="volume">{(warrant.volume / 10000).toFixed(1)}万</td>
                    <td className="time-value">{warrant.timeValue.toFixed(2)}</td>
                    <td className="status">
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(warrant.status) }}
                      >
                        {getStatusText(warrant.status)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 底部状态信息 */}
          <div className="info-panel">
            <div className="info-item">
              <span className="info-label">数据更新:</span>
              <span className="info-value">实时</span>
            </div>
            <div className="info-item">
              <span className="info-label">监控品种:</span>
              <span className="info-value">{warrants.length}</span>
            </div>
            <div className="info-item">
              <span className="info-label">最后刷新:</span>
              <span className="info-value">{new Date().toLocaleTimeString('zh-CN')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarrantsMonitoringPage;
