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
    <div className="semi-auto-trading-page">
      <div className="container">
        <div className="header">
          <h1>牛熊证半自动交易系统</h1>
          <p>智能信号生成 + 人工决策确认</p>
        </div>

        <div className="status-bar">
          <div className="status-indicator">
            <div className="status-dot" style={{background: '#00ff88'}}></div>
            <span>系统运行正常</span>
          </div>
          <div className="status-info">
            <span>风控等级: 中等</span>
            <span>信号数量: {signals.length}</span>
            <span>最后更新: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>

        <div className="main-content">
          {/* 左侧控制面板 */}
          <div className="control-panel">
            <div className="panel-section">
              <h3>信号生成</h3>
              <button 
                className="btn btn-generate"
                onClick={generateSignals}
                disabled={isLoading}
              >
                {isLoading ? '生成中...' : '生成交易信号'}
              </button>
            </div>

            <div className="panel-section">
              <h3>风险控制</h3>
              <div className="risk-rules">
                <div className="risk-item">
                  <span>最大仓位:</span>
                  <span>${riskRules.max_position_size}</span>
                </div>
                <div className="risk-item">
                  <span>单笔最大:</span>
                  <span>${riskRules.max_single_trade}</span>
                </div>
                <div className="risk-item">
                  <span>日亏损上限:</span>
                  <span>${riskRules.max_daily_loss}</span>
                </div>
                <div className="risk-item">
                  <span>最低置信度:</span>
                  <span>{(riskRules.min_confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <div className="panel-section">
              <h3>交易执行</h3>
              <div className="trade-controls">
                <div className="config-item">
                  <label>仓位大小 ($):</label>
                  <input 
                    type="number" 
                    value={positionSize}
                    onChange={(e) => setPositionSize(Number(e.target.value))}
                    min="100"
                    max="10000"
                  />
                </div>
                
                {selectedSignal && (
                  <button 
                    className="btn btn-execute"
                    onClick={executeTrade}
                    disabled={isLoading || !validationResult?.is_valid}
                  >
                    {isLoading ? '执行中...' : '确认执行交易'}
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* 右侧信息面板 */}
          <div className="info-panel">
            {/* 信号列表 */}
            <div className="panel-section">
              <h3>交易信号 ({signals.length})</h3>
              <div className="signals-list">
                {signals.map((signal, index) => (
                  <div 
                    key={index}
                    className={`signal-item ${selectedSignal === signal ? 'selected' : ''}`}
                    onClick={() => setSelectedSignal(signal)}
                  >
                    <div className="signal-header">
                      <span className="warrant-code">{signal.warrant_code}</span>
                      <span className={`signal-type ${signal.signal_type.toLowerCase()}`}>
                        {signal.signal_type}
                      </span>
                    </div>
                    <div className="signal-details">
                      <div className="signal-metrics">
                        <span>强度: {(signal.strength * 100).toFixed(0)}%</span>
                        <span>置信度: {(signal.confidence * 100).toFixed(0)}%</span>
                        <span>价格: ${signal.price}</span>
                      </div>
                      <div className="signal-reason">
                        {signal.reason}
                      </div>
                    </div>
                  </div>
                ))}
                {signals.length === 0 && (
                  <div className="no-signals">
                    暂无交易信号，点击生成按钮获取信号
                  </div>
                )}
              </div>
            </div>

            {/* 验证结果 */}
            {validationResult && selectedSignal && (
              <div className="panel-section">
                <h3>交易验证</h3>
                <div className={`validation-result ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
                  <div className="validation-header">
                    <span>验证状态: {validationResult.is_valid ? '通过' : '不通过'}</span>
                    <span className={`risk-level ${validationResult.risk_level.replace('风险', '')}`}>
                      {validationResult.risk_level}
                    </span>
                  </div>
                  {validationResult.warnings.map((warning: string, index: number) => (
                    <div key={index} className="warning-item">
                      ⚠️ {warning}
                    </div>
                  ))}
                  {validationResult.recommendations.map((rec: string, index: number) => (
                    <div key={index} className="recommendation-item">
                      💡 {rec}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 执行结果 */}
            {executionResult && (
              <div className="panel-section">
                <h3>执行结果</h3>
                <div className="execution-result">
                  <div className="execution-success">
                    ✅ 交易执行成功
                  </div>
                  <div className="execution-details">
                    <div>订单号: {executionResult.order_id}</div>
                    <div>执行价格: ${executionResult.executed_price}</div>
                    <div>仓位大小: ${executionResult.position_size}</div>
                    <div>时间: {new Date(executionResult.timestamp).toLocaleString()}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SemiAutoTradingPage;
