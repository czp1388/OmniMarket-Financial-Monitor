import axios from 'axios';

// API基础配置
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
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
    
    // 更新虚拟账户
    updateAccount: (accountId: string, accountData: any) => 
      apiClient.put(`/virtual/accounts/${accountId}`, accountData),
    
    // 删除虚拟账户
    deleteAccount: (accountId: string) => apiClient.delete(`/virtual/accounts/${accountId}`),
    
    // 下单交易
    placeOrder: (accountId: string, orderData: any) => 
      apiClient.post(`/virtual/accounts/${accountId}/orders`, orderData),
    
    // 获取订单列表
    getOrders: (accountId: string, status?: string) => 
      apiClient.get(`/virtual/accounts/${accountId}/orders`, { params: { status } }),
    
    // 取消订单
    cancelOrder: (accountId: string, orderId: string) => 
      apiClient.delete(`/virtual/accounts/${accountId}/orders/${orderId}`),
    
    // 获取持仓列表
    getPositions: (accountId: string) => 
      apiClient.get(`/virtual/accounts/${accountId}/positions`),
    
    // 获取交易记录
    getTrades: (accountId: string, symbol?: string) => 
      apiClient.get(`/virtual/accounts/${accountId}/trades`, { params: { symbol } }),
    
    // 获取绩效分析
    getPerformance: (accountId: string) => 
      apiClient.get(`/virtual/accounts/${accountId}/performance`),
  };
}

// 导出默认实例
export default apiClient;
