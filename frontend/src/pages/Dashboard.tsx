import React, { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import { Link, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import { realTimeDataService } from '../services/realTimeDataService';
import './Dashboard.css';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  last?: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  timestamp?: string;
  type?: string;
  source?: string;
  lastUpdate?: string;
}

const Dashboard: React.FC = () => {
  const location = useLocation();
  
  const navigation = [
    { name: '仪表板', href: '/', icon: '📊' },
    { name: '专业监控', href: '/financial-monitoring', icon: '📊' },
    { name: '图表分析', href: '/chart', icon: '📈' },
    { name: '预警管理', href: '/alerts', icon: '🔔' },
    { name: '投资组合', href: '/portfolio', icon: '💼' },
    { name: '虚拟交易', href: '/virtual-trading', icon: '💰' },
    { name: '牛熊证监控', href: '/warrants', icon: '📉' },
    { name: '系统设置', href: '/settings', icon: '⚙️' },
  ];

  const isActive = (path: string) => location.pathname === path;
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [systemStatus, setSystemStatus] = useState({
    lastUpdate: new Date().toLocaleString('zh-CN'),
    activeAlerts: 85,
    marketStatus: '正常',
    dataStatus: '实时',
    latency: '12ms'
  });

  const [selectedMarket, setSelectedMarket] = useState('股票');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1小时');
  const [selectedIndicator, setSelectedIndicator] = useState('无指标');

  // 使用真实实时数据服务
  useEffect(() => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
    const stopUpdates = realTimeDataService.startRealTimeUpdates(
      (data: any[]) => {
        const updatedMarketData = data.map(item => ({
          symbol: item.symbol,
          price: item.price,
          change: item.change,
          changePercent: item.changePercent,
          volume: item.volume || 0,
          last: item.price,
          open: item.open || item.price,
          high: item.high || item.price,
          low: item.low || item.price,
          close: item.close || item.price,
          timestamp: item.lastUpdate || new Date().toISOString(),
          type: item.type || 'crypto',
          source: item.source || 'realTimeDataService',
          lastUpdate: item.lastUpdate || new Date().toLocaleTimeString('zh-CN', { hour12: false })
        }));
        setMarketData(updatedMarketData);
        setSystemStatus(prev => ({
          ...prev,
          lastUpdate: new Date().toLocaleString('zh-CN')
        }));
      },
      symbols,
      5000 // 5秒更新间隔
    );
    return stopUpdates;
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

  const handleRefreshData = () => {
    // 手动刷新数据
    const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
    realTimeDataService.getMarketData(symbols).then(data => {
      const updatedMarketData = data.map(item => ({
        symbol: item.symbol,
        price: item.price,
        change: item.change,
        changePercent: item.changePercent,
        volume: item.volume || 0,
        last: item.price,
        open: item.open || item.price,
        high: item.high || item.price,
        low: item.low || item.price,
        close: item.close || item.price,
        timestamp: item.lastUpdate || new Date().toISOString(),
        type: item.type || 'crypto',
        source: item.source || 'realTimeDataService',
        lastUpdate: item.lastUpdate || new Date().toLocaleTimeString('zh-CN', { hour12: false })
      }));
      setMarketData(updatedMarketData);
      setSystemStatus(prev => ({
        ...prev,
        lastUpdate: new Date().toLocaleString('zh-CN')
      }));
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 专业顶部导航栏 */}
      <header className="bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border-b border-[#2a3a5a] shadow-2xl">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                OmniMarket
              </h1>
              <p className="text-gray-400 text-sm">寰宇多市场金融监控系统</p>
            </div>
            
            {/* 专业导航键 */}
            <div className="flex items-center gap-2 overflow-x-auto">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 whitespace-nowrap flex items-center gap-2',
                    isActive(item.href) 
                      ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black shadow-lg' 
                      : 'bg-[#141a2a] text-gray-400 hover:bg-[#1a2332] hover:text-white'
                  )}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.name}</span>
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-4">
              <div className="text-[#00ccff] font-mono text-sm">
                {new Date().toLocaleString('zh-CN')}
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#00ccff] to-[#00ff88] flex items-center justify-center font-bold text-black">
                U
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区域 - 30/70分栏布局 */}
      <div className="flex gap-4 p-6">
        {/* 左侧30% - 实时监控面板 */}
        <div className="w-full md:w-[30%] space-y-4">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
            <h3 className="text-2xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-3xl">📊</span>
              <span>实时监控品种</span>
            </h3>
            <div className="space-y-3">
              {marketData.map((data, index) => (
                <div key={index} className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 shadow-lg hover:scale-[1.02] transition-all duration-300">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[#00ccff] font-bold">█</span>
                    <span className="text-white font-bold text-lg">{data.symbol}</span>
                  </div>
                  <div className="text-2xl font-bold text-white font-mono">
                    ${data.price.toLocaleString()}
                  </div>
                  <div className={clsx(
                    'text-sm font-semibold flex items-center gap-2',
                    data.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                  )}>
                    <span>{data.change >= 0 ? '↗' : '↘'}</span>
                    <span>
                      {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)} ({data.changePercent.toFixed(2)}%)
                    </span>
                    <span className="ml-auto">{data.change >= 0 ? '🟢' : '🔴'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧70% - 核心功能区域 */}
        <div className="w-full md:w-[70%] space-y-4">
          {/* K线图表区域 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
            <h3 className="text-2xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-3xl">📊</span>
              <span>专业K线图表分析</span>
            </h3>
            <ReactECharts 
              option={getKLineOption()} 
              style={{ height: '400px', width: '100%' }}
              opts={{ renderer: 'svg' }}
            />
          </div>

          {/* 控制面板 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>🌏</span><span>市场选择</span>
                </label>
                <select 
                  value={selectedMarket} 
                  onChange={(e) => setSelectedMarket(e.target.value)}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-all"
                >
                  <option value="股票">股票(AAPL)</option>
                  <option value="加密货币">加密货币</option>
                  <option value="外汇">外汇</option>
                  <option value="期货">期货</option>
                  <option value="期权">期权</option>
                </select>
              </div>

              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>⏱️</span><span>时间周期</span>
                </label>
                <select 
                  value={selectedTimeframe} 
                  onChange={(e) => setSelectedTimeframe(e.target.value)}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-all"
                >
                  <option value="1分钟">1分钟</option>
                  <option value="5分钟">5分钟</option>
                  <option value="15分钟">15分钟</option>
                  <option value="30分钟">30分钟</option>
                  <option value="1小时">1小时</option>
                  <option value="4小时">4小时</option>
                  <option value="日线">日线</option>
                  <option value="周线">周线</option>
                </select>
              </div>

              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>📈</span><span>技术指标</span>
                </label>
                <select 
                  value={selectedIndicator} 
                  onChange={(e) => setSelectedIndicator(e.target.value)}
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-all"
                >
                  <option value="无指标">无指标</option>
                  <option value="MA">移动平均线</option>
                  <option value="EMA">指数移动平均</option>
                  <option value="MACD">MACD</option>
                  <option value="RSI">RSI</option>
                  <option value="布林带">布林带</option>
                  <option value="KDJ">KDJ</option>
                  <option value="OBV">OBV</option>
                </select>
              </div>

              <button 
                className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold px-6 py-3 rounded-lg hover:scale-105 transition-all duration-300 shadow-lg flex items-center justify-center gap-2"
                onClick={handleRefreshData}
              >
                <span className="text-lg">🔄</span>
                <span>刷新数据</span>
              </button>
            </div>
          </div>

          {/* 状态信息面板 */}
          <div className="bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-5 shadow-2xl">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🔔</span>
                <div>
                  <div className="text-xs text-gray-400">活跃预警</div>
                  <div className="text-xl font-bold text-[#ff4444]">{systemStatus.activeAlerts}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <div className="text-xs text-gray-400">市场状态</div>
                  <div className="text-xl font-bold text-[#00ff88]">{systemStatus.marketStatus}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">📡</span>
                <div>
                  <div className="text-xs text-gray-400">数据更新</div>
                  <div className="text-xl font-bold text-[#00ccff]">{systemStatus.dataStatus}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">⚡</span>
                <div>
                  <div className="text-xs text-gray-400">延迟</div>
                  <div className="text-xl font-bold text-white">{systemStatus.latency}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
