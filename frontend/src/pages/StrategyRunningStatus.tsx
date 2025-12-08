/**
 * 策略运行状态监控 - 助手模式核心体验
 * 
 * 设计原则：
 * - 用通俗语言描述状态
 * - 显示"下次做什么"而非"历史数据"
 * - 提供简单操作按钮
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface RunningStatus {
  instance_id: string;
  package_name: string;
  status: string;
  days_active: number;
  performance: {
    invested: number;
    current_value: number;
    profit: number;
    profit_rate: number;
  };
  next_action?: {
    date: string;
    type: string;
    amount: number;
    reason: string;
  };
}

const StrategyRunningStatus: React.FC = () => {
  const { instanceId } = useParams<{ instanceId: string }>();
  const navigate = useNavigate();
  
  const [status, setStatus] = useState<RunningStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPauseModal, setShowPauseModal] = useState(false);

  useEffect(() => {
    loadStatus();
    // 每30秒刷新一次
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, [instanceId]);

  const loadStatus = async () => {
    try {
      // TODO: 实际API调用
      // const response = await axios.get(`${API_BASE_URL}/assistant/strategies/running/${instanceId}`);
      // setStatus(response.data);
      
      // 模拟数据
      setStatus({
        instance_id: instanceId || '',
        package_name: '稳健增长定投宝',
        status: 'running',
        days_active: 15,
        performance: {
          invested: 5000,
          current_value: 5234,
          profit: 234,
          profit_rate: 4.68
        },
        next_action: {
          date: '2025-12-14',
          type: 'buy',
          amount: 1000,
          reason: '市场RSI低于30，触发买入信号'
        }
      });
    } catch (err) {
      console.error('加载运行状态失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePause = async () => {
    try {
      // await axios.post(`${API_BASE_URL}/assistant/strategies/${instanceId}/pause`);
      alert('策略已暂停');
      setShowPauseModal(false);
      navigate('/assistant');
    } catch (err) {
      alert('暂停失败，请重试');
    }
  };

  if (loading || !status) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#2a3a5a] border-t-[#00ccff] mx-auto shadow-lg shadow-[#00ccff]/20"></div>
          <div className="text-[#00ccff] text-lg animate-pulse">加载运行状态...</div>
        </div>
      </div>
    );
  }

  const isProfitable = status.performance.profit >= 0;

  // 模拟权益曲线数据
  const chartData = {
    labels: ['Day 1', 'Day 5', 'Day 10', 'Day 15'],
    datasets: [
      {
        label: '账户价值',
        data: [5000, 5050, 5180, 5234],
        borderColor: '#00ff88',
        backgroundColor: 'rgba(0, 255, 136, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: '#141a2a',
        titleColor: '#00ccff',
        bodyColor: '#ffffff',
        borderColor: '#2a3a5a',
        borderWidth: 1
      }
    },
    scales: {
      y: {
        ticks: { color: '#888888' },
        grid: { color: '#2a3a5a' }
      },
      x: {
        ticks: { color: '#888888' },
        grid: { color: '#2a3a5a' }
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 顶部导航 - 增强版 */}
      <header className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border-b border-[#2a3a5a] shadow-lg backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/assistant')}
                className="group flex items-center gap-2 px-3 py-2 text-gray-400 hover:text-white bg-[#1a2332] rounded-lg border border-[#2a3a5a] hover:border-[#00ccff] transition-all duration-300 hover:shadow-md hover:shadow-[#00ccff]/20"
              >
                <span className="transform group-hover:-translate-x-1 transition-transform">←</span>
                <span>返回</span>
              </button>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">{status.package_name}</h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-4 py-2 bg-gradient-to-r from-[#00ff88] to-[#00ccaa] text-black rounded-full text-sm font-bold shadow-md shadow-[#00ff88]/30">
                运行中
              </div>
              <span className="text-gray-400">已运行 <span className="text-[#00ccff] font-semibold">{status.days_active}</span> 天</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：当前表现 + 图表 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 当前表现卡片 - 增强版 */}
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-8 shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <span className="text-3xl">📊</span>
                <span className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">当前表现</span>
              </h2>
              
              <div className="grid grid-cols-3 gap-5 mb-8">
                <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] p-5 rounded-xl border border-[#2a3a5a] shadow-inner">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gray-500"></span>
                    投入金额
                  </div>
                  <div className="text-3xl font-bold">
                    ¥{status.performance.invested.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] p-5 rounded-xl border border-[#2a3a5a] shadow-inner">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#00ccff]"></span>
                    当前价值
                  </div>
                  <div className="text-3xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                    ¥{status.performance.current_value.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] p-5 rounded-xl border border-[#2a3a5a] shadow-inner">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${isProfitable ? 'bg-[#00ff88]' : 'bg-[#ff4444]'}`}></span>
                    累计收益
                  </div>
                  <div className={`text-3xl font-bold ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                    {isProfitable ? '+' : ''}¥{status.performance.profit.toLocaleString()}
                  </div>
                  <div className={`text-sm mt-1 ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                    {isProfitable ? '+' : ''}{status.performance.profit_rate.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* 通俗化解读 - 增强版 */}
              <div className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-6 shadow-inner">
                <div className="text-sm text-gray-400 mb-3 flex items-center gap-2">
                  <span className="text-xl">💡</span>
                  <span className="font-semibold">表现解读</span>
                </div>
                <div className="text-gray-300 leading-relaxed">
                  {isProfitable ? (
                    <>
                      您的投资正在<span className="text-[#00ff88] font-semibold">稳健增长</span>，
                      目前收益率{status.performance.profit_rate.toFixed(2)}%，
                      相当于{status.days_active}天赚了
                      <span className="text-[#00ff88] font-semibold"> {Math.round(status.performance.profit / status.days_active)} 元/天</span>，
                      表现{status.performance.profit_rate > 5 ? '优秀' : '良好'}！
                    </>
                  ) : (
                    <>
                      当前有小幅浮亏，这是正常波动。
                      建议保持定投，长期来看有望回本并盈利。
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* 权益曲线图表 - 增强版 */}
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-8 shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <span className="text-3xl">📈</span>
                <span className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">账户价值走势</span>
              </h2>
              <div className="h-64 bg-gradient-to-br from-[#0a0e17] to-[#141a2a] rounded-lg p-4 border border-[#2a3a5a]">
                <Line data={chartData} options={chartOptions} />
              </div>
              <div className="mt-4 text-sm text-gray-400 text-center bg-gradient-to-r from-[#1a2332] to-[#141a2a] rounded-lg p-3 border border-[#2a3a5a]/50">
                这条线显示您的账户价值变化，向上代表盈利
              </div>
            </div>
          </div>

          {/* 右侧：下次操作 + 操作按钮 */}
          <div className="space-y-6">
            {/* 下次操作卡片 - 增强版 */}
            {status.next_action && (
              <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6 shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300">
                <h2 className="text-lg font-semibold mb-5 flex items-center gap-2">
                  <span className="text-2xl">📅</span>
                  <span className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">下次操作</span>
                </h2>
                
                <div className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-5 mb-5 shadow-inner">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-gray-400">预计时间</span>
                    <span className="font-semibold text-[#00ccff]">{status.next_action.date}</span>
                  </div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-gray-400">操作类型</span>
                    <span className="px-3 py-1 bg-gradient-to-r from-[#00ff88] to-[#00ccaa] text-black rounded-full text-sm font-bold shadow-md shadow-[#00ff88]/30">
                      {status.next_action.type === 'buy' ? '买入' : '卖出'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">金额</span>
                    <span className="font-semibold text-xl bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                      ¥{status.next_action.amount.toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="bg-[#0a0e17] border border-[#2a3a5a] rounded-xl p-5">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="text-lg">💡</span>
                    <span>触发原因</span>
                  </div>
                  <div className="text-sm text-gray-300 leading-relaxed">{status.next_action.reason}</div>
                </div>
              </div>
            )}

            {/* 操作按钮 - 增强版 */}
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6 shadow-2xl">
              <h2 className="text-lg font-semibold mb-5 flex items-center gap-2">
                <span className="text-2xl">⚙️</span>
                <span className="bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">管理策略</span>
              </h2>
              
              <div className="space-y-3">
                <button
                  onClick={() => navigate(`/assistant/strategies/report/${instanceId}`)}
                  className="w-full py-4 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:from-[#3a4a6a] hover:to-[#2a3a5a] transition-all duration-300 shadow-md hover:shadow-lg hover:shadow-[#00ccff]/20 font-semibold flex items-center justify-center gap-2 group"
                >
                  <span className="text-xl">📊</span>
                  <span>查看详细报告</span>
                  <span className="transform group-hover:translate-x-1 transition-transform">→</span>
                </button>
                
                <button
                  onClick={() => navigate(`/assistant/strategies/adjust/${instanceId}`)}
                  className="w-full py-4 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:from-[#3a4a6a] hover:to-[#2a3a5a] transition-all duration-300 shadow-md hover:shadow-lg hover:shadow-[#00ccff]/20 font-semibold flex items-center justify-center gap-2 group"
                >
                  <span className="text-xl">🔧</span>
                  <span>调整参数</span>
                  <span className="transform group-hover:translate-x-1 transition-transform">→</span>
                </button>
                
                <button
                  onClick={() => setShowPauseModal(true)}
                  className="w-full py-4 bg-gradient-to-r from-[#ff4444]/20 to-[#ff2222]/15 border-2 border-[#ff4444] rounded-xl hover:from-[#ff4444]/30 hover:to-[#ff2222]/25 transition-all duration-300 text-[#ff4444] font-semibold shadow-md hover:shadow-lg hover:shadow-[#ff4444]/20 flex items-center justify-center gap-2"
                >
                  <span className="text-xl">⏸️</span>
                  <span>暂停策略</span>
                </button>
              </div>
            </div>

            {/* 帮助提示 - 增强版 */}
            <div className="bg-gradient-to-r from-[#00ccff]/10 to-[#00ff88]/10 border-2 border-[#00ccff] rounded-xl p-5 shadow-lg shadow-[#00ccff]/20">
              <div className="text-sm font-semibold mb-3 flex items-center gap-2">
                <span className="text-2xl">💡</span>
                <span className="text-[#00ccff]">提示</span>
              </div>
              <ul className="text-sm text-gray-300 space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-[#00ccff]">•</span>
                  <span>定投策略需要长期坚持</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#00ccff]">•</span>
                  <span>短期波动是正常现象</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#00ccff]">•</span>
                  <span>可随时调整金额和周期</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#00ccff]">•</span>
                  <span>这是虚拟交易，可放心尝试</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 暂停确认弹窗 - 增强版 */}
      {showPauseModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border-2 border-[#2a3a5a] rounded-2xl p-10 max-w-md shadow-2xl shadow-[#00ccff]/20 animate-scaleIn">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">⏸️</div>
              <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">确认暂停策略？</h2>
            </div>
            <p className="text-gray-300 mb-8 leading-relaxed text-center">
              暂停后，策略将停止自动交易，但不会卖出现有持仓。
              您可以随时重新启动策略。
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setShowPauseModal(false)}
                className="flex-1 py-4 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:from-[#3a4a6a] hover:to-[#2a3a5a] transition-all duration-300 font-semibold shadow-md hover:shadow-lg"
              >
                取消
              </button>
              <button
                onClick={handlePause}
                className="flex-1 py-4 bg-gradient-to-r from-[#ff4444] to-[#ff2222] rounded-xl hover:from-[#dd3333] hover:to-[#dd1111] transition-all duration-300 font-semibold shadow-lg hover:shadow-xl hover:shadow-[#ff4444]/30"
              >
                确认暂停
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategyRunningStatus;
