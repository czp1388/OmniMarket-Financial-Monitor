import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import { realTimeDataService, MarketData } from '../services/realTimeDataService';
import './VirtualTradingPage.css';

// 实时价格数据类型
interface SymbolData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  type: string;
  lastUpdate: string;
  source: string;
}

interface VirtualAccount {
  id: string;
  name: string;
  initial_balance: number;
  current_balance: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

interface Position {
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  unrealized_pnl: number;
  market_value: number;
}

interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit';
  quantity: number;
  price?: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  created_at: string;
  filled_at?: string;
}

interface PerformanceMetrics {
  total_return: number;
  daily_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  profitable_trades: number;
}

const VirtualTradingPage: React.FC = () => {
  // 实时价格监控状态
  const [symbolsData, setSymbolsData] = useState<SymbolData[]>([]);
  
  const [accounts, setAccounts] = useState<VirtualAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<VirtualAccount | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // 使用realTimeDataService获取实时数据
  const updateRealTimeData = async () => {
    try {
      const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
      const marketData = await realTimeDataService.getMarketData(symbols);
      
      const symbolData: SymbolData[] = marketData.map(item => ({
        symbol: item.symbol,
        price: item.price,
        change: item.change,
        changePercent: item.changePercent,
        volume: item.volume || 0,
        type: item.type,
        lastUpdate: item.lastUpdate,
        source: item.source
      }));
      
      setSymbolsData(symbolData);
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
      // 如果API调用失败，使用备用数据
      const fallbackData = generateFallbackData();
      setSymbolsData(fallbackData);
    }
  };

  // 备用数据生成（当API不可用时）
  const generateFallbackData = (): SymbolData[] => {
    const baseData = [
      { symbol: 'BTC/USDT', price: 42567.39, change: 975.42, changePercent: 2.34, volume: 28456789, type: 'crypto', lastUpdate: new Date().toLocaleString(), source: 'CoinGecko' },
      { symbol: 'ETH/USDT', price: 2345.67, change: 28.51, changePercent: 1.23, volume: 15678923, type: 'crypto', lastUpdate: new Date().toLocaleString(), source: 'CoinGecko' },
      { symbol: 'AAPL', price: 182.45, change: -1.03, changePercent: -0.56, volume: 4567890, type: 'stock', lastUpdate: new Date().toLocaleString(), source: 'Yahoo Finance' },
      { symbol: 'TSLA', price: 245.67, change: 3.21, changePercent: 1.32, volume: 2345678, type: 'stock', lastUpdate: new Date().toLocaleString(), source: 'Yahoo Finance' },
      { symbol: 'USD/CNY', price: 7.1987, change: 0.0086, changePercent: 0.12, volume: 123456789, type: 'forex', lastUpdate: new Date().toLocaleString(), source: 'ExchangeRate-API' },
      { symbol: 'EUR/USD', price: 1.0856, change: -0.0023, changePercent: -0.21, volume: 98765432, type: 'forex', lastUpdate: new Date().toLocaleString(), source: 'ExchangeRate-API' },
      { symbol: 'XAU/USD', price: 1987.45, change: 12.34, changePercent: 0.62, volume: 345678, type: 'commodity', lastUpdate: new Date().toLocaleString(), source: 'Alpha Vantage' },
      { symbol: 'SPY', price: 456.78, change: 2.34, changePercent: 0.51, volume: 1234567, type: 'stock', lastUpdate: new Date().toLocaleString(), source: 'Yahoo Finance' }
    ];
    
    // 添加一些随机波动以模拟实时更新
    return baseData.map(symbol => ({
      ...symbol,
      price: symbol.price + (Math.random() - 0.5) * symbol.price * 0.01,
      change: symbol.change + (Math.random() - 0.5) * 5,
      changePercent: symbol.changePercent + (Math.random() - 0.5) * 0.2,
      volume: symbol.volume + Math.random() * 500000
    }));
  };

  // 新建账户表单状态
  const [newAccountForm, setNewAccountForm] = useState({
    name: '',
    initial_balance: 100000,
    currency: 'USD'
  });

  // 订单表单状态
  const [orderForm, setOrderForm] = useState({
    symbol: '',
    side: 'buy' as 'buy' | 'sell',
    type: 'market' as 'market' | 'limit',
    quantity: 0,
    price: 0
  });

  // 加载账户列表
  const loadAccounts = async () => {
    try {
      const response = await ApiService.virtual.getAccounts();
      // 安全的类型检查
      if (Array.isArray(response)) {
        setAccounts(response);
      } else {
        console.error('Invalid accounts response format');
        setAccounts([]);
      }
    } catch (error) {
      console.error('Failed to load accounts:', error);
      setAccounts([]);
    }
  };

  // 加载账户详情
  const loadAccountDetails = async (accountId: string) => {
    try {
      setLoading(true);
      const [accountRes, ordersRes, performanceRes] = await Promise.all([
        ApiService.virtual.getAccount(accountId),
        ApiService.virtual.getOrderHistory(accountId),
        ApiService.virtual.getPerformance(accountId)
      ]);

      // 安全的类型检查 - 使用unknown进行类型中转
      if (accountRes && typeof accountRes === 'object') {
        setSelectedAccount(accountRes as unknown as VirtualAccount);
      } else {
        setSelectedAccount(null);
      }

      // 从账户信息中提取持仓数据
      if (accountRes && typeof accountRes === 'object') {
        const accountData = accountRes as any;
        if (accountData.positions && Array.isArray(accountData.positions)) {
          setPositions(accountData.positions as unknown as Position[]);
        } else {
          setPositions([]);
        }
      } else {
        setPositions([]);
      }

      if (Array.isArray(ordersRes)) {
        setOrders(ordersRes as unknown as Order[]);
      } else {
        setOrders([]);
      }

      if (performanceRes && typeof performanceRes === 'object') {
        setPerformance(performanceRes as unknown as PerformanceMetrics);
      } else {
        setPerformance(null);
      }
    } catch (error) {
      console.error('Failed to load account details:', error);
      setSelectedAccount(null);
      setPositions([]);
      setOrders([]);
      setPerformance(null);
    } finally {
      setLoading(false);
    }
  };

  // 创建新账户
  const createAccount = async () => {
    try {
      await ApiService.virtual.createAccount(newAccountForm);
      setNewAccountForm({ name: '', initial_balance: 100000, currency: 'USD' });
      await loadAccounts();
      alert('账户创建成功！');
    } catch (error) {
      console.error('Failed to create account:', error);
      alert('创建账户失败');
    }
  };

  // 下单
  const placeOrder = async () => {
    if (!selectedAccount) return;
    
    try {
      const orderData = {
        account_id: selectedAccount.id,
        symbol: orderForm.symbol,
        order_type: orderForm.type,
        side: orderForm.side,
        quantity: orderForm.quantity,
        price: orderForm.price || undefined
      };
      
      await ApiService.virtual.placeOrder(orderData);
      setOrderForm({ symbol: '', side: 'buy', type: 'market', quantity: 0, price: 0 });
      await loadAccountDetails(selectedAccount.id);
      alert('订单提交成功！');
    } catch (error) {
      console.error('Failed to place order:', error);
      alert('下单失败');
    }
  };

  // 取消订单
  const cancelOrder = async (orderId: string) => {
    try {
      await ApiService.virtual.cancelOrder(orderId);
      if (selectedAccount) {
        await loadAccountDetails(selectedAccount.id);
      }
      alert('订单取消成功！');
    } catch (error) {
      console.error('Failed to cancel order:', error);
      alert('取消订单失败');
    }
  };

  // 更新实时价格数据
  const updateSymbolData = async () => {
    await updateRealTimeData();
  };

  useEffect(() => {
    loadAccounts();
    // 初始化实时价格数据
    updateSymbolData();
    
    // 使用realTimeDataService的实时更新功能
    const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
    const stopUpdates = realTimeDataService.startRealTimeUpdates(
      (data: MarketData[]) => {
        const symbolData: SymbolData[] = data.map(item => ({
          symbol: item.symbol,
          price: item.price,
          change: item.change,
          changePercent: item.changePercent,
          volume: item.volume || 0,
          type: item.type,
          lastUpdate: item.lastUpdate,
          source: item.source
        }));
        setSymbolsData(symbolData);
      },
      symbols,
      5000 // 5秒更新间隔
    );
    
    return () => {
      stopUpdates();
    };
  }, []);

  // 格式化价格显示
  const formatPrice = (price: number, type: string) => {
    if (type === 'forex') return price.toFixed(4);
    if (type === 'crypto') return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    return `$${price.toFixed(2)}`;
  };

  // 格式化成交量显示
  const formatVolume = (volume: number) => {
    if (volume >= 1000000) return `${(volume / 1000000).toFixed(1)}M`;
    if (volume >= 1000) return `${(volume / 1000).toFixed(1)}K`;
    return volume.toFixed(0);
  };

  // 格式化变化金额显示
  const formatChange = (change: number, type: string) => {
    if (type === 'forex') return change.toFixed(4);
    return change.toFixed(2);
  };

  return (
    <div className="virtual-trading-container min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 风险提示横幅 - 增强版 */}
      <div className="bg-gradient-to-r from-[#ff4444]/20 to-[#ff6666]/20 border-l-4 border-[#ff4444] p-4 mb-6 backdrop-blur-sm">
        <div className="flex items-start gap-4 max-w-7xl mx-auto">
          <div className="text-4xl animate-pulse">⚠️</div>
          <div className="flex-1">
            <div className="text-xl font-bold text-[#ff4444] mb-2 flex items-center gap-2">
              <span>【模拟交易 - 仅供学习和测试使用】</span>
            </div>
            <div className="text-gray-300 leading-relaxed">
              本页面为虚拟交易环境，所有交易均使用模拟资金，不涉及真实资金交易。交易数据仅供学习和策略测试使用，不构成任何投资建议。
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-4 mb-6">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-3 mb-2">
          <span className="text-5xl">💼</span>
          <span>寰宇虚拟交易系统</span>
        </h1>
        <p className="text-gray-400 text-lg ml-16">专业级模拟交易平台 - 实时市场数据与高级分析</p>
      </div>

      <div className="max-w-7xl mx-auto px-6 flex gap-6">
        {/* 左侧实时价格监控 - 增强版 */}
        <div className="flex-shrink-0 w-80">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl sticky top-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-2xl">📊</span>
                <span>实时价格</span>
              </h3>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
                <span className="text-sm text-[#00ff88] font-semibold">实时</span>
              </div>
            </div>
            <div className="space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto pr-2 scrollbar-thin">
              {symbolsData.map((symbol) => (
                <div key={symbol.symbol} className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-3 hover:border-[#00ccff] transition-all duration-300 hover:shadow-md hover:shadow-[#00ccff]/10 cursor-pointer group">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-white group-hover:text-[#00ccff] transition-colors">{symbol.symbol}</span>
                    <span className="text-xs text-gray-500">{symbol.source}</span>
                  </div>
                  <div className="flex items-baseline justify-between mb-2">
                    <span className="text-xl font-bold text-white">
                      {formatPrice(symbol.price, symbol.type)}
                    </span>
                    <span className={`text-sm font-semibold flex items-center gap-1 ${
                      symbol.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                    }`}>
                      <span>{symbol.change >= 0 ? '↗' : '↘'}</span>
                      <span>{symbol.change >= 0 ? '+' : ''}{symbol.changePercent.toFixed(2)}%</span>
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">量: {formatVolume(symbol.volume)}</span>
                    <span className={`font-semibold ${
                      symbol.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                    }`}>
                      {symbol.change >= 0 ? '+' : ''}{formatChange(symbol.change, symbol.type)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧交易面板 - 增强版 */}
        <div className="flex-1 space-y-6">
          {/* 账户管理 - 增强版 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-6 flex items-center gap-2">
            <span className="text-3xl">👤</span>
            <span>账户管理</span>
          </h2>
          
          {/* 创建新账户 - 增强版 */}
          <div className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-5 mb-6">
            <h3 className="text-lg font-semibold text-[#00ccff] mb-4 flex items-center gap-2">
              <span className="text-xl">➕</span>
              <span>创建新账户</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <input
                type="text"
                placeholder="账户名称"
                value={newAccountForm.name}
                onChange={(e) => setNewAccountForm({...newAccountForm, name: e.target.value})}
                className="bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-[#00ccff] focus:outline-none transition-colors"
              />
              <input
                type="number"
                placeholder="初始资金"
                value={newAccountForm.initial_balance}
                onChange={(e) => setNewAccountForm({...newAccountForm, initial_balance: Number(e.target.value)})}
                className="bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-[#00ccff] focus:outline-none transition-colors"
              />
              <select
                value={newAccountForm.currency}
                onChange={(e) => setNewAccountForm({...newAccountForm, currency: e.target.value})}
                className="bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
              >
                <option value="USD">💵 USD</option>
                <option value="CNY">💴 CNY</option>
                <option value="HKD">💰 HKD</option>
              </select>
              <button
                onClick={createAccount}
                disabled={!newAccountForm.name}
                className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black rounded-lg px-6 py-3 font-bold hover:scale-[1.02] transition-all duration-300 shadow-lg shadow-[#00ccff]/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                ✓ 创建账户
              </button>
            </div>
          </div>

          {/* 账户列表 - 增强版 */}
          <div>
            <h3 className="text-lg font-semibold text-gray-300 mb-4 flex items-center gap-2">
              <span className="text-xl">📋</span>
              <span>账户列表</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {accounts.map(account => (
                <div
                  key={account.id}
                  className={`bg-gradient-to-br from-[#1a2332] to-[#141a2a] border rounded-xl p-5 cursor-pointer transition-all duration-300 hover:scale-[1.02] ${
                    selectedAccount?.id === account.id
                      ? 'border-[#00ccff] shadow-lg shadow-[#00ccff]/30'
                      : 'border-[#2a3a5a] hover:border-[#00ccff] hover:shadow-md hover:shadow-[#00ccff]/10'
                  }`}
                  onClick={() => loadAccountDetails(account.id)}
                >
                  <div className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                    <span className="text-2xl">💼</span>
                    <span>{account.name}</span>
                  </div>
                  <div className="text-3xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-3">
                    ${account.current_balance.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-400 space-y-1">
                    <div className="flex items-center justify-between">
                      <span>初始资金:</span>
                      <span className="text-white">${account.initial_balance.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>货币:</span>
                      <span className="text-[#00ccff] font-semibold">{account.currency}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          </div>

          {/* 选中的账户详情 - 增强版 */}
          {selectedAccount && (
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center justify-between mb-6 pb-5 border-b border-[#2a3a5a]">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <span className="text-3xl">📈</span>
                <span className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                  {selectedAccount.name} - 交易面板
                </span>
              </h2>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-sm text-gray-400 mb-1">当前余额</div>
                  <div className="text-3xl font-bold text-white">
                    ${selectedAccount.current_balance.toLocaleString()}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-400 mb-1">总收益</div>
                  <div className={`text-2xl font-bold flex items-center gap-1 ${
                    selectedAccount.current_balance >= selectedAccount.initial_balance ? 'text-[#00ff88]' : 'text-[#ff4444]'
                  }`}>
                    <span>{selectedAccount.current_balance >= selectedAccount.initial_balance ? '↗' : '↘'}</span>
                    <span>${(selectedAccount.current_balance - selectedAccount.initial_balance).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 选项卡 - 增强版 */}
            <div className="mb-6">
              <nav className="flex gap-3">
                {[
                  { key: 'overview', label: '概览', icon: '📊' },
                  { key: 'trading', label: '交易', icon: '💰' },
                  { key: 'positions', label: '持仓', icon: '📦' },
                  { key: 'orders', label: '订单', icon: '📋' },
                  { key: 'performance', label: '绩效', icon: '📈' }
                ].map(tab => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`px-5 py-3 rounded-xl transition-all duration-300 font-semibold flex items-center gap-2 ${
                      activeTab === tab.key
                        ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black shadow-lg shadow-[#00ccff]/30 scale-105'
                        : 'bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] hover:from-[#3a4a6a] hover:to-[#2a3a5a] shadow-md hover:scale-[1.02]'
                    }`}
                  >
                    <span className="text-xl">{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>

            {/* 选项卡内容 */}
            <div className="mt-6">
              {/* 概览选项卡 - 增强版 */}
              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* 账户概览 */}
                  <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-5 shadow-lg">
                    <h3 className="text-lg font-bold text-[#00ccff] mb-4 flex items-center gap-2">
                      <span className="text-2xl">📊</span>
                      <span>账户概览</span>
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between py-2 border-b border-[#2a3a5a]">
                        <span className="text-gray-400">当前余额:</span>
                        <span className="text-xl font-bold text-white">${selectedAccount.current_balance.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between py-2 border-b border-[#2a3a5a]">
                        <span className="text-gray-400">初始资金:</span>
                        <span className="text-white font-semibold">${selectedAccount.initial_balance.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between py-2 border-b border-[#2a3a5a]">
                        <span className="text-gray-400">总收益:</span>
                        <span className={`text-xl font-bold ${selectedAccount.current_balance >= selectedAccount.initial_balance ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                          ${(selectedAccount.current_balance - selectedAccount.initial_balance).toLocaleString()}
                        </span>
                      </div>
                      <div className="flex items-center justify-between py-2">
                        <span className="text-gray-400">收益率:</span>
                        <span className={`text-xl font-bold ${selectedAccount.current_balance >= selectedAccount.initial_balance ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                          {((selectedAccount.current_balance - selectedAccount.initial_balance) / selectedAccount.initial_balance * 100).toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 持仓概览 */}
                  <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-5 shadow-lg">
                    <h3 className="text-lg font-bold text-[#00ccff] mb-4 flex items-center gap-2">
                      <span className="text-2xl">📦</span>
                      <span>持仓概览</span>
                    </h3>
                    {positions.length === 0 ? (
                      <p className="text-gray-400 text-center py-8">暂无持仓</p>
                    ) : (
                      <div className="space-y-3">
                        {positions.slice(0, 3).map(position => (
                          <div key={position.symbol} className="flex items-center justify-between py-2 border-b border-[#2a3a5a] hover:bg-[#0a0e17]/30 transition-colors px-2 rounded">
                            <span className="font-bold text-white">{position.symbol}</span>
                            <span className="text-gray-400">{position.quantity} 股</span>
                            <span className={`font-bold ${position.unrealized_pnl >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                              ${position.unrealized_pnl.toFixed(2)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* 绩效概览 */}
                  <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-5 shadow-lg">
                    <h3 className="text-lg font-bold text-[#00ccff] mb-4 flex items-center gap-2">
                      <span className="text-2xl">📈</span>
                      <span>绩效概览</span>
                    </h3>
                    {performance ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between py-2 border-b border-[#2a3a5a]">
                          <span className="text-gray-400">夏普比率:</span>
                          <span className="font-bold text-white">{performance.sharpe_ratio.toFixed(2)}</span>
                        </div>
                        <div className="flex items-center justify-between py-2 border-b border-[#2a3a5a]">
                          <span className="text-gray-400">最大回撤:</span>
                          <span className="font-bold text-[#ff4444]">{performance.max_drawdown.toFixed(2)}%</span>
                        </div>
                        <div className="flex items-center justify-between py-2 border-b border-[#2a3a5a]">
                          <span className="text-gray-400">胜率:</span>
                          <span className="font-bold text-[#00ff88]">{performance.win_rate.toFixed(1)}%</span>
                        </div>
                        <div className="flex items-center justify-between py-2">
                          <span className="text-gray-400">总交易:</span>
                          <span className="font-bold text-white">{performance.total_trades}</span>
                        </div>
                      </div>
                    ) : (
                      <p className="text-gray-400 text-center py-8">暂无绩效数据</p>
                    )}
                  </div>
                </div>
              )}

              {/* 交易选项卡 - 增强版 */}
              {activeTab === 'trading' && (
                <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg">
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-6 flex items-center gap-2">
                    <span className="text-3xl">💰</span>
                    <span>下单交易</span>
                  </h3>
                  <div className="space-y-5">
                    <div>
                      <label className="block text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                        <span>🔍</span>
                        <span>交易标的</span>
                      </label>
                      <input
                        type="text"
                        placeholder="例如: AAPL, TSLA, BTC/USDT"
                        value={orderForm.symbol}
                        onChange={(e) => setOrderForm({...orderForm, symbol: e.target.value.toUpperCase()})}
                        className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white text-lg placeholder-gray-500 focus:border-[#00ccff] focus:outline-none transition-colors"
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-400 mb-2">交易方向</label>
                        <select
                          value={orderForm.side}
                          onChange={(e) => setOrderForm({...orderForm, side: e.target.value as 'buy' | 'sell'})}
                          className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
                        >
                          <option value="buy">📈 买入</option>
                          <option value="sell">📉 卖出</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-400 mb-2">订单类型</label>
                        <select
                          value={orderForm.type}
                          onChange={(e) => setOrderForm({...orderForm, type: e.target.value as 'market' | 'limit'})}
                          className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none transition-colors"
                        >
                          <option value="market">⚡ 市价单</option>
                          <option value="limit">🎯 限价单</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                        <span>📊</span>
                        <span>交易数量</span>
                      </label>
                      <input
                        type="number"
                        value={orderForm.quantity}
                        onChange={(e) => setOrderForm({...orderForm, quantity: Number(e.target.value)})}
                        className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white text-lg placeholder-gray-500 focus:border-[#00ccff] focus:outline-none transition-colors"
                      />
                    </div>

                    {orderForm.type === 'limit' && (
                      <div>
                        <label className="block text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
                          <span>💵</span>
                          <span>限价</span>
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          value={orderForm.price}
                          onChange={(e) => setOrderForm({...orderForm, price: Number(e.target.value)})}
                          className="w-full bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white text-lg placeholder-gray-500 focus:border-[#00ccff] focus:outline-none transition-colors"
                        />
                      </div>
                    )}

                    <button
                      onClick={placeOrder}
                      disabled={!orderForm.symbol || orderForm.quantity <= 0 || (orderForm.type === 'limit' && orderForm.price <= 0)}
                      className={`w-full py-5 rounded-xl font-bold text-lg transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 ${
                        orderForm.side === 'buy'
                          ? 'bg-gradient-to-r from-[#00ff88] to-[#00ccaa] text-black hover:scale-[1.02] shadow-[#00ff88]/30'
                          : 'bg-gradient-to-r from-[#ff4444] to-[#ff6666] text-white hover:scale-[1.02] shadow-[#ff4444]/30'
                      }`}
                    >
                      {orderForm.side === 'buy' ? '📈' : '📉'} {orderForm.side === 'buy' ? '买入' : '卖出'} {orderForm.symbol || '请选择标的'}
                    </button>
                  </div>
                </div>
              )}

              {/* 持仓选项卡 - 增强版 */}
              {activeTab === 'positions' && (
                <div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-5 flex items-center gap-2">
                    <span className="text-3xl">📦</span>
                    <span>当前持仓</span>
                  </h3>
                  {positions.length === 0 ? (
                    <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-12 text-center">
                      <div className="text-6xl mb-4">📦</div>
                      <p className="text-gray-400 text-lg">暂无持仓</p>
                    </div>
                  ) : (
                    <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl overflow-hidden shadow-lg">
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="bg-[#0a0e17] border-b border-[#2a3a5a]">
                              <th className="px-6 py-4 text-left text-sm font-bold text-gray-400">标的</th>
                              <th className="px-6 py-4 text-right text-sm font-bold text-gray-400">数量</th>
                              <th className="px-6 py-4 text-right text-sm font-bold text-gray-400">平均成本</th>
                              <th className="px-6 py-4 text-right text-sm font-bold text-gray-400">当前价格</th>
                              <th className="px-6 py-4 text-right text-sm font-bold text-gray-400">市值</th>
                              <th className="px-6 py-4 text-right text-sm font-bold text-gray-400">未实现盈亏</th>
                            </tr>
                          </thead>
                          <tbody>
                            {positions.map(position => (
                              <tr key={position.symbol} className="border-b border-[#2a3a5a] hover:bg-[#0a0e17]/50 transition-colors">
                                <td className="px-6 py-4 font-bold text-white">{position.symbol}</td>
                                <td className="px-6 py-4 text-right text-gray-300">{position.quantity}</td>
                                <td className="px-6 py-4 text-right text-gray-300">${position.average_price.toFixed(2)}</td>
                                <td className="px-6 py-4 text-right text-white font-semibold">${position.current_price.toFixed(2)}</td>
                                <td className="px-6 py-4 text-right text-white font-semibold">${position.market_value.toFixed(2)}</td>
                                <td className={`px-6 py-4 text-right font-bold text-lg ${position.unrealized_pnl >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                                  {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 订单选项卡 - 增强版 */}
              {activeTab === 'orders' && (
                <div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-5 flex items-center gap-2">
                    <span className="text-3xl">📋</span>
                    <span>订单历史</span>
                  </h3>
                  {orders.length === 0 ? (
                    <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-12 text-center">
                      <div className="text-6xl mb-4">📋</div>
                      <p className="text-gray-400 text-lg">暂无订单</p>
                    </div>
                  ) : (
                    <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl overflow-hidden shadow-lg">
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="bg-[#0a0e17] border-b border-[#2a3a5a]">
                              <th className="px-4 py-4 text-left text-sm font-bold text-gray-400">订单ID</th>
                              <th className="px-4 py-4 text-left text-sm font-bold text-gray-400">标的</th>
                              <th className="px-4 py-4 text-center text-sm font-bold text-gray-400">方向</th>
                              <th className="px-4 py-4 text-center text-sm font-bold text-gray-400">类型</th>
                              <th className="px-4 py-4 text-right text-sm font-bold text-gray-400">数量</th>
                              <th className="px-4 py-4 text-right text-sm font-bold text-gray-400">价格</th>
                              <th className="px-4 py-4 text-center text-sm font-bold text-gray-400">状态</th>
                              <th className="px-4 py-4 text-left text-sm font-bold text-gray-400">时间</th>
                              <th className="px-4 py-4 text-center text-sm font-bold text-gray-400">操作</th>
                            </tr>
                          </thead>
                          <tbody>
                            {orders.map(order => (
                              <tr key={order.id} className="border-b border-[#2a3a5a] hover:bg-[#0a0e17]/50 transition-colors">
                                <td className="px-4 py-4 text-gray-400 font-mono text-sm">{order.id.slice(0, 8)}...</td>
                                <td className="px-4 py-4 font-bold text-white">{order.symbol}</td>
                                <td className="px-4 py-4 text-center">
                                  <span className={`px-3 py-1 rounded-lg font-semibold ${order.side === 'buy' ? 'bg-[#00ff88]/20 text-[#00ff88]' : 'bg-[#ff4444]/20 text-[#ff4444]'}`}>
                                    {order.side === 'buy' ? '📈 买入' : '📉 卖出'}
                                  </span>
                                </td>
                                <td className="px-4 py-4 text-center text-gray-300">
                                  {order.type === 'market' ? '⚡ 市价' : '🎯 限价'}
                                </td>
                                <td className="px-4 py-4 text-right text-white">{order.quantity}</td>
                                <td className="px-4 py-4 text-right text-white font-semibold">
                                  {order.price ? `$${order.price}` : '市价'}
                                </td>
                                <td className="px-4 py-4 text-center">
                                  <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                                    order.status === 'filled' ? 'bg-[#00ff88]/20 text-[#00ff88]' :
                                    order.status === 'pending' ? 'bg-[#00ccff]/20 text-[#00ccff]' :
                                    order.status === 'cancelled' ? 'bg-gray-500/20 text-gray-400' :
                                    'bg-[#ff4444]/20 text-[#ff4444]'
                                  }`}>
                                    {order.status === 'filled' ? '✓ 已成交' :
                                     order.status === 'pending' ? '⏳ 待成交' :
                                     order.status === 'cancelled' ? '✕ 已取消' : '⛔ 已拒绝'}
                                  </span>
                                </td>
                                <td className="px-4 py-4 text-gray-400 text-sm">
                                  {new Date(order.created_at).toLocaleString()}
                                </td>
                                <td className="px-4 py-4 text-center">
                                  {order.status === 'pending' && (
                                    <button
                                      onClick={() => cancelOrder(order.id)}
                                      className="px-3 py-1 bg-[#ff4444]/20 text-[#ff4444] rounded-lg hover:bg-[#ff4444]/30 transition-colors font-semibold text-sm"
                                    >
                                      取消
                                    </button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 绩效选项卡 - 增强版 */}
              {activeTab === 'performance' && (
                <div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-5 flex items-center gap-2">
                    <span className="text-3xl">📈</span>
                    <span>绩效分析</span>
                  </h3>
                  {performance ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                      <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-300 hover:shadow-[#00ccff]/10">
                        <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                          <span>📈</span>
                          <span>总收益率</span>
                        </div>
                        <div className={`text-4xl font-bold mb-1 ${
                          performance.total_return >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                        }`}>
                          {performance.total_return >= 0 ? '+' : ''}{performance.total_return.toFixed(2)}%
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-300">
                        <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                          <span>📊</span>
                          <span>夏普比率</span>
                        </div>
                        <div className="text-4xl font-bold text-[#00ccff] mb-1">
                          {performance.sharpe_ratio.toFixed(2)}
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-300 hover:shadow-[#ff4444]/10">
                        <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                          <span>📉</span>
                          <span>最大回撤</span>
                        </div>
                        <div className="text-4xl font-bold text-[#ff4444] mb-1">
                          {performance.max_drawdown.toFixed(2)}%
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-300 hover:shadow-[#00ff88]/10">
                        <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                          <span>🎯</span>
                          <span>胜率</span>
                        </div>
                        <div className="text-4xl font-bold text-[#00ff88] mb-1">
                          {performance.win_rate.toFixed(1)}%
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-300">
                        <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                          <span>📊</span>
                          <span>总交易数</span>
                        </div>
                        <div className="text-4xl font-bold text-white mb-1">
                          {performance.total_trades}
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-300 hover:shadow-[#00ff88]/10">
                        <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                          <span>✓</span>
                          <span>盈利交易</span>
                        </div>
                        <div className="text-4xl font-bold text-[#00ff88] mb-1">
                          {performance.profitable_trades}
                        </div>
                      </div>
                      
                      <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-300">
                        <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                          <span>📅</span>
                          <span>日收益率</span>
                        </div>
                        <div className={`text-4xl font-bold mb-1 ${
                          performance.daily_return >= 0 ? 'text-[#00ff88]' : 'text-[#ff4444]'
                        }`}>
                          {performance.daily_return >= 0 ? '+' : ''}{performance.daily_return.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-12 text-center">
                      <div className="text-6xl mb-4">📈</div>
                      <p className="text-gray-400 text-lg">暂无绩效数据</p>
                    </div>
                  )}
                </div>
              )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VirtualTradingPage;
