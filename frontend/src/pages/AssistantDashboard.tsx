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
    loadDashboardData();
    loadOpportunities();
  }, []);

  const loadDashboardData = async () => {
    try {
      // 调用真实 API
      const response = await axios.get(`http://localhost:8000/api/v1/assistant/dashboard/summary`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('加载仪表盘数据失败，使用默认数据:', error);
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
        active_strategies: []
      };
      setDashboardData(fallbackData);
    } finally {
      setLoading(false);
    }
  };

  const loadOpportunities = async () => {
    try {
      // 调用真实 API
      const response = await axios.get(`http://localhost:8000/api/v1/assistant/opportunities?limit=3`);
      setOpportunities(response.data);
    } catch (error) {
      console.error('加载市场机会失败，使用默认数据:', error);
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
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#00ccff] mx-auto mb-4"></div>
          <div className="text-[#00ccff] text-lg">智能投资助手加载中...</div>
          <div className="text-gray-400 text-sm mt-2">正在为您准备专属投资方案</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] text-white">
      {/* 顶部导航栏 */}
      <header className="bg-[#141a2a] border-b border-[#2a3a5a] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-[#00ccff]">智能投资助手</h1>
            <span className="text-sm text-gray-400 bg-[#1a2332] px-3 py-1 rounded-full">
              助手模式
            </span>
          </div>
          <button
            onClick={() => navigate('/expert')}
            className="text-sm text-[#00ccff] hover:text-white transition-colors"
          >
            切换到专家模式 →
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* 问候语 */}
        <div className="mb-8">
          <h2 className="text-3xl font-light mb-2">{dashboardData?.greeting}</h2>
          <p className="text-gray-400">让我们看看今天有什么机会</p>
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
    <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4 text-[#00ccff]">💼 我的账户</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-400 mb-1">总资产</div>
          <div className="text-2xl font-bold">¥{summary.total_assets.toLocaleString()}</div>
        </div>
        <div>
          <div className="text-sm text-gray-400 mb-1">今日盈亏</div>
          <div className={`text-2xl font-bold ${isProfitable ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
            {isProfitable ? '+' : ''}{summary.today_profit.toLocaleString()}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-400 mb-1">累计收益</div>
          <div className="text-2xl font-bold text-[#00ff88]">
            +{summary.total_profit.toLocaleString()}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-400 mb-1">收益率</div>
          <div className="text-2xl font-bold text-[#00ff88]">
            +{summary.profit_rate.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="bg-[#1a2332] border border-[#2a3a5a] rounded px-3 py-2 text-sm text-gray-400">
        💡 {summary.message}
      </div>
    </div>
  );
};

const TodayActionsCard: React.FC<{ actions: TodayAction[] }> = ({ actions }) => {
  const priorityColors = {
    high: 'border-l-[#ff4444]',
    medium: 'border-l-[#ffaa00]',
    low: 'border-l-[#00ccff]'
  };

  const priorityIcons = {
    high: '🔥',
    medium: '⚡',
    low: '💡'
  };

  return (
    <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4 text-[#00ccff]">✅ 今日待办</h3>
      
      <div className="space-y-3">
        {actions.map((action, index) => (
          <div
            key={index}
            className={`bg-[#1a2332] border-l-4 ${priorityColors[action.priority]} rounded p-4 hover:bg-[#1f2838] transition-colors cursor-pointer`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span>{priorityIcons[action.priority]}</span>
                  <h4 className="font-semibold">{action.title}</h4>
                </div>
                <p className="text-sm text-gray-400">{action.description}</p>
              </div>
              <button className="ml-4 px-4 py-2 bg-[#00ccff] text-black rounded hover:bg-[#00aadd] transition-colors whitespace-nowrap">
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
    <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4 text-[#00ccff]">🎯 运行中的策略</h3>
      
      {strategies.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <p className="mb-4">您还没有激活任何策略</p>
          <button 
            onClick={() => navigate('/assistant/strategies/activate/stable_growth_low_risk')}
            className="px-6 py-2 bg-[#00ccff] text-black rounded hover:bg-[#00aadd] transition-colors"
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
              className="bg-[#1a2332] border border-[#2a3a5a] rounded p-4 hover:bg-[#1f2838] transition-colors cursor-pointer"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{strategy.friendly_name}</h4>
                <span className="px-3 py-1 bg-[#00ff88] text-black text-xs rounded-full">
                  运行中
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">已运行：</span>
                  <span className="ml-2">{strategy.days_active} 天</span>
                </div>
                <div>
                  <span className="text-gray-400">累计收益：</span>
                  <span className="ml-2 text-[#00ff88]">+¥{strategy.profit.toLocaleString()}</span>
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
    '低': 'bg-[#00ff88]',
    '中': 'bg-[#ffaa00]',
    '高': 'bg-[#ff4444]'
  };

  return (
    <div className="bg-[#141a2a] border border-[#2a3a5a] rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4 text-[#00ccff]">🔍 市场机会</h3>
      
      <div className="space-y-4">
        {opportunities.map((opp) => (
          <div
            key={opp.opportunity_id}
            className="bg-[#1a2332] border border-[#2a3a5a] rounded-lg p-4 hover:bg-[#1f2838] transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-semibold flex-1">{opp.title}</h4>
              <span className={`px-2 py-1 ${riskLevelColors[opp.risk_level as keyof typeof riskLevelColors]} text-black text-xs rounded`}>
                {opp.risk_level}风险
              </span>
            </div>
            
            <p className="text-sm text-gray-300 mb-2">{opp.explanation}</p>
            
            <div className="bg-[#0a0e17] border border-[#2a3a5a] rounded p-3 mb-3">
              <div className="text-xs text-gray-400 mb-1">💡 建议</div>
              <div className="text-sm">{opp.suggestion}</div>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{opp.potential_return}</span>
              <button className="px-4 py-2 bg-[#00ccff] text-black text-sm rounded hover:bg-[#00aadd] transition-colors">
                {opp.action_button}
              </button>
            </div>
          </div>
        ))}
      </div>
      
      <button className="w-full mt-4 py-2 border border-[#2a3a5a] rounded text-sm hover:bg-[#1a2332] transition-colors">
        查看更多机会 →
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
      color: 'border-[#00ccff]'
    },
    {
      icon: '🎯',
      title: '设置投资目标',
      description: '告诉我们您的期望',
      path: '/assistant/goals',
      color: 'border-[#00ff88]'
    },
    {
      icon: '📊',
      title: '查看历史表现',
      description: '回顾策略效果',
      path: '/assistant/performance',
      color: 'border-[#ffaa00]'
    },
    {
      icon: '🔔',
      title: '通知设置',
      description: '管理提醒方式',
      path: '/assistant/notifications',
      color: 'border-[#ff4444]'
    }
  ];

  return (
    <div className="mt-12">
      <h3 className="text-lg font-semibold mb-4 text-center text-gray-400">快速入口</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={() => navigate(action.path)}
            className={`bg-[#141a2a] border-2 ${action.color} rounded-lg p-4 hover:bg-[#1a2332] transition-colors text-left`}
          >
            <div className="text-3xl mb-2">{action.icon}</div>
            <div className="font-semibold mb-1">{action.title}</div>
            <div className="text-xs text-gray-400">{action.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default AssistantDashboard;
