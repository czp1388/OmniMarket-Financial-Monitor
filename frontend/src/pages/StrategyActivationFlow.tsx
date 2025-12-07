/**
 * 策略激活流程 - 助手模式核心体验
 * 
 * 3步向导设计：
 * Step 1: 确认策略信息（看懂这是什么）
 * Step 2: 设置参数（决定怎么做）
 * Step 3: 确认并启动（放心开始）
 * 
 * 设计原则：
 * - 每一步都用白话解释
 * - 默认值已优化，可直接下一步
 * - 关键决策点提供tooltips帮助
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface StrategyPackage {
  package_id: string;
  friendly_name: string;
  icon: string;
  tagline: string;
  description: string;
  risk_score: number;
  expected_return: string;
  max_drawdown: string;
  suitable_for: string[];
  analogy: string;
}

interface ActivationParams {
  investment_amount: number;
  frequency: 'weekly' | 'monthly';
  auto_execute: boolean;
}

const StrategyActivationFlow: React.FC = () => {
  const { packageId } = useParams<{ packageId: string }>();
  const navigate = useNavigate();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [strategy, setStrategy] = useState<StrategyPackage | null>(null);
  const [params, setParams] = useState<ActivationParams>({
    investment_amount: 5000,
    frequency: 'monthly',
    auto_execute: false
  });
  const [agreedToRisk, setAgreedToRisk] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStrategyDetails();
  }, [packageId]);

  const loadStrategyDetails = async () => {
    try {
      // 调用真实 API 获取策略包详情
      const response = await axios.get(`http://localhost:8000/api/v1/assistant/strategies/packages/${packageId}`);
      const strategyData = response.data;
      
      const strategyPackage: StrategyPackage = {
        package_id: strategyData.package_id,
        friendly_name: strategyData.friendly_name,
        icon: strategyData.icon,
        tagline: strategyData.tagline,
        description: strategyData.description,
        risk_score: strategyData.risk_score,
        expected_return: strategyData.expected_return,
        max_drawdown: strategyData.max_drawdown,
        suitable_for: strategyData.suitable_for,
        analogy: strategyData.analogy
      };
      setStrategy(strategyPackage);
    } catch (err) {
      console.error('加载策略信息失败:', err);
      // 降级到默认数据
      const fallbackStrategy: StrategyPackage = {
        package_id: packageId || 'stable_growth_low_risk',
        friendly_name: '稳健增长定投宝',
        icon: '🛡️',
        tagline: '安全第一，稳健增值',
        description: '采用低风险策略，通过定期定额投资，在控制风险的前提下实现资产稳健增长',
        risk_score: 2,
        expected_return: '年化 8-12%',
        max_drawdown: '最大回撤 ≤ 5%',
        suitable_for: ['投资新手', '风险厌恶者', '长期投资者'],
        analogy: '就像超市促销时多买，市场低迷时加仓，长期来看平均成本更低'
      };
      setStrategy(fallbackStrategy);
    }
  };

  const handleActivate = async () => {
    if (!agreedToRisk) {
      alert('请先阅读并确认风险提示');
      return;
    }

    setLoading(true);
    try {
      // 调用真实 API 激活策略
      const response = await axios.post('http://localhost:8000/api/v1/assistant/strategies/activate', {
        user_goal: 'stable_growth',  // 根据策略包推断
        risk_tolerance: investmentAmount < 10000 ? 'low' : 'medium',
        investment_amount: investmentAmount,
        investment_horizon: investmentPeriod,
        auto_execute: false
      });
      
      const instanceId = response.data.strategy_package_id;
      
      // 跳转到运行状态页
      navigate(`/assistant/strategies/running/${instanceId}`);
    } catch (err: any) {
      console.error('激活失败:', err);
      setError('激活失败，请重试: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (!strategy) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="text-[#00ccff]">加载中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] text-white">
      {/* 顶部导航 */}
      <header className="bg-[#141a2a] border-b border-[#2a3a5a] px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <button
            onClick={() => navigate('/assistant')}
            className="text-gray-400 hover:text-white"
          >
            ← 返回
          </button>
          <h1 className="text-xl font-bold text-[#00ccff]">激活策略</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* 进度指示器 */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center flex-1">
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center font-bold
                  ${currentStep >= step ? 'bg-[#00ccff] text-black' : 'bg-[#2a3a5a] text-gray-400'}
                `}>
                  {step}
                </div>
                {step < 3 && (
                  <div className={`flex-1 h-1 mx-2 ${currentStep > step ? 'bg-[#00ccff]' : 'bg-[#2a3a5a]'}`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-sm text-gray-400">
            <span>确认策略</span>
            <span>设置参数</span>
            <span>开始运行</span>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-[#ff4444] bg-opacity-20 border border-[#ff4444] rounded-lg p-4 mb-6">
            <p className="text-[#ff4444]">{error}</p>
          </div>
        )}

        {/* Step 1: 确认策略信息 */}
        {currentStep === 1 && (
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-8">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">{strategy.icon}</div>
              <h2 className="text-3xl font-bold mb-2">{strategy.friendly_name}</h2>
              <p className="text-xl text-gray-400">{strategy.tagline}</p>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <div className="bg-[#1a2332] rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">风险等级</div>
                <div className="flex items-center gap-2">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-8 h-8 rounded ${
                        i < strategy.risk_score
                          ? strategy.risk_score <= 2
                            ? 'bg-[#00ff88]'
                            : strategy.risk_score <= 3
                            ? 'bg-[#ffaa00]'
                            : 'bg-[#ff4444]'
                          : 'bg-[#2a3a5a]'
                      }`}
                    />
                  ))}
                  <span className="ml-2">{strategy.risk_score}/5</span>
                </div>
              </div>

              <div className="bg-[#1a2332] rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">预期收益</div>
                <div className="text-2xl font-bold text-[#00ff88]">{strategy.expected_return}</div>
              </div>
            </div>

            <div className="bg-[#1a2332] rounded-lg p-6 mb-8">
              <h3 className="font-semibold mb-2 text-[#00ccff]">策略说明</h3>
              <p className="text-gray-300 mb-4">{strategy.description}</p>
              
              <h3 className="font-semibold mb-2 text-[#00ccff]">通俗理解</h3>
              <p className="text-gray-300 mb-4">{strategy.analogy}</p>

              <h3 className="font-semibold mb-2 text-[#00ccff]">适合人群</h3>
              <div className="flex flex-wrap gap-2">
                {strategy.suitable_for.map((item, index) => (
                  <span key={index} className="px-3 py-1 bg-[#2a3a5a] rounded-full text-sm">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <button
              onClick={() => setCurrentStep(2)}
              className="w-full py-4 bg-[#00ccff] text-black font-bold rounded-lg hover:bg-[#00aadd] transition-colors"
            >
              看起来不错，继续 →
            </button>
          </div>
        )}

        {/* Step 2: 设置参数 */}
        {currentStep === 2 && (
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-8">
            <h2 className="text-2xl font-bold mb-6">设置投资参数</h2>

            {/* 投资金额 */}
            <div className="mb-8">
              <label className="block mb-2 font-semibold">
                投资金额
                <span className="ml-2 text-sm text-gray-400">（可随时调整）</span>
              </label>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setParams({ ...params, investment_amount: Math.max(1000, params.investment_amount - 1000) })}
                  className="w-12 h-12 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
                >
                  -
                </button>
                <div className="flex-1 bg-[#1a2332] rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-[#00ccff]">
                    ¥{params.investment_amount.toLocaleString()}
                  </div>
                </div>
                <button
                  onClick={() => setParams({ ...params, investment_amount: params.investment_amount + 1000 })}
                  className="w-12 h-12 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
                >
                  +
                </button>
              </div>
              <div className="mt-2 text-sm text-gray-400">
                💡 建议投入闲钱的30-50%，不影响日常生活
              </div>
            </div>

            {/* 定投周期 */}
            <div className="mb-8">
              <label className="block mb-2 font-semibold">定投周期</label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setParams({ ...params, frequency: 'weekly' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    params.frequency === 'weekly'
                      ? 'border-[#00ccff] bg-[#00ccff] bg-opacity-20'
                      : 'border-[#2a3a5a] hover:border-[#3a4a6a]'
                  }`}
                >
                  <div className="font-bold mb-1">每周定投</div>
                  <div className="text-sm text-gray-400">
                    每周投¥{Math.round(params.investment_amount / 4)}
                  </div>
                </button>
                <button
                  onClick={() => setParams({ ...params, frequency: 'monthly' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    params.frequency === 'monthly'
                      ? 'border-[#00ccff] bg-[#00ccff] bg-opacity-20'
                      : 'border-[#2a3a5a] hover:border-[#3a4a6a]'
                  }`}
                >
                  <div className="font-bold mb-1">每月定投</div>
                  <div className="text-sm text-gray-400">
                    每月投¥{params.investment_amount.toLocaleString()}
                  </div>
                </button>
              </div>
            </div>

            {/* 自动执行 */}
            <div className="mb-8">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={params.auto_execute}
                  onChange={(e) => setParams({ ...params, auto_execute: e.target.checked })}
                  className="w-5 h-5"
                />
                <div>
                  <div className="font-semibold">自动执行交易</div>
                  <div className="text-sm text-gray-400">
                    开启后，系统会在合适时机自动买入，无需手动确认（当前为虚拟交易）
                  </div>
                </div>
              </label>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setCurrentStep(1)}
                className="flex-1 py-4 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
              >
                ← 上一步
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="flex-1 py-4 bg-[#00ccff] text-black font-bold rounded-lg hover:bg-[#00aadd] transition-colors"
              >
                下一步 →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: 确认并启动 */}
        {currentStep === 3 && (
          <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-8">
            <h2 className="text-2xl font-bold mb-6">确认信息</h2>

            {/* 参数汇总 */}
            <div className="bg-[#1a2332] rounded-lg p-6 mb-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="text-sm text-gray-400 mb-1">策略名称</div>
                  <div className="font-semibold">{strategy.friendly_name}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">风险等级</div>
                  <div className="font-semibold">{strategy.risk_score}/5</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">投资金额</div>
                  <div className="font-semibold text-[#00ccff]">
                    ¥{params.investment_amount.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">定投周期</div>
                  <div className="font-semibold">
                    {params.frequency === 'weekly' ? '每周' : '每月'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">自动执行</div>
                  <div className="font-semibold">
                    {params.auto_execute ? '是' : '否'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">预期年化收益</div>
                  <div className="font-semibold text-[#00ff88]">{strategy.expected_return}</div>
                </div>
              </div>
            </div>

            {/* 风险提示 */}
            <div className="bg-[#ff4444] bg-opacity-10 border border-[#ff4444] rounded-lg p-6 mb-6">
              <h3 className="font-bold mb-3 text-[#ff4444]">⚠️ 重要风险提示</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• 这是虚拟交易，不涉及真实资金</li>
                <li>• 历史收益不代表未来表现</li>
                <li>• 投资有风险，可能面临本金损失</li>
                <li>• 建议仅投入可承受损失的闲钱</li>
                <li>• 最大可能回撤：{strategy.max_drawdown}</li>
              </ul>
              
              <label className="flex items-center gap-3 mt-4 cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreedToRisk}
                  onChange={(e) => setAgreedToRisk(e.target.checked)}
                  className="w-5 h-5"
                />
                <span className="font-semibold">我已阅读并理解上述风险</span>
              </label>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setCurrentStep(2)}
                className="flex-1 py-4 bg-[#2a3a5a] rounded-lg hover:bg-[#3a4a6a] transition-colors"
                disabled={loading}
              >
                ← 上一步
              </button>
              <button
                onClick={handleActivate}
                disabled={!agreedToRisk || loading}
                className={`flex-1 py-4 font-bold rounded-lg transition-colors ${
                  agreedToRisk && !loading
                    ? 'bg-[#00ff88] text-black hover:bg-[#00dd77]'
                    : 'bg-[#2a3a5a] text-gray-500 cursor-not-allowed'
                }`}
              >
                {loading ? '启动中...' : '🚀 启动策略'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyActivationFlow;
