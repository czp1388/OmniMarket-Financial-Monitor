import React, { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import { Link, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import { realTimeDataService } from '../services/realTimeDataService';
import './Dashboard.css';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  last?: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  timestamp?: string;
  type?: string;
  source?: string;
  lastUpdate?: string;
}

const Dashboard: React.FC = () => {
  const location = useLocation();
  
  const navigation = [
    { name: '仪表板', href: '/', icon: '📊' },
    { name: '专业监控', href: '/financial-monitoring', icon: '📊' },
    { name: '图表分析', href: '/chart', icon: '📈' },
    { name: '预警管理', href: '/alerts', icon: '🔔' },
    { name: '投资组合', href: '/portfolio', icon: '💼' },
    { name: '虚拟交易', href: '/virtual-trading', icon: '💰' },
    { name: '牛熊证监控', href: '/warrants', icon: '📉' },
    { name: '系统设置', href: '/settings', icon: '⚙️' },
  ];

  const isActive = (path: string) => location.pathname === path;
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [systemStatus, setSystemStatus] = useState({
    lastUpdate: new Date().toLocaleString('zh-CN'),
    activeAlerts: 85,
    marketStatus: '正常',
    dataStatus: '实时',
    latency: '12ms'
  });

  const [selectedMarket, setSelectedMarket] = useState('股票');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1小时');
  const [selectedIndicator, setSelectedIndicator] = useState('无指标');

  // 使用真实实时数据服务
  useEffect(() => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
    const stopUpdates = realTimeDataService.startRealTimeUpdates(
      (data: any[]) => {
        const updatedMarketData = data.map(item => ({
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
        setMarketData(updatedMarketData);
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

  // K线图配置
  const getKLineOption = () => {
    return {
      backgroundColor: '#0a0e14',
      grid: {
        left: '3%',
        right: '3%',
        bottom: '3%',
        top: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
        axisLine: {
          lineStyle: {
            color: '#2a2f3d'
          }
        },
        axisLabel: {
          color: '#8a94a6'
        }
      },
      yAxis: {
        type: 'value',
        scale: true,
        axisLine: {
          lineStyle: {
            color: '#2a2f3d'
          }
        },
        axisLabel: {
          color: '#8a94a6'
        },
        splitLine: {
          lineStyle: {
            color: '#1e2330',
            type: 'dashed'
          }
        }
      },
      series: [
        {
          type: 'candlestick',
          data: [
            [100, 102, 98, 101],
            [101, 105, 100, 103],
            [103, 108, 102, 107],
            [107, 110, 105, 108],
            [108, 112, 106, 110],
            [110, 115, 108, 113],
            [113, 118, 111, 116]
          ],
          itemStyle: {
            color: '#00ff88',
            color0: '#ff4444',
            borderColor: '#00ff88',
            borderColor0: '#ff4444'
          }
        }
      ]
    };
  };

  const handleRefreshData = () => {
    // 手动刷新数据
    const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
    realTimeDataService.getMarketData(symbols).then(data => {
      const updatedMarketData = data.map(item => ({
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
      setMarketData(updatedMarketData);
      setSystemStatus(prev => ({
        ...prev,
        lastUpdate: new Date().toLocaleString('zh-CN')
      }));
    });
  };

  return (
    <div className="financial-dashboard">
      {/* 专业顶部导航栏 - 彭博终端风格 */}
      <header className="top-navigation">
        <div className="nav-container">
          <div className="nav-brand">
            <h1 className="brand-title">OmniMarket</h1>
            <p className="brand-subtitle">寰宇多市场金融监控系统</p>
          </div>
          
          {/* 专业导航键 - 符合彭博终端标准 */}
          <div className="dashboard-nav-keys">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'dashboard-nav-key',
                  isActive(item.href) && 'active'
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>

          <div className="nav-info">
            <div className="current-time">
              {new Date().toLocaleString('zh-CN')}
            </div>
            <div className="user-avatar">
              <div className="avatar-circle">U</div>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区域 - 30/70分栏布局 */}
      <div className="dashboard-content">
        {/* 左侧30% - 专业品种监控面板 */}
        <div className="left-panel">
          <div className="panel-header">
            <h3 className="panel-title">实时监控品种</h3>
          </div>
          <div className="price-card-container">
            {marketData.map((data, index) => (
              <div key={index} className="price-card">
                <div className="card-header">
                  <span className="symbol-icon">█</span>
                  <span className="symbol">{data.symbol}</span>
                </div>
                <div className="price">${data.price.toLocaleString()}</div>
                <div className={`change ${data.change >= 0 ? 'positive' : 'negative'}`}>
                  {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)} ({data.changePercent.toFixed(2)}%)
                  <span className="status-indicator">{data.change >= 0 ? '🟢' : '🔴'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧70% - 核心功能区域 */}
        <div className="right-panel">
          {/* 专业K线图表区域 - 彭博终端风格 */}
          <div className="chart-container">
            <div className="chart-header">
              <h3>📊 专业K线图表分析</h3>
            </div>
            <ReactECharts 
              option={getKLineOption()} 
              style={{ height: '400px', width: '100%' }}
              opts={{ renderer: 'svg' }}
            />
          </div>

          {/* 专业控制面板 - 彭博终端风格 */}
          <div className="control-panel">
            <div className="control-group">
              <label>市场选择</label>
              <select 
                value={selectedMarket} 
                onChange={(e) => setSelectedMarket(e.target.value)}
                className="control-select"
              >
                <option value="股票">股票(AAPL)</option>
                <option value="加密货币">加密货币</option>
                <option value="外汇">外汇</option>
                <option value="期货">期货</option>
                <option value="期权">期权</option>
              </select>
            </div>

            <div className="control-group">
              <label>时间周期</label>
              <select 
                value={selectedTimeframe} 
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="control-select"
              >
                <option value="1分钟">1分钟</option>
                <option value="5分钟">5分钟</option>
                <option value="15分钟">15分钟</option>
                <option value="30分钟">30分钟</option>
                <option value="1小时">1小时</option>
                <option value="4小时">4小时</option>
                <option value="日线">日线</option>
                <option value="周线">周线</option>
              </select>
            </div>

            <div className="control-group">
              <label>技术指标</label>
              <select 
                value={selectedIndicator} 
                onChange={(e) => setSelectedIndicator(e.target.value)}
                className="control-select"
              >
                <option value="无指标">无指标</option>
                <option value="MA">移动平均线</option>
                <option value="EMA">指数移动平均</option>
                <option value="MACD">MACD</option>
                <option value="RSI">RSI</option>
                <option value="布林带">布林带</option>
                <option value="KDJ">KDJ</option>
                <option value="OBV">OBV</option>
              </select>
            </div>

            <button className="simulate-btn" onClick={handleRefreshData}>
              🔄 刷新数据
            </button>
          </div>

          {/* 专业状态信息面板 - 彭博终端风格 */}
          <div className="status-panel">
            <div className="status-item">
              <span className="status-icon">🔔</span>
              <span className="status-label">活跃预警</span>
              <span className="status-value warning">{systemStatus.activeAlerts}</span>
            </div>
            <div className="status-item">
              <span className="status-icon">✅</span>
              <span className="status-label">市场状态</span>
              <span className="status-value normal">{systemStatus.marketStatus}</span>
            </div>
            <div className="status-item">
              <span className="status-icon">📡</span>
              <span className="status-label">数据更新</span>
              <span className="status-value realtime">{systemStatus.dataStatus}</span>
            </div>
            <div className="status-item">
              <span className="status-icon">⚡</span>
              <span className="status-label">延迟</span>
              <span className="status-value latency">{systemStatus.latency}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
