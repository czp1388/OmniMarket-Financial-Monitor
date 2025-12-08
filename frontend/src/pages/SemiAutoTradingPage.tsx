import React, { useState, useEffect } from 'react';
import './SemiAutoTradingPage.css';

interface TradingSignal {
  warrant_code: string;
  signal_type: string;
  strength: number;
  confidence: number;
  price: number;
  stop_loss?: number;
  take_profit?: number;
  reason: string;
  timestamp: string;
}

interface RiskRules {
  max_position_size: number;
  max_daily_loss: number;
  max_single_trade: number;
  min_confidence: number;
}

const SemiAutoTradingPage: React.FC = () => {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [selectedSignal, setSelectedSignal] = useState<TradingSignal | null>(null);
  const [positionSize, setPositionSize] = useState<number>(1000);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [riskRules, setRiskRules] = useState<RiskRules>({
    max_position_size: 50000,
    max_daily_loss: 5000,
    max_single_trade: 10000,
    min_confidence: 0.7
  });
  const [isLoading, setIsLoading] = useState(false);

  // 模拟生成交易信号
  const generateSignals = async () => {
    setIsLoading(true);
    try {
      // 模拟API调用
      setTimeout(() => {
        const mockSignals: TradingSignal[] = [
          {
            warrant_code: "12345.HK",
            signal_type: "BUY",
            strength: 0.85,
            confidence: 0.78,
            price: 0.45,
            stop_loss: 0.40,
            take_profit: 0.55,
            reason: "技术指标金叉，突破阻力位",
            timestamp: new Date().toISOString()
          },
          {
            warrant_code: "67890.HK",
            signal_type: "SELL",
            strength: 0.72,
            confidence: 0.65,
            price: 1.20,
            stop_loss: 1.30,
            take_profit: 1.00,
            reason: "RSI超买，接近阻力位",
            timestamp: new Date().toISOString()
          }
        ];
        setSignals(mockSignals);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('生成信号失败:', error);
      setIsLoading(false);
    }
  };

  // 验证交易
  const validateTrade = async (signal: TradingSignal) => {
    try {
      // 模拟API调用
      setTimeout(() => {
        const validation = {
          is_valid: true,
          risk_level: "中等风险",
          max_position: 5000,
          warnings: ["注意市场波动性较高"],
          recommendations: ["建议分批建仓"]
        };
        setValidationResult(validation);
      }, 500);
    } catch (error) {
      console.error('验证失败:', error);
    }
  };

  // 执行交易
  const executeTrade = async () => {
    if (!selectedSignal) return;
    
    setIsLoading(true);
    try {
      // 模拟API调用
      setTimeout(() => {
        const execution = {
          success: true,
          order_id: `ORD${Date.now()}`,
          executed_price: selectedSignal.price,
          position_size: positionSize,
          timestamp: new Date().toISOString()
        };
        setExecutionResult(execution);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('执行失败:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedSignal) {
      validateTrade(selectedSignal);
    }
  }, [selectedSignal]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white p-6 space-y-4">
      {/* 风险提示横幅 */}
      <div className="bg-gradient-to-r from-[#ff4444]/20 via-[#ff8844]/20 to-[#ff4444]/20 border-2 border-[#ff4444] rounded-2xl p-5 shadow-2xl">
        <div className="flex items-start gap-4">
          <div className="text-5xl">⚠️</div>
          <div className="flex-1">
            <div className="text-2xl font-bold text-[#ff4444] mb-2">【模拟交易 - 仅供学习和测试使用】</div>
            <div className="text-gray-300">
              本页面为半自动交易测试环境，所有交易均使用模拟资金，不涉及真实资金交易。交易信号仅供参考，请谨慎决策，不构成任何投资建议。
            </div>
          </div>
        </div>
      </div>

      {/* 页面标题 */}
      <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-3">
          <span className="text-5xl">🤖</span>
          <span>牛熊证半自动交易系统</span>
        </h1>
        <p className="text-gray-400 mt-2">智能信号生成 + 人工决策确认</p>
      </div>

      {/* 状态栏 */}
      <div className="bg-gradient-to-r from-[#141a2a] via-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-4 shadow-2xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse shadow-lg shadow-[#00ff88]/50"></div>
            <span className="text-white font-semibold">系统运行正常</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-400">
            <span>风控等级: <span className="text-[#ffaa00] font-semibold">中等</span></span>
            <span>信号数量: <span className="text-[#00ccff] font-semibold">{signals.length}</span></span>
            <span>最后更新: <span className="text-[#00ff88] font-mono font-semibold">{new Date().toLocaleTimeString()}</span></span>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 左侧控制面板 */}
        <div className="space-y-4">
          {/* 信号生成 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
            <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              <span>信号生成</span>
            </h3>
            <button 
              className="w-full bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-semibold py-3 rounded-lg hover:scale-[1.02] transition-all shadow-lg"
              onClick={generateSignals}
              disabled={isLoading}
            >
              {isLoading ? '⏳ 生成中...' : '🔄 生成交易信号'}
            </button>
          </div>

          {/* 风险控制 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
            <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-2xl">⚠️</span>
              <span>风险控制</span>
            </h3>
            <div className="space-y-3">
              {[
                { label: '最大仓位', value: `$${riskRules.max_position_size}`, icon: '💰' },
                { label: '单笔最大', value: `$${riskRules.max_single_trade}`, icon: '📊' },
                { label: '日亏损上限', value: `$${riskRules.max_daily_loss}`, icon: '🔻' },
                { label: '最低置信度', value: `${(riskRules.min_confidence * 100).toFixed(0)}%`, icon: '✅' }
              ].map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-[#1a2332] rounded-lg">
                  <span className="text-gray-400 flex items-center gap-2">
                    <span>{item.icon}</span>
                    <span>{item.label}:</span>
                  </span>
                  <span className="text-white font-bold">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 交易执行 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
            <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-2xl">⚡</span>
              <span>交易执行</span>
            </h3>
            <div className="space-y-4">
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                  <span>💵</span><span>仓位大小 ($)</span>
                </label>
                <input 
                  type="number" 
                  value={positionSize}
                  onChange={(e) => setPositionSize(Number(e.target.value))}
                  min="100"
                  max="10000"
                  className="w-full bg-[#1a2332] border border-[#2a3a5a] rounded-lg px-4 py-3 text-white focus:border-[#00ccff] focus:outline-none"
                />
              </div>
              
              {selectedSignal && (
                <button 
                  className={`w-full font-semibold py-3 rounded-lg transition-all shadow-lg ${
                    isLoading || !validationResult?.is_valid
                      ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-[#ff4444] to-[#ff8844] text-white hover:scale-[1.02]'
                  }`}
                  onClick={executeTrade}
                  disabled={isLoading || !validationResult?.is_valid}
                >
                  {isLoading ? '⏳ 执行中...' : '✅ 确认执行交易'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* 右侧信息面板 */}
        <div className="md:col-span-2 space-y-4">
          {/* 信号列表 */}
          <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
            <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent flex items-center gap-2">
              <span className="text-2xl">📡</span>
              <span>交易信号 ({signals.length})</span>
            </h3>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {signals.map((signal, index) => (
                <div 
                  key={index}
                  className={`p-4 rounded-xl cursor-pointer transition-all ${
                    selectedSignal === signal
                      ? 'bg-gradient-to-r from-[#00ccff]/20 to-[#00ff88]/20 border-2 border-[#00ccff]'
                      : 'bg-[#1a2332] border border-[#2a3a5a] hover:bg-[#222b3d]'
                  }`}
                  onClick={() => setSelectedSignal(signal)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-bold text-lg">{signal.warrant_code}</span>
                    <span className={`px-3 py-1 rounded-lg font-semibold ${
                      signal.signal_type === 'BUY' 
                        ? 'bg-[#00ff88] text-black' 
                        : 'bg-[#ff4444] text-white'
                    }`}>
                      {signal.signal_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm mb-2">
                    <span className="text-gray-400">强度: <span className="text-[#00ccff] font-semibold">{(signal.strength * 100).toFixed(0)}%</span></span>
                    <span className="text-gray-400">置信度: <span className="text-[#00ff88] font-semibold">{(signal.confidence * 100).toFixed(0)}%</span></span>
                    <span className="text-gray-400">价格: <span className="text-white font-bold">${signal.price}</span></span>
                  </div>
                  <div className="text-sm text-gray-300">
                    {signal.reason}
                  </div>
                </div>
              ))}
              {signals.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                    暂无交易信号，点击生成按钮获取信号
                  </div>
                )}
            </div>
          </div>

          {/* 验证结果 */}
          {validationResult && selectedSignal && (
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
              <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">交易验证</h3>
              <div className={`p-4 rounded-xl ${validationResult.is_valid ? 'bg-[#00ff88]/10 border-2 border-[#00ff88]' : 'bg-[#ff4444]/10 border-2 border-[#ff4444]'}`}>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-white font-semibold">验证状态: {validationResult.is_valid ? '✅ 通过' : '❌ 不通过'}</span>
                  <span className="px-3 py-1 rounded-lg font-semibold bg-[#ffaa00] text-black">
                    {validationResult.risk_level}
                  </span>
                </div>
                {validationResult.warnings.map((warning: string, index: number) => (
                  <div key={index} className="text-[#ffaa00] text-sm mb-2">
                    ⚠️ {warning}
                  </div>
                ))}
                {validationResult.recommendations.map((rec: string, index: number) => (
                  <div key={index} className="text-[#00ccff] text-sm">
                    💡 {rec}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 执行结果 */}
          {executionResult && (
            <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-2xl p-5 shadow-2xl">
              <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">执行结果</h3>
              <div className="bg-[#00ff88]/10 border-2 border-[#00ff88] rounded-xl p-4">
                <div className="text-[#00ff88] text-lg font-bold mb-3">
                  ✅ 交易执行成功
                </div>
                <div className="space-y-2 text-white">
                  <div>订单号: <span className="text-[#00ccff] font-mono">{executionResult.order_id}</span></div>
                  <div>执行价格: <span className="text-[#00ff88] font-bold">${executionResult.executed_price}</span></div>
                  <div>仓位大小: <span className="text-white font-bold">${executionResult.position_size}</span></div>
                  <div>时间: <span className="text-gray-400 font-mono">{new Date(executionResult.timestamp).toLocaleString()}</span></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SemiAutoTradingPage;
