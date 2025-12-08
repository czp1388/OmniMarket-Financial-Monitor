import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import { realTimeDataService, MarketData } from '../services/realTimeDataService';
import './PortfolioPage.css';

interface PortfolioItem {
  id: string;
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercentage: number;
  marketValue: number;
  allocation: number;
  category: string;
}

interface SymbolData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  category: string;
  type: string;
  lastUpdate: string;
  source: string;
}

interface AssetAllocation {
  category: string;
  value: number;
  percentage: number;
  color: string;
}

interface ApiTicker {
  symbol: string;
  last: number;
  change: number;
  change_percent: number;
  volume: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  timestamp?: string;
}

const PortfolioPage: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [symbolsData, setSymbolsData] = useState<SymbolData[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalValue, setTotalValue] = useState(0);
  const [totalPnl, setTotalPnl] = useState(0);
  const [systemStatus, setSystemStatus] = useState('正常');
  const [connectionDelay, setConnectionDelay] = useState(45);
  const [currentTime, setCurrentTime] = useState('');
  const [activeAlertsCount, setActiveAlertsCount] = useState(12);
  const [assetAllocation, setAssetAllocation] = useState<AssetAllocation[]>([]);
  const [riskMetrics, setRiskMetrics] = useState({
    volatility: 18.5,
    sharpeRatio: 1.24,
    maxDrawdown: -12.3,
    beta: 0.89,
    var: -8.2
  });
  const [dataSource, setDataSource] = useState<'API' | '模拟数据'>('模拟数据');
  const [activeNav, setActiveNav] = useState('投资组合');

  // 从API获取实时数据
  const fetchRealTimeData = async () => {
    try {
      const response = await ApiService.market.getTickers();
      // 安全地处理API响应，确保是数组类型
      const tickers = Array.isArray(response) ? response : [];
      const portfolioData: SymbolData[] = tickers.map(ticker => ({
        symbol: ticker.symbol,
        price: ticker.last,
        change: ticker.change,
        changePercent: ticker.change_percent,
        volume: ticker.volume,
        category: getCategoryFromSymbol(ticker.symbol),
        type: getTypeFromSymbol(ticker.symbol),
        lastUpdate: new Date().toISOString(),
        source: 'API'
      }));
      setSymbolsData(portfolioData);
      setDataSource('API');
    } catch (error) {
      console.error('获取实时数据失败:', error);
      // 如果API失败，使用模拟数据作为后备
      const mockData: SymbolData[] = generateMockSymbolData();
      setSymbolsData(mockData);
      setDataSource('模拟数据');
    }
  };

  // 根据交易对符号判断类别
  const getCategoryFromSymbol = (symbol: string): string => {
    if (symbol.includes('BTC') || symbol.includes('ETH') || symbol.includes('USDT')) {
      return '加密货币';
    } else if (symbol.includes('/')) {
      return '外汇';
    } else if (symbol.length <= 5) {
      return '股票';
    } else {
      return '其他';
    }
  };

  // 根据交易对符号判断类型
  const getTypeFromSymbol = (symbol: string): string => {
    if (symbol.includes('BTC') || symbol.includes('ETH') || symbol.includes('USDT')) {
      return '现货';
    } else if (symbol.includes('/')) {
      return '现货';
    } else if (symbol.length <= 5) {
      return '股票';
    } else if (symbol.includes('ETF')) {
      return 'ETF';
    } else {
      return '其他';
    }
  };

  // 生成模拟数据作为后备
  const generateMockSymbolData = (): SymbolData[] => {
    const now = new Date().toISOString();
    return [
      { symbol: 'BTC/USDT', price: 42567.39, change: 975.42, changePercent: 2.34, volume: 28456789, category: '加密货币', type: '现货', lastUpdate: now, source: '模拟数据' },
      { symbol: 'ETH/USDT', price: 2345.67, change: 28.51, changePercent: 1.23, volume: 15678923, category: '加密货币', type: '现货', lastUpdate: now, source: '模拟数据' },
      { symbol: 'AAPL', price: 182.45, change: -1.03, changePercent: -0.56, volume: 4567890, category: '股票', type: '股票', lastUpdate: now, source: '模拟数据' },
      { symbol: 'TSLA', price: 245.67, change: 3.21, changePercent: 1.32, volume: 2345678, category: '股票', type: '股票', lastUpdate: now, source: '模拟数据' },
      { symbol: 'USD/CNY', price: 7.1987, change: 0.0086, changePercent: 0.12, volume: 123456789, category: '外汇', type: '现货', lastUpdate: now, source: '模拟数据' },
      { symbol: 'EUR/USD', price: 1.0856, change: -0.0023, changePercent: -0.21, volume: 98765432, category: '外汇', type: '现货', lastUpdate: now, source: '模拟数据' },
      { symbol: 'XAU/USD', price: 1987.45, change: 12.34, changePercent: 0.62, volume: 345678, category: '商品', type: '现货', lastUpdate: now, source: '模拟数据' },
      { symbol: 'SPY', price: 456.78, change: 2.34, changePercent: 0.51, volume: 1234567, category: 'ETF', type: 'ETF', lastUpdate: now, source: '模拟数据' }
    ];
  };

  useEffect(() => {
    // 初始化数据
    const initializeData = async () => {
      // 更新时间显示
      const updateTime = () => {
        const now = new Date();
        setCurrentTime(now.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        }));
      };

      updateTime();
      const timeInterval = setInterval(updateTime, 1000);

      // 模拟投资组合数据
      const mockPortfolio: PortfolioItem[] = [
        {
          id: '1',
          symbol: 'BTC/USDT',
          quantity: 0.5,
          avgPrice: 32000,
          currentPrice: 34850,
          pnl: 1425,
          pnlPercentage: 8.91,
          marketValue: 17425,
          allocation: 40.2,
          category: '加密货币'
        },
        {
          id: '2',
          symbol: 'ETH/USDT',
          quantity: 10,
          avgPrice: 1700,
          currentPrice: 1820,
          pnl: 1200,
          pnlPercentage: 7.06,
          marketValue: 18200,
          allocation: 42.0,
          category: '加密货币'
        },
        {
          id: '3',
          symbol: 'AAPL',
          quantity: 50,
          avgPrice: 145,
          currentPrice: 152.3,
          pnl: 365,
          pnlPercentage: 5.03,
          marketValue: 7615,
          allocation: 17.6,
          category: '股票'
        }
      ];
      
      setPortfolio(mockPortfolio);
      
      // 尝试从API获取实时数据
      await fetchRealTimeData();
      
      // 计算总投资组合价值
      const totalMarketValue = mockPortfolio.reduce((sum, item) => sum + item.marketValue, 0);
      const totalProfitLoss = mockPortfolio.reduce((sum, item) => sum + item.pnl, 0);
      
      setTotalValue(totalMarketValue);
      setTotalPnl(totalProfitLoss);
      setLoading(false);

      // 初始化资产分配数据
      const mockAssetAllocation: AssetAllocation[] = [
        { category: '加密货币', value: 35625, percentage: 82.2, color: '#00ff88' },
        { category: '股票', value: 7615, percentage: 17.6, color: '#007bff' },
        { category: '外汇', value: 0, percentage: 0, color: '#6c757d' },
        { category: '商品', value: 0, percentage: 0, color: '#ffc107' },
        { category: 'ETF', value: 0, percentage: 0, color: '#e83e8c' }
      ];
      setAssetAllocation(mockAssetAllocation);

      // 设置实时数据更新
      const dataInterval = setInterval(async () => {
        await fetchRealTimeData();
      }, 3000);

      return () => {
        clearInterval(timeInterval);
        clearInterval(dataInterval);
      };
    };

    initializeData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#2a3a5a] border-t-[#00ccff] mx-auto shadow-lg shadow-[#00ccff]/20"></div>
          <span className="text-[#00ccff] text-lg animate-pulse">加载投资组合数据...</span>
        </div>
      </div>
    );
  }

  const getSymbolIcon = (symbol: string) => {
    if (symbol.includes('BTC')) return 'icon-btc';
    if (symbol.includes('ETH')) return 'icon-eth';
    if (symbol.includes('/')) return 'icon-forex';
    return 'icon-stock';
  };

  const getSymbolLabel = (symbol: string) => {
    if (symbol.includes('BTC')) return 'BTC';
    if (symbol.includes('ETH')) return 'ETH';
    if (symbol.includes('/')) return 'FX';
    return 'STK';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 顶部状态栏 - 增强版 */}
      <div className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border-b border-[#2a3a5a] px-6 py-3 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-6">
          <span className="text-xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">OmniMarket</span>
          <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
            systemStatus === '正常' ? 'bg-[#00ff88]/20 text-[#00ff88]' :
            systemStatus === '连接异常' ? 'bg-yellow-500/20 text-yellow-500' :
            'bg-gray-500/20 text-gray-400'
          }`}>
            {systemStatus}
          </span>
          <span className="text-sm text-gray-400">延迟: <span className="text-[#00ccff] font-semibold">{connectionDelay}ms</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">市场状态: <span className="text-white font-semibold">{systemStatus === '市场关闭' ? '休市' : '开市'}</span></span>
          <span className="text-sm text-gray-400">活跃预警: <span className="text-[#ff4444] font-semibold">{activeAlertsCount}</span></span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-[#00ccff] font-mono">{currentTime}</span>
          <span className="text-sm text-gray-500">数据源: 模拟数据</span>
        </div>
      </div>

      {/* 功能导航栏 - 增强版 */}
      <div className="bg-[#0a0e17] border-b border-[#2a3a5a] px-6 py-3 flex items-center gap-2 overflow-x-auto">
        {[
          { key: '投资组合', icon: '💼' },
          { key: '资产分配', icon: '📊' },
          { key: '风险分析', icon: '⚠️' },
          { key: '持仓明细', icon: '📦' },
          { key: '交易历史', icon: '📋' },
          { key: '绩效报告', icon: '📈' },
          { key: '设置', icon: '⚙️' }
        ].map(nav => (
          <button 
            key={nav.key}
            className={`px-4 py-2 rounded-lg transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${
              activeNav === nav.key
                ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold shadow-lg shadow-[#00ccff]/30'
                : 'bg-[#141a2a] text-gray-400 hover:bg-[#1a2332] hover:text-white'
            }`}
            onClick={() => setActiveNav(nav.key)}
          >
            <span className="text-lg">{nav.icon}</span>
            <span>{nav.key}</span>
          </button>
        ))}
      </div>

      <div className="flex gap-6 p-6">
        {/* 实时价格监控侧边栏 - 增强版 */}
        <div className="flex-shrink-0 w-80">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl sticky top-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-2xl">📊</span>
                <span>实时监控</span>
              </h3>
              <div className="text-sm text-gray-400">{symbolsData.length}个品种</div>
            </div>
            <div className="space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto pr-2 scrollbar-thin">
              {symbolsData.map((symbol, index) => (
                <div key={index} className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-3 hover:border-[#00ccff] transition-all duration-300 cursor-pointer group">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-[#00ccff]/20 text-[#00ccff] text-xs font-bold">
                        {getSymbolLabel(symbol.symbol)}
                      </span>
                      <span className="font-bold text-white group-hover:text-[#00ccff] transition-colors text-sm">{symbol.symbol}</span>
                    </div>
                    <span className={`text-sm font-semibold ${
                      symbol.changePercent >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                    }`}>
                      {symbol.changePercent >= 0 ? '↗ +' : '↘ '}{symbol.changePercent.toFixed(2)}%
                    </span>
                  </div>
                  <div className="text-xl font-bold text-white mb-1">${symbol.price.toLocaleString()}</div>
                  <div className="flex items-center justify-between text-xs">
                    <span className={`font-semibold ${
                      symbol.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                    }`}>
                      {symbol.change >= 0 ? '+' : ''}{symbol.change.toLocaleString()}
                    </span>
                    <span className="text-gray-400">量: {symbol.volume.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      {/* 投资组合主内容区 - 增强版 */}
      <div className="flex-1 space-y-6">
        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-2 flex items-center gap-2">
                <span className="text-4xl">💼</span>
                <span>投资组合</span>
              </h1>
              <p className="text-gray-400 ml-14">监控您的资产分布和盈亏情况</p>
            </div>
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">总市值</div>
                <div className="text-2xl font-bold text-white">${totalValue.toLocaleString()}</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">总盈亏</div>
                <div className={`text-2xl font-bold ${
                  totalPnl >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                }`}>
                  {totalPnl >= 0 ? '+' : ''}${totalPnl.toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">持仓数量</div>
                <div className="text-2xl font-bold text-[#00ccff]">{portfolio.length}</div>
              </div>
            </div>
          </div>
        </div>

        {/* 资产分配和风险指标卡片 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 资产分配卡片 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl hover:shadow-[#00ccff]/20 transition-all duration-300">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">📊</span>
                <span>资产分配</span>
              </h3>
              <div className="text-sm text-gray-400">按资产类别</div>
            </div>
            <div className="space-y-5">
              <div className="flex rounded-full overflow-hidden h-8 mb-4 shadow-lg">
                {assetAllocation
                  .filter(item => item.percentage > 0)
                  .map((item, index) => (
                    <div
                      key={item.category}
                      className="transition-all duration-300 hover:opacity-80"
                      style={{
                        backgroundColor: item.color,
                        width: `${item.percentage}%`
                      }}
                      title={`${item.category}: ${item.percentage.toFixed(1)}%`}
                    />
                  ))}
              </div>
              <div className="space-y-3">
                {assetAllocation
                  .filter(item => item.percentage > 0)
                  .map((item, index) => (
                    <div key={item.category} className="flex items-center justify-between hover:bg-[#0a0e17]/50 p-3 rounded-xl transition-all duration-300 cursor-pointer group">
                      <div className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded-full shadow-lg" style={{ backgroundColor: item.color }}></div>
                        <span className="text-white font-semibold group-hover:text-[#00ccff] transition-colors">{item.category}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">{item.percentage.toFixed(1)}%</span>
                        <span className="text-gray-400 font-mono">${item.value.toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>

          {/* 风险指标卡片 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl hover:shadow-[#ff4444]/20 transition-all duration-300">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">⚠️</span>
                <span>风险指标</span>
              </h3>
              <div className="text-sm text-gray-400">投资组合分析</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 hover:border-yellow-500 transition-all duration-300">
                <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">📉 波动率</div>
                <div className="text-3xl font-bold text-yellow-400 mb-1">{riskMetrics.volatility.toFixed(1)}%</div>
                <div className="text-xs px-2 py-1 rounded bg-yellow-500/20 text-yellow-400 inline-block">中等</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 hover:border-[#00ff88] transition-all duration-300">
                <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">📈 夏普比率</div>
                <div className="text-3xl font-bold text-[#00ff88] mb-1">{riskMetrics.sharpeRatio.toFixed(2)}</div>
                <div className="text-xs px-2 py-1 rounded bg-[#00ff88]/20 text-[#00ff88] inline-block">良好</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 hover:border-[#ff4444] transition-all duration-300">
                <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">📊 最大回撤</div>
                <div className="text-3xl font-bold text-[#ff4444] mb-1">{riskMetrics.maxDrawdown.toFixed(1)}%</div>
                <div className="text-xs px-2 py-1 rounded bg-yellow-500/20 text-yellow-400 inline-block">可控</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 hover:border-[#00ff88] transition-all duration-300">
                <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">🎯 Beta</div>
                <div className="text-3xl font-bold text-[#00ccff] mb-1">{riskMetrics.beta.toFixed(2)}</div>
                <div className="text-xs px-2 py-1 rounded bg-[#00ff88]/20 text-[#00ff88] inline-block">低风险</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 hover:border-yellow-500 transition-all duration-300">
                <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">💰 VaR (95%)</div>
                <div className="text-3xl font-bold text-yellow-400 mb-1">{riskMetrics.var.toFixed(1)}%</div>
                <div className="text-xs px-2 py-1 rounded bg-yellow-500/20 text-yellow-400 inline-block">标准</div>
              </div>
              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 hover:border-[#00ccff] transition-all duration-300">
                <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">🛡️ 风险等级</div>
                <div className="text-3xl font-bold text-[#00ccff] mb-1">中等</div>
                <div className="text-xs px-2 py-1 rounded bg-[#00ccff]/20 text-[#00ccff] inline-block">平衡</div>
              </div>
            </div>
          </div>
        </div>

        {/* 持仓列表 */}
        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-3xl">📦</span>
              <span>持仓明细</span>
            </h2>
            <button className="px-6 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold rounded-xl hover:scale-105 transition-all duration-300 shadow-lg shadow-[#00ccff]/30 flex items-center gap-2">
              <span className="text-xl">➕</span>
              <span>添加新持仓</span>
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2a3a5a]">
                  <th className="text-left py-4 px-4 text-gray-400 font-semibold">交易对</th>
                  <th className="text-right py-4 px-4 text-gray-400 font-semibold">数量</th>
                  <th className="text-right py-4 px-4 text-gray-400 font-semibold">平均成本</th>
                  <th className="text-right py-4 px-4 text-gray-400 font-semibold">当前价格</th>
                  <th className="text-right py-4 px-4 text-gray-400 font-semibold">市值</th>
                  <th className="text-right py-4 px-4 text-gray-400 font-semibold">盈亏</th>
                  <th className="text-right py-4 px-4 text-gray-400 font-semibold">盈亏率</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.map((item) => (
                  <tr key={item.id} className="border-b border-[#2a3a5a]/50 hover:bg-[#1a2332] transition-colors duration-200 cursor-pointer">
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-[#00ccff]/20 text-[#00ccff] text-xs font-bold">
                          {getSymbolLabel(item.symbol)}
                        </span>
                        <span className="text-white font-semibold">{item.symbol}</span>
                      </div>
                    </td>
                    <td className="text-right py-4 px-4 text-white font-mono">{item.quantity}</td>
                    <td className="text-right py-4 px-4 text-gray-300 font-mono">${item.avgPrice.toLocaleString()}</td>
                    <td className="text-right py-4 px-4 text-white font-bold font-mono">${item.currentPrice.toLocaleString()}</td>
                    <td className="text-right py-4 px-4 text-white font-bold font-mono">${item.marketValue.toLocaleString()}</td>
                    <td className="text-right py-4 px-4">
                      <span className={`px-3 py-1 rounded-lg font-bold font-mono ${item.pnl >= 0 ? 'bg-[#00ff88]/20 text-[#00ff88]' : 'bg-[#ff4444]/20 text-[#ff4444]'}`}>
                        {item.pnl >= 0 ? '+' : ''}${item.pnl.toLocaleString()}
                      </span>
                    </td>
                    <td className="text-right py-4 px-4">
                      <span className={`px-3 py-1 rounded-lg font-bold font-mono ${item.pnlPercentage >= 0 ? 'bg-[#00ff88]/20 text-[#00ff88]' : 'bg-[#ff4444]/20 text-[#ff4444]'}`}>
                        {item.pnlPercentage >= 0 ? '↗ +' : '↘ '}{item.pnlPercentage.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

      {/* 底部状态栏 */}
      <div className="mt-6 bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border-t border-[#2a3a5a] px-6 py-4 flex items-center justify-between shadow-2xl">
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">总市值:</span>
          <span className="text-2xl font-bold text-white font-mono">${totalValue.toLocaleString()}</span>
          <span className="text-gray-500">|</span>
          <span className="text-sm text-gray-400">总盈亏:</span>
          <span className={`text-2xl font-bold font-mono ${totalPnl >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
            {totalPnl >= 0 ? '+' : ''}${totalPnl.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">风险等级:</span>
            <span className="px-3 py-1 rounded-lg bg-yellow-500/20 text-yellow-400 font-semibold">中等</span>
          </div>
          <span className="text-gray-500">|</span>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">杠杆:</span>
            <span className="text-white font-bold">1.0x</span>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-400">会话时间: <span className="text-[#00ccff] font-mono">08:00:00</span></span>
          <span className="text-gray-500">|</span>
          <span className="text-sm text-gray-400">CPU: <span className="text-[#00ff88] font-semibold">24%</span></span>
        </div>
      </div>
    </div>
  );
};

export default PortfolioPage;
