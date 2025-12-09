import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface FinancialReport {
  symbol: string;
  quarter: string;
  revenue: number;
  netIncome: number;
  eps: number;
  revenueGrowth: number;
  profitMargin: number;
  roe: number;
}

const FinancialReportPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchSymbol, setSearchSymbol] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<FinancialReport | null>(null);

  // 模拟财报数据
  const mockReports: FinancialReport[] = [
    {
      symbol: 'AAPL',
      quarter: '2024 Q4',
      revenue: 89498000000,
      netIncome: 22956000000,
      eps: 1.47,
      revenueGrowth: 6.07,
      profitMargin: 25.65,
      roe: 147.25
    },
    {
      symbol: 'MSFT',
      quarter: '2024 Q4',
      revenue: 62020000000,
      netIncome: 21871000000,
      eps: 2.93,
      revenueGrowth: 16.0,
      profitMargin: 35.27,
      roe: 38.45
    },
    {
      symbol: 'TSLA',
      quarter: '2024 Q3',
      revenue: 25182000000,
      netIncome: 2167000000,
      eps: 0.68,
      revenueGrowth: 7.85,
      profitMargin: 8.61,
      roe: 18.92
    },
    {
      symbol: 'GOOGL',
      quarter: '2024 Q4',
      revenue: 86309000000,
      netIncome: 20641000000,
      eps: 1.64,
      revenueGrowth: 15.09,
      profitMargin: 23.92,
      roe: 29.67
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
    const report = mockReports.find(r => r.symbol.toLowerCase() === searchSymbol.toLowerCase());
    setSelectedReport(report || null);
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
                setSelectedReport(report);
              }}
              className="px-4 py-2 bg-[#141a2a] hover:bg-[#1a2332] border border-[#2a3a5a] rounded-lg transition-all duration-300"
            >
              {report.symbol}
            </button>
          ))}
        </div>
      </div>

      {/* 财报详情 */}
      {selectedReport ? (
        <div className="space-y-6">
          {/* 公司信息卡片 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-3xl font-bold text-white">{selectedReport.symbol}</h2>
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
      ) : (
        <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">📊</div>
          <div className="text-gray-400 text-lg">
            {searchSymbol ? '未找到该股票的财报数据' : '请输入股票代码查询财报'}
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
