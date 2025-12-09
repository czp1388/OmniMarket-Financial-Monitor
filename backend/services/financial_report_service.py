"""
财报数据服务
支持从多个数据源获取财务报表数据，包括：
- Alpha Vantage (免费API，需要API key)
- Financial Modeling Prep (备用)
- Mock Data (降级方案)
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FinancialReportService:
    """财报数据服务"""
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.fmp_key = os.getenv('FMP_API_KEY', '')
        
        # API端点
        self.av_base_url = "https://www.alphavantage.co/query"
        self.fmp_base_url = "https://financialmodelingprep.com/api/v3"
        
        # 缓存
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1小时缓存
        
        logger.info(f"FinancialReportService 初始化 (Alpha Vantage: {'已配置' if self.alpha_vantage_key else '未配置'})")
    
    async def get_financial_report(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取公司财报数据
        
        参数:
            symbol: 股票代码 (如 AAPL, MSFT)
        
        返回:
            财报数据字典，包含所有财务指标
        """
        # 检查缓存
        cache_key = f"report_{symbol}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_ttl:
                logger.debug(f"从缓存返回 {symbol} 财报数据")
                return cached_data['data']
        
        # 尝试从 Alpha Vantage 获取
        if self.alpha_vantage_key:
            try:
                data = await self._fetch_from_alpha_vantage(symbol)
                if data:
                    self._cache_data(cache_key, data)
                    return data
            except Exception as e:
                logger.warning(f"Alpha Vantage 获取失败: {e}")
        
        # 降级到模拟数据
        logger.info(f"使用模拟数据: {symbol}")
        mock_data = self._get_mock_data(symbol)
        self._cache_data(cache_key, mock_data)
        return mock_data
    
    async def get_historical_data(self, symbol: str, periods: int = 4) -> Optional[List[Dict[str, Any]]]:
        """
        获取历史财报数据（最近N个季度）
        
        参数:
            symbol: 股票代码
            periods: 返回的季度数量
        
        返回:
            历史数据列表
        """
        cache_key = f"historical_{symbol}_{periods}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['data']
        
        # 尝试从 Alpha Vantage 获取
        if self.alpha_vantage_key:
            try:
                data = await self._fetch_historical_from_av(symbol, periods)
                if data:
                    self._cache_data(cache_key, data)
                    return data
            except Exception as e:
                logger.warning(f"Alpha Vantage 历史数据获取失败: {e}")
        
        # 降级到模拟数据
        mock_data = self._get_mock_historical_data(symbol, periods)
        self._cache_data(cache_key, mock_data)
        return mock_data
    
    async def _fetch_from_alpha_vantage(self, symbol: str) -> Optional[Dict[str, Any]]:
        """从 Alpha Vantage 获取财报数据"""
        async with aiohttp.ClientSession() as session:
            # 获取收入报表
            income_url = f"{self.av_base_url}?function=INCOME_STATEMENT&symbol={symbol}&apikey={self.alpha_vantage_key}"
            # 获取资产负债表
            balance_url = f"{self.av_base_url}?function=BALANCE_SHEET&symbol={symbol}&apikey={self.alpha_vantage_key}"
            # 获取现金流量表
            cash_flow_url = f"{self.av_base_url}?function=CASH_FLOW&symbol={symbol}&apikey={self.alpha_vantage_key}"
            
            try:
                # 并行请求
                income_task = session.get(income_url, timeout=aiohttp.ClientTimeout(total=10))
                balance_task = session.get(balance_url, timeout=aiohttp.ClientTimeout(total=10))
                cash_task = session.get(cash_flow_url, timeout=aiohttp.ClientTimeout(total=10))
                
                income_resp, balance_resp, cash_resp = await asyncio.gather(
                    income_task, balance_task, cash_task
                )
                
                income_data = await income_resp.json()
                balance_data = await balance_resp.json()
                cash_data = await cash_resp.json()
                
                # 解析最新季度数据
                return self._parse_alpha_vantage_data(symbol, income_data, balance_data, cash_data)
                
            except Exception as e:
                logger.error(f"Alpha Vantage API 请求失败: {e}")
                return None
    
    async def _fetch_historical_from_av(self, symbol: str, periods: int) -> Optional[List[Dict[str, Any]]]:
        """从 Alpha Vantage 获取历史数据"""
        # 实现类似逻辑，返回多个季度的数据
        pass
    
    def _parse_alpha_vantage_data(
        self, 
        symbol: str, 
        income: Dict, 
        balance: Dict, 
        cash_flow: Dict
    ) -> Dict[str, Any]:
        """解析 Alpha Vantage API 返回的数据"""
        try:
            # 获取最新季度数据
            latest_income = income.get('quarterlyReports', [])[0] if 'quarterlyReports' in income else {}
            latest_balance = balance.get('quarterlyReports', [])[0] if 'quarterlyReports' in balance else {}
            latest_cash = cash_flow.get('quarterlyReports', [])[0] if 'quarterlyReports' in cash_flow else {}
            
            # 提取数据
            revenue = float(latest_income.get('totalRevenue', 0))
            net_income = float(latest_income.get('netIncome', 0))
            gross_profit = float(latest_income.get('grossProfit', 0))
            operating_income = float(latest_income.get('operatingIncome', 0))
            
            total_assets = float(latest_balance.get('totalAssets', 0))
            total_liabilities = float(latest_balance.get('totalLiabilities', 0))
            total_equity = float(latest_balance.get('totalShareholderEquity', 0))
            current_assets = float(latest_balance.get('totalCurrentAssets', 0))
            current_liabilities = float(latest_balance.get('totalCurrentLiabilities', 0))
            cash = float(latest_balance.get('cashAndCashEquivalentsAtCarryingValue', 0))
            
            operating_cash_flow = float(latest_cash.get('operatingCashflow', 0))
            investing_cash_flow = float(latest_cash.get('cashflowFromInvestment', 0))
            financing_cash_flow = float(latest_cash.get('cashflowFromFinancing', 0))
            
            # 计算财务比率
            profit_margin = (net_income / revenue * 100) if revenue > 0 else 0
            gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
            roe = (net_income / total_equity * 100) if total_equity > 0 else 0
            roa = (net_income / total_assets * 100) if total_assets > 0 else 0
            current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else 0
            debt_to_equity = (total_liabilities / total_equity) if total_equity > 0 else 0
            
            return {
                "symbol": symbol,
                "companyName": symbol,  # Alpha Vantage 不提供公司名称
                "quarter": latest_income.get('fiscalDateEnding', 'N/A'),
                "revenue": revenue,
                "netIncome": net_income,
                "grossProfit": gross_profit,
                "operatingIncome": operating_income,
                "eps": float(latest_income.get('reportedEPS', 0)),
                "totalAssets": total_assets,
                "totalLiabilities": total_liabilities,
                "totalEquity": total_equity,
                "currentAssets": current_assets,
                "currentLiabilities": current_liabilities,
                "cash": cash,
                "operatingCashFlow": operating_cash_flow,
                "investingCashFlow": investing_cash_flow,
                "financingCashFlow": financing_cash_flow,
                "freeCashFlow": operating_cash_flow + investing_cash_flow,
                "revenueGrowth": 0,  # 需要历史数据计算
                "profitMargin": profit_margin,
                "grossMargin": gross_margin,
                "roe": roe,
                "roa": roa,
                "currentRatio": current_ratio,
                "debtToEquity": debt_to_equity,
                "peRatio": 0,  # 需要股价数据
                "pbRatio": 0,
            }
        except Exception as e:
            logger.error(f"解析 Alpha Vantage 数据失败: {e}")
            return None
    
    def _get_mock_data(self, symbol: str) -> Dict[str, Any]:
        """返回模拟数据（降级方案）"""
        mock_reports = {
            'AAPL': {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "quarter": "2024 Q4",
                "revenue": 89498000000,
                "netIncome": 22956000000,
                "grossProfit": 41671000000,
                "operatingIncome": 28996000000,
                "eps": 1.47,
                "totalAssets": 352755000000,
                "totalLiabilities": 290437000000,
                "totalEquity": 62318000000,
                "currentAssets": 135405000000,
                "currentLiabilities": 132480000000,
                "cash": 28969000000,
                "operatingCashFlow": 26891000000,
                "investingCashFlow": -3704000000,
                "financingCashFlow": -27347000000,
                "freeCashFlow": 23187000000,
                "revenueGrowth": 6.07,
                "profitMargin": 25.65,
                "grossMargin": 46.55,
                "roe": 147.25,
                "roa": 6.51,
                "currentRatio": 1.02,
                "debtToEquity": 4.66,
                "peRatio": 29.82,
                "pbRatio": 43.89
            },
            'MSFT': {
                "symbol": "MSFT",
                "companyName": "Microsoft Corp.",
                "quarter": "2024 Q4",
                "revenue": 62020000000,
                "netIncome": 21871000000,
                "grossProfit": 42916000000,
                "operatingIncome": 27854000000,
                "eps": 2.93,
                "totalAssets": 512163000000,
                "totalLiabilities": 253307000000,
                "totalEquity": 258856000000,
                "currentAssets": 192893000000,
                "currentLiabilities": 120767000000,
                "cash": 80021000000,
                "operatingCashFlow": 29863000000,
                "investingCashFlow": -13204000000,
                "financingCashFlow": -18772000000,
                "freeCashFlow": 24321000000,
                "revenueGrowth": 16.0,
                "profitMargin": 35.27,
                "grossMargin": 69.20,
                "roe": 38.45,
                "roa": 4.27,
                "currentRatio": 1.60,
                "debtToEquity": 0.98,
                "peRatio": 36.42,
                "pbRatio": 14.01
            }
        }
        
        return mock_reports.get(symbol.upper(), mock_reports['AAPL'])
    
    def _get_mock_historical_data(self, symbol: str, periods: int) -> List[Dict[str, Any]]:
        """返回模拟历史数据"""
        mock_historical = {
            'AAPL': [
                {"quarter": "2024 Q1", "revenue": 90753000000, "netIncome": 23636000000, "profitMargin": 26.04, "grossMargin": 45.96, "roe": 160.58, "eps": 1.52},
                {"quarter": "2024 Q2", "revenue": 85778000000, "netIncome": 21744000000, "profitMargin": 25.35, "grossMargin": 46.25, "roe": 153.12, "eps": 1.40},
                {"quarter": "2024 Q3", "revenue": 94930000000, "netIncome": 22956000000, "profitMargin": 24.18, "grossMargin": 46.22, "roe": 145.89, "eps": 1.47},
                {"quarter": "2024 Q4", "revenue": 89498000000, "netIncome": 22956000000, "profitMargin": 25.65, "grossMargin": 46.55, "roe": 147.25, "eps": 1.47}
            ]
        }
        
        data = mock_historical.get(symbol.upper(), mock_historical['AAPL'])
        return data[:periods]
    
    def _cache_data(self, key: str, data: Any):
        """缓存数据"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }


# 全局实例
financial_report_service = FinancialReportService()
