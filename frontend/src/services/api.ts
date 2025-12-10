import axios from 'axios';

// API基础配置
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 3000,  // 3秒超时，快速降级
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API服务类
export class ApiService {
  // 市场数据API
  static market = {
    // 健康检查
    health: () => apiClient.get('/market/health'),
    
    // 获取支持的交易所
    getExchanges: () => apiClient.get('/market/exchanges'),
    
    // 获取交易对列表
    getSymbols: (marketType?: string, exchange?: string) => 
      apiClient.get('/market/symbols', { params: { market_type: marketType, exchange } }),
    
    // 获取行情数据
    getTickers: (symbols?: string[], marketType?: string, exchange?: string) =>
      apiClient.get('/market/tickers', { params: { symbols, market_type: marketType, exchange } }),
    
    // 获取K线数据
    getKlines: (
      symbol: string,
      marketType: string,
      exchange: string,
      timeframe: string,
      startTime?: string,
      endTime?: string,
      limit: number = 1000
    ) =>
      apiClient.get('/market/klines', {
        params: {
          symbol,
          market_type: marketType,
          exchange,
          timeframe,
          start_time: startTime,
          end_time: endTime,
          limit,
        },
      }),
    
    // 获取历史数据
    getHistoricalData: (
      symbol: string,
      marketType: string,
      exchange: string,
      timeframe: string,
      days: number = 30
    ) =>
      apiClient.get(`/market/historical/${symbol}`, {
        params: {
          market_type: marketType,
          exchange,
          timeframe,
          days,
        },
      }),
  };

  // 技术指标API
  static technical = {
    // 健康检查
    health: () => apiClient.get('/technical/health'),
    
    // 计算技术指标
    calculateIndicators: (data: any, indicators: string[]) =>
      apiClient.post('/technical/calculate', { data, indicators }),
  };

  // 警报API
  static alerts = {
    // 健康检查
    health: () => apiClient.get('/alerts/health'),
    
    // 获取警报列表
    getAlerts: () => apiClient.get('/alerts'),
    
    // 创建警报
    createAlert: (alertData: any) => apiClient.post('/alerts', alertData),
    
    // 更新警报
    updateAlert: (id: string, alertData: any) => apiClient.put(`/alerts/${id}`, alertData),
    
    // 删除警报
    deleteAlert: (id: string) => apiClient.delete(`/alerts/${id}`),
  };

  // 用户API
  static users = {
    // 健康检查
    health: () => apiClient.get('/users/health'),
    
    // 获取用户信息
    getProfile: () => apiClient.get('/users/profile'),
    
    // 更新用户信息
    updateProfile: (userData: any) => apiClient.put('/users/profile', userData),
  };

  // 虚拟交易API
  static virtual = {
    // 健康检查
    health: () => apiClient.get('/virtual/health'),
    
    // 创建虚拟账户
    createAccount: (accountData: any) => apiClient.post('/virtual/accounts', accountData),
    
    // 获取虚拟账户列表
    getAccounts: () => apiClient.get('/virtual/accounts'),
    
    // 获取虚拟账户详情
    getAccount: (accountId: string) => apiClient.get(`/virtual/accounts/${accountId}`),
    
    // 下单交易
    placeOrder: (orderData: any) => apiClient.post('/virtual/orders', orderData),
    
    // 获取订单历史
    getOrderHistory: (accountId: string, limit?: number) => 
      apiClient.get(`/virtual/orders/${accountId}`, { params: { limit } }),
    
    // 取消订单
    cancelOrder: (orderId: string) => apiClient.delete(`/virtual/orders/${orderId}`),
    
    // 获取绩效分析
    getPerformance: (accountId: string) => apiClient.get(`/virtual/performance/${accountId}`),
    
    // 更新市场价格
    updateMarketPrices: () => apiClient.post('/virtual/market/update'),
  };

  // 全自动交易API
  static autoTrading = {
    // 健康检查
    health: () => apiClient.get('/auto-trading/health'),
    
    // 获取可用交易策略
    getStrategies: () => apiClient.get('/auto-trading/strategies'),
    
    // 获取交易状态
    getStatus: () => apiClient.get('/auto-trading/status'),
    
    // 获取交易绩效
    getPerformance: () => apiClient.get('/auto-trading/performance'),
    
    // 获取风险指标
    getRiskMetrics: () => apiClient.get('/auto-trading/risk-metrics'),
    
    // 获取交易日志
    getTradeLogs: () => apiClient.get('/auto-trading/trade-logs'),
    
    // 获取交易历史
    getTradingHistory: () => apiClient.get('/auto-trading/trading-history'),
    
    // 启动交易
    start: (strategies: string[], config?: any) => 
      apiClient.post('/auto-trading/start', { strategies, config }),
    
    // 停止交易
    stop: () => apiClient.post('/auto-trading/stop'),
    
    // 暂停交易
    pause: () => apiClient.post('/auto-trading/pause'),
    
    // 恢复交易
    resume: () => apiClient.post('/auto-trading/resume'),
    
    // 紧急停止
    emergencyStop: () => apiClient.post('/auto-trading/emergency-stop'),
    
    // 重置熔断
    resetBrakes: () => apiClient.post('/auto-trading/reset-brakes'),
    
    // 配置交易参数
    configure: (config: any) => apiClient.post('/auto-trading/configure', config),
  };

  // 牛熊证监控API
  static warrants = {
    // 获取所有牛熊证
    getAllWarrants: () => apiClient.get('/warrants-monitoring/warrants'),
    
    // 获取指定牛熊证
    getWarrant: (warrantCode: string) => apiClient.get(`/warrants-monitoring/warrants/${warrantCode}`),
    
    // 获取活跃预警
    getActiveAlerts: () => apiClient.get('/warrants-monitoring/alerts'),
    
    // 确认预警
    acknowledgeAlert: (warrantCode: string) => apiClient.post(`/warrants-monitoring/alerts/${warrantCode}/acknowledge`),
    
    // 获取牛熊证指标
    getWarrantMetrics: (warrantCode: string) => apiClient.get(`/warrants-monitoring/metrics/${warrantCode}`),
    
    // 启动监控
    startMonitoring: () => apiClient.post('/warrants-monitoring/monitoring/start'),
    
    // 停止监控
    stopMonitoring: () => apiClient.post('/warrants-monitoring/monitoring/stop'),
    
    // 获取监控状态
    getMonitoringStatus: () => apiClient.get('/warrants-monitoring/status'),
    
    // 获取示例数据
    getSampleWarrants: () => apiClient.get('/warrants-monitoring/sample-warrants'),
  };

  // 牛熊证分析API
  static warrantsAnalysis = {
    // 分析单只牛熊证
    analyzeSingle: (warrantData: any, underlyingData: any[], marketConditions?: any) =>
      apiClient.post('/warrants-analysis/analyze-single', {
        warrant_data: warrantData,
        underlying_data: underlyingData,
        market_conditions: marketConditions
      }),
    
    // 批量分析牛熊证
    analyzeBatch: (warrantsData: any[], underlyingDataDict: any) =>
      apiClient.post('/warrants-analysis/analyze-batch', {
        warrants_data: warrantsData,
        underlying_data_dict: underlyingDataDict
      }),
    
    // 策略回测
    backtestStrategy: (strategyType: string, historicalData: any, initialCapital?: number) =>
      apiClient.post('/warrants-analysis/backtest', {
        strategy_type: strategyType,
        historical_data: historicalData,
        initial_capital: initialCapital
      }),
    
    // 风险评估
    assessRisk: (distanceToKnockOut: number, probabilityKnockOut: number, effectiveLeverage: number) =>
      apiClient.get('/warrants-analysis/risk-assessment', {
        params: {
          distance_to_knock_out: distanceToKnockOut,
          probability_knock_out: probabilityKnockOut,
          effective_leverage: effectiveLeverage
        }
      }),
    
    // 计算安全边际
    calculateSafetyMargin: (distanceToKnockOut: number, probabilityKnockOut: number, effectiveLeverage: number) =>
      apiClient.get('/warrants-analysis/safety-margin', {
        params: {
          distance_to_knock_out: distanceToKnockOut,
          probability_knock_out: probabilityKnockOut,
          effective_leverage: effectiveLeverage
        }
      }),
    
    // 生成交易信号
    generateTradingSignal: (warrantData: any, underlyingData: any[]) =>
      apiClient.post('/warrants-analysis/trading-signal', {
        warrant_data: warrantData,
        underlying_data: underlyingData
      }),
    
    // 获取示例数据
    getSampleData: () => apiClient.get('/warrants-analysis/sample-data'),
  };

  // LEAN引擎API
  static lean = {
    // 健康检查
    health: () => apiClient.get('/lean/health'),
    
    // 启动回测
    startBacktest: (request: any) => apiClient.post('/lean/backtest/start', request),
    
    // 获取回测状态
    getBacktestStatus: (backtestId: string) => apiClient.get(`/lean/backtest/status/${backtestId}`),
    
    // 获取回测列表
    listBacktests: (strategyId?: string) => 
      apiClient.get('/lean/backtest/list', { params: { strategy_id: strategyId } }),
    
    // 取消回测
    cancelBacktest: (backtestId: string) => apiClient.post(`/lean/backtest/cancel/${backtestId}`),
    
    // 获取策略模板
    getStrategyTemplates: () => apiClient.get('/lean/strategies/templates'),
    
    // 从模板生成策略代码
    generateStrategyFromTemplate: (
      templateId: string,
      symbol: string,
      startDate: string,
      endDate: string,
      initialCapital: number = 10000.0,
      parameters?: any
    ) => apiClient.post('/lean/strategies/generate', {
      template_id: templateId,
      symbol,
      start_date: startDate,
      end_date: endDate,
      initial_capital: initialCapital,
      parameters
    }),
  };
}

// 导出默认实例
export default apiClient;
