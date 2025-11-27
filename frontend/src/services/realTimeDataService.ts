/**
 * 实时数据服务 - 集成多个合法合规的数据源
 * 支持加密货币、股票、外汇等市场数据
 */

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  last?: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  type: 'stock' | 'crypto' | 'forex' | 'commodity';
  lastUpdate: string;
  source: string;
  timestamp?: string;
}

interface DataSource {
  name: string;
  url: string;
  apiKey?: string;
  enabled: boolean;
}

class RealTimeDataService {
  private dataSources: DataSource[] = [
    {
      name: 'CoinGecko',
      url: 'https://api.coingecko.com/api/v3/simple/price',
      enabled: true
    },
    {
      name: 'Alpha Vantage',
      url: 'https://www.alphavantage.co/query',
      apiKey: 'demo', // 使用demo key，生产环境需要替换
      enabled: true
    },
    {
      name: 'Yahoo Finance',
      url: 'https://query1.finance.yahoo.com/v8/finance/chart',
      enabled: true
    },
    {
      name: 'ExchangeRate-API',
      url: 'https://api.exchangerate-api.com/v4/latest/USD',
      enabled: true
    }
  ];

  private cachedData: Map<string, MarketData> = new Map();
  private updateInterval: number = 5000; // 5秒更新间隔

  // 获取加密货币数据 (CoinGecko)
  async getCryptoData(symbols: string[]): Promise<MarketData[]> {
    try {
      const response = await fetch(
        `https://api.coingecko.com/api/v3/simple/price?ids=${symbols.join(',')}&vs_currencies=usd&include_24hr_change=true`
      );
      
      if (!response.ok) throw new Error('CoinGecko API请求失败');
      
      const data = await response.json();
      const result: MarketData[] = [];

      for (const [id, info] of Object.entries(data)) {
        const symbol = this.mapCoinGeckoSymbol(id);
        if (symbol) {
          result.push({
            symbol,
            price: (info as any).usd,
            change: (info as any).usd_24h_change || 0,
            changePercent: (info as any).usd_24h_change || 0,
            type: 'crypto',
            lastUpdate: new Date().toISOString(),
            source: 'CoinGecko'
          });
        }
      }

      return result;
    } catch (error) {
      console.warn('CoinGecko API失败，使用模拟数据:', error);
      return this.getMockCryptoData(symbols);
    }
  }

  // 获取股票数据 (Alpha Vantage)
  async getStockData(symbols: string[]): Promise<MarketData[]> {
    try {
      const results: MarketData[] = [];
      
      for (const symbol of symbols) {
        try {
          const response = await fetch(
            `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=demo`
          );
          
          if (!response.ok) continue;
          
          const data = await response.json();
          const quote = data['Global Quote'];
          
          if (quote) {
            results.push({
              symbol,
              price: parseFloat(quote['05. price']),
              change: parseFloat(quote['09. change']),
              changePercent: parseFloat(quote['10. change percent']),
              type: 'stock',
              lastUpdate: new Date().toISOString(),
              source: 'Alpha Vantage'
            });
          }
        } catch (error) {
          console.warn(`获取股票 ${symbol} 数据失败:`, error);
        }
      }

      return results.length > 0 ? results : this.getMockStockData(symbols);
    } catch (error) {
      console.warn('Alpha Vantage API失败，使用模拟数据:', error);
      return this.getMockStockData(symbols);
    }
  }

  // 获取外汇数据
  async getForexData(symbols: string[]): Promise<MarketData[]> {
    try {
      const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
      
      if (!response.ok) throw new Error('ExchangeRate API请求失败');
      
      const data = await response.json();
      const results: MarketData[] = [];

      for (const symbol of symbols) {
        const [base, quote] = symbol.split('/');
        if (base === 'USD' && data.rates[quote]) {
          results.push({
            symbol,
            price: data.rates[quote],
            change: 0, // 这个API不提供变化数据
            changePercent: 0,
            type: 'forex',
            lastUpdate: new Date().toISOString(),
            source: 'ExchangeRate-API'
          });
        }
      }

      return results.length > 0 ? results : this.getMockForexData(symbols);
    } catch (error) {
      console.warn('ExchangeRate API失败，使用模拟数据:', error);
      return this.getMockForexData(symbols);
    }
  }

  // 统一数据获取接口
  async getMarketData(symbols: string[]): Promise<MarketData[]> {
    const crypto: string[] = [];
    const stocks: string[] = [];
    const forex: string[] = [];

    // 分类符号
    symbols.forEach(symbol => {
      if (symbol.includes('/')) {
        if (symbol.includes('USD') || symbol.includes('CNY') || symbol.includes('EUR')) {
          forex.push(symbol);
        } else {
          crypto.push(symbol);
        }
      } else {
        stocks.push(symbol);
      }
    });

    const promises = [];
    
    if (crypto.length > 0) {
      promises.push(this.getCryptoData(crypto));
    } else {
      promises.push(Promise.resolve([]));
    }
    
    if (stocks.length > 0) {
      promises.push(this.getStockData(stocks));
    } else {
      promises.push(Promise.resolve([]));
    }
    
    if (forex.length > 0) {
      promises.push(this.getForexData(forex));
    } else {
      promises.push(Promise.resolve([]));
    }

    try {
      const results = await Promise.all(promises);
      const allData = results.flat();
      
      // 更新缓存
      allData.forEach(data => {
        this.cachedData.set(data.symbol, data);
      });
      
      return allData;
    } catch (error) {
      console.error('获取市场数据失败:', error);
      return this.getMockMarketData(symbols);
    }
  }

  // 模拟数据作为后备
  private getMockMarketData(symbols: string[]): MarketData[] {
    const mockData: { [key: string]: MarketData } = {
      'BTC/USDT': { symbol: 'BTC/USDT', price: 42567.39, change: 974.23, changePercent: 2.34, type: 'crypto', lastUpdate: new Date().toISOString(), source: '模拟数据' },
      'ETH/USDT': { symbol: 'ETH/USDT', price: 2345.67, change: 28.51, changePercent: 1.23, type: 'crypto', lastUpdate: new Date().toISOString(), source: '模拟数据' },
      'AAPL': { symbol: 'AAPL', price: 182.45, change: -1.03, changePercent: -0.56, type: 'stock', lastUpdate: new Date().toISOString(), source: '模拟数据' },
      'USD/CNY': { symbol: 'USD/CNY', price: 7.1987, change: 0.0086, changePercent: 0.12, type: 'forex', lastUpdate: new Date().toISOString(), source: '模拟数据' },
      'TSLA': { symbol: 'TSLA', price: 245.67, change: 3.51, changePercent: 1.45, type: 'stock', lastUpdate: new Date().toISOString(), source: '模拟数据' },
      'EUR/USD': { symbol: 'EUR/USD', price: 1.0856, change: -0.0009, changePercent: -0.08, type: 'forex', lastUpdate: new Date().toISOString(), source: '模拟数据' },
      'XAU/USD': { symbol: 'XAU/USD', price: 1987.65, change: 15.23, changePercent: 0.77, type: 'commodity', lastUpdate: new Date().toISOString(), source: '模拟数据' },
      'SPY': { symbol: 'SPY', price: 456.78, change: -2.34, changePercent: -0.51, type: 'stock', lastUpdate: new Date().toISOString(), source: '模拟数据' }
    };

    return symbols.map(symbol => mockData[symbol] || {
      symbol,
      price: 100,
      change: 0,
      changePercent: 0,
      type: 'stock',
      lastUpdate: new Date().toISOString(),
      source: '模拟数据'
    });
  }

  private getMockCryptoData(symbols: string[]): MarketData[] {
    return symbols.map(symbol => ({
      symbol,
      price: Math.random() * 50000 + 1000,
      change: (Math.random() - 0.5) * 1000,
      changePercent: (Math.random() - 0.5) * 10,
      type: 'crypto',
      lastUpdate: new Date().toISOString(),
      source: '模拟数据'
    }));
  }

  private getMockStockData(symbols: string[]): MarketData[] {
    return symbols.map(symbol => ({
      symbol,
      price: Math.random() * 500 + 50,
      change: (Math.random() - 0.5) * 10,
      changePercent: (Math.random() - 0.5) * 5,
      type: 'stock',
      lastUpdate: new Date().toISOString(),
      source: '模拟数据'
    }));
  }

  private getMockForexData(symbols: string[]): MarketData[] {
    return symbols.map(symbol => ({
      symbol,
      price: symbol.includes('CNY') ? 7.1 + Math.random() * 0.2 : 1.0 + Math.random() * 0.1,
      change: (Math.random() - 0.5) * 0.01,
      changePercent: (Math.random() - 0.5) * 0.5,
      type: 'forex',
      lastUpdate: new Date().toISOString(),
      source: '模拟数据'
    }));
  }

  private mapCoinGeckoSymbol(id: string): string | null {
    const mapping: { [key: string]: string } = {
      'bitcoin': 'BTC/USDT',
      'ethereum': 'ETH/USDT',
      'binancecoin': 'BNB/USDT',
      'ripple': 'XRP/USDT',
      'cardano': 'ADA/USDT',
      'solana': 'SOL/USDT',
      'polkadot': 'DOT/USDT',
      'dogecoin': 'DOGE/USDT'
    };
    return mapping[id] || null;
  }

  // 启动实时数据更新
  startRealTimeUpdates(callback: (data: MarketData[]) => void, symbols: string[], interval?: number): () => void {
    const updateInterval = interval || this.updateInterval;
    
    // 立即获取一次数据
    this.getMarketData(symbols).then(callback);
    
    // 设置定时更新
    const timer = setInterval(async () => {
      const data = await this.getMarketData(symbols);
      callback(data);
    }, updateInterval);

    // 返回停止函数
    return () => clearInterval(timer);
  }

  // 获取单个符号的数据
  async getSymbolData(symbol: string): Promise<MarketData | null> {
    const data = await this.getMarketData([symbol]);
    return data[0] || null;
  }

  // 获取缓存数据
  getCachedData(symbol: string): MarketData | undefined {
    return this.cachedData.get(symbol);
  }

  // 获取所有缓存数据
  getAllCachedData(): MarketData[] {
    return Array.from(this.cachedData.values());
  }
}

// 创建单例实例
export const realTimeDataService = new RealTimeDataService();

// 导出类型
export type { MarketData, DataSource };
