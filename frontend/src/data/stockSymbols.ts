/**
 * 常用股票代码列表
 * 用于搜索自动完成功能
 */

export interface StockSymbol {
  symbol: string;
  name: string;
  exchange: string;
  sector?: string;
}

// 美股热门股票
export const popularUSStocks: StockSymbol[] = [
  // 科技巨头 (FAANG+)
  { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'GOOGL', name: 'Alphabet Inc. Class A', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'GOOG', name: 'Alphabet Inc. Class C', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', exchange: 'NASDAQ', sector: 'Consumer Cyclical' },
  { symbol: 'META', name: 'Meta Platforms Inc.', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'NFLX', name: 'Netflix Inc.', exchange: 'NASDAQ', sector: 'Communication Services' },
  { symbol: 'NVDA', name: 'NVIDIA Corporation', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'TSLA', name: 'Tesla Inc.', exchange: 'NASDAQ', sector: 'Consumer Cyclical' },
  
  // 金融
  { symbol: 'JPM', name: 'JPMorgan Chase & Co.', exchange: 'NYSE', sector: 'Financial' },
  { symbol: 'BAC', name: 'Bank of America Corp.', exchange: 'NYSE', sector: 'Financial' },
  { symbol: 'WFC', name: 'Wells Fargo & Company', exchange: 'NYSE', sector: 'Financial' },
  { symbol: 'GS', name: 'Goldman Sachs Group Inc.', exchange: 'NYSE', sector: 'Financial' },
  { symbol: 'MS', name: 'Morgan Stanley', exchange: 'NYSE', sector: 'Financial' },
  { symbol: 'V', name: 'Visa Inc.', exchange: 'NYSE', sector: 'Financial' },
  { symbol: 'MA', name: 'Mastercard Inc.', exchange: 'NYSE', sector: 'Financial' },
  
  // 医药健康
  { symbol: 'JNJ', name: 'Johnson & Johnson', exchange: 'NYSE', sector: 'Healthcare' },
  { symbol: 'UNH', name: 'UnitedHealth Group Inc.', exchange: 'NYSE', sector: 'Healthcare' },
  { symbol: 'PFE', name: 'Pfizer Inc.', exchange: 'NYSE', sector: 'Healthcare' },
  { symbol: 'ABBV', name: 'AbbVie Inc.', exchange: 'NYSE', sector: 'Healthcare' },
  { symbol: 'TMO', name: 'Thermo Fisher Scientific Inc.', exchange: 'NYSE', sector: 'Healthcare' },
  
  // 消费品
  { symbol: 'KO', name: 'Coca-Cola Company', exchange: 'NYSE', sector: 'Consumer Defensive' },
  { symbol: 'PEP', name: 'PepsiCo Inc.', exchange: 'NASDAQ', sector: 'Consumer Defensive' },
  { symbol: 'WMT', name: 'Walmart Inc.', exchange: 'NYSE', sector: 'Consumer Defensive' },
  { symbol: 'COST', name: 'Costco Wholesale Corporation', exchange: 'NASDAQ', sector: 'Consumer Defensive' },
  { symbol: 'HD', name: 'Home Depot Inc.', exchange: 'NYSE', sector: 'Consumer Cyclical' },
  { symbol: 'MCD', name: 'McDonald\'s Corporation', exchange: 'NYSE', sector: 'Consumer Cyclical' },
  { symbol: 'NKE', name: 'NIKE Inc.', exchange: 'NYSE', sector: 'Consumer Cyclical' },
  
  // 能源
  { symbol: 'XOM', name: 'Exxon Mobil Corporation', exchange: 'NYSE', sector: 'Energy' },
  { symbol: 'CVX', name: 'Chevron Corporation', exchange: 'NYSE', sector: 'Energy' },
  
  // 工业
  { symbol: 'BA', name: 'Boeing Company', exchange: 'NYSE', sector: 'Industrials' },
  { symbol: 'CAT', name: 'Caterpillar Inc.', exchange: 'NYSE', sector: 'Industrials' },
  { symbol: 'GE', name: 'General Electric Company', exchange: 'NYSE', sector: 'Industrials' },
  
  // 通信
  { symbol: 'T', name: 'AT&T Inc.', exchange: 'NYSE', sector: 'Communication Services' },
  { symbol: 'VZ', name: 'Verizon Communications Inc.', exchange: 'NYSE', sector: 'Communication Services' },
  { symbol: 'DIS', name: 'Walt Disney Company', exchange: 'NYSE', sector: 'Communication Services' },
  
  // 半导体
  { symbol: 'INTC', name: 'Intel Corporation', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'AMD', name: 'Advanced Micro Devices Inc.', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'QCOM', name: 'QUALCOMM Inc.', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'TSM', name: 'Taiwan Semiconductor Manufacturing', exchange: 'NYSE', sector: 'Technology' },
  
  // 中概股
  { symbol: 'BABA', name: 'Alibaba Group Holding Ltd.', exchange: 'NYSE', sector: 'Consumer Cyclical' },
  { symbol: 'JD', name: 'JD.com Inc.', exchange: 'NASDAQ', sector: 'Consumer Cyclical' },
  { symbol: 'BIDU', name: 'Baidu Inc.', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'PDD', name: 'PDD Holdings Inc.', exchange: 'NASDAQ', sector: 'Consumer Cyclical' },
  { symbol: 'NIO', name: 'NIO Inc.', exchange: 'NYSE', sector: 'Consumer Cyclical' },
  
  // 其他热门
  { symbol: 'CRM', name: 'Salesforce Inc.', exchange: 'NYSE', sector: 'Technology' },
  { symbol: 'ORCL', name: 'Oracle Corporation', exchange: 'NYSE', sector: 'Technology' },
  { symbol: 'CSCO', name: 'Cisco Systems Inc.', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'ADBE', name: 'Adobe Inc.', exchange: 'NASDAQ', sector: 'Technology' },
  { symbol: 'IBM', name: 'International Business Machines', exchange: 'NYSE', sector: 'Technology' },
  { symbol: 'PYPL', name: 'PayPal Holdings Inc.', exchange: 'NASDAQ', sector: 'Financial' },
  { symbol: 'UBER', name: 'Uber Technologies Inc.', exchange: 'NYSE', sector: 'Technology' },
  { symbol: 'SPOT', name: 'Spotify Technology S.A.', exchange: 'NYSE', sector: 'Communication Services' },
];

/**
 * 搜索股票代码
 * @param query 搜索关键词
 * @param limit 返回结果数量限制
 * @returns 匹配的股票列表
 */
export function searchStockSymbols(query: string, limit: number = 10): StockSymbol[] {
  if (!query || query.trim().length === 0) {
    return popularUSStocks.slice(0, limit);
  }

  const searchTerm = query.toLowerCase().trim();
  
  // 搜索匹配：股票代码或公司名称
  const matches = popularUSStocks.filter(stock => {
    const symbolMatch = stock.symbol.toLowerCase().includes(searchTerm);
    const nameMatch = stock.name.toLowerCase().includes(searchTerm);
    return symbolMatch || nameMatch;
  });

  // 优先显示代码完全匹配的结果
  matches.sort((a, b) => {
    const aSymbolMatch = a.symbol.toLowerCase().startsWith(searchTerm);
    const bSymbolMatch = b.symbol.toLowerCase().startsWith(searchTerm);
    
    if (aSymbolMatch && !bSymbolMatch) return -1;
    if (!aSymbolMatch && bSymbolMatch) return 1;
    
    return a.symbol.localeCompare(b.symbol);
  });

  return matches.slice(0, limit);
}

/**
 * 按行业分组获取股票
 * @param sector 行业名称
 * @returns 该行业的股票列表
 */
export function getStocksBySector(sector: string): StockSymbol[] {
  return popularUSStocks.filter(stock => stock.sector === sector);
}

/**
 * 获取所有行业列表
 * @returns 去重的行业名称列表
 */
export function getAllSectors(): string[] {
  const sectors = popularUSStocks
    .map(stock => stock.sector)
    .filter((sector): sector is string => sector !== undefined);
  
  return Array.from(new Set(sectors)).sort();
}
