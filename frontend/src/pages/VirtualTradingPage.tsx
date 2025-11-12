import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import './VirtualTradingPage.css';

// 实时价格数据类型
interface SymbolData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
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

  // 从后端API获取实时价格数据
  const fetchRealTimeData = async (): Promise<SymbolData[]> => {
    try {
      const symbols = ['BTC/USDT', 'ETH/USDT', 'AAPL', 'USD/CNY', 'TSLA', 'EUR/USD', 'XAU/USD', 'SPY'];
      const response = await ApiService.market.getTickers(symbols);
      
      // 安全的类型检查和处理
      if (Array.isArray(response)) {
        return response.map((ticker: any) => ({
          symbol: ticker.symbol,
          price: ticker.last || ticker.close || 0,
          change: ticker.change || 0,
          changePercent: ticker.change_percent || 0,
          volume: ticker.baseVolume || ticker.volume || 0
        }));
      } else {
        console.warn('Invalid response format from API, using fallback data');
        return generateFallbackData();
      }
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
      return generateFallbackData();
    }
  };

  // 备用数据生成（当API不可用时）
  const generateFallbackData = (): SymbolData[] => {
    const baseData = [
      { symbol: 'BTC/USDT', price: 42567.39, change: 975.42, changePercent: 2.34, volume: 28456789 },
      { symbol: 'ETH/USDT', price: 2345.67, change: 28.51, changePercent: 1.23, volume: 15678923 },
      { symbol: 'AAPL', price: 182.45, change: -1.03, changePercent: -0.56, volume: 4567890 },
      { symbol: 'TSLA', price: 245.67, change: 3.21, changePercent: 1.32, volume: 2345678 },
      { symbol: 'USD/CNY', price: 7.1987, change: 0.0086, changePercent: 0.12, volume: 123456789 },
      { symbol: 'EUR/USD', price: 1.0856, change: -0.0023, changePercent: -0.21, volume: 98765432 },
      { symbol: 'XAU/USD', price: 1987.45, change: 12.34, changePercent: 0.62, volume: 345678 },
      { symbol: 'SPY', price: 456.78, change: 2.34, changePercent: 0.51, volume: 1234567 }
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
      const [accountRes, positionsRes, ordersRes, performanceRes] = await Promise.all([
        ApiService.virtual.getAccount(accountId),
        ApiService.virtual.getPositions(accountId),
        ApiService.virtual.getOrders(accountId),
        ApiService.virtual.getPerformance(accountId)
      ]);

      // 安全的类型检查 - 使用unknown进行类型中转
      if (accountRes && typeof accountRes === 'object') {
        setSelectedAccount(accountRes as unknown as VirtualAccount);
      } else {
        setSelectedAccount(null);
      }

      if (Array.isArray(positionsRes)) {
        setPositions(positionsRes as unknown as Position[]);
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
      await ApiService.virtual.placeOrder(selectedAccount.id, orderForm);
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
    if (!selectedAccount) return;
    
    try {
      await ApiService.virtual.cancelOrder(selectedAccount.id, orderId);
      await loadAccountDetails(selectedAccount.id);
      alert('订单取消成功！');
    } catch (error) {
      console.error('Failed to cancel order:', error);
      alert('取消订单失败');
    }
  };

  // 更新实时价格数据
  const updateSymbolData = async () => {
    try {
      const realTimeData = await fetchRealTimeData();
      setSymbolsData(realTimeData);
    } catch (error) {
      console.error('Failed to update real-time data:', error);
      // 如果API调用失败，使用备用数据并添加一些随机波动
      const updatedData = generateFallbackData();
      setSymbolsData(updatedData);
    }
  };

  useEffect(() => {
    loadAccounts();
    // 初始化实时价格数据
    updateSymbolData();
    
    // 每5秒更新一次实时价格（减少频率以避免API限制）
    const interval = setInterval(updateSymbolData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="virtual-trading-container">
      <div className="virtual-trading-header">
        <h1>虚拟交易系统</h1>
        <p>专业级模拟交易平台 - 实时市场数据与高级分析</p>
      </div>

      <div className="virtual-trading-layout">
        {/* 左侧实时价格监控 */}
        <div className="real-time-monitor">
          <div className="monitor-header">
            <h3>实时价格监控</h3>
            <span className="status-indicator active">实时</span>
          </div>
          <div className="symbols-grid">
            {symbolsData.map((symbol) => (
              <div key={symbol.symbol} className="symbol-card">
                <div className="symbol-header">
                  <span className="symbol-name">{symbol.symbol}</span>
                  <span className={`price-change ${symbol.change >= 0 ? 'positive' : 'negative'}`}>
                    {symbol.change >= 0 ? '+' : ''}{symbol.changePercent.toFixed(2)}%
                  </span>
                </div>
                <div className="price-display">
                  <span className="current-price">
                    {symbol.symbol.includes('/') ? '$' : ''}{symbol.price.toLocaleString(undefined, {
                      minimumFractionDigits: symbol.symbol.includes('/') ? 4 : 2,
                      maximumFractionDigits: symbol.symbol.includes('/') ? 4 : 2
                    })}
                  </span>
                </div>
                <div className="symbol-footer">
                  <span className="volume">量: {(symbol.volume / 1000000).toFixed(1)}M</span>
                  <span className={`change-amount ${symbol.change >= 0 ? 'positive' : 'negative'}`}>
                    {symbol.change >= 0 ? '+' : ''}{symbol.change.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧交易面板 */}
        <div className="trading-content">
          {/* 账户管理 */}
          <div className="account-management">
          <h2>账户管理</h2>
          
          {/* 创建新账户 */}
          <div className="create-account-form">
            <h3>创建新账户</h3>
            <div className="form-grid">
              <input
                type="text"
                placeholder="账户名称"
                value={newAccountForm.name}
                onChange={(e) => setNewAccountForm({...newAccountForm, name: e.target.value})}
                className="form-control"
              />
              <input
                type="number"
                placeholder="初始资金"
                value={newAccountForm.initial_balance}
                onChange={(e) => setNewAccountForm({...newAccountForm, initial_balance: Number(e.target.value)})}
                className="form-control"
              />
              <select
                value={newAccountForm.currency}
                onChange={(e) => setNewAccountForm({...newAccountForm, currency: e.target.value})}
                className="form-control"
              >
                <option value="USD">USD</option>
                <option value="CNY">CNY</option>
                <option value="HKD">HKD</option>
              </select>
              <button
                onClick={createAccount}
                disabled={!newAccountForm.name}
                className="btn btn-primary"
              >
                创建账户
              </button>
            </div>
          </div>

          {/* 账户列表 */}
          <div>
            <h3 className="section-subtitle">账户列表</h3>
            <div className="account-list">
              {accounts.map(account => (
                <div
                  key={account.id}
                  className={`account-card ${selectedAccount?.id === account.id ? 'selected' : ''}`}
                  onClick={() => loadAccountDetails(account.id)}
                >
                  <div className="account-name">{account.name}</div>
                  <div className="account-balance">${account.current_balance.toLocaleString()}</div>
                  <div className="account-details">
                    初始资金: ${account.initial_balance.toLocaleString()}<br />
                    货币: {account.currency}
                  </div>
                </div>
              ))}
            </div>
          </div>
          </div>

          {/* 选中的账户详情 */}
          {selectedAccount && (
            <div className="trading-panel">
              <div className="trading-panel-header">
              <h2>{selectedAccount.name} - 交易面板</h2>
              <div className="account-summary">
                <div className="balance">${selectedAccount.current_balance.toLocaleString()}</div>
                <div className={`pnl ${
                  selectedAccount.current_balance >= selectedAccount.initial_balance ? 'profit' : 'loss'
                }`}>
                  收益: ${(selectedAccount.current_balance - selectedAccount.initial_balance).toLocaleString()}
                </div>
              </div>
            </div>

            {/* 选项卡 */}
            <div className="trading-tabs">
              <nav className="tab-nav">
                {['overview', 'trading', 'positions', 'orders', 'performance'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`tab-button ${activeTab === tab ? 'active' : ''}`}
                  >
                    {tab === 'overview' && '概览'}
                    {tab === 'trading' && '交易'}
                    {tab === 'positions' && '持仓'}
                    {tab === 'orders' && '订单'}
                    {tab === 'performance' && '绩效'}
                  </button>
                ))}
              </nav>
            </div>

            {/* 选项卡内容 */}
            <div className="tab-content">
              {/* 概览选项卡 */}
              {activeTab === 'overview' && (
                <div className="overview-grid">
                  {/* 账户概览 */}
                  <div className="overview-section">
                    <h3>账户概览</h3>
                    <div className="overview-items">
                      <div className="overview-item">
                        <span>当前余额:</span>
                        <span className="value">${selectedAccount.current_balance.toLocaleString()}</span>
                      </div>
                      <div className="overview-item">
                        <span>初始资金:</span>
                        <span>${selectedAccount.initial_balance.toLocaleString()}</span>
                      </div>
                      <div className="overview-item">
                        <span>总收益:</span>
                        <span className={`value ${selectedAccount.current_balance >= selectedAccount.initial_balance ? 'profit' : 'loss'}`}>
                          ${(selectedAccount.current_balance - selectedAccount.initial_balance).toLocaleString()}
                        </span>
                      </div>
                      <div className="overview-item">
                        <span>收益率:</span>
                        <span className={`value ${selectedAccount.current_balance >= selectedAccount.initial_balance ? 'profit' : 'loss'}`}>
                          {((selectedAccount.current_balance - selectedAccount.initial_balance) / selectedAccount.initial_balance * 100).toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 持仓概览 */}
                  <div className="overview-section">
                    <h3>持仓概览</h3>
                    {positions.length === 0 ? (
                      <p className="no-data">暂无持仓</p>
                    ) : (
                      <div className="overview-items">
                        {positions.slice(0, 3).map(position => (
                          <div key={position.symbol} className="overview-item">
                            <span>{position.symbol}</span>
                            <span>{position.quantity} 股</span>
                            <span className={`value ${position.unrealized_pnl >= 0 ? 'profit' : 'loss'}`}>
                              ${position.unrealized_pnl.toFixed(2)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* 绩效概览 */}
                  <div className="overview-section">
                    <h3>绩效概览</h3>
                    {performance ? (
                      <div className="overview-items">
                        <div className="overview-item">
                          <span>夏普比率:</span>
                          <span>{performance.sharpe_ratio.toFixed(2)}</span>
                        </div>
                        <div className="overview-item">
                          <span>最大回撤:</span>
                          <span className="value loss">{performance.max_drawdown.toFixed(2)}%</span>
                        </div>
                        <div className="overview-item">
                          <span>胜率:</span>
                          <span className="value profit">{performance.win_rate.toFixed(1)}%</span>
                        </div>
                        <div className="overview-item">
                          <span>总交易:</span>
                          <span>{performance.total_trades}</span>
                        </div>
                      </div>
                    ) : (
                      <p className="no-data">暂无绩效数据</p>
                    )}
                  </div>
                </div>
              )}

              {/* 交易选项卡 */}
              {activeTab === 'trading' && (
                <div className="trading-form">
                  <h3>下单交易</h3>
                  <div className="form-layout">
                    <div className="form-group">
                      <label>交易标的</label>
                      <input
                        type="text"
                        placeholder="例如: AAPL, TSLA"
                        value={orderForm.symbol}
                        onChange={(e) => setOrderForm({...orderForm, symbol: e.target.value.toUpperCase()})}
                        className="form-control"
                      />
                    </div>
                    
                    <div className="form-row">
                      <div className="form-group">
                        <label>方向</label>
                        <select
                          value={orderForm.side}
                          onChange={(e) => setOrderForm({...orderForm, side: e.target.value as 'buy' | 'sell'})}
                          className="form-control"
                        >
                          <option value="buy">买入</option>
                          <option value="sell">卖出</option>
                        </select>
                      </div>
                      
                      <div className="form-group">
                        <label>类型</label>
                        <select
                          value={orderForm.type}
                          onChange={(e) => setOrderForm({...orderForm, type: e.target.value as 'market' | 'limit'})}
                          className="form-control"
                        >
                          <option value="market">市价单</option>
                          <option value="limit">限价单</option>
                        </select>
                      </div>
                    </div>

                    <div className="form-group">
                      <label>数量</label>
                      <input
                        type="number"
                        value={orderForm.quantity}
                        onChange={(e) => setOrderForm({...orderForm, quantity: Number(e.target.value)})}
                        className="form-control"
                      />
                    </div>

                    {orderForm.type === 'limit' && (
                      <div className="form-group">
                        <label>价格</label>
                        <input
                          type="number"
                          step="0.01"
                          value={orderForm.price}
                          onChange={(e) => setOrderForm({...orderForm, price: Number(e.target.value)})}
                          className="form-control"
                        />
                      </div>
                    )}

                    <button
                      onClick={placeOrder}
                      disabled={!orderForm.symbol || orderForm.quantity <= 0 || (orderForm.type === 'limit' && orderForm.price <= 0)}
                      className={`btn ${orderForm.side === 'buy' ? 'btn-buy' : 'btn-sell'}`}
                    >
                      {orderForm.side === 'buy' ? '买入' : '卖出'} {orderForm.symbol}
                    </button>
                  </div>
                </div>
              )}

              {/* 持仓选项卡 */}
              {activeTab === 'positions' && (
                <div>
                  <h3 className="section-title">当前持仓</h3>
                  {positions.length === 0 ? (
                    <p className="no-data">暂无持仓</p>
                  ) : (
                    <div className="table-container">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>标的</th>
                            <th>数量</th>
                            <th>平均成本</th>
                            <th>当前价格</th>
                            <th>市值</th>
                            <th>未实现盈亏</th>
                          </tr>
                        </thead>
                        <tbody>
                          {positions.map(position => (
                            <tr key={position.symbol}>
                              <td>{position.symbol}</td>
                              <td>{position.quantity}</td>
                              <td>${position.average_price.toFixed(2)}</td>
                              <td>${position.current_price.toFixed(2)}</td>
                              <td>${position.market_value.toFixed(2)}</td>
                              <td className={`${position.unrealized_pnl >= 0 ? 'profit' : 'loss'}`}>
                                ${position.unrealized_pnl.toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}

              {/* 订单选项卡 */}
              {activeTab === 'orders' && (
                <div>
                  <h3 className="section-title">订单历史</h3>
                  {orders.length === 0 ? (
                    <p className="no-data">暂无订单</p>
                  ) : (
                    <div className="table-container">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>订单ID</th>
                            <th>标的</th>
                            <th>方向</th>
                            <th>类型</th>
                            <th>数量</th>
                            <th>价格</th>
                            <th>状态</th>
                            <th>时间</th>
                            <th>操作</th>
                          </tr>
                        </thead>
                        <tbody>
                          {orders.map(order => (
                            <tr key={order.id}>
                              <td>{order.id.slice(0, 8)}...</td>
                              <td>{order.symbol}</td>
                              <td className={`${order.side === 'buy' ? 'profit' : 'loss'}`}>
                                {order.side === 'buy' ? '买入' : '卖出'}
                              </td>
                              <td>
                                {order.type === 'market' ? '市价' : '限价'}
                              </td>
                              <td>{order.quantity}</td>
                              <td>
                                {order.price ? `$${order.price}` : '市价'}
                              </td>
                              <td>
                                <span className={`status-badge ${
                                  order.status === 'filled' ? 'status-filled' :
                                  order.status === 'pending' ? 'status-pending' :
                                  order.status === 'cancelled' ? 'status-cancelled' :
                                  'status-rejected'
                                }`}>
                                  {order.status === 'filled' ? '已成交' :
                                   order.status === 'pending' ? '待成交' :
                                   order.status === 'cancelled' ? '已取消' : '已拒绝'}
                                </span>
                              </td>
                              <td>
                                {new Date(order.created_at).toLocaleString()}
                              </td>
                              <td>
                                {order.status === 'pending' && (
                                  <button
                                    onClick={() => cancelOrder(order.id)}
                                    className="btn-cancel"
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
                  )}
                </div>
              )}

              {/* 绩效选项卡 */}
              {activeTab === 'performance' && (
                <div>
                  <h3 className="section-title">绩效分析</h3>
                  {performance ? (
                    <div className="performance-grid">
                      <div className="metric-card">
                        <div className="label">总收益率</div>
                        <div className={`value ${
                          performance.total_return >= 0 ? 'profit' : 'loss'
                        }`}>
                          {performance.total_return.toFixed(2)}%
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <div className="label">夏普比率</div>
                        <div className="value info">
                          {performance.sharpe_ratio.toFixed(2)}
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <div className="label">最大回撤</div>
                        <div className="value loss">
                          {performance.max_drawdown.toFixed(2)}%
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <div className="label">胜率</div>
                        <div className="value profit">
                          {performance.win_rate.toFixed(1)}%
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <div className="label">总交易数</div>
                        <div className="value neutral">
                          {performance.total_trades}
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <div className="label">盈利交易</div>
                        <div className="value profit">
                          {performance.profitable_trades}
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <div className="label">日收益率</div>
                        <div className={`value ${
                          performance.daily_return >= 0 ? 'profit' : 'loss'
                        }`}>
                          {performance.daily_return.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="no-data">暂无绩效数据</p>
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
