import React, { useState } from 'react';

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    // 数据源设置
    dataSources: {
      crypto: true,
      stocks: true,
      forex: false,
      futures: false
    },
    // 通知设置
    notifications: {
      email: true,
      push: true,
      sound: false,
      telegram: false
    },
    // 图表设置
    chart: {
      theme: 'light',
      timezone: 'Asia/Shanghai',
      defaultTimeframe: '1h'
    },
    // 风险设置
    risk: {
      maxDrawdown: 10,
      maxPositionSize: 25,
      stopLossEnabled: true
    }
  });

  const handleDataSourceChange = (source: string, value: boolean) => {
    setSettings({
      ...settings,
      dataSources: {
        ...settings.dataSources,
        [source]: value
      }
    });
  };

  const handleNotificationChange = (type: string, value: boolean) => {
    setSettings({
      ...settings,
      notifications: {
        ...settings.notifications,
        [type]: value
      }
    });
  };

  const handleChartSettingChange = (setting: string, value: string) => {
    setSettings({
      ...settings,
      chart: {
        ...settings.chart,
        [setting]: value
      }
    });
  };

  const handleRiskSettingChange = (setting: string, value: number | boolean) => {
    setSettings({
      ...settings,
      risk: {
        ...settings.risk,
        [setting]: value
      }
    });
  };

  const saveSettings = () => {
    // 这里应该调用API保存设置
    console.log('保存设置:', settings);
    alert('设置已保存！');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">系统设置</h1>
        <p className="text-gray-600">配置您的监控系统偏好</p>
      </div>

      <div className="space-y-8">
        {/* 数据源设置 */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">数据源设置</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="crypto"
                checked={settings.dataSources.crypto}
                onChange={(e) => handleDataSourceChange('crypto', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="crypto" className="ml-2 block text-sm text-gray-900">
                加密货币数据
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="stocks"
                checked={settings.dataSources.stocks}
                onChange={(e) => handleDataSourceChange('stocks', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="stocks" className="ml-2 block text-sm text-gray-900">
                股票数据
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="forex"
                checked={settings.dataSources.forex}
                onChange={(e) => handleDataSourceChange('forex', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="forex" className="ml-2 block text-sm text-gray-900">
                外汇数据
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="futures"
                checked={settings.dataSources.futures}
                onChange={(e) => handleDataSourceChange('futures', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="futures" className="ml-2 block text-sm text-gray-900">
                期货数据
              </label>
            </div>
          </div>
        </div>

        {/* 通知设置 */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">通知设置</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="email"
                checked={settings.notifications.email}
                onChange={(e) => handleNotificationChange('email', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="email" className="ml-2 block text-sm text-gray-900">
                邮件通知
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="push"
                checked={settings.notifications.push}
                onChange={(e) => handleNotificationChange('push', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="push" className="ml-2 block text-sm text-gray-900">
                推送通知
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="sound"
                checked={settings.notifications.sound}
                onChange={(e) => handleNotificationChange('sound', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="sound" className="ml-2 block text-sm text-gray-900">
                声音提示
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="telegram"
                checked={settings.notifications.telegram}
                onChange={(e) => handleNotificationChange('telegram', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="telegram" className="ml-2 block text-sm text-gray-900">
                Telegram通知
              </label>
            </div>
          </div>
        </div>

        {/* 图表设置 */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">图表设置</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-2">
                主题
              </label>
              <select
                id="theme"
                value={settings.chart.theme}
                onChange={(e) => handleChartSettingChange('theme', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="light">浅色</option>
                <option value="dark">深色</option>
              </select>
            </div>
            <div>
              <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-2">
                时区
              </label>
              <select
                id="timezone"
                value={settings.chart.timezone}
                onChange={(e) => handleChartSettingChange('timezone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Asia/Shanghai">北京时间</option>
                <option value="America/New_York">纽约时间</option>
                <option value="Europe/London">伦敦时间</option>
                <option value="UTC">UTC</option>
              </select>
            </div>
            <div>
              <label htmlFor="timeframe" className="block text-sm font-medium text-gray-700 mb-2">
                默认时间周期
              </label>
              <select
                id="timeframe"
                value={settings.chart.defaultTimeframe}
                onChange={(e) => handleChartSettingChange('defaultTimeframe', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="1m">1分钟</option>
                <option value="5m">5分钟</option>
                <option value="15m">15分钟</option>
                <option value="1h">1小时</option>
                <option value="4h">4小时</option>
                <option value="1d">日线</option>
              </select>
            </div>
          </div>
        </div>

        {/* 风险管理设置 */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">风险管理设置</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="maxDrawdown" className="block text-sm font-medium text-gray-700 mb-2">
                最大回撤 (%) 
              </label>
              <input
                type="number"
                id="maxDrawdown"
                value={settings.risk.maxDrawdown}
                onChange={(e) => handleRiskSettingChange('maxDrawdown', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                max="100"
              />
            </div>
            <div>
              <label htmlFor="maxPositionSize" className="block text-sm font-medium text-gray-700 mb-2">
                最大仓位规模 (%)
              </label>
              <input
                type="number"
                id="maxPositionSize"
                value={settings.risk.maxPositionSize}
                onChange={(e) => handleRiskSettingChange('maxPositionSize', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                max="100"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="stopLossEnabled"
                checked={settings.risk.stopLossEnabled}
                onChange={(e) => handleRiskSettingChange('stopLossEnabled', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="stopLossEnabled" className="ml-2 block text-sm text-gray-900">
                启用止损
              </label>
            </div>
          </div>
        </div>

        {/* API 配置 */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">API 配置</h2>
          <div className="space-y-4">
            <div>
              <label htmlFor="binanceApi" className="block text-sm font-medium text-gray-700 mb-2">
                Binance API Key
              </label>
              <input
                type="password"
                id="binanceApi"
                placeholder="输入您的Binance API Key"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="telegramBot" className="block text-sm font-medium text-gray-700 mb-2">
                Telegram Bot Token
              </label>
              <input
                type="password"
                id="telegramBot"
                placeholder="输入您的Telegram Bot Token"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 保存按钮 */}
        <div className="flex justify-end">
          <button
            onClick={saveSettings}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md transition duration-200"
          >
            保存设置
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
