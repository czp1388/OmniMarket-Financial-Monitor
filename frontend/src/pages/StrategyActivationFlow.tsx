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
      <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-[#2a3a5a] border-t-[#00ccff] mx-auto shadow-lg shadow-[#00ccff]/20"></div>
          <div className="text-[#00ccff] text-lg animate-pulse">加载策略详情...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 顶部导航 - 增强版 */}
      <header className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border-b border-[#2a3a5a] shadow-lg backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/assistant')}
              className="group flex items-center gap-2 px-3 py-2 text-gray-400 hover:text-white bg-[#1a2332] rounded-lg border border-[#2a3a5a] hover:border-[#00ccff] transition-all duration-300 hover:shadow-md hover:shadow-[#00ccff]/20"
            >
              <span className="transform group-hover:-translate-x-1 transition-transform">←</span>
              <span>返回</span>
            </button>
            <div className="flex-1">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                激活投资策略
              </h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* 进度指示器 - 增强版 */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-4">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center flex-1">
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300
                  ${currentStep >= step 
                    ? 'bg-gradient-to-br from-[#00ccff] to-[#00ff88] text-black shadow-lg shadow-[#00ccff]/30 scale-110' 
                    : 'bg-[#2a3a5a] text-gray-400'}
                `}>
                  {currentStep > step ? '✓' : step}
                </div>
                {step < 3 && (
                  <div className={`flex-1 h-1.5 mx-3 rounded-full transition-all duration-500 ${currentStep > step ? 'bg-gradient-to-r from-[#00ccff] to-[#00ff88]' : 'bg-[#2a3a5a]'}`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-sm font-medium">
            <span className={currentStep >= 1 ? 'text-[#00ccff]' : 'text-gray-400'}>确认策略</span>
            <span className={currentStep >= 2 ? 'text-[#00ccff]' : 'text-gray-400'}>设置参数</span>
            <span className={currentStep >= 3 ? 'text-[#00ccff]' : 'text-gray-400'}>开始运行</span>
          </div>
        </div>

        {/* 错误提示 - 增强版 */}
        {error && (
          <div className="bg-gradient-to-r from-[#ff4444]/20 to-[#ff2222]/20 border border-[#ff4444] rounded-xl p-5 mb-6 shadow-lg shadow-[#ff4444]/20 animate-fadeIn">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⚠️</span>
              <p className="text-[#ff4444] flex-1">{error}</p>
            </div>
          </div>
        )}

        {/* Step 1: 确认策略信息 - 增强版 */}
        {currentStep === 1 && (
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-10 shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300 animate-fadeIn">
            <div className="text-center mb-8">
              <div className="inline-block text-8xl mb-6 transform hover:scale-110 transition-transform duration-300">{strategy.icon}</div>
              <h2 className="text-4xl font-bold mb-3 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">{strategy.friendly_name}</h2>
              <p className="text-2xl text-gray-400">{strategy.tagline}</p>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] rounded-xl p-6 border border-[#2a3a5a] hover:border-[#00ccff]/50 transition-all duration-300 hover:shadow-lg hover:shadow-[#00ccff]/20">
                <div className="text-sm text-gray-400 mb-3 font-medium flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-gray-500"></span>
                  风险等级
                </div>
                <div className="flex items-center gap-2">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-10 h-10 rounded-lg transition-all duration-300 ${
                        i < strategy.risk_score
                          ? strategy.risk_score <= 2
                            ? 'bg-gradient-to-br from-[#00ff88] to-[#00ccaa] shadow-md shadow-[#00ff88]/30'
                            : strategy.risk_score <= 3
                            ? 'bg-gradient-to-br from-[#ffaa00] to-[#ff8800] shadow-md shadow-[#ffaa00]/30'
                            : 'bg-gradient-to-br from-[#ff4444] to-[#ff2222] shadow-md shadow-[#ff4444]/30'
                          : 'bg-[#2a3a5a]'
                      }`}
                    />
                  ))}
                  <span className="ml-3 text-xl font-bold">{strategy.risk_score}/5</span>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] rounded-xl p-6 border border-[#2a3a5a] hover:border-[#00ff88]/50 transition-all duration-300 hover:shadow-lg hover:shadow-[#00ff88]/20">
                <div className="text-sm text-gray-400 mb-3 font-medium flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#00ff88]"></span>
                  预期收益
                </div>
                <div className="text-3xl font-bold text-[#00ff88]">{strategy.expected_return}</div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] rounded-xl p-8 mb-8 border border-[#2a3a5a] shadow-inner">
              <h3 className="font-semibold mb-3 text-xl flex items-center gap-2">
                <span className="text-[#00ccff]">📋</span>
                <span className="text-transparent bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text">策略说明</span>
              </h3>
              <p className="text-gray-300 mb-6 leading-relaxed text-lg">{strategy.description}</p>
              
              <h3 className="font-semibold mb-3 text-xl flex items-center gap-2">
                <span className="text-[#00ccff]">💡</span>
                <span className="text-transparent bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text">通俗理解</span>
              </h3>
              <p className="text-gray-300 mb-6 leading-relaxed text-lg">{strategy.analogy}</p>

              <h3 className="font-semibold mb-4 text-xl flex items-center gap-2">
                <span className="text-[#00ccff]">👥</span>
                <span className="text-transparent bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text">适合人群</span>
              </h3>
              <div className="flex flex-wrap gap-3">
                {strategy.suitable_for.map((item, index) => (
                  <span key={index} className="px-4 py-2 bg-gradient-to-r from-[#2a3a5a] to-[#1a2332] border border-[#2a3a5a] rounded-full text-sm font-medium hover:border-[#00ccff] hover:shadow-md hover:shadow-[#00ccff]/20 transition-all duration-300">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <button
              onClick={() => setCurrentStep(2)}
              className="w-full py-5 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold text-lg rounded-xl hover:from-[#00aadd] hover:to-[#00ccaa] transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-[#00ccff]/30 transform hover:scale-[1.02] flex items-center justify-center gap-2 group"
            >
              <span>看起来不错，继续</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </button>
          </div>
        )}

        {/* Step 2: 设置参数 - 增强版 */}
        {currentStep === 2 && (
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-10 shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300 animate-fadeIn">
            <h2 className="text-3xl font-bold mb-8 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">设置投资参数</h2>

            {/* 投资金额 */}
            <div className="mb-10">
              <label className="block mb-4 text-lg font-semibold flex items-center gap-2">
                <span className="text-[#00ccff]">💰</span>
                <span>投资金额</span>
                <span className="ml-2 text-sm text-gray-400 font-normal">（可随时调整）</span>
              </label>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setParams({ ...params, investment_amount: Math.max(1000, params.investment_amount - 1000) })}
                  className="w-14 h-14 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:from-[#3a4a6a] hover:to-[#2a3a5a] transition-all duration-300 font-bold text-xl shadow-md hover:shadow-lg hover:shadow-[#00ccff]/20 hover:scale-105"
                >
                  -
                </button>
                <div className="flex-1 bg-gradient-to-br from-[#1a2332] to-[#141a2a] rounded-xl p-6 text-center border border-[#2a3a5a] shadow-inner">
                  <div className="text-4xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                    ¥{params.investment_amount.toLocaleString()}
                  </div>
                </div>
                <button
                  onClick={() => setParams({ ...params, investment_amount: params.investment_amount + 1000 })}
                  className="w-14 h-14 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:from-[#3a4a6a] hover:to-[#2a3a5a] transition-all duration-300 font-bold text-xl shadow-md hover:shadow-lg hover:shadow-[#00ccff]/20 hover:scale-105"
                >
                  +
                </button>
              </div>
              <div className="mt-4 text-sm text-gray-400 bg-gradient-to-r from-[#1a2332] to-[#141a2a] rounded-lg p-4 border border-[#2a3a5a]/50">
                <span className="text-lg mr-2">💡</span>
                建议投入闲钱的30-50%，不影响日常生活
              </div>
            </div>

            {/* 定投周期 */}
            <div className="mb-10">
              <label className="block mb-4 text-lg font-semibold flex items-center gap-2">
                <span className="text-[#00ccff]">📅</span>
                <span>定投周期</span>
              </label>
              <div className="grid grid-cols-2 gap-5">
                <button
                  onClick={() => setParams({ ...params, frequency: 'weekly' })}
                  className={`p-6 rounded-xl border-2 transition-all duration-300 ${
                    params.frequency === 'weekly'
                      ? 'border-[#00ccff] bg-gradient-to-br from-[#00ccff]/20 to-[#00ff88]/10 shadow-lg shadow-[#00ccff]/30 scale-105'
                      : 'border-[#2a3a5a] bg-gradient-to-br from-[#1a2332] to-[#141a2a] hover:border-[#00ccff]/50 hover:shadow-md hover:shadow-[#00ccff]/10'
                  }`}
                >
                  <div className="font-bold text-lg mb-2 flex items-center gap-2">
                    <span className="text-2xl">📆</span>
                    <span>每周定投</span>
                  </div>
                  <div className="text-sm text-gray-400">
                    每周投 <span className="text-[#00ccff] font-bold">¥{Math.round(params.investment_amount / 4).toLocaleString()}</span>
                  </div>
                </button>
                <button
                  onClick={() => setParams({ ...params, frequency: 'monthly' })}
                  className={`p-6 rounded-xl border-2 transition-all duration-300 ${
                    params.frequency === 'monthly'
                      ? 'border-[#00ccff] bg-gradient-to-br from-[#00ccff]/20 to-[#00ff88]/10 shadow-lg shadow-[#00ccff]/30 scale-105'
                      : 'border-[#2a3a5a] bg-gradient-to-br from-[#1a2332] to-[#141a2a] hover:border-[#00ccff]/50 hover:shadow-md hover:shadow-[#00ccff]/10'
                  }`}
                >
                  <div className="font-bold text-lg mb-2 flex items-center gap-2">
                    <span className="text-2xl">🗓️</span>
                    <span>每月定投</span>
                  </div>
                  <div className="text-sm text-gray-400">
                    每月投 <span className="text-[#00ccff] font-bold">¥{params.investment_amount.toLocaleString()}</span>
                  </div>
                </button>
              </div>
            </div>

            {/* 自动执行 */}
            <div className="mb-10">
              <label className="flex items-start gap-4 cursor-pointer p-6 bg-gradient-to-r from-[#1a2332] to-[#141a2a] rounded-xl border border-[#2a3a5a] hover:border-[#00ccff]/50 transition-all duration-300 hover:shadow-md hover:shadow-[#00ccff]/10">
                <input
                  type="checkbox"
                  checked={params.auto_execute}
                  onChange={(e) => setParams({ ...params, auto_execute: e.target.checked })}
                  className="w-6 h-6 mt-1 accent-[#00ccff]"
                />
                <div className="flex-1">
                  <div className="font-semibold text-lg mb-2 flex items-center gap-2">
                    <span className="text-[#00ccff]">⚙️</span>
                    <span>自动执行交易</span>
                  </div>
                  <div className="text-sm text-gray-400 leading-relaxed">
                    开启后，系统会在合适时机自动买入，无需手动确认（当前为虚拟交易）
                  </div>
                </div>
              </label>
            </div>

            <div className="flex gap-5">
              <button
                onClick={() => setCurrentStep(1)}
                className="flex-1 py-5 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:from-[#3a4a6a] hover:to-[#2a3a5a] transition-all duration-300 font-semibold shadow-md hover:shadow-lg group flex items-center justify-center gap-2"
              >
                <span className="transform group-hover:-translate-x-1 transition-transform">←</span>
                <span>上一步</span>
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="flex-1 py-5 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-bold rounded-xl hover:from-[#00aadd] hover:to-[#00ccaa] transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-[#00ccff]/30 transform hover:scale-[1.02] group flex items-center justify-center gap-2"
              >
                <span>下一步</span>
                <span className="transform group-hover:translate-x-1 transition-transform">→</span>
              </button>
            </div>
          </div>
        )}

        {/* Step 3: 确认并启动 - 增强版 */}
        {currentStep === 3 && (
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-10 shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300 animate-fadeIn">
            <h2 className="text-3xl font-bold mb-8 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">确认信息</h2>

            {/* 参数汇总 */}
            <div className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] rounded-xl p-8 mb-8 border border-[#2a3a5a] shadow-inner">
              <div className="grid grid-cols-2 gap-8">
                <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] p-5 rounded-lg border border-[#2a3a5a]">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gray-500"></span>
                    策略名称
                  </div>
                  <div className="font-semibold text-lg">{strategy.friendly_name}</div>
                </div>
                <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] p-5 rounded-lg border border-[#2a3a5a]">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gray-500"></span>
                    风险等级
                  </div>
                  <div className="font-semibold text-lg">{strategy.risk_score}/5</div>
                </div>
                <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] p-5 rounded-lg border border-[#2a3a5a]">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#00ccff]"></span>
                    投资金额
                  </div>
                  <div className="font-bold text-xl bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                    ¥{params.investment_amount.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] p-5 rounded-lg border border-[#2a3a5a]">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gray-500"></span>
                    定投周期
                  </div>
                  <div className="font-semibold text-lg">
                    {params.frequency === 'weekly' ? '每周' : '每月'}
                  </div>
                </div>
                <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] p-5 rounded-lg border border-[#2a3a5a]">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-gray-500"></span>
                    自动执行
                  </div>
                  <div className="font-semibold text-lg">
                    {params.auto_execute ? '是' : '否'}
                  </div>
                </div>
                <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] p-5 rounded-lg border border-[#2a3a5a]">
                  <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#00ff88]"></span>
                    预期年化收益
                  </div>
                  <div className="font-bold text-xl text-[#00ff88]">{strategy.expected_return}</div>
                </div>
              </div>
            </div>

            {/* 风险提示 */}
            <div className="bg-gradient-to-r from-[#ff4444]/20 to-[#ff2222]/15 border-2 border-[#ff4444] rounded-xl p-8 mb-8 shadow-lg shadow-[#ff4444]/20">
              <h3 className="font-bold mb-5 text-xl flex items-center gap-3">
                <span className="text-3xl">⚠️</span>
                <span className="text-[#ff4444]">重要风险提示</span>
              </h3>
              <ul className="space-y-3 text-sm text-gray-300 mb-6">
                <li className="flex items-start gap-3">
                  <span className="text-[#00ccff] text-lg">•</span>
                  <span>这是虚拟交易，不涉及真实资金</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#00ccff] text-lg">•</span>
                  <span>历史收益不代表未来表现</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#00ccff] text-lg">•</span>
                  <span>投资有风险，可能面临本金损失</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#00ccff] text-lg">•</span>
                  <span>建议仅投入可承受损失的闲钱</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-[#00ccff] text-lg">•</span>
                  <span>最大可能回撤：<span className="font-bold text-[#ff4444]">{strategy.max_drawdown}</span></span>
                </li>
              </ul>
              
              <label className="flex items-start gap-4 cursor-pointer p-5 bg-[#141a2a]/50 rounded-lg border border-[#ff4444]/50 hover:bg-[#141a2a]/70 transition-all duration-300">
                <input
                  type="checkbox"
                  checked={agreedToRisk}
                  onChange={(e) => setAgreedToRisk(e.target.checked)}
                  className="w-6 h-6 mt-0.5 accent-[#ff4444]"
                />
                <span className="font-semibold text-base">我已阅读并理解上述风险</span>
              </label>
            </div>

            <div className="flex gap-5">
              <button
                onClick={() => setCurrentStep(2)}
                className="flex-1 py-5 bg-gradient-to-br from-[#2a3a5a] to-[#1a2332] rounded-xl hover:from-[#3a4a6a] hover:to-[#2a3a5a] transition-all duration-300 font-semibold shadow-md hover:shadow-lg group flex items-center justify-center gap-2"
                disabled={loading}
              >
                <span className="transform group-hover:-translate-x-1 transition-transform">←</span>
                <span>上一步</span>
              </button>
              <button
                onClick={handleActivate}
                disabled={!agreedToRisk || loading}
                className={`flex-1 py-6 font-bold text-lg rounded-xl transition-all duration-300 shadow-lg group flex items-center justify-center gap-3 ${
                  agreedToRisk && !loading
                    ? 'bg-gradient-to-r from-[#00ff88] to-[#00ccaa] text-black hover:from-[#00dd77] hover:to-[#00aa88] hover:shadow-xl hover:shadow-[#00ff88]/30 transform hover:scale-[1.02]'
                    : 'bg-[#2a3a5a] text-gray-500 cursor-not-allowed'
                }`}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-black border-t-transparent"></div>
                    <span>启动中...</span>
                  </>
                ) : (
                  <>
                    <span className="text-2xl">🚀</span>
                    <span>启动策略</span>
                    <span className="transform group-hover:translate-x-1 transition-transform">→</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyActivationFlow;
