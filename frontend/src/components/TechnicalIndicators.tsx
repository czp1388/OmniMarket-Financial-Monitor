import React, { useState, useEffect } from 'react';

interface IndicatorData {
  symbol: string;
  rsi: number;
  macd: number;
  macdSignal: number;
  macdHistogram: number;
  bollingerUpper: number;
  bollingerLower: number;
  bollingerMiddle: number;
  timestamp: string;
}

const TechnicalIndicators: React.FC = () => {
  const [indicators, setIndicators] = useState<IndicatorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIndicators = async () => {
      try {
        // 模拟技术指标数据
        const mockData: IndicatorData[] = [
          {
            symbol: 'BTC/USDT',
            rsi: 65.2,
            macd: 12.5,
            macdSignal: 10.2,
            macdHistogram: 2.3,
            bollingerUpper: 36000,
            bollingerLower: 34000,
            bollingerMiddle: 35000,
            timestamp: new Date().toISOString()
          },
          {
            symbol: 'ETH/USDT',
            rsi: 45.8,
            macd: -5.2,
            macdSignal: -3.8,
            macdHistogram: -1.4,
            bollingerUpper: 1850,
            bollingerLower: 1750,
            bollingerMiddle: 1800,
            timestamp: new Date().toISOString()
          },
          {
            symbol: 'AAPL',
            rsi: 58.7,
            macd: 1.2,
            macdSignal: 0.8,
            macdHistogram: 0.4,
            bollingerUpper: 155,
            bollingerLower: 145,
            bollingerMiddle: 150,
            timestamp: new Date().toISOString()
          }
        ];
        
        setIndicators(mockData);
        setLoading(false);
      } catch (err) {
        setError('获取技术指标失败');
        setLoading(false);
      }
    };

    fetchIndicators();
    
    // 每10秒更新一次数据
    const interval = setInterval(fetchIndicators, 10000);
    return () => clearInterval(interval);
  }, []);

  const getRSIColor = (rsi: number) => {
    if (rsi > 70) return 'text-red-600'; // 超买
    if (rsi < 30) return 'text-green-600'; // 超卖
    return 'text-gray-600';
  };

  const getMACDColor = (macd: number, signal: number) => {
    return macd > signal ? 'text-green-600' : 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2">加载技术指标...</span>
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
        <h2 className="text-lg font-semibold text-gray-800">技术指标</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                交易对
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                RSI
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                MACD
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                信号线
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                柱状图
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                布林带
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {indicators.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {item.symbol}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getRSIColor(item.rsi)}`}>
                  {item.rsi.toFixed(1)}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getMACDColor(item.macd, item.macdSignal)}`}>
                  {item.macd.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {item.macdSignal.toFixed(2)}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                  item.macdHistogram >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {item.macdHistogram.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {item.bollingerLower.toFixed(0)} - {item.bollingerUpper.toFixed(0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="bg-gray-50 px-6 py-3 border-t">
        <div className="text-xs text-gray-500">
          <span className="inline-block w-3 h-3 bg-red-100 border border-red-300 mr-1"></span>
          {'RSI > 70: 超买 |'}
          <span className="inline-block w-3 h-3 bg-green-100 border border-green-300 mx-1"></span>
          {'RSI < 30: 超卖 |'}
          <span className="text-green-600 ml-1">{'MACD > 信号线: 看涨 |'}</span>
          <span className="text-red-600 ml-1">{'MACD < 信号线: 看跌'}</span>
        </div>
      </div>
    </div>
  );
};

export default TechnicalIndicators;
