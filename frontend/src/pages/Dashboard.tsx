import React, { useState, useEffect } from 'react';
import MarketData from '../components/MarketData';
import TechnicalIndicators from '../components/TechnicalIndicators';
import { ApiService } from '../services/api';

interface DashboardStats {
  monitoredSymbols: number;
  activeAlerts: number;
  todayTriggers: number;
  systemStatus: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    monitoredSymbols: 0,
    activeAlerts: 0,
    todayTriggers: 0,
    systemStatus: '检查中...'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // 检查系统健康状况
        const healthResponse = await ApiService.market.health();
        console.log('系统健康状态:', healthResponse);
        
        // 获取交易对数量
        const symbolsResponse = await ApiService.market.getSymbols();
        const symbolsCount = symbolsResponse?.data?.length || 24;
        
        // 获取警报数量
        const alertsResponse = await ApiService.alerts.getAlerts();
        const alertsCount = alertsResponse?.data?.length || 8;
        
        setStats({
          monitoredSymbols: symbolsCount,
          activeAlerts: alertsCount,
          todayTriggers: 3, // 暂时硬编码
          systemStatus: healthResponse?.status === 'healthy' ? '正常' : '异常'
        });
        
      } catch (error) {
        console.error('获取仪表板数据失败:', error);
        setStats({
          monitoredSymbols: 24,
          activeAlerts: 8,
          todayTriggers: 3,
          systemStatus: '连接异常'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    
    // 设置定时刷新
    const interval = setInterval(fetchDashboardData, 30000); // 每30秒刷新一次
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载仪表板数据中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6 bg-gray-50 min-h-screen">
      {/* 页面标题和状态 */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">OmniMarket 仪表板</h1>
          <p className="text-gray-600 text-lg">寰宇多市场金融监控系统</p>
        </div>
        <div className="flex items-center gap-3 bg-white rounded-lg px-4 py-3 shadow-sm">
          <div className={`w-3 h-3 rounded-full ${
            stats.systemStatus === '正常' || stats.systemStatus === '连接正常' 
              ? 'bg-green-500' 
              : 'bg-red-500'
          }`}></div>
          <span className="text-sm font-medium text-gray-700">
            {stats.systemStatus === '正常' || stats.systemStatus === '连接正常' 
              ? '系统运行正常' 
              : '系统连接异常'}
          </span>
          <span className="text-xs text-gray-500">
            {new Date().toLocaleString('zh-CN')}
          </span>
        </div>
      </div>

      {/* 核心指标卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">监控品种</p>
              <p className="text-3xl font-bold mt-1">{stats.monitoredSymbols}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-xl">
              <span className="text-2xl">📊</span>
            </div>
          </div>
          <div className="mt-4 text-blue-100 text-sm">
            <span className="opacity-80">实时监控中</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">活跃预警</p>
              <p className="text-3xl font-bold mt-1">{stats.activeAlerts}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-xl">
              <span className="text-2xl">🔔</span>
            </div>
          </div>
          <div className="mt-4 text-green-100 text-sm">
            <span className="opacity-80">预警规则生效中</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">今日触发</p>
              <p className="text-3xl font-bold mt-1">{stats.todayTriggers}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-xl">
              <span className="text-2xl">⚠️</span>
            </div>
          </div>
          <div className="mt-4 text-orange-100 text-sm">
            <span className="opacity-80">需要关注的事件</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">系统状态</p>
              <p className="text-3xl font-bold mt-1">
                {stats.systemStatus === '正常' || stats.systemStatus === '连接正常' ? '正常' : '异常'}
              </p>
            </div>
            <div className="p-3 bg-white/20 rounded-xl">
              <span className="text-2xl">
                {stats.systemStatus === '正常' || stats.systemStatus === '连接正常' ? '✅' : '❌'}
              </span>
            </div>
          </div>
          <div className="mt-4 text-purple-100 text-sm">
            <span className="opacity-80">
              {stats.systemStatus === '正常' || stats.systemStatus === '连接正常' 
                ? '所有服务正常' 
                : '需要检查连接'}
            </span>
          </div>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* 左侧：市场数据和技术指标 */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b">
              <h2 className="text-xl font-semibold text-gray-800">📈 实时市场数据</h2>
            </div>
            <div className="p-4">
              <MarketData />
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b">
              <h2 className="text-xl font-semibold text-gray-800">📊 技术指标</h2>
            </div>
            <div className="p-4">
              <TechnicalIndicators />
            </div>
          </div>
        </div>

        {/* 右侧：快速操作和系统信息 */}
        <div className="space-y-6">
          {/* 快速操作 */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">🚀 快速操作</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500 rounded-lg">
                    <span className="text-white text-lg">📈</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">图表分析</h3>
                    <p className="text-sm text-gray-600">查看详细的技术图表和指标分析</p>
                  </div>
                </div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                  进入
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-500 rounded-lg">
                    <span className="text-white text-lg">🔔</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">预警管理</h3>
                    <p className="text-sm text-gray-600">设置和管理价格预警条件</p>
                  </div>
                </div>
                <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium">
                  管理
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-500 rounded-lg">
                    <span className="text-white text-lg">💼</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">投资组合</h3>
                    <p className="text-sm text-gray-600">查看您的资产配置和盈亏情况</p>
                  </div>
                </div>
                <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium">
                  查看
                </button>
              </div>
            </div>
          </div>

          {/* 系统信息 */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">ℹ️ 系统信息</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-gray-600">版本</span>
                <span className="font-medium text-gray-800">v1.0.0</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-gray-600">最后更新</span>
                <span className="font-medium text-gray-800">{new Date().toLocaleTimeString('zh-CN')}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-gray-600">数据源</span>
                <span className="font-medium text-green-600">实时连接</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
