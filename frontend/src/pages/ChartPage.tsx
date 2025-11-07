import React, { useState, useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

interface KLineData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const ChartPage: React.FC = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [loading, setLoading] = useState(true);

  const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'TSLA', 'EUR/USD'];
  const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w'];

  // 模拟K线数据生成
  const generateMockKLineData = (): KLineData[] => {
    const data: KLineData[] = [];
    let basePrice = 35000;
    const startTime = new Date('2024-01-01').getTime();
    
    for (let i = 0; i < 100; i++) {
      const time = new Date(startTime + i * 3600000).toISOString().split('T')[0];
      const open = basePrice;
      const change = (Math.random() - 0.5) * 1000;
      const close = open + change;
      const high = Math.max(open, close) + Math.random() * 500;
      const low = Math.min(open, close) - Math.random() * 500;
      const volume = Math.random() * 1000 + 100;
      
      data.push({
        time,
        open,
        high,
        low,
        close,
        volume
      });
      
      basePrice = close;
    }
    
    return data;
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    setLoading(true);

    // 清理之前的图表
    while (chartContainerRef.current.firstChild) {
      chartContainerRef.current.removeChild(chartContainerRef.current.firstChild);
    }

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: 'black',
      },
      grid: {
        vertLines: { color: '#f0f3fa' },
        horzLines: { color: '#f0f3fa' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.7,
        bottom: 0,
      },
    });

    // 生成模拟数据
    const klineData = generateMockKLineData();
    const volumeData = klineData.map((item, index) => ({
      time: item.time,
      value: item.volume,
      color: item.close >= item.open ? '#26a69a' : '#ef5350',
    }));

    candleSeries.setData(klineData);
    volumeSeries.setData(volumeData);

    // 添加技术指标
    const smaSeries = chart.addLineSeries({
      color: 'rgba(4, 111, 232, 1)',
      lineWidth: 2,
    });

    const smaData = klineData.map((item, index) => {
      const window = 20;
      if (index < window - 1) {
        return { time: item.time, value: item.close };
      }
      const sum = klineData
        .slice(index - window + 1, index + 1)
        .reduce((acc, curr) => acc + curr.close, 0);
      return { time: item.time, value: sum / window };
    });

    smaSeries.setData(smaData);

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    setLoading(false);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [selectedSymbol, timeframe]);

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">图表分析</h1>
        
        {/* 控制面板 */}
        <div className="flex flex-wrap gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              交易对
            </label>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {symbols.map(symbol => (
                <option key={symbol} value={symbol}>{symbol}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              时间周期
            </label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {timeframes.map(tf => (
                <option key={tf} value={tf}>{tf}</option>
              ))}
            </select>
          </div>
        </div>

        {/* 图表容器 */}
        <div className="bg-white shadow-lg rounded-lg p-4">
          {loading && (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-2">加载图表数据...</span>
            </div>
          )}
          <div 
            ref={chartContainerRef}
            className="w-full"
            style={{ minHeight: '500px' }}
          />
        </div>

        {/* 图表说明 */}
        <div className="mt-4 text-sm text-gray-600">
          <p>当前显示: {selectedSymbol} - {timeframe} K线图</p>
          <p className="mt-1">
            <span className="text-green-600">绿色</span>: 上涨 | 
            <span className="text-red-600 ml-2">红色</span>: 下跌 |
            <span className="text-blue-600 ml-2">蓝色线</span>: 20周期SMA
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChartPage;
