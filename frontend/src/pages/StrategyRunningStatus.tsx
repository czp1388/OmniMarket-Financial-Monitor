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
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="text-[#00ccff]">加载中...</div>
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
    <div className="min-h-screen bg-[#0a0e17] text-white">
      {/* 顶部导航 */}
      <header className="bg-[#141a2a] border-b border-[#2a3a5a] px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/assistant')}
              className="text-gray-400 hover:text-white"
            >
              ← 返回
            </button>
            <h1 className="text-xl font-bold text-[#00ccff]">{status.package_name}</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="px-3 py-1 bg-[#00ff88] text-black rounded-full text-sm font-bold">
              运行中
            </div>
            <span className="text-gray-400">已运行 {status.days_active} 天</span>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：当前表现 + 图表 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 当前表现卡片 */}
            <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4 text-[#00ccff]">📊 当前表现</h2>
              
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div>
                  <div className="text-sm text-gray-400 mb-1">投入金额</div>
                  <div className="text-2xl font-bold">
                    ¥{status.performance.invested.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">当前价值</div>
                  <div className="text-2xl font-bold text-[#00ccff]">
                    ¥{status.performance.current_value.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">累计收益</div>
                  <div className={`text-2xl font-bold ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                    {isProfitable ? '+' : ''}¥{status.performance.profit.toLocaleString()}
                  </div>
                  <div className={`text-sm ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                    {isProfitable ? '+' : ''}{status.performance.profit_rate.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* 通俗化解读 */}
              <div className="bg-[#1a2332] border border-[#2a3a5a] rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">💡 表现解读</div>
                <div className="text-gray-300">
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

            {/* 权益曲线图表 */}
            <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4 text-[#00ccff]">📈 账户价值走势</h2>
              <div className="h-64">
                <Line data={chartData} options={chartOptions} />
              </div>
              <div className="mt-4 text-sm text-gray-400 text-center">
                这条线显示您的账户价值变化，向上代表盈利
              </div>
            </div>
          </div>

          {/* 右侧：下次操作 + 操作按钮 */}
          <div className="space-y-6">
            {/* 下次操作卡片 */}
            {status.next_action && (
              <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4 text-[#00ccff]">📅 下次操作</h2>
                
                <div className="bg-[#1a2332] border border-[#2a3a5a] rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">预计时间</span>
                    <span className="font-semibold">{status.next_action.date}</span>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">操作类型</span>
                    <span className="px-3 py-1 bg-[#00ff88] text-black rounded-full text-sm font-bold">
                      {status.next_action.type === 'buy' ? '买入' : '卖出'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">金额</span>
                    <span className="font-semibold text-[#00ccff]">
                      ¥{status.next_action.amount.toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="bg-[#0a0e17] border border-[#2a3a5a] rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">触发原因</div>
                  <div className="text-sm text-gray-300">{status.next_action.reason}</div>
                </div>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
              <h2 className="text-lg font-semibold mb-4 text-[#00ccff]">⚙️ 管理策略</h2>
              
              <div className="space-y-3">
                <button
                  onClick={() => navigate(`/assistant/strategies/report/${instanceId}`)}
                  className="w-full py-3 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
                >
                  📊 查看详细报告
                </button>
                
                <button
                  onClick={() => navigate(`/assistant/strategies/adjust/${instanceId}`)}
                  className="w-full py-3 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
                >
                  🔧 调整参数
                </button>
                
                <button
                  onClick={() => setShowPauseModal(true)}
                  className="w-full py-3 bg-[#ff4444] bg-opacity-20 border border-[#ff4444] rounded-lg hover:bg-opacity-30 transition-colors text-[#ff4444]"
                >
                  ⏸️ 暂停策略
                </button>
              </div>
            </div>

            {/* 帮助提示 */}
            <div className="bg-[#00ccff] bg-opacity-10 border border-[#00ccff] rounded-lg p-4">
              <div className="text-sm text-[#00ccff] font-semibold mb-2">💡 提示</div>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• 定投策略需要长期坚持</li>
                <li>• 短期波动是正常现象</li>
                <li>• 可随时调整金额和周期</li>
                <li>• 这是虚拟交易，可放心尝试</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 暂停确认弹窗 */}
      {showPauseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-8 max-w-md">
            <h2 className="text-2xl font-bold mb-4">确认暂停策略？</h2>
            <p className="text-gray-300 mb-6">
              暂停后，策略将停止自动交易，但不会卖出现有持仓。
              您可以随时重新启动策略。
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setShowPauseModal(false)}
                className="flex-1 py-3 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
              >
                取消
              </button>
              <button
                onClick={handlePause}
                className="flex-1 py-3 bg-[#ff4444] rounded-lg hover:bg-[#dd3333] transition-colors"
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
