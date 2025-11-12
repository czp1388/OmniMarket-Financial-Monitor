import React, { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import './ChartPage.css';
import { ApiService } from '../services/api';

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
  const [dataSource, setDataSource] = useState<'API' | '模拟数据'>('模拟数据');

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

  // 初始化符号数据
  useEffect(() => {
    setSymbolsData(generateMockSymbolData());
    
    // 每2秒更新价格数据
    const interval = setInterval(() => {
      setSymbolsData(generateMockSymbolData());
    }, 2000);

    return () => clearInterval(interval);
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

    return {
      animation: false,
      legend: {
        bottom: 10,
        left: 'center',
        data: [selectedSymbol, '成交量', 'MA20'],
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
    <div className="chart-container">
      {/* 顶部标题栏 */}
      <div className="chart-header">
        <h1 className="chart-title">专业图表分析</h1>
        <div className="chart-controls">
          <div className="control-group">
            <span className="control-label">交易对</span>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="control-select"
            >
              {symbols.map(symbol => (
                <option key={symbol} value={symbol}>{symbol}</option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <span className="control-label">时间周期</span>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="control-select"
            >
              {timeframes.map(tf => (
                <option key={tf} value={tf}>{tf}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="chart-main">
        {/* 左侧品种列表 */}
        <div className="chart-sidebar">
          <div className="symbol-list">
            {symbolsData.map((symbol) => (
              <div
                key={symbol.symbol}
                className={`symbol-card ${selectedSymbol === symbol.symbol ? 'active' : ''}`}
                onClick={() => setSelectedSymbol(symbol.symbol)}
              >
                <div className="symbol-name">{symbol.symbol}</div>
                <div className="symbol-price">{formatPrice(symbol.price)}</div>
                <div className={`symbol-change ${symbol.change >= 0 ? 'positive' : 'negative'}`}>
                  {formatChange(symbol.change, symbol.changePercent)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧图表区域 */}
        <div className="chart-content">
          {/* 图表工具栏 */}
          <div className="chart-toolbar">
            <div className="toolbar-controls">
              <div className="indicator-selector">
                <span className="control-label">技术指标:</span>
                {indicators.map(indicator => (
                  <div
                    key={indicator}
                    className={`indicator-badge ${activeIndicator === indicator ? 'active' : ''}`}
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
          </div>

          {/* 图表区域 */}
          <div className="chart-area">
            <div className="chart-wrapper">
              {loading && (
                <div className="loading-overlay">
                  <div className="loading-spinner"></div>
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
          <div className="chart-status">
            <div className="status-info">
              <div className="status-item">
                <span>当前品种:</span>
                <span className="status-value">{selectedSymbol}</span>
              </div>
              <div className="status-item">
                <span>时间周期:</span>
                <span className="status-value">{timeframe}</span>
              </div>
              <div className="status-item">
                <span>技术指标:</span>
                <span className="status-value">
                  {activeIndicator === 'none' ? '无' : 
                   activeIndicator === 'ma' ? '移动平均线' :
                   activeIndicator === 'macd' ? 'MACD' :
                   activeIndicator === 'rsi' ? 'RSI' : '布林带'}
                </span>
              </div>
              <div className="status-item">
                <span>数据状态:</span>
                <span className="status-value positive">实时</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartPage;
