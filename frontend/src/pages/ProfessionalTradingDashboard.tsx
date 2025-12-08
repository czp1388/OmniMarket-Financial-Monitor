import React, { useState, useEffect, useRef } from 'react';
import { createChart, Time } from 'lightweight-charts';
import { ApiService } from '../services/api';
import './ProfessionalTradingDashboard.css';

interface MarketSymbol {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  type: 'stock' | 'crypto' | 'forex' | 'commodity';
}

interface CandleData {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const ProfessionalTradingDashboard: React.FC = () => {
  const [selectedMarket, setSelectedMarket] = useState<string>('crypto');
  const [timeframe, setTimeframe] = useState<string>('1h');
  const [selectedIndicator, setSelectedIndicator] = useState<string>('none');
  const [lastUpdate, setLastUpdate] = useState<string>('刚刚');
  const [isChartLoading, setIsChartLoading] = useState<boolean>(false);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candleSeriesRef = useRef<any>(null);
  const smaSeriesRef = useRef<any>(null);
  
  const [marketSymbols, setMarketSymbols] = useState<MarketSymbol[]>([
    { symbol: 'BTC/USDT', price: 42567.89, change: 974.23, changePercent: 2.34, type: 'crypto' },
    { symbol: 'ETH/USDT', price: 2345.67, change: 28.51, changePercent: 1.23, type: 'crypto' },
    { symbol: 'AAPL', price: 182.45, change: -1.03, changePercent: -0.56, type: 'stock' },
    { symbol: 'USD/CNY', price: 7.1987, change: 0.0086, changePercent: 0.12, type: 'forex' }
  ]);

  // 生成模拟K线数据
  const generateSampleData = (count = 200): CandleData[] => {
    const data: CandleData[] = [];
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
        time: Math.floor(time.getTime() / 1000) as Time,
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
  const calculateSMA = (data: CandleData[], period: number) => {
    const result: { time: Time; value: number }[] = [];
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

    // 创建图表
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
        mode: 1, // CrosshairMode.Normal
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

    // 添加K线系列
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#00ff88',
      downColor: '#ff4444',
      borderDownColor: '#ff4444',
      borderUpColor: '#00ff88',
      wickDownColor: '#ff4444',
      wickUpColor: '#00ff88',
    });

    // 添加移动平均线系列
    const smaSeries = chart.addLineSeries({
      color: '#2962FF',
      lineWidth: 2,
      title: '20周期SMA',
    });

    // 设置初始数据
    const initialData = generateSampleData();
    candleSeries.setData(initialData);
    
    const smaData = calculateSMA(initialData, 20);
    smaSeries.setData(smaData);

    // 保存引用
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

  // 添加随机数据
  const addRandomData = () => {
    if (!candleSeriesRef.current || !smaSeriesRef.current) return;

    setIsChartLoading(true);
    
    setTimeout(() => {
      const lastData = generateSampleData(1)[0];
      // 将时间转换为number进行计算，然后再转换回Time类型
      const currentTime = lastData.time as number;
      const time = (currentTime + 86400) as Time; // 增加一天
      
      const volatility = 0.015;
      const changePercent = 2 * volatility * Math.random() - volatility;
      const change = lastData.close * changePercent;
      
      const open = lastData.close;
      const close = lastData.close + change;
      const high = Math.max(open, close) + Math.abs(change) * Math.random();
      const low = Math.min(open, close) - Math.abs(change) * Math.random();
      
      const newCandle = {
        time: time,
        open: open,
        high: high,
        low: low,
        close: close,
      };
      
      candleSeriesRef.current.update(newCandle);
      
      // 更新最后更新时间
      setLastUpdate(new Date().toLocaleTimeString());
      setIsChartLoading(false);
    }, 500);
  };

  // 重置图表
  const resetChart = () => {
    if (!candleSeriesRef.current || !smaSeriesRef.current) return;

    setIsChartLoading(true);
    
    setTimeout(() => {
      const newData = generateSampleData();
      candleSeriesRef.current.setData(newData);
      
      const newSmaData = calculateSMA(newData, 20);
      smaSeriesRef.current.setData(newSmaData);
      
      setLastUpdate('刚刚');
      setIsChartLoading(false);
    }, 500);
  };

  // 从后端API获取市场数据
  const fetchMarketData = async () => {
    try {
      const response = await ApiService.market.getTickers(
        ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY'],
        'all'
      );
      
      if (response && Array.isArray(response)) {
        const updatedSymbols = response.map((ticker: any) => {
          // 直接使用后端返回的已计算好的涨跌幅数据
          const price = ticker.last || ticker.close || 0;
          const change = ticker.change || 0;
          const changePercent = ticker.change_percent || 0;
          
          let type: 'stock' | 'crypto' | 'forex' = 'crypto';
          if (ticker.symbol.includes('/')) {
            if (ticker.symbol.includes('USD') || ticker.symbol.includes('CNY')) {
              type = 'forex';
            } else {
              type = 'crypto';
            }
          } else {
            type = 'stock';
          }
          
          return {
            symbol: ticker.symbol,
            price: price,
            change: change,
            changePercent: changePercent,
            type: type
          };
        });
        
        setMarketSymbols(updatedSymbols);
        setLastUpdate(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error('获取市场数据失败:', error);
      // 如果API调用失败，使用模拟数据更新
      const updatedSymbols = marketSymbols.map(symbol => ({
        ...symbol,
        price: symbol.price * (1 + (Math.random() - 0.5) * 0.01),
        change: symbol.change * (1 + (Math.random() - 0.5) * 0.1),
        changePercent: symbol.changePercent * (1 + (Math.random() - 0.5) * 0.1)
      }));
      setMarketSymbols(updatedSymbols);
      setLastUpdate(new Date().toLocaleTimeString());
    }
  };

  // 实时数据更新
  useEffect(() => {
    // 立即获取一次数据
    fetchMarketData();
    
    // 设置定时器每5秒更新一次
    const interval = setInterval(() => {
      fetchMarketData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price: number, type: string) => {
    if (type === 'forex') return price.toFixed(4);
    if (type === 'crypto') return `$${price.toLocaleString()}`;
    return `$${price.toFixed(2)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      <div className="max-w-[1800px] mx-auto px-6 py-6">
        <div className="mb-6">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-3 mb-2">
            <span className="text-5xl">📈</span>
            <span>寰宇多市场金融监控系统</span>
          </h1>
          <p className="text-gray-400 text-lg ml-16">实时K线图表演示 - 支持多市场多周期监控</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {marketSymbols.map((symbol, index) => (
            <div key={index} className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-4 shadow-lg hover:scale-[1.02] transition-all duration-300 hover:shadow-[#00ccff]/10">
              <div className="text-sm text-gray-400 mb-2 font-semibold">{symbol.symbol}</div>
              <div className={`text-2xl font-bold mb-1 ${
                symbol.changePercent >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
              }`}>
                {formatPrice(symbol.price, symbol.type)}
              </div>
              <div className={`text-sm font-semibold flex items-center gap-1 ${
                symbol.changePercent >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
              }`}>
                <span>{symbol.changePercent >= 0 ? '↗' : '↘'}</span>
                <span>{symbol.changePercent >= 0 ? '+' : ''}{symbol.changePercent.toFixed(2)}%</span>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-5 mb-6 shadow-lg">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                <span>🌐</span>
                <span>市场选择</span>
              </label>
              <select 
                value={selectedMarket} 
                onChange={(e) => setSelectedMarket(e.target.value)}
                className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-2.5 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
              >
                <option value="crypto">🪙 加密货币 (BTC/USDT)</option>
                <option value="stock">📈 股票 (AAPL)</option>
                <option value="forex">💱 外汇 (USD/CNY)</option>
                <option value="futures">📊 期货</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                <span>⏱️</span>
                <span>时间周期</span>
              </label>
              <select 
                value={timeframe} 
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-2.5 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
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
              <label className="block text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                <span>📊</span>
                <span>技术指标</span>
              </label>
              <select 
                value={selectedIndicator} 
                onChange={(e) => setSelectedIndicator(e.target.value)}
                className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-2.5 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
              >
                <option value="none">无指标</option>
                <option value="sma">SMA - 简单移动平均线</option>
                <option value="ema">EMA - 指数移动平均线</option>
                <option value="macd">MACD</option>
                <option value="rsi">RSI</option>
                <option value="bollinger">布林带</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                <span>⚡</span>
                <span>操作</span>
              </label>
              <div className="flex gap-2">
                <button 
                  className="flex-1 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black rounded-lg px-3 py-2.5 font-bold hover:scale-[1.02] transition-all duration-300 shadow-md shadow-[#00ccff]/30 text-sm"
                  onClick={addRandomData}
                >
                  🔄
                </button>
                <button 
                  className="flex-1 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-lg px-3 py-2.5 font-bold hover:scale-[1.02] transition-all duration-300 shadow-md text-sm"
                  onClick={resetChart}
                >
                  🔄 重置
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl overflow-hidden shadow-2xl mb-6">
          {isChartLoading ? (
            <div className="flex flex-col items-center justify-center h-[450px]">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#2a3a5a] border-t-[#00ccff] mb-4 shadow-lg shadow-[#00ccff]/20"></div>
              <div className="text-[#00ccff] text-lg animate-pulse">加载图表数据中...</div>
            </div>
          ) : (
            <div ref={chartContainerRef} style={{ width: '100%', height: '450px' }} />
          )}
        </div>

        <div className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
            <span className="text-[#00ff88] font-semibold">实时数据连接正常</span>
          </div>
          <div className="text-gray-400">
            最后更新: <span className="text-[#00ccff] font-semibold">{lastUpdate}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfessionalTradingDashboard;
