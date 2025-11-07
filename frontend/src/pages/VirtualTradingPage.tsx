import React, { useState, useEffect } from 'react';
import { ApiService } from '../services/api';

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
  const [accounts, setAccounts] = useState<VirtualAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<VirtualAccount | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

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

  useEffect(() => {
    loadAccounts();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">虚拟交易系统</h1>

      {/* 账户管理 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">账户管理</h2>
        
        {/* 创建新账户 */}
        <div className="mb-6 p-4 border rounded-lg">
          <h3 className="text-lg font-medium mb-3">创建新账户</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="账户名称"
              value={newAccountForm.name}
              onChange={(e) => setNewAccountForm({...newAccountForm, name: e.target.value})}
              className="px-3 py-2 border rounded-md"
            />
            <input
              type="number"
              placeholder="初始资金"
              value={newAccountForm.initial_balance}
              onChange={(e) => setNewAccountForm({...newAccountForm, initial_balance: Number(e.target.value)})}
              className="px-3 py-2 border rounded-md"
            />
            <select
              value={newAccountForm.currency}
              onChange={(e) => setNewAccountForm({...newAccountForm, currency: e.target.value})}
              className="px-3 py-2 border rounded-md"
            >
              <option value="USD">USD</option>
              <option value="CNY">CNY</option>
              <option value="HKD">HKD</option>
            </select>
            <button
              onClick={createAccount}
              disabled={!newAccountForm.name}
              className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400"
            >
              创建账户
            </button>
          </div>
        </div>

        {/* 账户列表 */}
        <div>
          <h3 className="text-lg font-medium mb-3">账户列表</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {accounts.map(account => (
              <div
                key={account.id}
                className={`border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow ${
                  selectedAccount?.id === account.id ? 'border-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => loadAccountDetails(account.id)}
              >
                <div className="font-semibold">{account.name}</div>
                <div className="text-sm text-gray-600">余额: ${account.current_balance.toLocaleString()}</div>
                <div className="text-sm text-gray-600">初始: ${account.initial_balance.toLocaleString()}</div>
                <div className="text-sm text-gray-600">货币: {account.currency}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 选中的账户详情 */}
      {selectedAccount && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">{selectedAccount.name} - 交易面板</h2>
            <div className="text-right">
              <div className="text-lg font-bold">${selectedAccount.current_balance.toLocaleString()}</div>
              <div className={`text-sm ${
                selectedAccount.current_balance >= selectedAccount.initial_balance ? 'text-green-600' : 'text-red-600'
              }`}>
                收益: ${(selectedAccount.current_balance - selectedAccount.initial_balance).toLocaleString()}
              </div>
            </div>
          </div>

          {/* 选项卡 */}
          <div className="border-b mb-4">
            <nav className="flex space-x-8">
              {['overview', 'trading', 'positions', 'orders', 'performance'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
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

          {/* 概览选项卡 */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* 账户概览 */}
              <div className="col-span-1">
                <h3 className="text-lg font-medium mb-3">账户概览</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>当前余额:</span>
                    <span className="font-semibold">${selectedAccount.current_balance.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>初始资金:</span>
                    <span>${selectedAccount.initial_balance.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>总收益:</span>
                    <span className={selectedAccount.current_balance >= selectedAccount.initial_balance ? 'text-green-600' : 'text-red-600'}>
                      ${(selectedAccount.current_balance - selectedAccount.initial_balance).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>收益率:</span>
                    <span className={selectedAccount.current_balance >= selectedAccount.initial_balance ? 'text-green-600' : 'text-red-600'}>
                      {((selectedAccount.current_balance - selectedAccount.initial_balance) / selectedAccount.initial_balance * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* 持仓概览 */}
              <div className="col-span-1">
                <h3 className="text-lg font-medium mb-3">持仓概览</h3>
                {positions.length === 0 ? (
                  <p className="text-gray-500">暂无持仓</p>
                ) : (
                  <div className="space-y-2">
                    {positions.slice(0, 3).map(position => (
                      <div key={position.symbol} className="flex justify-between text-sm">
                        <span>{position.symbol}</span>
                        <span>{position.quantity} 股</span>
                        <span className={position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                          ${position.unrealized_pnl.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 绩效概览 */}
              <div className="col-span-1">
                <h3 className="text-lg font-medium mb-3">绩效概览</h3>
                {performance ? (
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>夏普比率:</span>
                      <span>{performance.sharpe_ratio.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>最大回撤:</span>
                      <span className="text-red-600">{performance.max_drawdown.toFixed(2)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>胜率:</span>
                      <span className="text-green-600">{performance.win_rate.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>总交易:</span>
                      <span>{performance.total_trades}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">暂无绩效数据</p>
                )}
              </div>
            </div>
          )}

          {/* 交易选项卡 */}
          {activeTab === 'trading' && (
            <div className="max-w-md">
              <h3 className="text-lg font-medium mb-4">下单交易</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">交易标的</label>
                  <input
                    type="text"
                    placeholder="例如: AAPL, TSLA"
                    value={orderForm.symbol}
                    onChange={(e) => setOrderForm({...orderForm, symbol: e.target.value.toUpperCase()})}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">方向</label>
                    <select
                      value={orderForm.side}
                      onChange={(e) => setOrderForm({...orderForm, side: e.target.value as 'buy' | 'sell'})}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      <option value="buy">买入</option>
                      <option value="sell">卖出</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">类型</label>
                    <select
                      value={orderForm.type}
                      onChange={(e) => setOrderForm({...orderForm, type: e.target.value as 'market' | 'limit'})}
                      className="w-full px-3 py-2 border rounded-md"
                    >
                      <option value="market">市价单</option>
                      <option value="limit">限价单</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">数量</label>
                  <input
                    type="number"
                    value={orderForm.quantity}
                    onChange={(e) => setOrderForm({...orderForm, quantity: Number(e.target.value)})}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>

                {orderForm.type === 'limit' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">价格</label>
                    <input
                      type="number"
                      step="0.01"
                      value={orderForm.price}
                      onChange={(e) => setOrderForm({...orderForm, price: Number(e.target.value)})}
                      className="w-full px-3 py-2 border rounded-md"
                    />
                  </div>
                )}

                <button
                  onClick={placeOrder}
                  disabled={!orderForm.symbol || orderForm.quantity <= 0 || (orderForm.type === 'limit' && orderForm.price <= 0)}
                  className={`w-full px-4 py-2 rounded-md font-medium ${
                    orderForm.side === 'buy' 
                      ? 'bg-green-500 text-white hover:bg-green-600' 
                      : 'bg-red-500 text-white hover:bg-red-600'
                  } disabled:bg-gray-400`}
                >
                  {orderForm.side === 'buy' ? '买入' : '卖出'} {orderForm.symbol}
                </button>
              </div>
            </div>
          )}

          {/* 持仓选项卡 */}
          {activeTab === 'positions' && (
            <div>
              <h3 className="text-lg font-medium mb-4">当前持仓</h3>
              {positions.length === 0 ? (
                <p className="text-gray-500">暂无持仓</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">标的</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数量</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">平均成本</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">当前价格</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">市值</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">未实现盈亏</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {positions.map(position => (
                        <tr key={position.symbol}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{position.symbol}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{position.quantity}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${position.average_price.toFixed(2)}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${position.current_price.toFixed(2)}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${position.market_value.toFixed(2)}</td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
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
              <h3 className="text-lg font-medium mb-4">订单历史</h3>
              {orders.length === 0 ? (
                <p className="text-gray-500">暂无订单</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">订单ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">标的</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">方向</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数量</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">价格</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {orders.map(order => (
                        <tr key={order.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.id.slice(0, 8)}...</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.symbol}</td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            order.side === 'buy' ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {order.side === 'buy' ? '买入' : '卖出'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {order.type === 'market' ? '市价' : '限价'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.quantity}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {order.price ? `$${order.price}` : '市价'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              order.status === 'filled' ? 'bg-green-100 text-green-800' :
                              order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              order.status === 'cancelled' ? 'bg-gray-100 text-gray-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {order.status === 'filled' ? '已成交' :
                               order.status === 'pending' ? '待成交' :
                               order.status === 'cancelled' ? '已取消' : '已拒绝'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(order.created_at).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            {order.status === 'pending' && (
                              <button
                                onClick={() => cancelOrder(order.id)}
                                className="text-red-600 hover:text-red-900"
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
              <h3 className="text-lg font-medium mb-4">绩效分析</h3>
              {performance ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">总收益率</div>
                    <div className={`text-2xl font-bold ${
                      performance.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {performance.total_return.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">夏普比率</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {performance.sharpe_ratio.toFixed(2)}
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">最大回撤</div>
                    <div className="text-2xl font-bold text-red-600">
                      {performance.max_drawdown.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">胜率</div>
                    <div className="text-2xl font-bold text-green-600">
                      {performance.win_rate.toFixed(1)}%
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">总交易数</div>
                    <div className="text-2xl font-bold text-gray-800">
                      {performance.total_trades}
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">盈利交易</div>
                    <div className="text-2xl font-bold text-green-600">
                      {performance.profitable_trades}
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">日收益率</div>
                    <div className={`text-2xl font-bold ${
                      performance.daily_return >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {performance.daily_return.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">暂无绩效数据</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VirtualTradingPage;
