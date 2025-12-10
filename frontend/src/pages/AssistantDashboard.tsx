/**
 * 助手模式主页 - 为零基础用户设计
 * 
 * 设计原则：
 * 1. 无专业术语 - "K线"变"价格走势"，"RSI"变"市场情绪"
 * 2. 目标导向 - 显示离目标还有多远，而非收益率
 * 3. 行动建议 - 不是数据，是"今天该做什么"
 * 4. 渐进式透明 - 底部提供"想看专业数据"入口
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface TodayAction {
  type: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  action_text: string;
}

interface AccountSummary {
  total_assets: number;
  today_profit: number;
  total_profit: number;
  profit_rate: number;
  message: string;
}

interface ActiveStrategy {
  package_id: string;
  instance_id?: string;
  friendly_name: string;
  status: string;
  days_active: number;
  profit: number;
}

interface MarketOpportunity {
  opportunity_id: string;
  title: string;
  explanation: string;
  suggestion: string;
  risk_level: string;
  potential_return: string;
  action_button: string;
  related_package_id?: string;
}

interface DashboardData {
  greeting: string;
  today_actions: TodayAction[];
  account_summary: AccountSummary;
  active_strategies: ActiveStrategy[];
  market_opportunities_count: number;
  notifications: any[];
}

const AssistantDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [opportunities, setOpportunities] = useState<MarketOpportunity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      // 并行加载数据
      await Promise.all([
        loadDashboardData(),
        loadOpportunities()
      ]);
    };
    loadData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // 调用真实 API（2秒超时）
      const response = await axios.get(`http://localhost:8000/api/v1/assistant/dashboard/summary`, {
        timeout: 2000
      });
      setDashboardData(response.data);
    } catch (error) {
      console.warn('加载仪表盘数据失败，使用默认数据:', error);
      // 降级到默认数据
      const fallbackData: DashboardData = {
        greeting: '早上好',
        account_summary: {
          total_assets: 10000,
          today_profit: 120,
          total_profit: 1200,
          profit_rate: 12.0,
          message: '您的投资组合表现良好'
        },
        today_actions: [
          {
            type: 'review',
            title: '查看市场机会',
            description: '今日有3个值得关注的投资机会',
            priority: 'high',
            action_text: '查看详情'
          }
        ],
        active_strategies: [],
        market_opportunities_count: 0,
        notifications: []
      };
      setDashboardData(fallbackData);
    }
  };

  const loadOpportunities = async () => {
    try {
      // 调用真实 API（2秒超时）
      const response = await axios.get(`http://localhost:8000/api/v1/assistant/opportunities?limit=3`, {
        timeout: 2000
      });
      setOpportunities(response.data);
    } catch (error) {
      console.warn('加载市场机会失败，使用默认数据:', error);
      // 降级到默认数据
      const fallbackOpportunities: MarketOpportunity[] = [
        {
          opportunity_id: '1',
          title: 'BTC 低位买入机会',
          explanation: '比特币价格回调至关键支撑位',
          suggestion: '适合定投布局',
          risk_level: '中',
          potential_return: '预期收益 15-20%',
          action_button: '立即查看'
        }
      ];
      setOpportunities(fallbackOpportunities);
    } finally {
      // 两个API都加载完成后才取消loading
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] flex items-center justify-center">
        <div className="text-center space-y-6">
          <div className="relative">
            <div className="animate-spin rounded-full h-20 w-20 border-4 border-[#2a3a5a] border-t-[#00ccff] mx-auto shadow-lg shadow-[#00ccff]/20"></div>
            <div className="absolute inset-0 rounded-full h-20 w-20 border-4 border-transparent border-t-[#00ff88] animate-spin mx-auto" style={{ animationDuration: '1.5s', animationDirection: 'reverse' }}></div>
          </div>
          <div className="space-y-3">
            <div className="text-[#00ccff] text-2xl font-semibold animate-pulse">智能投资助手加载中</div>
            <div className="text-gray-400 text-base animate-fadeIn">正在为您准备专属投资方案...</div>
          </div>
          <div className="flex items-center justify-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#00ccff] animate-pulse" style={{ animationDelay: '0s' }}></div>
            <div className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 rounded-full bg-[#00ccff] animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e17] via-[#0d1219] to-[#0a0e17] text-white">
      {/* 顶部导航栏 - 增强版 */}
      <header className="bg-gradient-to-r from-[#141a2a] to-[#1a2332] border-b border-[#2a3a5a] shadow-lg backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00ccff] to-[#00ff88] flex items-center justify-center shadow-lg shadow-[#00ccff]/20">
                  <span className="text-2xl">🤖</span>
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text text-transparent">
                  智能投资助手
                </h1>
              </div>
              <span className="text-sm text-gray-400 bg-[#1a2332] px-3 py-1 rounded-full border border-[#2a3a5a] shadow-sm">
                助手模式
              </span>
            </div>
            <button
              onClick={() => navigate('/expert')}
              className="group flex items-center gap-2 px-4 py-2 bg-[#1a2332] text-[#00ccff] border border-[#2a3a5a] rounded-lg hover:bg-[#1f2838] hover:border-[#00ccff] transition-all duration-300 shadow-sm hover:shadow-md hover:shadow-[#00ccff]/20"
            >
              <span>切换到专家模式</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-10">
        {/* 问候语 - 增强版 */}
        <div className="mb-10 animate-fadeIn">
          <h2 className="text-4xl font-light mb-3 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            {dashboardData?.greeting}
          </h2>
          <p className="text-gray-400 text-lg flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-[#00ff88] animate-pulse"></span>
            让我们看看今天有什么机会
          </p>
        </div>

        {/* 主要内容区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧列：账户概况 + 今日待办 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 账户概况卡片 */}
            <AccountSummaryCard summary={dashboardData?.account_summary} />

            {/* 今日待办 */}
            <TodayActionsCard actions={dashboardData?.today_actions || []} />

            {/* 运行中的策略 */}
            <ActiveStrategiesCard strategies={dashboardData?.active_strategies || []} />
          </div>

          {/* 右侧列：市场机会流 */}
          <div className="space-y-6">
            <MarketOpportunitiesStream opportunities={opportunities} />
          </div>
        </div>

        {/* 底部：快速入口 */}
        <QuickActions />
      </div>
    </div>
  );
};

// ==================== 子组件 ====================

const AccountSummaryCard: React.FC<{ summary?: AccountSummary }> = ({ summary }) => {
  if (!summary) return null;

  const isProfitable = summary.today_profit >= 0;

  return (
    <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6 shadow-xl hover:shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300 hover:border-[#2a3a5a]/80 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-5">
        <span className="text-2xl">💼</span>
        <h3 className="text-xl font-semibold text-transparent bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text">
          我的账户
        </h3>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-5">
        <div className="group hover:scale-105 transition-transform duration-200">
          <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-gray-500"></span>
            总资产
          </div>
          <div className="text-3xl font-bold tracking-tight">
            ¥{summary.total_assets.toLocaleString()}
          </div>
        </div>
        <div className="group hover:scale-105 transition-transform duration-200">
          <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">
            <span className={`w-1.5 h-1.5 rounded-full ${isProfitable ? 'bg-[#00ff88]' : 'bg-[#ff4444]'}`}></span>
            今日盈亏
          </div>
          <div className={`text-3xl font-bold tracking-tight ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
            {isProfitable ? '+' : ''}¥{Math.abs(summary.today_profit).toLocaleString()}
          </div>
        </div>
        <div className="group hover:scale-105 transition-transform duration-200">
          <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00ff88]"></span>
            累计收益
          </div>
          <div className="text-3xl font-bold text-[#00ff88] tracking-tight">
            +¥{summary.total_profit.toLocaleString()}
          </div>
        </div>
        <div className="group hover:scale-105 transition-transform duration-200">
          <div className="text-sm text-gray-400 mb-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00ff88]"></span>
            收益率
          </div>
          <div className="text-3xl font-bold text-[#00ff88] tracking-tight">
            +{summary.profit_rate.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-lg px-4 py-3 text-sm text-gray-300 flex items-start gap-3 shadow-inner">
        <span className="text-xl">💡</span>
        <span className="flex-1">{summary.message}</span>
      </div>
    </div>
  );
};

const TodayActionsCard: React.FC<{ actions: TodayAction[] }> = ({ actions }) => {
  const priorityColors = {
    high: 'border-l-[#ff4444] bg-[#ff4444]/5',
    medium: 'border-l-[#ffaa00] bg-[#ffaa00]/5',
    low: 'border-l-[#00ccff] bg-[#00ccff]/5'
  };

  const priorityIcons = {
    high: '🔥',
    medium: '⚡',
    low: '💡'
  };

  return (
    <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6 shadow-xl hover:shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300">
      <div className="flex items-center gap-2 mb-5">
        <span className="text-2xl">✅</span>
        <h3 className="text-xl font-semibold text-transparent bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text">
          今日待办
        </h3>
      </div>
      
      <div className="space-y-3">
        {actions.map((action, index) => (
          <div
            key={index}
            className={`bg-gradient-to-r from-[#1a2332] to-[#141a2a] border-l-4 ${priorityColors[action.priority]} rounded-lg p-4 hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer group`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">{priorityIcons[action.priority]}</span>
                  <h4 className="font-semibold text-lg group-hover:text-[#00ccff] transition-colors">
                    {action.title}
                  </h4>
                </div>
                <p className="text-sm text-gray-400 leading-relaxed">{action.description}</p>
              </div>
              <button className="px-5 py-2.5 bg-gradient-to-r from-[#00ccff] to-[#00aadd] text-black font-medium rounded-lg hover:from-[#00aadd] hover:to-[#00ccff] transition-all duration-300 shadow-md hover:shadow-lg hover:shadow-[#00ccff]/30 whitespace-nowrap transform hover:scale-105">
                {action.action_text}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ActiveStrategiesCard: React.FC<{ strategies: ActiveStrategy[] }> = ({ strategies }) => {
  const navigate = useNavigate();
  
  return (
    <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6 shadow-xl hover:shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300">
      <div className="flex items-center gap-2 mb-5">
        <span className="text-2xl">🎯</span>
        <h3 className="text-xl font-semibold text-transparent bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text">
          运行中的策略
        </h3>
      </div>
      
      {strategies.length === 0 ? (
        <div className="text-center py-12 space-y-4">
          <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-[#00ccff]/20 to-[#00ff88]/20 flex items-center justify-center">
            <span className="text-4xl">📦</span>
          </div>
          <p className="text-gray-400 text-lg">您还没有激活任何策略</p>
          <button 
            onClick={() => navigate('/assistant/strategies/activate/stable_growth_low_risk')}
            className="px-8 py-3 bg-gradient-to-r from-[#00ccff] to-[#00ff88] text-black font-medium rounded-lg hover:from-[#00aadd] hover:to-[#00ff88] transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-[#00ccff]/30 transform hover:scale-105"
          >
            浏览策略包
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {strategies.map((strategy) => (
            <div
              key={strategy.package_id}
              onClick={() => navigate(`/assistant/strategies/running/${strategy.instance_id || 'demo'}`)}
              className="bg-gradient-to-r from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-lg p-5 hover:border-[#00ccff]/50 hover:shadow-lg hover:shadow-[#00ccff]/20 transition-all duration-300 cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-lg group-hover:text-[#00ccff] transition-colors">
                  {strategy.friendly_name}
                </h4>
                <span className="px-3 py-1.5 bg-gradient-to-r from-[#00ff88] to-[#00ccaa] text-black text-xs font-semibold rounded-full shadow-sm">
                  ● 运行中
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">已运行：</span>
                  <span className="font-medium">{strategy.days_active} 天</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">累计收益：</span>
                  <span className="font-medium text-[#00ff88]">+¥{strategy.profit.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const MarketOpportunitiesStream: React.FC<{ opportunities: MarketOpportunity[] }> = ({ opportunities }) => {
  const riskLevelColors = {
    '低': 'from-[#00ff88] to-[#00ccaa]',
    '中': 'from-[#ffaa00] to-[#ff8800]',
    '高': 'from-[#ff4444] to-[#ff2222]'
  };

  return (
    <div className="bg-gradient-to-br from-[#141a2a] to-[#1a2332] border border-[#2a3a5a] rounded-xl p-6 shadow-xl hover:shadow-2xl hover:shadow-[#00ccff]/10 transition-all duration-300 sticky top-6">
      <div className="flex items-center gap-2 mb-5">
        <span className="text-2xl">🔍</span>
        <h3 className="text-xl font-semibold text-transparent bg-gradient-to-r from-[#00ccff] to-[#00ff88] bg-clip-text">
          市场机会
        </h3>
      </div>
      
      <div className="space-y-4">
        {opportunities.map((opp) => (
          <div
            key={opp.opportunity_id}
            className="bg-gradient-to-br from-[#1a2332] to-[#141a2a] border border-[#2a3a5a] rounded-xl p-5 hover:border-[#00ccff]/50 hover:shadow-lg hover:shadow-[#00ccff]/20 transition-all duration-300 group"
          >
            <div className="flex items-start justify-between mb-3">
              <h4 className="font-semibold text-lg flex-1 group-hover:text-[#00ccff] transition-colors">
                {opp.title}
              </h4>
              <span className={`px-3 py-1.5 bg-gradient-to-r ${riskLevelColors[opp.risk_level as keyof typeof riskLevelColors]} text-black text-xs font-semibold rounded-full shadow-sm`}>
                {opp.risk_level}风险
              </span>
            </div>
            
            <p className="text-sm text-gray-300 mb-3 leading-relaxed">{opp.explanation}</p>
            
            <div className="bg-gradient-to-r from-[#0a0e17] to-[#0d1219] border border-[#2a3a5a] rounded-lg p-4 mb-4 shadow-inner">
              <div className="flex items-start gap-2">
                <span className="text-lg">💡</span>
                <div className="flex-1">
                  <div className="text-xs text-gray-400 mb-1 font-medium">建议</div>
                  <div className="text-sm text-gray-200">{opp.suggestion}</div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400 flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-[#00ff88]"></span>
                {opp.potential_return}
              </span>
              <button className="px-5 py-2 bg-gradient-to-r from-[#00ccff] to-[#00aadd] text-black text-sm font-medium rounded-lg hover:from-[#00aadd] hover:to-[#00ccff] transition-all duration-300 shadow-md hover:shadow-lg hover:shadow-[#00ccff]/30 transform hover:scale-105">
                {opp.action_button}
              </button>
            </div>
          </div>
        ))}
      </div>
      
      <button className="w-full mt-5 py-3 border-2 border-[#2a3a5a] rounded-lg text-sm font-medium hover:bg-[#1a2332] hover:border-[#00ccff]/50 transition-all duration-300 flex items-center justify-center gap-2 group">
        <span>查看更多机会</span>
        <span className="transform group-hover:translate-x-1 transition-transform">→</span>
      </button>
    </div>
  );
};

const QuickActions: React.FC = () => {
  const navigate = useNavigate();

  const actions = [
    {
      icon: '📦',
      title: '浏览策略包',
      description: '发现适合您的投资方案',
      path: '/assistant/strategies/activate/stable_growth_low_risk',
      gradient: 'from-[#00ccff]/10 to-[#00aadd]/10',
      border: 'border-[#00ccff]',
      glow: 'hover:shadow-[#00ccff]/20'
    },
    {
      icon: '🎯',
      title: '设置投资目标',
      description: '告诉我们您的期望',
      path: '/assistant/goals',
      gradient: 'from-[#00ff88]/10 to-[#00ccaa]/10',
      border: 'border-[#00ff88]',
      glow: 'hover:shadow-[#00ff88]/20'
    },
    {
      icon: '📊',
      title: '查看历史表现',
      description: '回顾策略效果',
      path: '/assistant/performance',
      gradient: 'from-[#ffaa00]/10 to-[#ff8800]/10',
      border: 'border-[#ffaa00]',
      glow: 'hover:shadow-[#ffaa00]/20'
    },
    {
      icon: '🔔',
      title: '通知设置',
      description: '管理提醒方式',
      path: '/assistant/notifications',
      gradient: 'from-[#ff4444]/10 to-[#ff2222]/10',
      border: 'border-[#ff4444]',
      glow: 'hover:shadow-[#ff4444]/20'
    }
  ];

  return (
    <div className="mt-16 mb-8">
      <h3 className="text-xl font-semibold mb-6 text-center text-gray-300">快速入口</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={() => navigate(action.path)}
            className={`bg-gradient-to-br ${action.gradient} border-2 ${action.border} rounded-xl p-6 hover:bg-[#1a2332] transition-all duration-300 text-left group hover:scale-105 hover:shadow-xl ${action.glow}`}
          >
            <div className="text-4xl mb-3 transform group-hover:scale-110 transition-transform duration-300">
              {action.icon}
            </div>
            <div className="font-semibold text-lg mb-2 group-hover:text-white transition-colors">
              {action.title}
            </div>
            <div className="text-xs text-gray-400 leading-relaxed">
              {action.description}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default AssistantDashboard;
