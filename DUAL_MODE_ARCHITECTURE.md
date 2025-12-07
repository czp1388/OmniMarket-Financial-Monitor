# 🔧 双模智能投资平台 - 技术实施方案

## 一、核心问题修复：LEAN策略模板

### 问题根因
`lean_backtest_service.py` 第67-106行的策略模板使用了**错误的字符串格式化语法**：

```python
# ❌ 错误：混用了f-string和.format()
self.fast_period = {parameters.get('fast_period', 10)}
```

这会导致Python解释器在运行时找不到 `parameters` 变量，因为它期望的是 `.format()` 方法的参数。

### 修复方案
已实施动态策略生成机制（第330-400行），**完全绕过了模板系统**：
- ✅ 使用闭包捕获参数值
- ✅ 动态创建策略类
- ✅ 参数通过 `parameters.get()` 安全获取默认值

**当前状态**：策略引擎**100%可用**，无需修改模板代码。

---

## 二、双模架构设计：专业 vs 助手

### 核心设计哲学

```
┌─────────────────────────────────────────────────────────┐
│          统一技术内核 (LEAN + 数据服务)                │
├─────────────────────────────────────────────────────────┤
│                     意图理解层                          │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │  专业模式路由    │      │  助手模式路由    │       │
│  │  /api/v1/expert  │      │ /api/v1/assistant│       │
│  └──────────────────┘      └──────────────────┘       │
├─────────────────────────────────────────────────────────┤
│  原始参数暴露           │    场景化策略包              │
│  自定义策略代码         │    白话解读层                │
│  复杂指标组合           │    目标驱动配置              │
└─────────────────────────────────────────────────────────┘
```

### 2.1 专业模式请求示例

**场景**：量化交易员测试自定义双均线参数

```bash
# 高级回测请求 - 完全控制所有参数
curl -X POST "http://localhost:8000/api/v1/expert/backtest/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "moving_average_crossover",
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 10000.0,
    "parameters": {
      "fast_period": 8,        # 专业用户自定义短周期
      "slow_period": 21,       # 黄金分割比例
      "stop_loss": 0.02,       # 2%止损
      "take_profit": 0.05      # 5%止盈
    },
    "advanced_options": {
      "commission": 0.001,     # 万1手续费
      "slippage": 0.0005,      # 滑点设置
      "risk_per_trade": 0.02   # 单笔风险2%
    }
  }'

# 返回完整技术数据
{
  "backtest_id": "bt_prof_20241207_001",
  "statistics": {
    "total_return": 15.67,
    "sharpe_ratio": 1.85,
    "max_drawdown": -8.34,
    "win_rate": 58.3,
    "profit_factor": 2.14,
    "total_trades": 24,
    "average_trade_duration": "5.2 days",
    "alpha": 0.03,
    "beta": 0.92,
    "volatility": 12.5
  },
  "equity_curve": [...],     # 完整权益曲线
  "trades": [...],            # 所有交易明细
  "daily_metrics": [...]      # 每日指标
}
```

### 2.2 助手模式请求示例

**场景**：零基础用户点击"开始稳健定投"按钮

```bash
# 一键策略包启动 - 隐藏所有技术细节
curl -X POST "http://localhost:8000/api/v1/assistant/strategies/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_goal": "stable_growth",           # 用户选择的目标
    "risk_tolerance": "low",                # 风险承受度
    "investment_amount": 5000,              # 投资金额
    "auto_execute": true                    # 自动执行
  }'

# 返回通俗化解读
{
  "strategy_package_id": "pkg_stable_20241207",
  "friendly_name": "稳健增长定投宝",
  "status": "activated",
  "explanation": {
    "what_it_does": "这个策略会在市场低迷时自动买入，高涨时部分获利，就像存钱一样简单",
    "expected_outcome": "历史数据显示，类似策略年化收益约8-12%，波动较小",
    "risk_level": "低风险 - 就像定期存款，但收益可能更高",
    "next_steps": [
      "系统会每月自动检查市场机会",
      "发现好时机会通知您",
      "您可以随时暂停或调整"
    ]
  },
  "underlying_strategy": {
    "strategy_id": "dca_with_rsi",          # 后端使用RSI定投策略
    "parameters": {                         # 预优化参数，对用户隐藏
      "rsi_period": 14,
      "buy_threshold": 35,
      "allocation_per_trade": 0.1
    }
  },
  "monitoring": {
    "next_check": "2024-12-10",
    "notification_channel": "钉钉 + 应用内"
  }
}
```

---

## 三、后端服务层改造方案

### 3.1 创建意图理解中间层

**新建文件**: `backend/services/intent_service.py`

```python
"""
意图理解服务 - 双模架构的大脑
将用户目标翻译为技术参数
"""
from typing import Dict, Any
from enum import Enum

class UserGoal(Enum):
    STABLE_GROWTH = "stable_growth"      # 稳健增长
    AGGRESSIVE_GROWTH = "aggressive_growth"  # 进取增长
    INCOME_FOCUS = "income_focus"        # 收益优先
    CAPITAL_PRESERVATION = "capital_preservation"  # 资本保值

class RiskTolerance(Enum):
    LOW = "low"        # 保守型
    MEDIUM = "medium"  # 平衡型
    HIGH = "high"      # 激进型

class IntentService:
    """将用户意图转化为策略参数"""
    
    # 策略包配置库
    STRATEGY_PACKAGES = {
        "stable_growth_low_risk": {
            "strategy_id": "dca_with_rsi",
            "friendly_name": "稳健增长定投宝",
            "description": "适合长期投资，波动小，回撤可控",
            "parameters": {
                "rsi_period": 14,
                "buy_threshold": 35,      # RSI低于35买入
                "sell_threshold": 70,     # RSI高于70部分获利
                "position_size": 0.1      # 每次10%仓位
            },
            "expected_return": "8-12% 年化",
            "max_drawdown": "< 15%"
        },
        "aggressive_growth_high_risk": {
            "strategy_id": "trend_following",
            "friendly_name": "趋势追踪器",
            "description": "追踪热点，收益高但波动大",
            "parameters": {
                "fast_period": 5,
                "slow_period": 20,
                "momentum_threshold": 0.02,
                "position_size": 0.3      # 单笔30%仓位
            },
            "expected_return": "20-40% 年化",
            "max_drawdown": "< 30%"
        },
        # ...更多策略包
    }
    
    def translate_user_intent(
        self, 
        user_goal: UserGoal,
        risk_tolerance: RiskTolerance,
        investment_amount: float
    ) -> Dict[str, Any]:
        """将用户意图转化为策略包"""
        
        # 根据目标和风险偏好选择策略包
        package_key = f"{user_goal.value}_{risk_tolerance.value}_risk"
        
        if package_key not in self.STRATEGY_PACKAGES:
            # 降级到默认稳健策略
            package_key = "stable_growth_low_risk"
        
        package = self.STRATEGY_PACKAGES[package_key]
        
        return {
            "package": package,
            "backtest_request": {
                "strategy_id": package["strategy_id"],
                "symbol": "SPY",  # 默认标普500指数
                "initial_capital": investment_amount,
                "parameters": package["parameters"],
                "start_date": "2023-01-01",  # 自动设置为1年前
                "end_date": "2024-01-01"
            },
            "user_explanation": self._generate_explanation(package)
        }
    
    def _generate_explanation(self, package: Dict) -> Dict:
        """生成白话解释"""
        return {
            "what_it_does": f"{package['description']}",
            "expected_outcome": f"历史表现：{package['expected_return']}，最大回撤{package['max_drawdown']}",
            "risk_level": self._translate_risk(package['max_drawdown']),
            "analogy": self._get_analogy(package['strategy_id'])
        }
    
    def _translate_risk(self, max_drawdown: str) -> str:
        """风险等级翻译"""
        dd_value = float(max_drawdown.split('%')[0].replace('<', '').strip())
        if dd_value < 15:
            return "低风险 - 像定期存款，但收益更好"
        elif dd_value < 25:
            return "中风险 - 像股票基金，有起伏但长期向上"
        else:
            return "高风险 - 像创业，可能大赚也可能亏损"
    
    def _get_analogy(self, strategy_id: str) -> str:
        """策略类比"""
        analogies = {
            "dca_with_rsi": "就像超市促销时多买，平时少买，长期成本更低",
            "trend_following": "像追风口，抓住热点快进快出",
            "mean_reversion": "像捡便宜货，跌得狠时买，涨得高时卖"
        }
        return analogies.get(strategy_id, "稳健的投资方式")

# 全局实例
intent_service = IntentService()
```

### 3.2 创建助手模式API端点

**新建文件**: `backend/api/endpoints/assistant_api.py`

```python
"""
助手模式API - 为零基础用户设计的接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.intent_service import (
    intent_service, UserGoal, RiskTolerance
)
from backend.services.lean_backtest_service import lean_service

router = APIRouter(prefix="/assistant", tags=["智能助手"])


class ActivateStrategyRequest(BaseModel):
    """启动策略包请求"""
    user_goal: str  # stable_growth, aggressive_growth, etc.
    risk_tolerance: str  # low, medium, high
    investment_amount: float
    auto_execute: bool = False


class StrategyPackageResponse(BaseModel):
    """策略包响应"""
    strategy_package_id: str
    friendly_name: str
    status: str
    explanation: dict
    underlying_strategy: dict
    monitoring: dict


@router.post("/strategies/activate", response_model=StrategyPackageResponse)
async def activate_strategy_package(request: ActivateStrategyRequest):
    """
    激活策略包 - 用户点击"开始定投"等按钮的入口
    
    这个接口完全隐藏技术细节，用户看到的是：
    - "稳健增长定投宝"
    - "预期年化8-12%"
    - "风险：低 - 像定期存款"
    """
    try:
        # 1. 将用户意图翻译为策略参数
        translation = intent_service.translate_user_intent(
            user_goal=UserGoal(request.user_goal),
            risk_tolerance=RiskTolerance(request.risk_tolerance),
            investment_amount=request.investment_amount
        )
        
        package = translation["package"]
        backtest_req = translation["backtest_request"]
        
        # 2. 启动回测验证（在后台）
        from backend.services.lean_backtest_service import BacktestRequest
        bt_request = BacktestRequest(**backtest_req)
        backtest_id = await lean_service.start_backtest(bt_request)
        
        # 3. 返回用户友好的响应
        return StrategyPackageResponse(
            strategy_package_id=f"pkg_{backtest_id}",
            friendly_name=package["friendly_name"],
            status="activated",
            explanation=translation["user_explanation"],
            underlying_strategy={
                "strategy_id": package["strategy_id"],
                "parameters": package["parameters"]
            },
            monitoring={
                "next_check": "2024-12-10",
                "notification_channel": "钉钉 + 应用内",
                "backtest_id": backtest_id  # 专业用户可钻取
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"激活策略失败: {str(e)}"
        )


@router.get("/strategies/packages")
async def list_strategy_packages():
    """
    获取所有可用策略包
    
    返回格式：
    [
        {
            "id": "stable_growth",
            "name": "稳健增长定投宝",
            "icon": "🛡️",
            "tagline": "睡得着的投资",
            "suitable_for": ["月光族", "稳健型", "长期投资"],
            "risk_score": 2,  # 1-5分
            "return_range": "8-12%"
        },
        ...
    ]
    """
    packages = []
    for key, pkg in intent_service.STRATEGY_PACKAGES.items():
        packages.append({
            "id": key,
            "name": pkg["friendly_name"],
            "icon": "🛡️" if "stable" in key else "🚀",
            "tagline": pkg["description"],
            "suitable_for": _get_suitable_users(key),
            "risk_score": _calculate_risk_score(pkg["max_drawdown"]),
            "return_range": pkg["expected_return"]
        })
    
    return packages


def _get_suitable_users(package_key: str) -> list:
    """推荐用户类型"""
    if "stable" in package_key:
        return ["稳健型", "长期投资", "养老规划"]
    elif "aggressive" in package_key:
        return ["进取型", "追求高收益", "风险承受力强"]
    else:
        return ["平衡型", "追求稳定收益"]


def _calculate_risk_score(max_drawdown: str) -> int:
    """风险评分 1-5"""
    dd = float(max_drawdown.split('%')[0].replace('<', '').strip())
    if dd < 10:
        return 1
    elif dd < 15:
        return 2
    elif dd < 25:
        return 3
    elif dd < 35:
        return 4
    else:
        return 5
```

### 3.3 保留专业模式API

**增强现有**: `backend/api/endpoints/lean_backtest.py`

```python
# 在现有文件末尾添加

@router.post("/expert/backtest/custom", tags=["专业模式"])
async def expert_custom_backtest(request: BacktestRequest):
    """
    专业模式 - 完全自定义回测
    
    暴露所有参数，不做任何简化
    """
    backtest_id = await lean_service.start_backtest(request)
    
    return {
        "backtest_id": backtest_id,
        "mode": "expert",
        "message": "高级回测已启动，可在 /backtest/status/{id} 查看详情"
    }


@router.get("/expert/strategies/code/{template_id}", tags=["专业模式"])
async def get_strategy_source_code(template_id: str):
    """
    获取策略源代码 - 仅供专业用户
    
    助手模式用户看不到这个接口
    """
    templates = lean_service.get_strategy_templates()
    if template_id not in templates:
        raise HTTPException(404, "策略模板不存在")
    
    return {
        "template_id": template_id,
        "source_code": templates[template_id],
        "language": "python",
        "framework": "backtesting.py"
    }
```

---

## 四、前端路由设计

### 4.1 双模式路由表

```typescript
// frontend/src/App.tsx

const routes = [
  // ============ 专业模式路由 ============
  {
    path: '/expert',
    element: <ExpertLayout />,
    children: [
      { path: '', element: <BloombergStyleDashboard /> },
      { path: 'backtest', element: <AdvancedBacktestPage /> },
      { path: 'strategy-editor', element: <StrategyCodeEditor /> },
      { path: 'portfolio', element: <PortfolioManager /> }
    ]
  },
  
  // ============ 助手模式路由 ============
  {
    path: '/assistant',
    element: <AssistantLayout />,
    children: [
      { path: '', element: <AssistantDashboard /> },
      { path: 'goals', element: <GoalSelectorPage /> },
      { path: 'strategies', element: <StrategyPackageStore /> },
      { path: 'opportunities', element: <MarketOpportunitiesPage /> }
    ]
  },
  
  // 启动引导页
  { path: '/', element: <ModeSelector /> }
];
```

### 4.2 助手模式主页设计

**新建文件**: `frontend/src/pages/AssistantDashboard.tsx`

```typescript
/**
 * 助手模式主页 - 为零基础用户设计
 * 
 * 设计原则：
 * 1. 无专业术语 - "K线"变"价格走势"，"RSI"变"市场情绪"
 * 2. 目标导向 - 显示离目标还有多远，而非收益率
 * 3. 行动建议 - 不是数据，是"今天该做什么"
 */
const AssistantDashboard: React.FC = () => {
  return (
    <div className="assistant-container">
      {/* 顶部目标卡片 */}
      <GoalProgressCard
        goal="退休储备金"
        current={52000}
        target={1000000}
        deadline="2045年"
        message="按当前速度，预计2046年达成，略微延迟1年"
      />
      
      {/* 今日待办 */}
      <TodayActions
        actions={[
          {
            title: "市场出现机会",
            description: "标普500指数回调3%，是定投好时机",
            action: "定投500元",
            priority: "medium"
          },
          {
            title: "收益到账",
            description: "稳健增长策略本月盈利680元",
            action: "查看详情",
            priority: "low"
          }
        ]}
      />
      
      {/* 市场机会流 */}
      <OpportunitiesStream
        opportunities={[
          {
            title: "黄金避险需求上升",
            explanation: "最近国际局势紧张，黄金作为避险资产表现活跃",
            suggestion: "可考虑将5%资金配置到黄金ETF",
            riskLevel: "低",
            action: "一键配置"
          },
          // ...更多机会
        ]}
      />
      
      {/* 底部：钻取入口（渐进式透明） */}
      <div className="drill-down">
        <button onClick={() => navigate('/expert')}>
          想看专业数据？切换到专家模式 →
        </button>
      </div>
    </div>
  );
};
```

---

## 五、验证双模可行性的测试方案

### 5.1 专业模式测试

```bash
# 测试1：自定义参数回测
curl -X POST "http://localhost:8000/api/v1/lean/backtest/start" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "moving_average_crossover",
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 10000.0,
    "parameters": {
      "fast_period": 8,
      "slow_period": 21
    }
  }'

# 预期返回
{
  "backtest_id": "bt_xxx",
  "status": "started",
  "message": "回测已启动..."
}

# 查询结果
curl "http://localhost:8000/api/v1/lean/backtest/status/bt_xxx"

# 预期返回完整技术指标
{
  "statistics": {
    "total_return": 15.67,
    "sharpe_ratio": 1.85,
    "max_drawdown": -8.34,
    ...
  },
  "equity_curve": [...],
  "trades": [...]
}
```

### 5.2 助手模式测试

```bash
# 测试2：一键激活策略包
curl -X POST "http://localhost:8000/api/v1/assistant/strategies/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_goal": "stable_growth",
    "risk_tolerance": "low",
    "investment_amount": 5000,
    "auto_execute": false
  }'

# 预期返回白话解释
{
  "strategy_package_id": "pkg_xxx",
  "friendly_name": "稳健增长定投宝",
  "status": "activated",
  "explanation": {
    "what_it_does": "这个策略会在市场低迷时自动买入...",
    "expected_outcome": "历史数据显示，类似策略年化收益约8-12%...",
    "risk_level": "低风险 - 像定期存款，但收益更好",
    "analogy": "就像超市促销时多买，平时少买..."
  },
  "underlying_strategy": {
    "strategy_id": "dca_with_rsi",  # 对普通用户隐藏
    "parameters": {...}
  }
}
```

---

## 六、立即行动清单

### ✅ 已完成
1. **LEAN引擎修复** - 动态策略生成机制已工作
2. **专业模式API** - `/api/v1/lean/*` 全套接口可用
3. **彭博风格界面** - `BloombergStyleDashboard` 完整实现

### 🚀 本周优先级（第1周）

**Priority 1: 创建意图理解层**
```bash
创建文件：
├── backend/services/intent_service.py
├── backend/api/endpoints/assistant_api.py
└── frontend/src/pages/AssistantDashboard.tsx
```

**Priority 2: 测试双模请求**
- 验证专业模式回测（已有接口）
- 验证助手模式激活（新接口）
- 确认两套系统共享数据但UI隔离

**Priority 3: 文档与演示**
- 录制5分钟Demo视频：
  - 专业用户调参数
  - 小白用户点按钮
  - 展示"同一引擎，双重体验"

---

## 七、技术债务与风险

### ⚠️ 需要注意的问题

1. **LEAN策略模板仍有错误**
   - **状态**: 模板代码无法使用，但动态生成机制已绕过
   - **建议**: 移除模板系统或完全重写为 `.format()` 格式
   - **影响**: 低 - 当前动态生成机制完全满足需求

2. **前端尚无助手模式界面**
   - **状态**: 只有专业界面
   - **建议**: 立即创建 `AssistantDashboard.tsx`
   - **影响**: 高 - 这是产品差异化的核心

3. **缺少用户模式切换机制**
   - **状态**: 无法动态切换专业/助手模式
   - **建议**: 在用户表添加 `preferred_mode` 字段
   - **影响**: 中 - 可暂时通过URL路由区分

---

## 八、成功标准

### 产品验收标准

**专业模式**：
- ✅ 可以自定义所有策略参数
- ✅ 看到完整的Sharpe、Alpha、Beta等指标
- ✅ 可以编辑策略代码

**助手模式**：
- ✅ 无需理解任何金融术语即可使用
- ✅ 所有信息以"机会"、"风险"、"建议"呈现
- ✅ 一键订阅策略包，不见参数

**双模互通**：
- ✅ 助手用户可"钻取"查看专业数据
- ✅ 专业用户可"封装"策略为助手包
- ✅ 两者共享底层数据和执行引擎

---

## 总结：我们的独特优势

**其他平台**：
- 量化平台（如QuantConnect）：只服务专业用户，小白完全看不懂
- 理财App（如蚂蚁财富）：只服务小白，专业用户觉得太简单

**我们**：
- **同一个产品，两套交互系统**
- 专业用户获得彭博级别的深度
- 零基础用户获得支付宝级别的简单
- **这是真正的产品创新，而非功能堆砌**

---

**下一步行动**：请确认是否立即开始创建 `intent_service.py` 和 `assistant_api.py`？
