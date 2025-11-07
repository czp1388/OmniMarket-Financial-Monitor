import React, { useState, useEffect } from 'react';

interface Alert {
  id: string;
  symbol: string;
  condition: string;
  value: number;
  currentValue: number;
  isActive: boolean;
  createdAt: string;
  triggeredAt?: string;
}

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [newAlert, setNewAlert] = useState({
    symbol: 'BTC/USDT',
    condition: 'price_above',
    value: 0
  });

  useEffect(() => {
    // 模拟预警数据
    const mockAlerts: Alert[] = [
      {
        id: '1',
        symbol: 'BTC/USDT',
        condition: 'price_above',
        value: 35000,
        currentValue: 34850,
        isActive: true,
        createdAt: new Date().toISOString()
      },
      {
        id: '2',
        symbol: 'ETH/USDT',
        condition: 'rsi_below',
        value: 30,
        currentValue: 45.8,
        isActive: true,
        createdAt: new Date().toISOString()
      },
      {
        id: '3',
        symbol: 'AAPL',
        condition: 'price_below',
        value: 150,
        currentValue: 152.3,
        isActive: false,
        createdAt: new Date().toISOString(),
        triggeredAt: new Date().toISOString()
      }
    ];
    
    setAlerts(mockAlerts);
    setLoading(false);
  }, []);

  const handleCreateAlert = () => {
    const alert: Alert = {
      id: Date.now().toString(),
      symbol: newAlert.symbol,
      condition: newAlert.condition,
      value: newAlert.value,
      currentValue: 0, // 这应该从实时数据获取
      isActive: true,
      createdAt: new Date().toISOString()
    };
    
    setAlerts([...alerts, alert]);
    setNewAlert({ symbol: 'BTC/USDT', condition: 'price_above', value: 0 });
  };

  const toggleAlert = (id: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, isActive: !alert.isActive } : alert
    ));
  };

  const deleteAlert = (id: string) => {
    setAlerts(alerts.filter(alert => alert.id !== id));
  };

  const getConditionText = (condition: string) => {
    const conditions: { [key: string]: string } = {
      'price_above': '价格高于',
      'price_below': '价格低于',
      'rsi_above': 'RSI高于',
      'rsi_below': 'RSI低于',
      'volume_above': '成交量高于'
    };
    return conditions[condition] || condition;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2">加载预警数据...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">预警管理</h1>
        <p className="text-gray-600">创建和管理您的市场预警条件</p>
      </div>

      {/* 创建新预警 */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">创建新预警</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              交易对
            </label>
            <select
              value={newAlert.symbol}
              onChange={(e) => setNewAlert({...newAlert, symbol: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="AAPL">AAPL</option>
              <option value="TSLA">TSLA</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              预警条件
            </label>
            <select
              value={newAlert.condition}
              onChange={(e) => setNewAlert({...newAlert, condition: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="price_above">价格高于</option>
              <option value="price_below">价格低于</option>
              <option value="rsi_above">RSI高于</option>
              <option value="rsi_below">RSI低于</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              阈值
            </label>
            <input
              type="number"
              value={newAlert.value}
              onChange={(e) => setNewAlert({...newAlert, value: parseFloat(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入阈值"
            />
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handleCreateAlert}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition duration-200"
            >
              创建预警
            </button>
          </div>
        </div>
      </div>

      {/* 预警列表 */}
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-800">预警列表</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  交易对
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  预警条件
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  阈值
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  当前值
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {alert.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {getConditionText(alert.condition)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {alert.value}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {alert.currentValue}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      alert.isActive 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {alert.isActive ? '活跃' : '已触发'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => toggleAlert(alert.id)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      {alert.isActive ? '禁用' : '启用'}
                    </button>
                    <button
                      onClick={() => deleteAlert(alert.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AlertsPage;
