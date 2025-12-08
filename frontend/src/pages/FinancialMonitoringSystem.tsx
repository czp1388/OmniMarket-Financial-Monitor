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
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-2 flex items-center justify-center gap-3">
          <span className="text-6xl">💹</span>
          <span>寰宇多市场金融监控系统</span>
        </h1>
        <p className="text-gray-400 text-lg">实时K线图表演示 - 支持多市场多周期监控</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {marketData.map((item, index) => (
          <div key={index} className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-4 shadow-lg hover:scale-[1.02] transition-all duration-300">
            <div className="text-white font-bold text-lg mb-2">{item.symbol}</div>
            <div className={`text-2xl font-bold mb-1 ${item.isPositive ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
              {formatPrice(item.price, item.type)}
            </div>
            <div className={`text-sm font-semibold ${item.isPositive ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
              {item.isPositive ? '↗' : '↘'} {formatChange(item.change)}
            </div>
          </div>
        ))}
      </div>

      <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
              <span>🌏</span><span>市场选择</span>
            </label>
            <select 
              value={selectedMarket} 
              onChange={(e) => setSelectedMarket(e.target.value)}
              className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
            >
              <option value="crypto">加密货币 (BTC/USDT)</option>
              <option value="stock">股票 (AAPL)</option>
              <option value="forex">外汇 (USD/CNY)</option>
              <option value="futures">期货</option>
            </select>
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
              <span>⏱️</span><span>时间周期</span>
            </label>
            <select 
              value={timeframe} 
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
            >
              <option value="1m">1分钟</option>
              <option value="5m">5分钟</option>
              <option value="15m">15分钟</option>
              <option value="1h">1小时</option>
              <option value="4h">4小时</option>
              <option value="1d">日线</option>
            </select>
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
              <span>📈</span><span>技术指标</span>
            </label>
            <select 
              value={technicalIndicator} 
              onChange={(e) => setTechnicalIndicator(e.target.value)}
              className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
            >
              <option value="none">无指标</option>
              <option value="sma">简单移动平均线</option>
              <option value="ema">指数移动平均线</option>
              <option value="macd">MACD</option>
              <option value="rsi">RSI</option>
              <option value="bollinger">布林带</option>
            </select>
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
              <span>⚡</span><span>操作</span>
            </label>
            <div className="flex gap-2">
              <button className="flex-1 px-3 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold rounded-lg hover:scale-105 transition-all duration-300 shadow-lg shadow-[#00ccff]/30 text-sm">
                🔄 更新
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-4 flex items-center gap-2">
          <span className="text-3xl">📊</span><span>实时K线图表</span>
        </h2>
        <div ref={chartContainerRef} style={{ width: '100%', height: '450px' }}></div>
      </div>

      <div className="bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl px-6 py-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
          <span className="text-white font-semibold">实时数据连接正常</span>
        </div>
        <div className="text-gray-400 text-sm">
          最后更新: <span className="text-[#00ccff] font-mono font-semibold">刚刚</span>
        </div>
      </div>
    </div>
  );
};

export default FinancialMonitoringSystem;
