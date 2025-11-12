import React, { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import { Link, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import './Dashboard.css';

interface PriceCard {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

const Dashboard: React.FC = () => {
  const location = useLocation();
  
  const navigation = [
    { name: '仪表板', href: '/', icon: '📊' },
    { name: '专业监控', href: '/financial-monitoring', icon: '📊' },
    { name: '图表分析', href: '/chart', icon: '📈' },
    { name: '预警管理', href: '/alerts', icon: '🔔' },
    { name: '投资组合', href: '/portfolio', icon: '💼' },
    { name: '系统设置', href: '/settings', icon: '⚙️' },
  ];

  const isActive = (path: string) => location.pathname === path;
  const [priceCards, setPriceCards] = useState<PriceCard[]>([
    { symbol: 'BTC/USDT', price: 42567.89, change: 2.34, changePercent: 2.34 },
    { symbol: 'ETH/USDT', price: 2345.67, change: 1.23, changePercent: 1.23 },
    { symbol: 'AAPL', price: 182.45, change: -0.56, changePercent: -0.56 },
    { symbol: 'USD/CNY', price: 7.1987, change: 0.12, changePercent: 0.12 }
  ]);

  const [selectedMarket, setSelectedMarket] = useState('股票');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1小时');
  const [selectedIndicator, setSelectedIndicator] = useState('无指标');

  // 模拟实时数据更新
  useEffect(() => {
    const priceUpdateInterval = setInterval(() => {
      setPriceCards(prev => prev.map(card => {
        const randomChange = (Math.random() - 0.5) * 2;
        const newPrice = card.price * (1 + randomChange / 100);
        const change = newPrice - card.price;
        const changePercent = (change / card.price) * 100;
        
        return {
          ...card,
          price: parseFloat(newPrice.toFixed(2)),
          change: parseFloat(change.toFixed(2)),
          changePercent: parseFloat(changePercent.toFixed(2))
        };
      }));
    }, 3000);

    return () => clearInterval(priceUpdateInterval);
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

  const handleSimulateData = () => {
    setPriceCards(prev => prev.map(card => {
      const randomChange = (Math.random() - 0.5) * 4;
      const newPrice = card.price * (1 + randomChange / 100);
      const change = newPrice - card.price;
      const changePercent = (change / card.price) * 100;
      
      return {
        ...card,
        price: parseFloat(newPrice.toFixed(2)),
        change: parseFloat(change.toFixed(2)),
        changePercent: parseFloat(changePercent.toFixed(2))
      };
    }));
  };

  return (
    <div className="financial-dashboard">
      {/* 顶部导航栏 */}
      <header className="top-navigation" style={{ background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)' }}>
        <div className="nav-container">
          <div className="nav-brand">
            <h1 className="brand-title">OmniMarket</h1>
            <p className="brand-subtitle">寰宇多市场金融监控系统</p>
          </div>
          
          {/* 统一导航键 */}
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
        {/* 左侧30% - 品种监控 */}
        <div className="left-panel">
          <div className="panel-header">
            <h3 className="panel-title">监控品种</h3>
          </div>
          <div className="price-card-container">
            {priceCards.map((card, index) => (
              <div key={index} className="price-card">
                <div className="card-header">
                  <span className="symbol-icon">█</span>
                  <span className="symbol">{card.symbol}</span>
                </div>
                <div className="price">${card.price.toLocaleString()}</div>
                <div className={`change ${card.change >= 0 ? 'positive' : 'negative'}`}>
                  {card.change >= 0 ? '+' : ''}{card.change} ({card.changePercent}%)
                  <span className="status-indicator">{card.change >= 0 ? '🟢' : '🔴'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧70% - 核心功能区域 */}
        <div className="right-panel">
          {/* 专业K线图表区域 */}
          <div className="chart-container">
            <div className="chart-header">
              <h3>📊 专业K线图表区域</h3>
            </div>
            <ReactECharts 
              option={getKLineOption()} 
              style={{ height: '400px', width: '100%' }}
              opts={{ renderer: 'svg' }}
            />
          </div>

          {/* 控制面板 */}
          <div className="control-panel">
            <div className="control-group">
              <label>市场选择 ▾</label>
              <select 
                value={selectedMarket} 
                onChange={(e) => setSelectedMarket(e.target.value)}
                className="control-select"
              >
                <option value="股票">股票(AAPL)</option>
                <option value="加密货币">加密货币</option>
                <option value="外汇">外汇</option>
                <option value="期货">期货</option>
              </select>
            </div>

            <div className="control-group">
              <label>时间周期 ▾</label>
              <select 
                value={selectedTimeframe} 
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="control-select"
              >
                <option value="1分钟">1分钟</option>
                <option value="5分钟">5分钟</option>
                <option value="15分钟">15分钟</option>
                <option value="1小时">1小时</option>
                <option value="4小时">4小时</option>
                <option value="日线">日线</option>
              </select>
            </div>

            <div className="control-group">
              <label>技术指标 ▾</label>
              <select 
                value={selectedIndicator} 
                onChange={(e) => setSelectedIndicator(e.target.value)}
                className="control-select"
              >
                <option value="无指标">无指标</option>
                <option value="MA">移动平均线</option>
                <option value="MACD">MACD</option>
                <option value="RSI">RSI</option>
                <option value="布林带">布林带</option>
              </select>
            </div>

            <button className="simulate-btn" onClick={handleSimulateData}>
              🔄 模拟新数据
            </button>
          </div>

          {/* 状态信息面板 */}
          <div className="status-panel">
            <div className="status-item">
              <span className="status-icon">🔔</span>
              <span className="status-label">活跃预警:</span>
              <span className="status-value warning">85%</span>
            </div>
            <div className="status-item">
              <span className="status-icon">✅</span>
              <span className="status-label">市场状态:</span>
              <span className="status-value normal">正常</span>
            </div>
            <div className="status-item">
              <span className="status-icon">📡</span>
              <span className="status-label">数据更新:</span>
              <span className="status-value realtime">实时</span>
            </div>
            <div className="status-item">
              <span className="status-icon">⚡</span>
              <span className="status-label">延迟:</span>
              <span className="status-value latency">12ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
