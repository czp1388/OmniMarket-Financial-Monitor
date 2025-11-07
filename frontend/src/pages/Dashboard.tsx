import React from 'react';
import MarketData from '../components/MarketData';
import TechnicalIndicators from '../components/TechnicalIndicators';
import AlertManager from '../components/AlertManager';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* 欢迎卡片 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          欢迎使用 OmniMarket
        </h1>
        <p className="text-gray-600">
          寰宇多市场金融监控系统 - 实时监控全球金融市场
        </p>
      </div>

      {/* 市场概览 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">监控品种</p>
              <p className="text-2xl font-bold text-gray-800">24</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <span className="text-blue-600 text-xl">📊</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">活跃预警</p>
              <p className="text-2xl font-bold text-gray-800">8</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-green-600 text-xl">🔔</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">今日触发</p>
              <p className="text-2xl font-bold text-gray-800">3</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-yellow-600 text-xl">⚠️</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">系统状态</p>
              <p className="text-2xl font-bold text-green-600">正常</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-green-600 text-xl">✅</span>
            </div>
          </div>
        </div>
      </div>

      {/* 实时市场数据 */}
      <MarketData />

      {/* 技术指标 */}
      <TechnicalIndicators />

      {/* 快速操作 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">图表分析</h3>
          <p className="text-gray-600 mb-4">查看详细的技术图表和指标分析</p>
          <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
            进入图表
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">预警管理</h3>
          <p className="text-gray-600 mb-4">设置和管理价格预警条件</p>
          <button className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
            管理预警
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">投资组合</h3>
          <p className="text-gray-600 mb-4">查看您的资产配置和盈亏情况</p>
          <button className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors">
            查看组合
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
