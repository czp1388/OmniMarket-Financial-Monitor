import React, { useState, useEffect, useRef } from 'react';
import { createChart, UTCTimestamp } from 'lightweight-charts';
import './FinancialMonitoringSystem.css';

const FinancialMonitoringSystem: React.FC = () => {
  const [selectedMarket, setSelectedMarket] = useState<string>('crypto');
  const [timeframe, setTimeframe] = useState<string>('1h');
  const [technicalIndicator, setTechnicalIndicator] = useState<string>('none');
  const [activeNav, setActiveNav] = useState<string>('overview');
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candleSeriesRef = useRef<any>(null);
  const smaSeriesRef = useRef<any>(null);

  // 专业金融数据 - 彭博终端风格
  const [marketData] = useState([
    { 
      symbol: 'BTC/USDT', 
      price: 42567.89, 
      change: 2.34,
      changeAmount: 975.42,
      volume: '28.4M',
      type: 'crypto',
      isPositive: true
    },
    { 
      symbol: 'ETH/USDT', 
      price: 2345.67, 
      change: 1.23,
      changeAmount: 28.54,
      volume: '15.2M',
      type: 'crypto',
      isPositive: true
    },
    { 
      symbol: 'AAPL', 
      price: 182.45, 
      change: -0.56,
      changeAmount: -1.02,
      volume: '45.6M',
      type: 'stock',
      isPositive: false
    },
    { 
      symbol: 'USD/CNY', 
      price: 7.1987, 
      change: 0.12,
      changeAmount: 0.0086,
      volume: '1.2B',
      type: 'forex',
      isPositive: true
    }
  ]);

  // 初始化图表
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 450,
      layout: {
        background: { color: '#1a1a1a' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
      },
      crosshair: {
        mode: 1,
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

    // 生成模拟K线数据
    const generateSampleData = (count = 200) => {
      const data = [];
      let time = new Date();
      time.setHours(0, 0, 0, 0);
      time.setDate(time.getDate() - count);
      
      let price = 42000;
      
      for (let i = 0; i < count; ++i) {
        time.setDate(time.getDate() + 1);
        
        const volatility = 0.02;
        const changePercent = 2 * volatility * Math.random() - volatility;
        const change = price * changePercent;
        
        const open = price;
        const close = price + change;
        const high = Math.max(open, close) + Math.abs(change) * Math.random();
        const low = Math.min(open, close) - Math.abs(change) * Math.random();
        const volume = Math.random() * 1000 + 500;
        
        data.push({
          time: (time.getTime() / 1000) as UTCTimestamp,
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

    // 计算SMA
    const calculateSMA = (data: any[], period: number) => {
      const result = [];
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

    const initialData = generateSampleData();
    candleSeries.setData(initialData);

    const smaData = calculateSMA(initialData, 20);
    smaSeries.setData(smaData);

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    smaSeriesRef.current = smaSeries;

    // 响应式调整
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // 格式化价格显示
  const formatPrice = (price: number, type: string) => {
    if (type === 'forex') return price.toFixed(4);
    if (type === 'crypto') return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    return `$${price.toFixed(2)}`;
  };

  // 格式化涨跌幅显示
  const formatChange = (change: number) => {
    return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
  };

  return (
    <div className="financial-monitoring-system">
      <div className="container">
        <div className="header">
          <h1>寰宇多市场金融监控系统</h1>
          <p>实时K线图表演示 - 支持多市场多周期监控</p>
        </div>

        <div className="market-info">
          {marketData.map((item, index) => (
            <div key={index} className="info-card">
              <div>{item.symbol}</div>
              <div className={`info-value ${item.isPositive ? 'positive' : 'negative'}`}>
                {formatPrice(item.price, item.type)}
              </div>
              <div>{formatChange(item.change)}</div>
            </div>
          ))}
        </div>

        <div className="controls">
          <div className="control-group">
            <label>市场选择:</label>
            <select 
              value={selectedMarket} 
              onChange={(e) => setSelectedMarket(e.target.value)}
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
            <label>技术指标:</label>
            <select 
              value={technicalIndicator} 
              onChange={(e) => setTechnicalIndicator(e.target.value)}
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
            <button>模拟新数据</button>
            <button>重置图表</button>
          </div>
        </div>

        <div className="chart-container" ref={chartContainerRef}></div>

        <div className="status-bar">
          <div className="status">
            <div className="status-dot"></div>
            <span>实时数据连接正常</span>
          </div>
          <div className="last-update">最后更新: <span>刚刚</span></div>
        </div>
      </div>
    </div>
  );
};

export default FinancialMonitoringSystem;
