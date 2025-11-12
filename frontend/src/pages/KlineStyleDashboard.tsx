import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { createChart, ColorType, CrosshairMode, CandlestickData, LineData } from 'lightweight-charts';
import './KlineStyleDashboard.css';

interface MarketSymbol {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  type: 'stock' | 'crypto' | 'forex' | 'commodity';
}

interface ChartData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const KlineStyleDashboard: React.FC = () => {
  const navigate = useNavigate();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candleSeriesRef = useRef<any>(null);
  const smaSeriesRef = useRef<any>(null);
  
  const [selectedMarket, setSelectedMarket] = useState<string>('crypto');
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

  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string>('刚刚');

  // 生成模拟K线数据 - 完全匹配kline_demo.html的逻辑
  const generateSampleData = (count: number = 200): ChartData[] => {
    const data: ChartData[] = [];
    let time = new Date();
    time.setHours(0, 0, 0, 0);
    time.setDate(time.getDate() - count);
    
    let price = 42000; // 初始价格
    
    for (let i = 0; i < count; ++i) {
      time.setDate(time.getDate() + 1);
      
      const volatility = 0.02; // 2% 波动率
      const changePercent = 2 * volatility * Math.random() - volatility;
      const change = price * changePercent;
      
      const open = price;
      const close = price + change;
      const high = Math.max(open, close) + Math.abs(change) * Math.random();
      const low = Math.min(open, close) - Math.abs(change) * Math.random();
      const volume = Math.random() * 1000 + 500;
      
      data.push({
        time: time.getTime() / 1000, // 使用浮点数而不是整数
        open: open,
        high: high,
        low: low,
        close: close,
        volume: volume,
      });
      
      price = close;
    }
    
    return data;
  };

  // 计算移动平均线
  const calculateSMA = (data: ChartData[], period: number) => {
    const result: { time: number; value: number }[] = [];
    for (let i = period - 1; i < data.length; i++) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j].close;
      }
      result.push({
        time: data[i].time,
        value: sum / period,
      });
    }
    return result;
  };

  // 初始化图表
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 450,
      layout: {
        background: { type: ColorType.Solid, color: '#1a1a1a' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: '#2b2b43',
      },
      timeScale: {
        borderColor: '#2b2b43',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#00ff88',
      downColor: '#ff4444',
      borderDownColor: '#ff4444',
      borderUpColor: '#00ff88',
      wickDownColor: '#ff4444',
      wickUpColor: '#00ff88',
    });

    const smaSeries = chart.addLineSeries({
      color: '#2962FF',
      lineWidth: 2,
      title: '20周期SMA',
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    smaSeriesRef.current = smaSeries;

    // 初始化数据
    const initialData = generateSampleData();
    setChartData(initialData);
    candleSeries.setData(initialData);

    const smaData = calculateSMA(initialData, 20);
    smaSeries.setData(smaData);

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, []);

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

  // 模拟新数据按钮功能 - 匹配kline_demo.html的逻辑
  const addRandomData = () => {
    if (chartData.length === 0 || !candleSeriesRef.current || !smaSeriesRef.current) return;

    const lastData = chartData[chartData.length - 1];
    const time = lastData.time + 86400; // 增加一天
    
    const volatility = 0.015;
    const changePercent = 2 * volatility * Math.random() - volatility;
    const change = lastData.close * changePercent;
    
    const open = lastData.close;
    const close = lastData.close + change;
    const high = Math.max(open, close) + Math.abs(change) * Math.random();
    const low = Math.min(open, close) - Math.abs(change) * Math.random();
    
    const newCandle: ChartData = {
      time: time,
      open: open,
      high: high,
      low: low,
      close: close,
      volume: Math.random() * 1000 + 500,
    };
    
    const newChartData = [...chartData, newCandle];
    setChartData(newChartData);
    candleSeriesRef.current.update(newCandle);
    
    // 更新SMA
    if (newChartData.length >= 20) {
      const newSmaData = calculateSMA(newChartData, 20);
      smaSeriesRef.current.setData(newSmaData);
    }
    
    // 更新最后更新时间
    setLastUpdate(new Date().toLocaleTimeString('zh-CN', { hour12: false }));
  };

  // 重置图表函数 - 匹配kline_demo.html的逻辑
  const resetChart = () => {
    const newData = generateSampleData();
    setChartData(newData);
    
    if (candleSeriesRef.current && smaSeriesRef.current) {
      candleSeriesRef.current.setData(newData);
      
      const newSmaData = calculateSMA(newData, 20);
      smaSeriesRef.current.setData(newSmaData);
    }
    
    setLastUpdate('刚刚');
  };

  const formatPrice = (price: number, type: string) => {
    if (type === 'forex') return price.toFixed(4);
    if (type === 'crypto') return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    return `$${price.toFixed(2)}`;
  };

  return (
    <div className="kline-terminal">
      <div className="container">
        <div className="header">
          <h1>寰宇多市场金融监控系统</h1>
          <p>实时K线图表演示 - 支持多市场多周期监控</p>
        </div>

        {/* 功能导航栏 */}
        <div className="nav-bar">
          <button 
            className="nav-btn active"
            onClick={() => navigate('/')}
          >
            仪表板
          </button>
          <button 
            className="nav-btn"
            onClick={() => navigate('/chart')}
          >
            图表分析
          </button>
          <button 
            className="nav-btn"
            onClick={() => navigate('/virtual-trading')}
          >
            虚拟交易
          </button>
          <button 
            className="nav-btn"
            onClick={() => navigate('/alerts')}
          >
            预警管理
          </button>
          <button 
            className="nav-btn"
            onClick={() => navigate('/portfolio')}
          >
            组合管理
          </button>
          <button 
            className="nav-btn"
            onClick={() => navigate('/warrants')}
          >
            权证监控
          </button>
          <button 
            className="nav-btn"
            onClick={() => navigate('/settings')}
          >
            系统设置
          </button>
        </div>

        {/* 市场信息卡片 - 匹配kline_demo.html的网格布局 */}
        <div className="market-info">
          {marketSymbols.slice(0, 4).map((symbol, index) => (
            <div key={index} className="info-card">
              <div>{symbol.symbol}</div>
              <div className={`info-value ${symbol.changePercent >= 0 ? 'positive' : 'negative'}`}>
                {formatPrice(symbol.price, symbol.type)}
              </div>
              <div className={symbol.changePercent >= 0 ? 'positive' : 'negative'}>
                {symbol.changePercent >= 0 ? '+' : ''}{symbol.changePercent}%
              </div>
            </div>
          ))}
        </div>

        {/* 控制面板 - 匹配kline_demo.html的网格布局 */}
        <div className="controls">
          <div className="control-group">
            <label>市场选择:</label>
            <select 
              value={selectedMarket} 
              onChange={(e) => setSelectedMarket(e.target.value)}
              className="control-select"
            >
              <option value="crypto">加密货币 (BTC/USDT)</option>
              <option value="stock">股票 (AAPL)</option>
              <option value="forex">外汇 (USD/CNY)</option>
              <option value="futures">期货</option>
            </select>
          </div>
          <div className="control-group">
            <label>时间周期:</label>
            <select 
              value={timeframe} 
              onChange={(e) => setTimeframe(e.target.value)}
              className="control-select"
            >
              <option value="1m">1分钟</option>
              <option value="5m">5分钟</option>
              <option value="15m">15分钟</option>
              <option value="30m">30分钟</option>
              <option value="1h">1小时</option>
              <option value="4h">4小时</option>
              <option value="1d">日线</option>
              <option value="1w">周线</option>
              <option value="1M">月线</option>
              <option value="3M">季线</option>
              <option value="1y">年线</option>
            </select>
          </div>
          <div className="control-group">
            <label>技术指标:</label>
            <select 
              value={selectedIndicator} 
              onChange={(e) => setSelectedIndicator(e.target.value)}
              className="control-select"
            >
              <option value="none">无指标</option>
              <option value="sma">简单移动平均线</option>
              <option value="ema">指数移动平均线</option>
              <option value="macd">MACD</option>
              <option value="rsi">RSI</option>
              <option value="bollinger">布林带</option>
            </select>
          </div>
          <div className="control-group">
            <label>操作:</label>
            <button className="control-btn" onClick={addRandomData}>
              模拟新数据
            </button>
            <button className="control-btn" onClick={resetChart}>
              重置图表
            </button>
          </div>
        </div>

        {/* 图表区域 - 使用Lightweight Charts */}
        <div className="chart-container">
          <div ref={chartContainerRef} style={{ width: '100%', height: '100%' }} />
        </div>

        {/* 状态栏 */}
        <div className="status-bar">
          <div className="status">
            <div className="status-dot"></div>
            <span>实时数据连接正常</span>
          </div>
          <div>最后更新: <span>{lastUpdate}</span></div>
        </div>
      </div>
    </div>
  );
};

export default KlineStyleDashboard;
