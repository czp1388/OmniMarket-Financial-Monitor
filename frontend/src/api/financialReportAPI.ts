/**
 * 财报API客户端
 * 与后端财报API交互
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface FinancialReport {
  symbol: string;
  companyName: string;
  quarter: string;
  revenue: number;
  netIncome: number;
  grossProfit: number;
  operatingIncome: number;
  eps: number;
  totalAssets: number;
  totalLiabilities: number;
  totalEquity: number;
  currentAssets: number;
  currentLiabilities: number;
  cash: number;
  operatingCashFlow: number;
  investingCashFlow: number;
  financingCashFlow: number;
  freeCashFlow: number;
  revenueGrowth: number;
  profitMargin: number;
  grossMargin: number;
  roe: number;
  roa: number;
  currentRatio: number;
  debtToEquity: number;
  peRatio: number;
  pbRatio: number;
}

export interface HistoricalData {
  quarter: string;
  revenue: number;
  netIncome: number;
  profitMargin: number;
  grossMargin: number;
  roe: number;
  eps: number;
}

export interface StockSymbol {
  symbol: string;
  name: string;
}

class FinancialReportAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}/financial-reports`;
  }

  /**
   * 获取公司最新财报
   */
  async getFinancialReport(symbol: string): Promise<FinancialReport> {
    const response = await fetch(`${this.baseURL}/?symbol=${symbol}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`未找到股票代码 "${symbol}" 的财报数据`);
      }
      throw new Error(`获取财报失败: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * 获取历史财报数据
   */
  async getHistoricalData(symbol: string, periods: number = 4): Promise<HistoricalData[]> {
    const response = await fetch(`${this.baseURL}/historical?symbol=${symbol}&periods=${periods}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`未找到股票代码 "${symbol}" 的历史数据`);
      }
      throw new Error(`获取历史数据失败: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * 搜索股票代码
   */
  async searchSymbols(keyword: string): Promise<StockSymbol[]> {
    const response = await fetch(`${this.baseURL}/search?keyword=${encodeURIComponent(keyword)}`);
    
    if (!response.ok) {
      throw new Error(`搜索失败: ${response.statusText}`);
    }
    
    return response.json();
  }
}

// 导出单例实例
export const financialReportAPI = new FinancialReportAPI();
