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
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="text-[#00ccff]">生成报告中...</div>
      </div>
    );
  }

  const isProfitable = report.summary.profit >= 0;

  return (
    <div className="min-h-screen bg-[#0a0e17] text-white">
      {/* 顶部导航 */}
      <header className="bg-[#141a2a] border-b border-[#2a3a5a] px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(`/assistant/strategies/running/${instanceId}`)}
              className="text-gray-400 hover:text-white"
            >
              ← 返回
            </button>
            <h1 className="text-xl font-bold text-[#00ccff]">进度报告</h1>
          </div>
          
          {/* 周期切换 */}
          <div className="flex gap-2">
            <button
              onClick={() => setPeriod('weekly')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                period === 'weekly'
                  ? 'bg-[#00ccff] text-black'
                  : 'bg-[#2a3a5a] hover:bg-[#3a4a6a]'
              }`}
            >
              周报
            </button>
            <button
              onClick={() => setPeriod('monthly')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                period === 'monthly'
                  ? 'bg-[#00ccff] text-black'
                  : 'bg-[#2a3a5a] hover:bg-[#3a4a6a]'
              }`}
            >
              月报
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* 时间标题 */}
        <div className="text-center">
          <div className="text-3xl font-bold mb-2">
            {period === 'weekly' ? '本周表现' : '本月表现'}
          </div>
          <div className="text-gray-400">
            {report.start_date} 至 {report.end_date}
          </div>
        </div>

        {/* 核心数据卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">本周投入</div>
            <div className="text-3xl font-bold text-[#00ccff]">
              ¥{report.summary.invested.toLocaleString()}
            </div>
            <div className="text-sm text-gray-400 mt-2">
              {report.summary.actions_count} 次操作
            </div>
          </div>

          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">本周收益</div>
            <div className={`text-3xl font-bold ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
              {isProfitable ? '+' : ''}¥{report.summary.profit.toLocaleString()}
            </div>
            <div className={`text-sm mt-2 ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
              {isProfitable ? '+' : ''}{report.summary.profit_rate.toFixed(2)}%
            </div>
          </div>

          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">目标进度</div>
            <div className="text-3xl font-bold text-[#00ccff]">
              {report.goal_progress.progress_percent.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400 mt-2">
              预计 {report.goal_progress.estimated_days_left} 天完成
            </div>
          </div>
        </div>

        {/* 目标进度条 */}
        <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-[#00ccff]">🎯 目标进度</h2>
          
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span>当前: ¥{report.goal_progress.current_amount.toLocaleString()}</span>
              <span>目标: ¥{report.goal_progress.target_amount.toLocaleString()}</span>
            </div>
            
            {/* 进度条 */}
            <div className="w-full bg-[#2a3a5a] rounded-full h-8 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#00ccff] to-[#00ff88] flex items-center justify-end pr-4 transition-all duration-500"
                style={{ width: `${Math.min(report.goal_progress.progress_percent, 100)}%` }}
              >
                <span className="text-sm font-bold text-black">
                  {report.goal_progress.progress_percent.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          <div className="bg-[#1a2332] border border-[#2a3a5a] rounded-lg p-4">
            <div className="text-sm text-gray-300">
              按当前速度，预计 <span className="text-[#00ccff] font-semibold">
                {report.goal_progress.estimated_days_left} 天
              </span> 后达成目标。
              继续保持定投，就像坚持每天存钱一样，小钱也能变大钱！
            </div>
          </div>
        </div>

        {/* 本周亮点 */}
        <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-[#00ccff]">✨ 本周亮点</h2>
          
          <div className="space-y-3">
            {report.highlights.map((highlight, index) => (
              <div
                key={index}
                className="bg-[#1a2332] border border-[#2a3a5a] rounded-lg p-4 flex items-start gap-3"
              >
                <div className="text-[#00ff88] text-xl">✓</div>
                <div className="text-gray-300">{highlight}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 下周建议 */}
        <div className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-opacity-10 border border-[#00ccff] rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-[#00ccff]">💡 下周建议</h2>
          <div className="text-gray-300 text-lg leading-relaxed">
            {report.next_week_advice}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-4">
          <button
            onClick={() => navigate(`/assistant/strategies/running/${instanceId}`)}
            className="flex-1 py-4 bg-[#00ccff] text-black rounded-lg font-bold hover:bg-[#00bbee] transition-colors"
          >
            返回监控页面
          </button>
          <button
            onClick={() => window.print()}
            className="px-6 py-4 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
          >
            📄 打印报告
          </button>
        </div>

        {/* 免责声明 */}
        <div className="text-center text-sm text-gray-400 border-t border-[#2a3a5a] pt-6">
          <p>⚠️ 这是虚拟交易报告，数据仅供参考，不构成投资建议</p>
          <p className="mt-2">历史表现不代表未来收益，投资需谨慎</p>
        </div>
      </div>
    </div>
  );
};

export default SimpleProgressReport;
