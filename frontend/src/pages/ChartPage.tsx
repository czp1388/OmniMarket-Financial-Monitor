import React, { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import './ChartPage.css';
import { ApiService } from '../services/api';
import { realTimeDataService } from '../services/realTimeDataService';

interface KLineData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface SymbolData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  category?: string;
}

interface ApiTicker {
  symbol: string;
  last: number;
  change: number;
  change_percent: number;
  volume: number;
  category?: string;
}

const ChartPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [activeIndicator, setActiveIndicator] = useState('none');
  const [loading, setLoading] = useState(false);
  const [symbolsData, setSymbolsData] = useState<SymbolData[]>([]);
  const [klineData, setKlineData] = useState<KLineData[]>([]);

  const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'TSLA', 'EUR/USD', 'USD/CNY', 'XAU/USD', 'SPY'];
  const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w'];
  const indicators = ['none', 'ma', 'macd', 'rsi', 'bollinger'];
  const [dataSource, setDataSource] = useState<'API' | '模拟数据' | '实时数据服务'>('实时数据服务');

  // 根据符号名称推断类别
  const getCategoryFromSymbol = (symbol: string): string => {
    if (symbol.includes('/USDT') || symbol.includes('BTC') || symbol.includes('ETH')) {
      return '加密货币';
    } else if (symbol.includes('/USD') || symbol.includes('EUR/') || symbol.includes('USD/')) {
      return '外汇';
    } else if (symbol.includes('XAU')) {
      return '贵金属';
    } else {
      return '股票';
    }
  };

  // 模拟实时价格数据生成
  const generateMockSymbolData = (): SymbolData[] => {
    const basePrices: { [key: string]: number } = {
      'BTC/USDT': 42567.39,
      'ETH/USDT': 2345.67,
      'AAPL': 182.45,
      'TSLA': 245.32,
      'EUR/USD': 1.0856,
      'USD/CNY': 7.1987,
      'XAU/USD': 1987.65,
      'SPY': 456.78
    };

    const baseVolumes: { [key: string]: number } = {
      'BTC/USDT': 28456789,
      'ETH/USDT': 15678923,
      'AAPL': 4567890,
      'TSLA': 2345678,
      'EUR/USD': 98765432,
      'USD/CNY': 123456789,
      'XAU/USD': 345678,
      'SPY': 1234567
    };

    return symbols.map(symbol => {
      const basePrice = basePrices[symbol];
      const changePercent = (Math.random() - 0.5) * 4; // -2% 到 +2%
      const change = basePrice * (changePercent / 100);
      const price = basePrice + change;
      const volume = baseVolumes[symbol] + Math.random() * 1000000;

      return {
        symbol,
        price,
        change,
        changePercent,
        volume,
        category: getCategoryFromSymbol(symbol)
      };
    });
  };

  // 从API获取实时数据
  const fetchRealTimeData = async () => {
    try {
      const response = await ApiService.market.getTickers();
      const tickers = Array.isArray(response) ? response : [];
      const symbolData: SymbolData[] = tickers.map((ticker: ApiTicker) => ({
        symbol: ticker.symbol,
        price: ticker.last,
        change: ticker.change,
        changePercent: ticker.change_percent,
        volume: ticker.volume,
        category: getCategoryFromSymbol(ticker.symbol)
      }));
      setSymbolsData(symbolData);
      setDataSource('API');
    } catch (error) {
      console.error('获取实时数据失败:', error);
      const mockData: SymbolData[] = generateMockSymbolData();
      setSymbolsData(mockData);
      setDataSource('模拟数据');
    }
  };

  // 模拟K线数据生成
  const generateMockKLineData = (): KLineData[] => {
    const data: KLineData[] = [];
    const basePrice = symbolsData.find(s => s.symbol === selectedSymbol)?.price || 35000;
    const startTime = new Date('2024-01-01').getTime();
    
    for (let i = 0; i < 100; i++) {
      const time = new Date(startTime + i * 3600000).toISOString().split('T')[0];
      const open = basePrice;
      const change = (Math.random() - 0.5) * (basePrice * 0.02); // 2% 波动
      const close = open + change;
      const high = Math.max(open, close) + Math.random() * (basePrice * 0.01);
      const low = Math.min(open, close) - Math.random() * (basePrice * 0.01);
      const volume = Math.random() * 1000 + 100;
      
      data.push({
        time,
        open,
        high,
        low,
        close,
        volume
      });
    }
    
    return data;
  };

  // 初始化符号数据 - 使用实时数据服务
  useEffect(() => {
    const stopUpdates = realTimeDataService.startRealTimeUpdates(
      (data: any[]) => {
        const updatedSymbolData: SymbolData[] = data.map(item => ({
          symbol: item.symbol,
          price: item.price,
          change: item.change,
          changePercent: item.changePercent,
          volume: item.volume || 0,
          category: getCategoryFromSymbol(item.symbol)
        }));
        setSymbolsData(updatedSymbolData);
        setDataSource('实时数据服务');
      },
      symbols,
      3000 // 3秒更新间隔
    );

    return stopUpdates;
  }, []);

  // 更新K线数据
  useEffect(() => {
    setKlineData(generateMockKLineData());
  }, [selectedSymbol, symbolsData]);

  // ECharts配置
  const getChartOption = () => {
    const upColor = '#00ff88';
    const downColor = '#ff4444';
    const volumeUpColor = 'rgba(0, 255, 136, 0.5)';
    const volumeDownColor = 'rgba(255, 68, 68, 0.5)';

    // 准备K线数据
    const klineDataFormatted = klineData.map(item => [
      item.time,
      item.open,
      item.close,
      item.low,
      item.high
    ]);

    // 准备成交量数据
    const volumeData = klineData.map((item, index) => {
      return {
        value: item.volume,
        itemStyle: {
          color: item.close >= item.open ? volumeUpColor : volumeDownColor
        }
      };
    });

  // 计算移动平均线
  const maData = klineData.map((item, index) => {
    const window = 20;
    if (index < window - 1) {
      return item.close;
    }
    const sum = klineData
      .slice(index - window + 1, index + 1)
      .reduce((acc, curr) => acc + curr.close, 0);
    return sum / window;
  });

  // 计算MACD指标
  const calculateMACD = () => {
    const ema12 = calculateEMA(klineData, 12);
    const ema26 = calculateEMA(klineData, 26);
    const dif = ema12.map((ema12Val, i) => ema12Val - ema26[i]);
    
    // 为DEA计算创建临时K线数据
    const tempDataForDea: KLineData[] = dif.map((val, i) => ({
      time: klineData[i]?.time || '',
      open: val,
      high: val,
      low: val,
      close: val,
      volume: 0
    }));
    
    const dea = calculateEMA(tempDataForDea, 9);
    const macd = dif.map((difVal, i) => (difVal - dea[i]) * 2);
    
    return { dif, dea, macd };
  };

  // 计算指数移动平均线
  const calculateEMA = (data: KLineData[], period: number) => {
    const ema: number[] = [];
    const multiplier = 2 / (period + 1);
    
    // 第一个EMA是SMA
    let sma = 0;
    for (let i = 0; i < period && i < data.length; i++) {
      sma += data[i].close;
    }
    sma = sma / Math.min(period, data.length);
    ema.push(sma);
    
    // 计算后续EMA
    for (let i = 1; i < data.length; i++) {
      const currentEMA = (data[i].close - ema[i-1]) * multiplier + ema[i-1];
      ema.push(currentEMA);
    }
    
    return ema;
  };

  // 计算RSI指标
  const calculateRSI = (period: number = 14) => {
    const rsi: number[] = [];
    const gains: number[] = [];
    const losses: number[] = [];
    
    // 计算价格变化
    for (let i = 1; i < klineData.length; i++) {
      const change = klineData[i].close - klineData[i-1].close;
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? Math.abs(change) : 0);
    }
    
    // 计算初始平均增益和平均损失
    let avgGain = gains.slice(0, period).reduce((sum, gain) => sum + gain, 0) / period;
    let avgLoss = losses.slice(0, period).reduce((sum, loss) => sum + loss, 0) / period;
    
    // 填充前period个RSI值为50
    for (let i = 0; i < period; i++) {
      rsi.push(50);
    }
    
    // 计算后续RSI值
    for (let i = period; i < gains.length; i++) {
      avgGain = (avgGain * (period - 1) + gains[i]) / period;
      avgLoss = (avgLoss * (period - 1) + losses[i]) / period;
      
      const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
      const rsiValue = 100 - (100 / (1 + rs));
      rsi.push(rsiValue);
    }
    
    // 确保长度与原始数据一致
    while (rsi.length < klineData.length) {
      rsi.unshift(50);
    }
    
    return rsi;
  };

  // 计算布林带指标
  const calculateBollingerBands = (period: number = 20, stdDev: number = 2) => {
    const middle: number[] = [];
    const upper: number[] = [];
    const lower: number[] = [];
    
    for (let i = 0; i < klineData.length; i++) {
      if (i < period - 1) {
        middle.push(klineData[i].close);
        upper.push(klineData[i].close);
        lower.push(klineData[i].close);
        continue;
      }
      
      const slice = klineData.slice(i - period + 1, i + 1);
      const prices = slice.map(item => item.close);
      const mean = prices.reduce((sum, price) => sum + price, 0) / period;
      
      const variance = prices.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / period;
      const standardDeviation = Math.sqrt(variance);
      
      middle.push(mean);
      upper.push(mean + standardDeviation * stdDev);
      lower.push(mean - standardDeviation * stdDev);
    }
    
    return { middle, upper, lower };
  };

    // 根据激活的指标添加相应的图表系列
    const indicatorSeries = [];

    if (activeIndicator === 'ma' || activeIndicator === 'none') {
      indicatorSeries.push({
        name: 'MA20',
        type: 'line',
        data: maData,
        smooth: true,
        lineStyle: {
          color: 'rgba(0, 150, 255, 1)',
          width: 2
        },
        symbol: 'none'
      });
    }

    if (activeIndicator === 'macd') {
      const { dif, dea, macd } = calculateMACD();
      
      // 添加MACD子图
      indicatorSeries.push(
        {
          name: 'DIF',
          type: 'line',
          data: dif,
          smooth: true,
          lineStyle: {
            color: '#ff9900',
            width: 2
          },
          symbol: 'none'
        },
        {
          name: 'DEA',
          type: 'line',
          data: dea,
          smooth: true,
          lineStyle: {
            color: '#00ff88',
            width: 2
          },
          symbol: 'none'
        },
        {
          name: 'MACD',
          type: 'bar',
          data: macd.map((value, index) => ({
            value: value,
            itemStyle: {
              color: value >= 0 ? '#00ff88' : '#ff4444'
            }
          })),
          barWidth: '60%'
        }
      );
    }

    if (activeIndicator === 'rsi') {
      const rsiData = calculateRSI();
      
      indicatorSeries.push({
        name: 'RSI14',
        type: 'line',
        data: rsiData,
        smooth: true,
        lineStyle: {
          color: '#ff9900',
          width: 2
        },
        symbol: 'none',
        markLine: {
          data: [
            { yAxis: 70, name: '超买线', lineStyle: { color: '#ff4444', type: 'dashed' } },
            { yAxis: 30, name: '超卖线', lineStyle: { color: '#00ff88', type: 'dashed' } }
          ]
        }
      });
    }

    if (activeIndicator === 'bollinger') {
      const { middle, upper, lower } = calculateBollingerBands();
      
      indicatorSeries.push(
        {
          name: '布林带中线',
          type: 'line',
          data: middle,
          smooth: true,
          lineStyle: {
            color: '#ff9900',
            width: 2
          },
          symbol: 'none'
        },
        {
          name: '布林带上轨',
          type: 'line',
          data: upper,
          smooth: true,
          lineStyle: {
            color: '#00ff88',
            width: 1,
            type: 'dashed'
          },
          symbol: 'none'
        },
        {
          name: '布林带下轨',
          type: 'line',
          data: lower,
          smooth: true,
          lineStyle: {
            color: '#ff4444',
            width: 1,
            type: 'dashed'
          },
          symbol: 'none'
        }
      );
    }

    // 更新图例数据
    const legendData = [selectedSymbol, '成交量'];
    if (activeIndicator === 'ma' || activeIndicator === 'none') {
      legendData.push('MA20');
    }
    if (activeIndicator === 'macd') {
      legendData.push('DIF', 'DEA', 'MACD');
    }
    if (activeIndicator === 'rsi') {
      legendData.push('RSI14');
    }
    if (activeIndicator === 'bollinger') {
      legendData.push('布林带中线', '布林带上轨', '布林带下轨');
    }

    return {
      animation: false,
      legend: {
        bottom: 10,
        left: 'center',
        data: legendData,
        textStyle: {
          color: '#e0e0e0'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        borderWidth: 1,
        borderColor: '#2a2f3d',
        backgroundColor: 'rgba(10, 14, 20, 0.9)',
        textStyle: {
          color: '#e0e0e0'
        },
        formatter: function (params: any) {
          const [klineParam, volumeParam] = params;
          const data = klineParam.data;
          return `
            <div style="font-size: 14px; margin-bottom: 5px;">
              ${data[0]}
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="margin-right: 10px;">开盘:</span>
              <span style="color: ${data[1] <= data[2] ? upColor : downColor}">${data[1]}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="margin-right: 10px;">收盘:</span>
              <span style="color: ${data[1] <= data[2] ? upColor : downColor}">${data[2]}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="margin-right: 10px;">最低:</span>
              <span>${data[3]}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="margin-right: 10px;">最高:</span>
              <span>${data[4]}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="margin-right: 10px;">成交量:</span>
              <span>${volumeParam.data.value}</span>
            </div>
          `;
        }
      },
      grid: [
        {
          left: '10%',
          right: '10%',
          top: '50px',
          height: '60%',
          backgroundColor: '#0a0e14'
        },
        {
          left: '10%',
          right: '10%',
          top: '70%',
          height: '15%',
          backgroundColor: '#0a0e14'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: klineData.map(item => item.time),
          scale: true,
          boundaryGap: false,
          axisLine: { 
            onZero: false,
            lineStyle: {
              color: '#2a2f3d'
            }
          },
          splitLine: { show: false },
          splitNumber: 20,
          axisLabel: {
            color: '#e0e0e0'
          }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: klineData.map(item => item.time),
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(42, 47, 61, 0.3)', 'rgba(42, 47, 61, 0.1)']
            }
          },
          axisLabel: {
            color: '#e0e0e0',
            formatter: '{value}'
          },
          splitLine: {
            lineStyle: {
              color: '#2a2f3d'
            }
          },
          axisLine: {
            lineStyle: {
              color: '#2a2f3d'
            }
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 80,
          end: 100,
          filterMode: 'filter'
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          top: '85%',
          start: 80,
          end: 100,
          backgroundColor: '#1a1f2d',
          borderColor: '#2a2f3d',
          textStyle: {
            color: '#e0e0e0'
          },
          handleStyle: {
            color: '#00ff88'
          }
        }
      ],
      series: [
        {
          name: selectedSymbol,
          type: 'candlestick',
          data: klineDataFormatted,
          itemStyle: {
            color: upColor,
            color0: downColor,
            borderColor: upColor,
            borderColor0: downColor
          },
          markPoint: {
            label: {
              color: '#e0e0e0'
            },
            data: [
              {
                name: '最高值',
                type: 'max',
                valueDim: 'highest'
              },
              {
                name: '最低值',
                type: 'min',
                valueDim: 'lowest'
              }
            ]
          }
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumeData
        },
        ...(activeIndicator === 'ma' || activeIndicator === 'none' ? [{
          name: 'MA20',
          type: 'line',
          data: maData,
          smooth: true,
          lineStyle: {
            color: 'rgba(0, 150, 255, 1)',
            width: 2
          },
          symbol: 'none'
        }] : [])
      ]
    };
  };

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (price >= 1) {
      return `$${price.toFixed(2)}`;
    } else {
      return price.toFixed(4);
    }
  };

  const formatChange = (change: number, percent: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)} (${sign}${percent.toFixed(2)}%)`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white p-6 space-y-4">
      {/* 顶部标题栏 */}
      <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
        <div className="flex items-center justify-between">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-3">
            <span className="text-5xl">📊</span>
            <span>专业图表分析</span>
          </h1>
          <div className="flex items-center gap-4">
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>💱</span><span>交易对</span>
              </label>
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-2 text-white focus:border-[#00ccff] focus:outline-none"
              >
                {symbols.map(symbol => (
                  <option key={symbol} value={symbol}>{symbol}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <span>⏱️</span><span>时间周期</span>
              </label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-2 text-white focus:border-[#00ccff] focus:outline-none"
              >
                {timeframes.map(tf => (
                  <option key={tf} value={tf}>{tf}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex gap-4">
        {/* 左侧品种列表 */}
        <div className="w-full md:w-[25%] bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-4 shadow-2xl">
          <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
            <span className="text-2xl">📈</span>
            <span>品种列表</span>
          </h3>
          <div className="space-y-2">
            {symbolsData.map((symbol) => (
              <div
                key={symbol.symbol}
                className={`p-3 rounded-xl cursor-pointer transition-all duration-300 ${
                  selectedSymbol === symbol.symbol
                    ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold scale-[1.02]'
                    : 'bg-[#1a2332] hover:bg-[#222b3d] text-white'
                }`}
                onClick={() => setSelectedSymbol(symbol.symbol)}
              >
                <div className="font-bold">{symbol.symbol}</div>
                <div className="text-lg font-mono">{formatPrice(symbol.price)}</div>
                <div className={selectedSymbol === symbol.symbol ? '' : (symbol.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]')}>
                  {formatChange(symbol.change, symbol.changePercent)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧图表区域 */}
        <div className="w-full md:w-[75%] space-y-4">
          {/* 图表工具栏 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-4 shadow-2xl">
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm flex items-center gap-2">
                <span>📈</span><span>技术指标:</span>
              </span>
              {indicators.map(indicator => (
                <div
                  key={indicator}
                  className={`px-4 py-2 rounded-lg cursor-pointer transition-all duration-300 text-sm font-semibold ${
                    activeIndicator === indicator
                      ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black'
                      : 'bg-[#1a2332] text-gray-400 hover:bg-[#222b3d] hover:text-white'
                  }`}
                  onClick={() => setActiveIndicator(indicator)}
                >
                  {indicator === 'none' ? '无指标' : 
                   indicator === 'ma' ? '移动平均线' :
                   indicator === 'macd' ? 'MACD' :
                   indicator === 'rsi' ? 'RSI' : '布林带'}
                </div>
              ))}
            </div>
          </div>

          {/* 图表区域 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
            <div className="relative" style={{ height: '500px' }}>
              {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-xl z-10">
                  <div className="w-12 h-12 border-4 border-[#00ccff] border-t-transparent rounded-full animate-spin"></div>
                </div>
              )}
              <ReactECharts
                option={getChartOption()}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
          </div>

          {/* 底部状态栏 */}
          <div className="bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 shadow-2xl">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <span className="text-gray-400 text-sm">当前品种:</span>
                <span className="text-[#00ccff] font-semibold">{selectedSymbol}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-400 text-sm">时间周期:</span>
                <span className="text-white font-semibold">{timeframe}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-400 text-sm">技术指标:</span>
                <span className="text-white font-semibold">
                  {activeIndicator === 'none' ? '无' : 
                   activeIndicator === 'ma' ? '移动平均线' :
                   activeIndicator === 'macd' ? 'MACD' :
                   activeIndicator === 'rsi' ? 'RSI' : '布林带'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
                <span className="text-gray-400 text-sm">数据状态:</span>
                <span className="text-[#00ff88] font-semibold">实时</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartPage;
