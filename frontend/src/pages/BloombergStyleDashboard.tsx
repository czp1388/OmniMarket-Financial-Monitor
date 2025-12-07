import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import DrawingToolbar from '../components/DrawingToolbar';
import { useDrawingManager } from '../hooks/useDrawingManager';
import './BloombergStyleDashboard.css';

interface MarketSymbol {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  type: 'stock' | 'crypto' | 'forex' | 'commodity';
}

interface ChartData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const BloombergStyleDashboard: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // 绘图工具集成
  const {
    drawings,
    currentTool,
    setCurrentTool,
    addDrawing,
    removeDrawing,
    clearAllDrawings,
    loadDrawings,
    saveDrawings
  } = useDrawingManager();
  
  const [selectedMarket, setSelectedMarket] = useState<string>('AAPL');
  const [timeframe, setTimeframe] = useState<string>('1h');
  const [selectedIndicator, setSelectedIndicator] = useState<string>('none');
  const [marketSymbols, setMarketSymbols] = useState<MarketSymbol[]>([
    { symbol: 'BTC/USDT', price: 42567.39, change: 2.34, changePercent: 2.34, type: 'crypto', volume: 28456789 },
    { symbol: 'ETH/USDT', price: 2345.67, change: 1.23, changePercent: 1.23, type: 'crypto', volume: 15678900 },
    { symbol: 'AAPL', price: 182.45, change: -0.56, changePercent: -0.56, type: 'stock', volume: 45678900 },
    { symbol: 'USD/CNY', price: 7.1987, change: 0.12, changePercent: 0.12, type: 'forex', volume: 98765432 },
    { symbol: 'TSLA', price: 245.67, change: 1.45, changePercent: 1.45, type: 'stock', volume: 34567890 },
    { symbol: 'EUR/USD', price: 1.0856, change: -0.08, changePercent: -0.08, type: 'forex', volume: 87654321 },
    { symbol: 'XAU/USD', price: 1987.65, change: 15.23, changePercent: 0.77, type: 'commodity', volume: 1234567 },
    { symbol: 'SPY', price: 456.78, change: -2.34, changePercent: -0.51, type: 'stock', volume: 56789012 }
  ]);

  const [chartData, setChartData] = useState<ChartData[]>([
    { time: '09:00', open: 180, high: 185, low: 178, close: 183, volume: 10000 },
    { time: '10:00', open: 183, high: 188, low: 182, close: 187, volume: 12000 },
    { time: '11:00', open: 187, high: 190, low: 185, close: 189, volume: 15000 },
    { time: '12:00', open: 189, high: 192, low: 187, close: 191, volume: 13000 },
    { time: '13:00', open: 191, high: 195, low: 190, close: 193, volume: 14000 },
    { time: '14:00', open: 193, high: 196, low: 191, close: 194, volume: 16000 },
    { time: '15:00', open: 194, high: 198, low: 192, close: 196, volume: 18000 }
  ]);

  // 生成K线图配置
  const getChartOption = () => {
    const upColor = '#00b300';
    const upBorderColor = '#00b300';
    const downColor = '#ff4444';
    const downBorderColor = '#ff4444';

    return {
      backgroundColor: '#0a0e14',
      animation: false,
      legend: {
        bottom: 10,
        left: 'center',
        data: ['K线', 'MA5', 'MA20'],
        textStyle: { color: '#ccc' }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        borderWidth: 1,
        borderColor: '#ccc',
        backgroundColor: 'rgba(255,255,255,0.9)',
        textStyle: { color: '#000' },
        formatter: function (params: any) {
          const data = params[0].data;
          return [
            `时间: ${data[0]}<br/>`,
            `开盘: ${data[1][0]}<br/>`,
            `收盘: ${data[1][1]}<br/>`,
            `最低: ${data[1][2]}<br/>`,
            `最高: ${data[1][3]}`
          ].join('');
        }
      },
      grid: {
        left: '1%',
        right: '1%',
        bottom: '15%',
        top: '5%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: chartData.map(item => item.time),
        scale: true,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#666' } },
        axisLabel: { color: '#999', fontSize: 10 },
        splitLine: { show: false }
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitNumber: 5,
        axisLine: { lineStyle: { color: '#666' } },
        axisLabel: { color: '#999', fontSize: 10 },
        splitLine: { lineStyle: { color: '#1a1a1a' } }
      },
      dataZoom: [
        {
          type: 'inside',
          start: 50,
          end: 100
        },
        {
          show: true,
          type: 'slider',
          top: '90%',
          start: 50,
          end: 100,
          handleSize: 8,
          handleStyle: {
            color: '#666',
            borderColor: '#aaa'
          },
          textStyle: { color: '#999' }
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: chartData.map(item => [
            item.open,
            item.close,
            item.low,
            item.high
          ]),
          itemStyle: {
            color: upColor,
            color0: downColor,
            borderColor: upBorderColor,
            borderColor0: downBorderColor
          }
        },
        {
          name: 'MA5',
          type: 'line',
          data: calculateMA(5),
          smooth: true,
          lineStyle: { color: '#ff7f50', width: 1 },
          symbol: 'none'
        },
        {
          name: 'MA20',
          type: 'line',
          data: calculateMA(20),
          smooth: true,
          lineStyle: { color: '#87ceeb', width: 1 },
          symbol: 'none'
        }
      ]
    };
  };

  // 计算移动平均线
  const calculateMA = (dayCount: number) => {
    const result = [];
    for (let i = 0; i < chartData.length; i++) {
      if (i < dayCount) {
        result.push('-');
        continue;
      }
      let sum = 0;
      for (let j = 0; j < dayCount; j++) {
        sum += chartData[i - j].close;
      }
      result.push(+(sum / dayCount).toFixed(2));
    }
    return result;
  };

  // 模拟实时数据更新
  useEffect(() => {
    const interval = setInterval(() => {
      setMarketSymbols(prev => prev.map(symbol => {
        const randomChange = (Math.random() - 0.5) * 0.5;
        const newPrice = symbol.price * (1 + randomChange / 100);
        const change = newPrice - symbol.price;
        const changePercent = (change / symbol.price) * 100;
        
        return {
          ...symbol,
          price: parseFloat(newPrice.toFixed(symbol.type === 'forex' ? 4 : 2)),
          change: parseFloat(change.toFixed(symbol.type === 'forex' ? 4 : 2)),
          changePercent: parseFloat(changePercent.toFixed(2))
        };
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // 模拟新数据按钮功能
  const simulateNewData = () => {
    const lastClose = chartData[chartData.length - 1].close;
    const newPrice = lastClose * (1 + (Math.random() - 0.5) * 0.02);
    const newHigh = Math.max(lastClose, newPrice) * (1 + Math.random() * 0.01);
    const newLow = Math.min(lastClose, newPrice) * (1 - Math.random() * 0.01);
    
    const newDataPoint: ChartData = {
      time: `${16 + Math.floor(Math.random() * 4)}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`,
      open: lastClose,
      high: parseFloat(newHigh.toFixed(2)),
      low: parseFloat(newLow.toFixed(2)),
      close: parseFloat(newPrice.toFixed(2)),
      volume: Math.floor(Math.random() * 20000) + 10000
    };

    setChartData(prev => [...prev.slice(1), newDataPoint]);
  };

  const formatPrice = (price: number, type: string) => {
    if (type === 'forex') return price.toFixed(4);
    if (type === 'crypto') return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    return `$${price.toFixed(2)}`;
  };

  const formatChange = (change: number, type: string) => {
    const sign = change >= 0 ? '+' : '';
    if (type === 'forex') return `${sign}${change.toFixed(4)}`;
    return `${sign}${change.toFixed(2)}`;
  };

  return (
    <div className="bloomberg-terminal">
      {/* 第1步：基础布局 - 导航栏 */}
      <header className="terminal-navbar">
        <div className="navbar-left">
          <h1 className="terminal-title">寰宇多市场金融监控系统</h1>
          <nav className="main-navigation">
            <button 
              className={`nav-btn ${location.pathname === '/' ? 'active' : ''}`}
              onClick={() => navigate('/')}
            >
              市场数据
            </button>
            <button 
              className={`nav-btn ${location.pathname === '/chart' ? 'active' : ''}`}
              onClick={() => navigate('/chart')}
            >
              分析工具
            </button>
            <button 
              className={`nav-btn ${location.pathname === '/virtual-trading' ? 'active' : ''}`}
              onClick={() => navigate('/virtual-trading')}
            >
              交易执行
            </button>
            <button 
              className={`nav-btn ${location.pathname === '/portfolio' ? 'active' : ''}`}
              onClick={() => navigate('/portfolio')}
            >
              投资组合
            </button>
            <button 
              className={`nav-btn ${location.pathname === '/alerts' ? 'active' : ''}`}
              onClick={() => navigate('/alerts')}
            >
              预警管理
            </button>
            <button 
              className={`nav-btn ${location.pathname === '/warrants' ? 'active' : ''}`}
              onClick={() => navigate('/warrants')}
            >
              牛熊证监控
            </button>
            <button 
              className={`nav-btn ${location.pathname === '/settings' ? 'active' : ''}`}
              onClick={() => navigate('/settings')}
            >
              系统设置
            </button>
          </nav>
        </div>
        <div className="navbar-right">
          <div className="status-info">
            <span className="status-item">延迟: <span className="status-value">12ms</span></span>
            <span className="status-item">数据源: <span className="status-value positive">实时</span></span>
            <span className="status-item">时间: <span className="status-value">{new Date().toLocaleTimeString('zh-CN', { hour12: false })}</span></span>
          </div>
        </div>
      </header>

      <div className="terminal-layout">
        {/* 左侧品种监控区域 */}
        <aside className="symbols-sidebar">
          <div className="sidebar-header">
            <h3>监控列表</h3>
            <span className="symbols-count">{marketSymbols.length} 个品种</span>
          </div>
          <div className="symbols-grid">
            {marketSymbols.map((symbol, index) => (
              <div key={index} className={`symbol-row ${symbol.changePercent >= 0 ? 'positive' : 'negative'}`}>
                <div className="symbol-name">{symbol.symbol}</div>
                <div className="symbol-price">{formatPrice(symbol.price, symbol.type)}</div>
                <div className="symbol-change">{formatChange(symbol.change, symbol.type)}</div>
                <div className={`symbol-percent ${symbol.changePercent >= 0 ? 'positive' : 'negative'}`}>
                  {symbol.changePercent >= 0 ? '+' : ''}{symbol.changePercent}%
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* 右侧主内容区 */}
        <main className="main-content-area">
          {/* 第2步：控制面板 */}
          <div className="control-panel">
            <div className="control-group">
              <label className="control-label">市场</label>
              <select 
                value={selectedMarket} 
                onChange={(e) => setSelectedMarket(e.target.value)}
                className="control-select"
              >
                <option value="AAPL">股票</option>
                <option value="BTC">加密货币</option>
                <option value="EURUSD">外汇</option>
                <option value="XAU">商品</option>
              </select>
            </div>

            <div className="control-group">
              <label className="control-label">时间周期</label>
              <select 
                value={timeframe} 
                onChange={(e) => setTimeframe(e.target.value)}
                className="control-select"
              >
                <option value="1m">1分钟</option>
                <option value="5m">5分钟</option>
                <option value="15m">15分钟</option>
                <option value="1h">1小时</option>
                <option value="4h">4小时</option>
                <option value="1d">日线</option>
              </select>
            </div>

            <div className="control-group">
              <label className="control-label">技术指标</label>
              <select 
                value={selectedIndicator} 
                onChange={(e) => setSelectedIndicator(e.target.value)}
                className="control-select"
              >
                <option value="none">无</option>
                <option value="ma">移动平均</option>
                <option value="macd">MACD</option>
                <option value="rsi">RSI</option>
                <option value="bollinger">布林带</option>
              </select>
            </div>

            <div className="control-group">
              <label className="control-label">操作</label>
              <button 
                className="control-btn primary"
                onClick={simulateNewData}
              >
                模拟数据
              </button>
            </div>
          </div>

          {/* 第3步：图表区域 */}
          <div className="chart-section">
            <div className="chart-header">
              <div className="chart-title">
                <span className="symbol-display">{selectedMarket}</span>
                <span className="timeframe-display">{timeframe.toUpperCase()} 图表</span>
              </div>
              <div className="chart-stats">
                <span className="stat-item">开: 182.34</span>
                <span className="stat-item">高: 185.67</span>
                <span className="stat-item">低: 181.23</span>
                <span className="stat-item">收: 184.56</span>
                <span className="stat-item positive">+1.22%</span>
              </div>
            </div>
            
            <div className="chart-container">
              {/* 绘图工具栏 */}
              <DrawingToolbar
                currentTool={currentTool}
                onToolChange={setCurrentTool}
                onClear={clearAllDrawings}
              />
              <ReactECharts 
                option={getChartOption()} 
                style={{ height: '500px', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
          </div>

          {/* 底部状态栏 */}
          <div className="status-bar">
            <div className="market-status">
              <span className="status-tag positive">市场开放</span>
              <span className="status-tag">成交量: 45.6M</span>
              <span className="status-tag">上涨: 1,234</span>
              <span className="status-tag">下跌: 876</span>
            </div>
            <div className="system-status">
              <span className="system-tag positive">已连接</span>
              <span className="system-tag">数据: 实时</span>
              <span className="system-tag">预警: 12 个活跃</span>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default BloombergStyleDashboard;
