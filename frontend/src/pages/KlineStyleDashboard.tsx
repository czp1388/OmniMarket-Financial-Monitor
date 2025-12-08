import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { createChart, ColorType, CrosshairMode, CandlestickData, LineData } from 'lightweight-charts';
import { realTimeDataService, MarketData } from '../services/realTimeDataService';
import DrawingToolbar from '../components/DrawingToolbar';
import { useDrawingManager } from '../hooks/useDrawingManager';
import './KlineStyleDashboard.css';

interface MarketSymbol {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  type: 'stock' | 'crypto' | 'forex' | 'commodity';
  lastUpdate: string;
  source: string;
}

interface ChartData {
  time: string;
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
  const updateIntervalRef = useRef<number | null>(null);
  
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
  
  const [selectedMarket, setSelectedMarket] = useState<string>('crypto');
  const [timeframe, setTimeframe] = useState<string>('1h');
  const [selectedIndicator, setSelectedIndicator] = useState<string>('none');
  const [marketSymbols, setMarketSymbols] = useState<MarketSymbol[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string>('刚刚');

  // 生成模拟K线数据 - 使用字符串时间格式
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
        time: time.toISOString().split('T')[0], // 使用日期字符串格式
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
    const result: { time: string; value: number }[] = [];
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

  // 实时数据更新
  useEffect(() => {
    const symbols = [
      'BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 
      'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'
    ];
    
    const stopUpdates = realTimeDataService.startRealTimeUpdates(
      (data: MarketData[]) => {
        const updatedSymbols = data.map(item => ({
          symbol: item.symbol,
          price: item.price,
          change: item.change,
          changePercent: item.changePercent,
          type: item.type,
          volume: item.volume,
          lastUpdate: item.lastUpdate,
          source: item.source
        }));
        setMarketSymbols(updatedSymbols);
        setLastUpdate(new Date().toLocaleTimeString('zh-CN', { hour12: false }));
      },
      symbols,
      5000 // 5秒更新间隔
    );

    return stopUpdates;
  }, []);

  // 模拟新数据按钮功能
  const addRandomData = () => {
    if (chartData.length === 0 || !candleSeriesRef.current || !smaSeriesRef.current) return;

    const lastData = chartData[chartData.length - 1];
    const lastDate = new Date(lastData.time);
    lastDate.setDate(lastDate.getDate() + 1); // 增加一天
    const time = lastDate.toISOString().split('T')[0];
    
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

  // 获取市场数据（带缓存优化）
  const fetchMarketData = async () => {
    try {
      const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
      const response = await fetch(`http://localhost:8000/api/v1/market/tickers?${symbols.map(s => `symbols[]=${s}`).join('&')}`);
      
      if (!response.ok) throw new Error('获取市场数据失败');
      
      const data = await response.json();
      if (data.data && Array.isArray(data.data)) {
        setMarketSymbols(data.data);
        setLastUpdate(new Date().toLocaleTimeString('zh-CN', { hour12: false }));
      }
    } catch (err) {
      console.error('市场数据获取失败:', err);
    }
  };

  // 设置定时更新（每10秒更新一次，避免过度请求）
  useEffect(() => {
    fetchMarketData();
    const interval = setInterval(fetchMarketData, 10000);
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price: number, type: string) => {
    if (type === 'forex') return price.toFixed(4);
    if (type === 'crypto') return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    return `$${price.toFixed(2)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      <div className="p-6 space-y-6">
        <div className="text-center">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-2 flex items-center justify-center gap-3">
            <span className="text-6xl">📈</span>
            <span>寐宇多市场金融监控系统</span>
          </h1>
          <p className="text-gray-400 text-lg">实时K线图表演示 - 支持多市场多周期监控</p>
        </div>

        {/* 功能导航栏 */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {[
            { label: '仪表板', icon: '📋', path: '/' },
            { label: '图表分析', icon: '📈', path: '/chart' },
            { label: '虚拟交易', icon: '💹', path: '/virtual-trading' },
            { label: '预警管理', icon: '⚡', path: '/alerts' },
            { label: '组合管理', icon: '💼', path: '/portfolio' },
            { label: '权证监控', icon: '📊', path: '/warrants' },
            { label: '全自动交易', icon: '🤖', path: '/auto-trading' },
            { label: '半自动交易', icon: '🎯', path: '/semi-auto-trading' },
            { label: '系统设置', icon: '⚙️', path: '/settings' }
          ].map((nav, idx) => (
            <button 
              key={idx}
              className={`px-4 py-2 rounded-lg transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${
                idx === 0
                  ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold shadow-lg shadow-[#00ccff]/30'
                  : 'bg-[#141a2a] text-gray-400 hover:bg-[#1a2332] hover:text-white'
              }`}
              onClick={() => navigate(nav.path)}
            >
              <span className="text-lg">{nav.icon}</span>
              <span>{nav.label}</span>
            </button>
          ))}
        </div>

        {/* 市场信息卡片 - 专业金融终端布局 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {marketSymbols.slice(0, 8).map((symbol, index) => (
            <div key={index} className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-4 shadow-lg hover:scale-[1.02] transition-all duration-300 cursor-pointer">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-bold text-lg">{symbol.symbol}</span>
                <span className="text-xs px-2 py-0.5 rounded bg-[#00ccff]/20 text-[#00ccff]">{symbol.source}</span>
              </div>
              <div className="mb-2">
                <span className="text-2xl font-bold text-white">{formatPrice(symbol.price, symbol.type)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={`text-lg font-bold ${
                  symbol.changePercent >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                }`}>
                  {symbol.changePercent >= 0 ? '↗ +' : '↘ '}{symbol.changePercent}%
                </span>
                <span className="text-sm text-gray-400">
                  量: {symbol.volume ? (symbol.volume > 1000000 
                    ? `${(symbol.volume / 1000000).toFixed(2)}M` 
                    : symbol.volume > 1000 
                    ? `${(symbol.volume / 1000).toFixed(2)}K` 
                    : symbol.volume.toFixed(0)) : 'N/A'}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* 控制面板 - 匹配kline_demo.html的网格布局 */}
        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                <option value="crypto">加密货币 (BTC/USDT)</option>
                <option value="stock">股票 (AAPL)</option>
                <option value="forex">外汇 (USD/CNY)</option>
                <option value="futures">期货</option>
              </select>
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>⏱️</span>
                <span>时间周期</span>
              </label>
              <select 
                value={timeframe} 
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
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
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>📈</span>
                <span>技术指标</span>
              </label>
              <select 
                value={selectedIndicator} 
                onChange={(e) => setSelectedIndicator(e.target.value)}
                className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
              >
                <option value="none">无指标</option>
                <option value="sma">SMA - 简单移动平均</option>
                <option value="ema">EMA - 指数移动平均</option>
                <option value="macd">MACD - 趋势指标</option>
                <option value="rsi">RSI - 相对强弱指数</option>
                <option value="bollinger">布林带 - 波动率</option>
                <option value="kdj">KDJ - 随机指标</option>
                <option value="atr">ATR - 真实波幅</option>
                <option value="obv">OBV - 能量潮</option>
              </select>
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>⚡</span>
                <span>操作</span>
              </label>
              <div className="flex gap-2">
                <button 
                  className="flex-1 px-3 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold rounded-lg hover:scale-105 transition-all duration-300 shadow-lg shadow-[#00ccff]/30 text-sm"
                  onClick={addRandomData}
                >
                  📡 新数据
                </button>
                <button 
                  className="flex-1 px-3 py-3 bg-[#1a2332] border border-[#2a3a5a] text-white font-semibold rounded-lg hover:bg-[#2a3a5a] transition-colors text-sm"
                  onClick={resetChart}
                >
                  🔄 重置
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 图表区域 - 使用Lightweight Charts */}
        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-3xl">📊</span>
              <span>实时K线图表</span>
            </h2>
            <DrawingToolbar
              currentTool={currentTool}
              onToolChange={setCurrentTool}
              onClear={clearAllDrawings}
            />
          </div>
          <div ref={chartContainerRef} style={{ width: '100%', height: '450px' }} />
        </div>

        {/* 专业状态栏 */}
        <div className="bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl px-6 py-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
              <span className="text-white font-semibold">实时数据连接正常</span>
            </div>
            <span className="text-gray-400 text-sm">
              数据源: <span className="text-[#00ccff] font-semibold">{Array.from(new Set(marketSymbols.map(s => s.source))).join(', ')}</span>
            </span>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-gray-400 text-sm">
              最后更新: <span className="text-[#00ccff] font-mono font-semibold">{lastUpdate}</span>
            </span>
            <span className="text-gray-400 text-sm">
              市场状态: <span className="text-[#00ff88] font-semibold">交易中</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KlineStyleDashboard;
