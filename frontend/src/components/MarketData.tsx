import React, { useState, useEffect } from 'react';

interface MarketDataItem {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: string;
}

const MarketData: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketDataItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        // 这里暂时使用模拟数据，后续会连接到真实API
        const mockData: MarketDataItem[] = [
          {
            symbol: 'BTC/USDT',
            price: 35000,
            change: 500,
            changePercent: 1.45,
            volume: 25000000,
            timestamp: new Date().toISOString()
          },
          {
            symbol: 'ETH/USDT',
            price: 1800,
            change: -20,
            changePercent: -1.10,
            volume: 12000000,
            timestamp: new Date().toISOString()
          },
          {
            symbol: 'AAPL',
            price: 150.25,
            change: 2.75,
            changePercent: 1.86,
            volume: 5000000,
            timestamp: new Date().toISOString()
          }
        ];
        
        setMarketData(mockData);
        setLoading(false);
      } catch (err) {
        setError('获取市场数据失败');
        setLoading(false);
      }
    };

    fetchMarketData();
    
    // 每5秒更新一次数据
    const interval = setInterval(fetchMarketData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2">加载市场数据...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-6 py-4 border-b">
        <h2 className="text-lg font-semibold text-gray-800">实时市场数据</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                交易对
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                价格
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                涨跌
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                涨跌幅
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                成交量
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {marketData.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {item.symbol}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${item.price.toLocaleString()}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                  item.change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {item.change >= 0 ? '+' : ''}{item.change}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                  item.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {item.changePercent >= 0 ? '+' : ''}{item.changePercent}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {item.volume.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MarketData;
