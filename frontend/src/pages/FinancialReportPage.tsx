import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface FinancialReport {
  // 基础信息
  symbol: string;
  companyName: string;
  quarter: string;
  
  // 利润表
  revenue: number;
  netIncome: number;
  grossProfit: number;
  operatingIncome: number;
  eps: number;
  
  // 资产负债表
  totalAssets: number;
  totalLiabilities: number;
  totalEquity: number;
  currentAssets: number;
  currentLiabilities: number;
  cash: number;
  
  // 现金流量表
  operatingCashFlow: number;
  investingCashFlow: number;
  financingCashFlow: number;
  freeCashFlow: number;
  
  // 财务比率
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

const FinancialReportPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchSymbol, setSearchSymbol] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<FinancialReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // 模拟财报数据
  const mockReports: FinancialReport[] = [
    {
      symbol: 'AAPL',
      companyName: 'Apple Inc.',
      quarter: '2024 Q4',
      // 利润表
      revenue: 89498000000,
      netIncome: 22956000000,
      grossProfit: 41671000000,
      operatingIncome: 28996000000,
      eps: 1.47,
      // 资产负债表
      totalAssets: 352755000000,
      totalLiabilities: 290437000000,
      totalEquity: 62318000000,
      currentAssets: 135405000000,
      currentLiabilities: 132480000000,
      cash: 28969000000,
      // 现金流量表
      operatingCashFlow: 26891000000,
      investingCashFlow: -3704000000,
      financingCashFlow: -27347000000,
      freeCashFlow: 23187000000,
      // 财务比率
      revenueGrowth: 6.07,
      profitMargin: 25.65,
      grossMargin: 46.55,
      roe: 147.25,
      roa: 6.51,
      currentRatio: 1.02,
      debtToEquity: 4.66,
      peRatio: 29.82,
      pbRatio: 43.89
    },
    {
      symbol: 'MSFT',
      companyName: 'Microsoft Corp.',
      quarter: '2024 Q4',
      // 利润表
      revenue: 62020000000,
      netIncome: 21871000000,
      grossProfit: 42916000000,
      operatingIncome: 27854000000,
      eps: 2.93,
      // 资产负债表
      totalAssets: 512163000000,
      totalLiabilities: 253307000000,
      totalEquity: 258856000000,
      currentAssets: 192893000000,
      currentLiabilities: 120767000000,
      cash: 80021000000,
      // 现金流量表
      operatingCashFlow: 29863000000,
      investingCashFlow: -13204000000,
      financingCashFlow: -18772000000,
      freeCashFlow: 24321000000,
      // 财务比率
      revenueGrowth: 16.0,
      profitMargin: 35.27,
      grossMargin: 69.20,
      roe: 38.45,
      roa: 4.27,
      currentRatio: 1.60,
      debtToEquity: 0.98,
      peRatio: 36.42,
      pbRatio: 14.01
    },
    {
      symbol: 'TSLA',
      companyName: 'Tesla Inc.',
      quarter: '2024 Q3',
      // 利润表
      revenue: 25182000000,
      netIncome: 2167000000,
      grossProfit: 4516000000,
      operatingIncome: 1762000000,
      eps: 0.68,
      // 资产负债表
      totalAssets: 106618000000,
      totalLiabilities: 69154000000,
      totalEquity: 37464000000,
      currentAssets: 43049000000,
      currentLiabilities: 31663000000,
      cash: 26077000000,
      // 现金流量表
      operatingCashFlow: 2939000000,
      investingCashFlow: -2462000000,
      financingCashFlow: 113000000,
      freeCashFlow: 477000000,
      // 财务比率
      revenueGrowth: 7.85,
      profitMargin: 8.61,
      grossMargin: 17.94,
      roe: 18.92,
      roa: 2.03,
      currentRatio: 1.36,
      debtToEquity: 1.85,
      peRatio: 62.35,
      pbRatio: 11.78
    },
    {
      symbol: 'GOOGL',
      companyName: 'Alphabet Inc.',
      quarter: '2024 Q4',
      // 利润表
      revenue: 86309000000,
      netIncome: 20641000000,
      grossProfit: 48165000000,
      operatingIncome: 25465000000,
      eps: 1.64,
      // 资产负债表
      totalAssets: 402392000000,
      totalLiabilities: 124000000000,
      totalEquity: 278392000000,
      currentAssets: 155669000000,
      currentLiabilities: 80900000000,
      cash: 107726000000,
      // 现金流量表
      operatingCashFlow: 28346000000,
      investingCashFlow: -12098000000,
      financingCashFlow: -14682000000,
      freeCashFlow: 23715000000,
      // 财务比率
      revenueGrowth: 15.09,
      profitMargin: 23.92,
      grossMargin: 55.81,
      roe: 29.67,
      roa: 5.13,
      currentRatio: 1.92,
      debtToEquity: 0.45,
      peRatio: 24.17,
      pbRatio: 7.17
    }
  ];

  const formatNumber = (num: number): string => {
    if (num >= 1000000000) {
      return `$${(num / 1000000000).toFixed(2)}B`;
    } else if (num >= 1000000) {
      return `$${(num / 1000000).toFixed(2)}M`;
    }
    return `$${num.toFixed(2)}`;
  };

  const handleSearch = () => {
    setError('');
    setIsLoading(true);
    
    // 模拟API延迟
    setTimeout(() => {
      const report = mockReports.find(r => r.symbol.toLowerCase() === searchSymbol.toLowerCase());
      if (report) {
        setSelectedReport(report);
        setError('');
      } else {
        setSelectedReport(null);
        setError(`未找到股票代码 "${searchSymbol}" 的财报数据`);
      }
      setIsLoading(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[#0a0e17] text-white p-6">
      {/* 顶部导航 */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-[#141a2a] hover:bg-[#1a2332] rounded-lg transition-all duration-300 flex items-center gap-2"
        >
          <span>←</span>
          <span>返回首页</span>
        </button>
      </div>

      {/* 标题 */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
          📊 财报分析
        </h1>
        <p className="text-gray-400 text-lg">Financial Report Analysis - 深度解析公司财务状况</p>
      </div>

      {/* 搜索栏 */}
      <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="输入股票代码 (如: AAPL, MSFT, TSLA)"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1 bg-[#0a0e17] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00ccff] transition-all"
          />
          <button
            onClick={handleSearch}
            className="px-6 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold rounded-lg hover:shadow-lg hover:shadow-[#00ccff]/30 transition-all duration-300"
          >
            查询财报
          </button>
        </div>
      </div>

      {/* 快速选择 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-300">快速选择</h3>
        <div className="flex gap-3 flex-wrap">
          {mockReports.map((report) => (
            <button
              key={report.symbol}
              onClick={() => {
                setSearchSymbol(report.symbol);
                setError('');
                setIsLoading(true);
                setTimeout(() => {
                  setSelectedReport(report);
                  setIsLoading(false);
                }, 800);
              }}
              className="px-4 py-2 bg-[#141a2a] hover:bg-[#1a2332] border border-[#2a3a5a] rounded-lg transition-all duration-300 hover:border-[#00ccff]"
            >
              {report.symbol}
            </button>
          ))}
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 text-red-500">
            <span className="text-xl">⚠️</span>
            <span className="font-mono text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* 加载动画 */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#00ccff]"></div>
        </div>
      )}

      {/* 财报详情 */}
      {!isLoading && selectedReport ? (
        <div className="space-y-6">
          {/* 公司信息卡片 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-3xl font-bold text-white">{selectedReport.symbol}</h2>
                <p className="text-gray-400 text-sm mt-1">{selectedReport.companyName}</p>
              </div>
              <span className="px-4 py-2 bg-[#00ccff]/20 text-[#00ccff] rounded-lg font-mono text-sm">
                {selectedReport.quarter}
              </span>
            </div>
          </div>

          {/* 核心财务指标 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6">
              <div className="text-gray-400 text-sm mb-2">营业收入</div>
              <div className="text-3xl font-bold text-[#00ff88] mb-1">
                {formatNumber(selectedReport.revenue)}
              </div>
              <div className="text-sm text-[#00ff88]">
                ↗ +{selectedReport.revenueGrowth}% YoY
              </div>
            </div>

            <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6">
              <div className="text-gray-400 text-sm mb-2">净利润</div>
              <div className="text-3xl font-bold text-[#00ccff] mb-1">
                {formatNumber(selectedReport.netIncome)}
              </div>
              <div className="text-sm text-gray-400">
                利润率: {selectedReport.profitMargin.toFixed(2)}%
              </div>
            </div>

            <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6">
              <div className="text-gray-400 text-sm mb-2">每股收益 (EPS)</div>
              <div className="text-3xl font-bold text-white mb-1">
                ${selectedReport.eps.toFixed(2)}
              </div>
              <div className="text-sm text-gray-400">
                ROE: {selectedReport.roe.toFixed(2)}%
              </div>
            </div>
          </div>

          {/* 资产负债表 */}
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <span>💼</span>
              <span>资产负债表</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 资产 */}
              <div className="space-y-3">
                <div className="text-sm font-semibold text-[#00ccff] mb-3">资产</div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">总资产</span>
                  <span className="font-mono text-white">{formatNumber(selectedReport.totalAssets)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">流动资产</span>
                  <span className="font-mono text-white">{formatNumber(selectedReport.currentAssets)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">现金及现金等价物</span>
                  <span className="font-mono text-[#00ff88]">{formatNumber(selectedReport.cash)}</span>
                </div>
              </div>

              {/* 负债与权益 */}
              <div className="space-y-3">
                <div className="text-sm font-semibold text-[#ff6b6b] mb-3">负债与权益</div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">总负债</span>
                  <span className="font-mono text-white">{formatNumber(selectedReport.totalLiabilities)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">股东权益</span>
                  <span className="font-mono text-white">{formatNumber(selectedReport.totalEquity)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">资产负债率</span>
                  <span className={`font-mono ${selectedReport.debtToEquity > 2 ? 'text-[#ff6b6b]' : 'text-[#00ff88]'}`}>
                    {(selectedReport.totalLiabilities / selectedReport.totalAssets * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 现金流量表 */}
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <span>💰</span>
              <span>现金流量表</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex justify-between items-center p-3 bg-[#0a0e17] rounded-lg">
                <span className="text-gray-400 text-sm">经营活动现金流</span>
                <span className={`font-mono font-bold ${selectedReport.operatingCashFlow > 0 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
                  {formatNumber(selectedReport.operatingCashFlow)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[#0a0e17] rounded-lg">
                <span className="text-gray-400 text-sm">投资活动现金流</span>
                <span className={`font-mono font-bold ${selectedReport.investingCashFlow > 0 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
                  {formatNumber(selectedReport.investingCashFlow)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[#0a0e17] rounded-lg">
                <span className="text-gray-400 text-sm">筹资活动现金流</span>
                <span className={`font-mono font-bold ${selectedReport.financingCashFlow > 0 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
                  {formatNumber(selectedReport.financingCashFlow)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[#0a0e17] rounded-lg border-2 border-[#00ccff]">
                <span className="text-[#00ccff] text-sm font-semibold">自由现金流</span>
                <span className={`font-mono font-bold ${selectedReport.freeCashFlow > 0 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
                  {formatNumber(selectedReport.freeCashFlow)}
                </span>
              </div>
            </div>
          </div>

          {/* 关键财务比率 */}
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
              <span>📊</span>
              <span>关键财务比率</span>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">毛利率</div>
                <div className="text-2xl font-bold text-[#00ff88]">{selectedReport.grossMargin.toFixed(1)}%</div>
              </div>
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">ROA</div>
                <div className="text-2xl font-bold text-[#00ccff]">{selectedReport.roa.toFixed(1)}%</div>
              </div>
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">流动比率</div>
                <div className={`text-2xl font-bold ${selectedReport.currentRatio >= 1 ? 'text-[#00ff88]' : 'text-[#ff6b6b]'}`}>
                  {selectedReport.currentRatio.toFixed(2)}
                </div>
              </div>
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">资产负债比</div>
                <div className={`text-2xl font-bold ${selectedReport.debtToEquity < 2 ? 'text-[#00ff88]' : 'text-[#ffa500]'}`}>
                  {selectedReport.debtToEquity.toFixed(2)}
                </div>
              </div>
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">P/E 市盈率</div>
                <div className="text-2xl font-bold text-white">{selectedReport.peRatio.toFixed(2)}</div>
              </div>
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">P/B 市净率</div>
                <div className="text-2xl font-bold text-white">{selectedReport.pbRatio.toFixed(2)}</div>
              </div>
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">净利润率</div>
                <div className="text-2xl font-bold text-[#00ff88]">{selectedReport.profitMargin.toFixed(1)}%</div>
              </div>
              <div className="text-center p-4 bg-[#0a0e17] rounded-lg">
                <div className="text-gray-400 text-xs mb-2">ROE</div>
                <div className="text-2xl font-bold text-[#00ccff]">{selectedReport.roe.toFixed(1)}%</div>
              </div>
            </div>
          </div>

          {/* 财务分析 */}
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-white">📈 财务分析</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <span className="text-[#00ff88] text-xl">✓</span>
                <div>
                  <div className="font-semibold text-white">盈利能力</div>
                  <div className="text-gray-400 text-sm">
                    净利润率 {selectedReport.profitMargin.toFixed(2)}%，
                    {selectedReport.profitMargin > 20 ? '盈利能力强' : '盈利能力中等'}
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <span className="text-[#00ccff] text-xl">✓</span>
                <div>
                  <div className="font-semibold text-white">成长性</div>
                  <div className="text-gray-400 text-sm">
                    营收同比增长 {selectedReport.revenueGrowth.toFixed(2)}%，
                    {selectedReport.revenueGrowth > 10 ? '保持高速增长' : '增长平稳'}
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <span className="text-yellow-500 text-xl">✓</span>
                <div>
                  <div className="font-semibold text-white">股东回报</div>
                  <div className="text-gray-400 text-sm">
                    净资产收益率 (ROE) {selectedReport.roe.toFixed(2)}%，
                    {selectedReport.roe > 15 ? '为股东创造良好回报' : '回报率一般'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 投资建议 */}
          <div className="bg-gradient-to-r from-[#00ccff]/10 to-[#00ff88]/10 border border-[#00ccff]/30 rounded-xl p-6">
            <h3 className="text-xl font-bold mb-3 text-white flex items-center gap-2">
              <span>💡</span>
              <span>AI 投资建议</span>
            </h3>
            <p className="text-gray-300 leading-relaxed">
              基于 {selectedReport.symbol} 最新财报数据，公司{selectedReport.revenueGrowth > 10 ? '保持强劲增长势头' : '业绩稳健'}，
              净利润率达 {selectedReport.profitMargin.toFixed(1)}%，显示出{selectedReport.profitMargin > 20 ? '优秀的' : '良好的'}盈利能力。
              {selectedReport.roe > 25 && ' 高ROE表明公司具备优秀的资本运营效率。'}
              建议{selectedReport.revenueGrowth > 10 && selectedReport.profitMargin > 20 ? '积极关注' : '持续跟踪'}该股票。
            </p>
          </div>
        </div>
      ) : null}

      {/* 空状态 */}
      {!isLoading && !selectedReport && !error && (
        <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">📊</div>
          <div className="text-gray-400 text-lg">
            请输入股票代码或点击快速选择按钮查询财报
          </div>
        </div>
      )}

      {/* 使用提示 */}
      <div className="mt-6 bg-[#141a2a]/50 border border-[#2a3a5a]/50 rounded-xl p-4">
        <div className="text-sm text-gray-400">
          <span className="text-[#00ccff]">💡 提示：</span>
          当前使用模拟数据演示。生产环境将接入真实财报 API（如 Alpha Vantage, Financial Modeling Prep）
        </div>
      </div>
    </div>
  );
};

export default FinancialReportPage;
