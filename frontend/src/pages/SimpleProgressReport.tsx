/**
 * 简单进度报告 - 周报/月报
 * 
 * 设计原则：
 * - 白话文总结（"这周做了什么，赚了多少钱"）
 * - 进度可视化（距离目标还有多远）
 * - 下周建议（简单的行动指引）
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface ProgressReport {
  report_id: string;
  period: 'weekly' | 'monthly';
  start_date: string;
  end_date: string;
  summary: {
    actions_count: number;
    invested: number;
    profit: number;
    profit_rate: number;
  };
  goal_progress: {
    target_amount: number;
    current_amount: number;
    progress_percent: number;
    estimated_days_left: number;
  };
  highlights: string[];
  next_week_advice: string;
}

const SimpleProgressReport: React.FC = () => {
  const { instanceId } = useParams<{ instanceId: string }>();
  const navigate = useNavigate();
  
  const [report, setReport] = useState<ProgressReport | null>(null);
  const [period, setPeriod] = useState<'weekly' | 'monthly'>('weekly');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReport();
  }, [instanceId, period]);

  const loadReport = async () => {
    try {
      // TODO: 实际API调用
      // const response = await axios.get(
      //   `${API_BASE_URL}/assistant/strategies/report/${instanceId}?period=${period}`
      // );
      // setReport(response.data);
      
      // 模拟数据
      setReport({
        report_id: 'rpt_123',
        period,
        start_date: '2025-12-01',
        end_date: '2025-12-07',
        summary: {
          actions_count: 2,
          invested: 2000,
          profit: 124,
          profit_rate: 6.2
        },
        goal_progress: {
          target_amount: 50000,
          current_amount: 5234,
          progress_percent: 10.47,
          estimated_days_left: 210
        },
        highlights: [
          '本周执行了2次定投，投入¥2000',
          '账户总价值增长到¥5234，累计收益+¥234',
          '市场波动较小，策略稳定运行',
          '收益率6.2%，超过银行定期3倍'
        ],
        next_week_advice: '市场处于低位，建议继续定投。下周预计买入1次，金额¥1000。'
      });
    } catch (err) {
      console.error('加载报告失败:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !report) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#2a3a5a] border-t-[#00ccff] mx-auto shadow-lg shadow-[#00ccff]/20"></div>
          <div className="text-[#00ccff] text-lg animate-pulse">生成报告中...</div>
        </div>
      </div>
    );
  }

  const isProfitable = report.summary.profit >= 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 顶部导航 - 增强版 */}
      <header className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border-b border-[#2a3a5a] shadow-lg backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(`/assistant/strategies/running/${instanceId}`)}
                className="group flex items-center gap-2 px-3 py-2 text-gray-400 hover:text-white bg-[#1a2332] rounded-lg border border-[#2a3a5a] hover:border-[#00ccff] transition-all duration-300 hover:shadow-md hover:shadow-[#00ccff]/20"
              >
                <span className="transform group-hover:-translate-x-1 transition-transform">←</span>
                <span>返回</span>
              </button>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
                <span className="text-3xl">📊</span>
                <span>进度报告</span>
              </h1>
            </div>
            
            {/* 周期切换 - 增强版 */}
            <div className="flex gap-3">
              <button
                onClick={() => setPeriod('weekly')}
                className={`px-5 py-2.5 rounded-xl transition-all duration-300 font-semibold ${
                  period === 'weekly'
                    ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black shadow-lg shadow-[#00ccff]/30 scale-105'
                    : 'bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] hover:from-[#3a4a6a] hover:to-[#2a3a5a] shadow-md'
                }`}
              >
                📅 周报
              </button>
              <button
                onClick={() => setPeriod('monthly')}
                className={`px-5 py-2.5 rounded-xl transition-all duration-300 font-semibold ${
                  period === 'monthly'
                    ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black shadow-lg shadow-[#00ccff]/30 scale-105'
                    : 'bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] hover:from-[#3a4a6a] hover:to-[#2a3a5a] shadow-md'
                }`}
              >
                📆 月报
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* 时间标题 - 增强版 */}
        <div className="text-center animate-fadeIn">
          <div className="text-4xl font-bold mb-3 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            {period === 'weekly' ? '本周表现' : '本月表现'}
          </div>
          <div className="text-gray-400 text-lg flex items-center justify-center gap-2">
            <span className="text-[#00ccff]">📅</span>
            <span>{report.start_date} 至 {report.end_date}</span>
          </div>
        </div>

        {/* 核心数据卡片 - 增强版 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 text-center shadow-2xl hover:shadow-[#00ccff]/20 transition-all duration-300 hover:scale-[1.02]">
            <div className="text-sm text-gray-400 mb-3 flex items-center justify-center gap-2">
              <span className="text-2xl">💰</span>
              <span>本周投入</span>
            </div>
            <div className="text-4xl font-bold text-white mb-2">
              ¥{report.summary.invested.toLocaleString()}
            </div>
            <div className="text-sm text-gray-500 flex items-center justify-center gap-1">
              <span>📊</span>
              <span>{report.summary.actions_count} 次操作</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 text-center shadow-2xl hover:shadow-[#00ff88]/20 transition-all duration-300 hover:scale-[1.02]">
            <div className="text-sm text-gray-400 mb-3 flex items-center justify-center gap-2">
              <span className="text-2xl">{isProfitable ? '📈' : '📉'}</span>
              <span>本周收益</span>
            </div>
            <div className={`text-4xl font-bold mb-2 ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
              {isProfitable ? '+' : ''}¥{report.summary.profit.toLocaleString()}
            </div>
            <div className={`text-sm font-semibold flex items-center justify-center gap-1 ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
              <span>{isProfitable ? '↗' : '↘'}</span>
              <span>{isProfitable ? '+' : ''}{report.summary.profit_rate.toFixed(2)}%</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 text-center shadow-2xl hover:shadow-[#00ccff]/20 transition-all duration-300 hover:scale-[1.02]">
            <div className="text-sm text-gray-400 mb-3 flex items-center justify-center gap-2">
              <span className="text-2xl">🎯</span>
              <span>目标进度</span>
            </div>
            <div className="text-4xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent mb-2">
              {report.goal_progress.progress_percent.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500 flex items-center justify-center gap-1">
              <span>⏰</span>
              <span>预计 {report.goal_progress.estimated_days_left} 天完成</span>
            </div>
          </div>
        </div>

        {/* 目标进度条 - 增强版 */}
        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
          <h2 className="text-xl font-semibold mb-5 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
            <span className="text-3xl">🎯</span>
            <span>目标进度</span>
          </h2>
          
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-3 font-medium">
              <span className="text-gray-400 flex items-center gap-1">
                <span>📊</span>
                <span>当前: <span className="text-white">¥{report.goal_progress.current_amount.toLocaleString()}</span></span>
              </span>
              <span className="text-gray-400 flex items-center gap-1">
                <span>🎯</span>
                <span>目标: <span className="text-[#00ccff]">¥{report.goal_progress.target_amount.toLocaleString()}</span></span>
              </span>
            </div>
            
            {/* 进度条 - 增强版 */}
            <div className="w-full bg-gradient-to-r from-[#2a3a5a] to-[#1a2332] rounded-full h-10 overflow-hidden shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-[#00ccff] to-[#00ff88] flex items-center justify-end pr-4 transition-all duration-700 shadow-lg shadow-[#00ccff]/30 relative"
                style={{ width: `${Math.min(report.goal_progress.progress_percent, 100)}%` }}
              >
                <span className="text-sm font-bold text-black animate-pulse">
                  {report.goal_progress.progress_percent.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 shadow-md">
            <div className="text-sm text-gray-300 flex items-start gap-2">
              <span className="text-xl">💡</span>
              <span>
                按当前速度，预计 <span className="text-[#00ccff] font-bold text-base">
                  {report.goal_progress.estimated_days_left} 天
                </span> 后达成目标。
                继续保持定投，就像坚持每天存钱一样，小钱也能变大钱！
              </span>
            </div>
          </div>
        </div>

        {/* 本周亮点 - 增强版 */}
        <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-6 shadow-2xl">
          <h2 className="text-xl font-semibold mb-5 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
            <span className="text-3xl">✨</span>
            <span>本周亮点</span>
          </h2>
          
          <div className="space-y-3">
            {report.highlights.map((highlight, index) => (
              <div
                key={index}
                className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 flex items-start gap-3 hover:border-[#00ccff] transition-all duration-300 hover:shadow-md hover:shadow-[#00ccff]/10 group"
              >
                <div className="text-[#00ff88] text-3xl group-hover:scale-110 transition-transform">✓</div>
                <div className="text-gray-300 text-base leading-relaxed">{highlight}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 下周建议 - 增强版 */}
        <div className="bg-gradient-to-br from-[#00ccff]/10 to-[#00ff88]/10 border-2 border-[#00ccff] rounded-2xl p-6 shadow-2xl shadow-[#00ccff]/10">
          <h2 className="text-xl font-semibold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
            <span className="text-3xl">💡</span>
            <span>下周建议</span>
          </h2>
          <div className="text-gray-200 text-lg leading-relaxed pl-2 border-l-4 border-[#00ccff]">
            {report.next_week_advice}
          </div>
        </div>

        {/* 操作按钮 - 增强版 */}
        <div className="flex gap-4">
          <button
            onClick={() => navigate(`/assistant/strategies/running/${instanceId}`)}
            className="flex-1 py-5 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black rounded-xl font-bold hover:scale-[1.02] transition-all duration-300 shadow-lg shadow-[#00ccff]/30 hover:shadow-[#00ccff]/50 flex items-center justify-center gap-2 text-lg"
          >
            <span>← 返回监控页面</span>
          </button>
          <button
            onClick={() => window.print()}
            className="px-6 py-5 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:scale-[1.02] transition-all duration-300 shadow-md hover:shadow-lg flex items-center gap-2 text-base font-semibold border border-[#2a3a5a] hover:border-[#00ccff]"
          >
            <span className="text-xl">📄</span>
            <span>打印报告</span>
          </button>
        </div>

        {/* 免责声明 - 增强版 */}
        <div className="text-center text-sm text-gray-400 border-t border-[#2a3a5a] pt-6 space-y-2">
          <p className="flex items-center justify-center gap-2">
            <span className="text-yellow-500 text-lg">⚠️</span>
            <span>这是虚拟交易报告，数据仅供参考，不构成投资建议</span>
          </p>
          <p className="text-gray-500">历史表现不代表未来收益，投资需谨慎</p>
        </div>
      </div>
    </div>
  );
};

export default SimpleProgressReport;
