# OmniMarket 金融监控系统 - API 文档

## 概述

本文档描述了 OmniMarket 金融监控系统的所有后端 API 端点。所有 API 端点都以 `/api/v1` 为前缀。

**基础 URL**: `http://localhost:8000/api/v1`

**认证方式**: JWT Bearer Token (部分端点需要认证)

**内容类型**: `application/json`

---

## 目录

1. [市场数据 API](#市场数据-api)
2. [预警系统 API](#预警系统-api)
3. [用户管理 API](#用户管理-api)
4. [技术指标 API](#技术指标-api)
5. [虚拟交易 API](#虚拟交易-api)
6. [窝轮分析 API](#窝轮分析-api)
7. [窝轮监控 API](#窝轮监控-api)
8. [半自动交易 API](#半自动交易-api)
9. [自动交易 API](#自动交易-api)
10. [交易分析 API](#交易分析-api)
11. [LEAN 回测 API](#lean-回测-api)

---

## 市场数据 API

### 获取 K 线数据
获取指定品种的 K 线历史数据。

**端点**: `GET /market/klines`

**查询参数**:
- `symbol` (string, required): 交易品种代码 (如 "BTC/USDT", "AAPL")
- `market_type` (string, required): 市场类型 ("CRYPTO", "STOCK", "FOREX", "FUTURES")
- `exchange` (string, optional): 交易所名称
- `timeframe` (string, required): 时间周期 ("1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M")
- `limit` (integer, optional, default=100): 返回数据条数

**响应示例**:
```json
[
  {
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "market_type": "CRYPTO",
    "timestamp": "2024-01-01T00:00:00Z",
    "open": 42000.50,
    "high": 42500.00,
    "low": 41800.00,
    "close": 42300.00,
    "volume": 1234.56
  }
]
```

### 获取实时行情
获取指定品种的实时行情数据。

**端点**: `GET /market/quote`

**查询参数**:
- `symbol` (string, required): 交易品种代码
- `market_type` (string, required): 市场类型

**响应示例**:
```json
{
  "symbol": "BTC/USDT",
  "price": 42300.00,
  "change": 300.00,
  "change_percent": 0.71,
  "volume": 123456.78,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 获取支持的品种列表
获取系统支持的所有交易品种。

**端点**: `GET /market/symbols`

**查询参数**:
- `market_type` (string, optional): 按市场类型筛选

**响应示例**:
```json
{
  "symbols": ["BTC/USDT", "ETH/USDT", "AAPL", "TSLA"],
  "count": 4
}
```

---

## 预警系统 API

### 创建预警
创建新的价格或技术指标预警。

**端点**: `POST /alerts`

**认证**: 需要

**请求体**:
```json
{
  "name": "BTC 价格预警",
  "symbol": "BTC/USDT",
  "market_type": "CRYPTO",
  "condition_type": "PRICE_ABOVE",
  "condition_config": {
    "target_price": 45000.0
  },
  "notification_types": ["in_app", "email"],
  "is_active": true
}
```

**响应示例**:
```json
{
  "id": "alert_123",
  "name": "BTC 价格预警",
  "symbol": "BTC/USDT",
  "status": "ACTIVE",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 获取预警列表
获取用户的所有预警。

**端点**: `GET /alerts`

**认证**: 需要

**查询参数**:
- `status` (string, optional): 筛选状态 ("ACTIVE", "TRIGGERED", "DISABLED")
- `symbol` (string, optional): 筛选品种

**响应示例**:
```json
{
  "alerts": [
    {
      "id": "alert_123",
      "name": "BTC 价格预警",
      "symbol": "BTC/USDT",
      "status": "ACTIVE",
      "condition_type": "PRICE_ABOVE",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1
}
```

### 更新预警
更新现有预警配置。

**端点**: `PUT /alerts/{alert_id}`

**认证**: 需要

**请求体**:
```json
{
  "name": "BTC 价格预警（更新）",
  "is_active": false
}
```

### 删除预警
删除指定预警。

**端点**: `DELETE /alerts/{alert_id}`

**认证**: 需要

**响应**: `204 No Content`

### 测试预警条件
测试预警条件是否触发（不保存）。

**端点**: `POST /alerts/test`

**请求体**:
```json
{
  "symbol": "BTC/USDT",
  "market_type": "CRYPTO",
  "condition_type": "PRICE_ABOVE",
  "condition_config": {
    "target_price": 45000.0
  }
}
```

**响应示例**:
```json
{
  "triggered": true,
  "current_value": 45100.0,
  "message": "条件满足：当前价格 45100.0 高于目标价格 45000.0"
}
```

---

## 用户管理 API

### 用户注册
注册新用户账户。

**端点**: `POST /users/register`

**请求体**:
```json
{
  "username": "trader123",
  "email": "trader@example.com",
  "password": "SecurePassword123!"
}
```

**响应示例**:
```json
{
  "id": "user_123",
  "username": "trader123",
  "email": "trader@example.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 用户登录
用户登录获取访问令牌。

**端点**: `POST /users/login`

**请求体**:
```json
{
  "username": "trader123",
  "password": "SecurePassword123!"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 获取用户信息
获取当前登录用户的信息。

**端点**: `GET /users/me`

**认证**: 需要

**响应示例**:
```json
{
  "id": "user_123",
  "username": "trader123",
  "email": "trader@example.com",
  "created_at": "2024-01-01T12:00:00Z",
  "preferences": {
    "default_market": "CRYPTO",
    "default_timeframe": "1h"
  }
}
```

---

## 技术指标 API

### 计算移动平均线
计算指定品种的移动平均线。

**端点**: `GET /technical/ma`

**查询参数**:
- `symbol` (string, required): 交易品种
- `market_type` (string, required): 市场类型
- `timeframe` (string, required): 时间周期
- `period` (integer, optional, default=20): MA 周期
- `ma_type` (string, optional, default="SMA"): MA 类型 ("SMA", "EMA")

**响应示例**:
```json
{
  "symbol": "BTC/USDT",
  "indicator": "MA",
  "period": 20,
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 42150.00
    }
  ]
}
```

### 计算 MACD
计算 MACD 指标。

**端点**: `GET /technical/macd`

**查询参数**:
- `symbol` (string, required)
- `market_type` (string, required)
- `timeframe` (string, required)
- `fast_period` (integer, optional, default=12)
- `slow_period` (integer, optional, default=26)
- `signal_period` (integer, optional, default=9)

**响应示例**:
```json
{
  "symbol": "BTC/USDT",
  "indicator": "MACD",
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "macd": 120.5,
      "signal": 110.3,
      "histogram": 10.2
    }
  ]
}
```

### 计算 RSI
计算相对强弱指数。

**端点**: `GET /technical/rsi`

**查询参数**:
- `symbol` (string, required)
- `market_type` (string, required)
- `timeframe` (string, required)
- `period` (integer, optional, default=14)

**响应示例**:
```json
{
  "symbol": "BTC/USDT",
  "indicator": "RSI",
  "period": 14,
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 65.5
    }
  ]
}
```

### 计算布林带
计算布林带指标。

**端点**: `GET /technical/bollinger`

**查询参数**:
- `symbol` (string, required)
- `market_type` (string, required)
- `timeframe` (string, required)
- `period` (integer, optional, default=20)
- `std_dev` (float, optional, default=2.0)

**响应示例**:
```json
{
  "symbol": "BTC/USDT",
  "indicator": "BOLLINGER",
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "upper": 43000.0,
      "middle": 42000.0,
      "lower": 41000.0
    }
  ]
}
```

---

## 虚拟交易 API

### 创建虚拟账户
创建新的虚拟交易账户。

**端点**: `POST /virtual/accounts`

**认证**: 需要

**请求体**:
```json
{
  "name": "测试账户",
  "initial_capital": 100000.0,
  "currency": "USD"
}
```

**响应示例**:
```json
{
  "account_id": "va_123",
  "name": "测试账户",
  "balance": 100000.0,
  "currency": "USD",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 下单
在虚拟账户中下单。

**端点**: `POST /virtual/orders`

**认证**: 需要

**请求体**:
```json
{
  "account_id": "va_123",
  "symbol": "BTC/USDT",
  "order_type": "LIMIT",
  "side": "BUY",
  "quantity": 0.1,
  "price": 42000.0
}
```

**响应示例**:
```json
{
  "order_id": "order_123",
  "status": "PENDING",
  "symbol": "BTC/USDT",
  "order_type": "LIMIT",
  "side": "BUY",
  "quantity": 0.1,
  "price": 42000.0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 获取持仓
获取虚拟账户的持仓信息。

**端点**: `GET /virtual/positions`

**认证**: 需要

**查询参数**:
- `account_id` (string, required)

**响应示例**:
```json
{
  "positions": [
    {
      "symbol": "BTC/USDT",
      "quantity": 0.5,
      "avg_price": 41500.0,
      "current_price": 42300.0,
      "unrealized_pnl": 400.0,
      "unrealized_pnl_percent": 1.93
    }
  ]
}
```

### 获取订单历史
获取虚拟账户的历史订单。

**端点**: `GET /virtual/orders/history`

**认证**: 需要

**查询参数**:
- `account_id` (string, required)
- `status` (string, optional): 筛选订单状态
- `limit` (integer, optional, default=50)

**响应示例**:
```json
{
  "orders": [
    {
      "order_id": "order_123",
      "symbol": "BTC/USDT",
      "order_type": "LIMIT",
      "side": "BUY",
      "quantity": 0.1,
      "price": 42000.0,
      "status": "FILLED",
      "filled_quantity": 0.1,
      "avg_fill_price": 42000.0,
      "created_at": "2024-01-01T12:00:00Z",
      "filled_at": "2024-01-01T12:05:00Z"
    }
  ]
}
```

---

## 窝轮分析 API

### 单个窝轮分析
分析单个窝轮的定价和Greeks。

**端点**: `POST /warrants/analyze-single`

**请求体**:
```json
{
  "warrant_code": "12345.HK",
  "underlying_price": 100.0,
  "strike_price": 105.0,
  "warrant_type": "CALL",
  "maturity_date": "2024-12-31",
  "volatility": 0.25
}
```

**响应示例**:
```json
{
  "warrant_code": "12345.HK",
  "theoretical_price": 2.50,
  "greeks": {
    "delta": 0.55,
    "gamma": 0.03,
    "theta": -0.02,
    "vega": 0.15
  },
  "leverage": 4.2,
  "implied_volatility": 0.27
}
```

### 批量窝轮分析
批量分析多个窝轮。

**端点**: `POST /warrants/analyze-batch`

**请求体**:
```json
{
  "warrants": [
    {
      "warrant_code": "12345.HK",
      "underlying_price": 100.0,
      "strike_price": 105.0,
      "warrant_type": "CALL",
      "maturity_date": "2024-12-31"
    }
  ]
}
```

### 窝轮回测
回测窝轮交易策略。

**端点**: `POST /warrants/backtest`

**请求体**:
```json
{
  "warrant_code": "12345.HK",
  "strategy": "momentum",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000.0
}
```

### 风险评估
评估窝轮的综合风险。

**端点**: `GET /warrants/risk-assessment`

**查询参数**:
- `warrant_code` (string, required)
- `current_price` (float, required)
- `underlying_price` (float, required)

**响应示例**:
```json
{
  "warrant_code": "12345.HK",
  "risk_level": "MEDIUM",
  "risk_score": 6.5,
  "knock_out_probability": 0.15,
  "time_decay_rate": 0.02,
  "leverage_ratio": 4.2
}
```

### 综合风险分析
执行窝轮的综合风险分析。

**端点**: `POST /warrants/risk-analysis/comprehensive`

**请求体**:
```json
{
  "warrant_code": "12345.HK",
  "current_price": 2.50,
  "underlying_price": 100.0,
  "strike_price": 105.0,
  "warrant_type": "CALL",
  "maturity_date": "2024-12-31",
  "knock_out_price": 95.0,
  "volatility": 0.25
}
```

---

## 窝轮监控 API

### 获取窝轮列表
获取系统监控的窝轮列表。

**端点**: `GET /warrants-monitoring/warrants`

**响应示例**:
```json
[
  {
    "warrant_code": "12345.HK",
    "name": "腾讯认购轮",
    "underlying_code": "0700.HK",
    "current_price": 2.50,
    "change_percent": 1.5,
    "volume": 1000000,
    "last_update": "2024-01-01T12:00:00Z"
  }
]
```

### 获取单个窝轮详情
获取指定窝轮的详细信息。

**端点**: `GET /warrants-monitoring/warrants/{warrant_code}`

**响应示例**:
```json
{
  "warrant_code": "12345.HK",
  "name": "腾讯认购轮",
  "underlying_code": "0700.HK",
  "warrant_type": "CALL",
  "strike_price": 105.0,
  "maturity_date": "2024-12-31",
  "conversion_ratio": 10.0,
  "current_price": 2.50,
  "underlying_price": 100.0,
  "leverage": 4.2,
  "premium": 0.05
}
```

### 获取预警
获取窝轮监控预警。

**端点**: `GET /warrants-monitoring/alerts`

**响应示例**:
```json
[
  {
    "alert_id": "wa_123",
    "warrant_code": "12345.HK",
    "alert_type": "PRICE_CHANGE",
    "message": "价格上涨超过 5%",
    "severity": "HIGH",
    "timestamp": "2024-01-01T12:00:00Z",
    "acknowledged": false
  }
]
```

### 确认预警
确认已读预警。

**端点**: `POST /warrants-monitoring/alerts/{warrant_code}/acknowledge`

**响应**: `200 OK`

### 获取窝轮指标
获取指定窝轮的实时指标。

**端点**: `GET /warrants-monitoring/metrics/{warrant_code}`

**响应示例**:
```json
{
  "warrant_code": "12345.HK",
  "implied_volatility": 0.27,
  "delta": 0.55,
  "gamma": 0.03,
  "theta": -0.02,
  "vega": 0.15,
  "leverage": 4.2,
  "premium": 0.05,
  "distance_to_knockout": 5.0
}
```

### 启动监控
启动窝轮监控服务。

**端点**: `POST /warrants-monitoring/monitoring/start`

**响应示例**:
```json
{
  "status": "started",
  "message": "窝轮监控服务已启动",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 停止监控
停止窝轮监控服务。

**端点**: `POST /warrants-monitoring/monitoring/stop`

**响应示例**:
```json
{
  "status": "stopped",
  "message": "窝轮监控服务已停止",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 获取监控状态
获取窝轮监控服务状态。

**端点**: `GET /warrants-monitoring/status`

**响应示例**:
```json
{
  "is_running": true,
  "monitored_warrants": 2,
  "active_alerts": 3,
  "last_update": "2024-01-01T12:00:00Z"
}
```

---

## 半自动交易 API

### 创建交易信号
创建半自动交易信号。

**端点**: `POST /semi-auto-trading/signals`

**认证**: 需要

**请求体**:
```json
{
  "symbol": "BTC/USDT",
  "signal_type": "BUY",
  "price": 42000.0,
  "quantity": 0.1,
  "reason": "技术指标突破"
}
```

**响应示例**:
```json
{
  "signal_id": "signal_123",
  "status": "PENDING_CONFIRMATION",
  "symbol": "BTC/USDT",
  "signal_type": "BUY",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 确认交易信号
确认并执行交易信号。

**端点**: `POST /semi-auto-trading/signals/{signal_id}/confirm`

**认证**: 需要

**响应示例**:
```json
{
  "signal_id": "signal_123",
  "status": "EXECUTED",
  "order_id": "order_456",
  "executed_at": "2024-01-01T12:05:00Z"
}
```

### 获取待确认信号
获取所有待确认的交易信号。

**端点**: `GET /semi-auto-trading/signals/pending`

**认证**: 需要

**响应示例**:
```json
{
  "signals": [
    {
      "signal_id": "signal_123",
      "symbol": "BTC/USDT",
      "signal_type": "BUY",
      "price": 42000.0,
      "quantity": 0.1,
      "reason": "技术指标突破",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

## 自动交易 API

### 创建交易策略
创建新的自动交易策略。

**端点**: `POST /auto-trading/strategies`

**认证**: 需要

**请求体**:
```json
{
  "name": "移动平均线交叉策略",
  "symbol": "BTC/USDT",
  "strategy_type": "MA_CROSSOVER",
  "parameters": {
    "fast_period": 10,
    "slow_period": 30
  },
  "risk_config": {
    "max_position_size": 1000.0,
    "stop_loss_percent": 0.05,
    "take_profit_percent": 0.10
  }
}
```

**响应示例**:
```json
{
  "strategy_id": "strat_123",
  "name": "移动平均线交叉策略",
  "status": "INACTIVE",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 启动策略
启动自动交易策略。

**端点**: `POST /auto-trading/strategies/{strategy_id}/start`

**认证**: 需要

**响应示例**:
```json
{
  "strategy_id": "strat_123",
  "status": "ACTIVE",
  "started_at": "2024-01-01T12:00:00Z"
}
```

### 停止策略
停止自动交易策略。

**端点**: `POST /auto-trading/strategies/{strategy_id}/stop`

**认证**: 需要

**响应示例**:
```json
{
  "strategy_id": "strat_123",
  "status": "STOPPED",
  "stopped_at": "2024-01-01T12:30:00Z"
}
```

### 获取策略列表
获取用户的所有交易策略。

**端点**: `GET /auto-trading/strategies`

**认证**: 需要

**响应示例**:
```json
{
  "strategies": [
    {
      "strategy_id": "strat_123",
      "name": "移动平均线交叉策略",
      "symbol": "BTC/USDT",
      "status": "ACTIVE",
      "pnl": 1250.50,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### 获取策略表现
获取策略的详细表现数据。

**端点**: `GET /auto-trading/strategies/{strategy_id}/performance`

**认证**: 需要

**响应示例**:
```json
{
  "strategy_id": "strat_123",
  "total_trades": 45,
  "win_rate": 0.62,
  "total_pnl": 1250.50,
  "sharpe_ratio": 1.85,
  "max_drawdown": 0.12,
  "equity_curve": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "equity": 100000.0
    }
  ]
}
```

---

## 交易分析 API

### 获取交易统计
获取账户的交易统计信息。

**端点**: `GET /analytics/statistics`

**认证**: 需要

**查询参数**:
- `account_id` (string, required)
- `start_date` (string, optional)
- `end_date` (string, optional)

**响应示例**:
```json
{
  "total_trades": 120,
  "winning_trades": 75,
  "losing_trades": 45,
  "win_rate": 0.625,
  "total_pnl": 12500.50,
  "avg_win": 250.00,
  "avg_loss": -180.00,
  "profit_factor": 1.85,
  "sharpe_ratio": 1.62
}
```

### 获取权益曲线
获取账户的权益曲线数据。

**端点**: `GET /analytics/equity-curve`

**认证**: 需要

**查询参数**:
- `account_id` (string, required)
- `start_date` (string, optional)
- `end_date` (string, optional)

**响应示例**:
```json
{
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "equity": 100000.0,
      "balance": 95000.0,
      "unrealized_pnl": 5000.0
    }
  ]
}
```

### 获取风险指标
获取账户的风险分析指标。

**端点**: `GET /analytics/risk-metrics`

**认证**: 需要

**查询参数**:
- `account_id` (string, required)

**响应示例**:
```json
{
  "max_drawdown": 0.15,
  "max_drawdown_duration_days": 12,
  "volatility": 0.25,
  "var_95": -2500.0,
  "sharpe_ratio": 1.62,
  "sortino_ratio": 2.10,
  "calmar_ratio": 3.50
}
```

---

## LEAN 回测 API

### 创建回测
创建新的策略回测任务。

**端点**: `POST /lean/backtest`

**认证**: 需要

**请求体**:
```json
{
  "strategy_id": "ma_cross",
  "strategy_code": "class MyStrategy(QCAlgorithm): ...",
  "symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 10000.0,
  "parameters": {
    "fast_period": 10,
    "slow_period": 30
  }
}
```

**响应示例**:
```json
{
  "backtest_id": "bt_123",
  "status": "RUNNING",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 获取回测状态
获取回测任务的当前状态。

**端点**: `GET /lean/backtest/{backtest_id}`

**认证**: 需要

**响应示例**:
```json
{
  "backtest_id": "bt_123",
  "status": "COMPLETED",
  "progress": 100,
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:15:00Z"
}
```

### 获取回测结果
获取回测的详细结果。

**端点**: `GET /lean/backtest/{backtest_id}/results`

**认证**: 需要

**响应示例**:
```json
{
  "backtest_id": "bt_123",
  "statistics": {
    "total_return": 0.25,
    "annual_return": 0.25,
    "sharpe_ratio": 1.85,
    "max_drawdown": 0.12,
    "win_rate": 0.65,
    "total_trades": 45
  },
  "equity_curve": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "equity": 10000.0
    }
  ],
  "trades": [
    {
      "timestamp": "2023-01-15T10:00:00Z",
      "symbol": "AAPL",
      "side": "BUY",
      "quantity": 10,
      "price": 150.0,
      "pnl": 0.0
    }
  ]
}
```

### 获取回测列表
获取用户的所有回测任务。

**端点**: `GET /lean/backtests`

**认证**: 需要

**响应示例**:
```json
{
  "backtests": [
    {
      "backtest_id": "bt_123",
      "strategy_id": "ma_cross",
      "symbol": "AAPL",
      "status": "COMPLETED",
      "total_return": 0.25,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

## 错误响应

所有 API 端点在发生错误时返回统一的错误格式：

**格式**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": {}
  }
}
```

**常见错误码**:
- `400`: 请求参数错误
- `401`: 未授权，需要登录
- `403`: 权限不足
- `404`: 资源未找到
- `422`: 数据验证失败
- `500`: 服务器内部错误

**示例**:
```json
{
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "交易品种代码无效",
    "details": {
      "symbol": "INVALID_SYMBOL",
      "valid_formats": ["BTC/USDT", "AAPL"]
    }
  }
}
```

---

## WebSocket API

### 连接
连接到 WebSocket 服务器以接收实时数据。

**端点**: `ws://localhost:8000/ws`

**认证**: 通过查询参数传递 token（可选）

**示例**: `ws://localhost:8000/ws?token=YOUR_JWT_TOKEN`

### 订阅市场数据
订阅指定品种的实时行情。

**消息格式**:
```json
{
  "action": "subscribe",
  "symbol": "BTC/USDT",
  "market_type": "CRYPTO"
}
```

**响应消息**:
```json
{
  "type": "quote",
  "symbol": "BTC/USDT",
  "price": 42300.0,
  "change": 300.0,
  "change_percent": 0.71,
  "volume": 123456.78,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 取消订阅
取消订阅指定品种。

**消息格式**:
```json
{
  "action": "unsubscribe",
  "symbol": "BTC/USDT"
}
```

### 接收预警通知
订阅预警通知。

**响应消息**:
```json
{
  "type": "alert",
  "alert_id": "alert_123",
  "symbol": "BTC/USDT",
  "message": "BTC 价格突破 45000",
  "severity": "HIGH",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 速率限制

为保护系统资源，API 实施以下速率限制：

- **未认证请求**: 每分钟 60 次
- **已认证请求**: 每分钟 300 次
- **WebSocket 连接**: 每个用户最多 5 个并发连接

超过限制时返回 `429 Too Many Requests` 错误。

---

## 版本历史

- **v1.0.0** (2024-01-01): 初始版本发布
  - 基础市场数据 API
  - 预警系统 API
  - 用户管理 API
  - 虚拟交易 API
  - 窝轮分析和监控 API
  - 自动交易 API
  - LEAN 回测 API

---

## 支持

如有问题或建议，请联系开发团队或在 GitHub 提交 Issue。

**项目地址**: https://github.com/czp1388/OmniMarket-Financial-Monitor

---

*最后更新: 2024-01-01*
*API 版本: v1.0.0*
