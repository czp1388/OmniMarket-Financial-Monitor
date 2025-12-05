# OmniMarket 金融监控系统 - AI 编码指南

## 项目概览
多市场金融分析平台，支持加密货币、A股、港股、外汇等市场的实时监控、技术分析、虚拟交易和自动交易。

**技术栈**: FastAPI + React 18 + TypeScript + InfluxDB/PostgreSQL/Redis + WebSocket

## 架构核心

### 服务层架构模式
所有后端服务遵循单例异步服务模式：
- 每个服务导出小写的全局实例（如 `alert_service`, `data_service`）
- 使用 `async def start_monitoring()` 初始化后台任务
- 在 `backend/main.py` 的 `lifespan()` 中统一启动服务
- 服务间通过直接导入实例通信（非依赖注入）

```python
# 标准服务模式 - 参考 backend/services/alert_service.py
class AlertService:
    def __init__(self):
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self):
        if self.is_running:
            return
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

alert_service = AlertService()  # 导出全局单例
```

### 数据源容错策略
`DataService` 实现多数据源降级机制（`backend/services/data_service.py:75-220`）：

**加密货币数据源优先级**：
1. CoinGecko（免费，无需API密钥）
2. Alpha Vantage（免费，需API密钥）
3. CCXT Binance（交易所直连）
4. Mock Data（模拟数据兜底）

**股票数据源优先级**：
1. Alpha Vantage（免费，需API密钥）
2. Yahoo Finance（yfinance，免费）
3. AkShare（A股专用，免费）
4. Mock Data（模拟数据兜底）

**外汇数据源**：
- Alpha Vantage（唯一外汇数据源）

**容错机制**：
- 每个源失败后自动尝试下一个，使用 `data_quality_monitor.record_error()` 记录
- 所有源失败时自动降级到模拟数据，保证系统始终可用
- 所有数据通过 `data_cache_service` 缓存（TTL=300秒）减少API调用

### 数据库架构
- **InfluxDB**: K线时序数据，通过 `influx_write_api/influx_query_api` 全局访问
- **PostgreSQL**: 用户、预警、交易记录（SQLAlchemy ORM）
- **Redis**: 市场数据缓存、WebSocket消息队列
- **容错**: 所有数据库连接失败时记录警告但继续运行（`database.py:26-57`）

### WebSocket 实时通信
`websocket_manager` 管理所有实时数据推送：
- FastAPI端点: `/ws` (HTTP升级)
- 独立WebSocket服务器: `localhost:8774`（用于跨服务通信）
- 订阅模式: 客户端发送 `{"action": "subscribe", "symbol": "BTC/USDT"}` 订阅特定品种

## 开发工作流

### 启动命令
```bash
# 后端（端口8000）
cd backend
uvicorn main:app --reload

# 前端（端口5173）
cd frontend
npm run dev

# 项目诊断
python project_diagnostic.py
```

### 添加新API端点
1. 在 `backend/api/endpoints/` 创建路由文件
2. 在 `backend/api/routes.py` 中使用 `api_router.include_router()` 注册
3. 所有路由自动带 `/api/v1` 前缀

### 添加新服务
1. 在 `backend/services/` 创建服务文件
2. 实现 `start_monitoring()` 异步初始化方法
3. 导出小写单例实例（如 `my_service = MyService()`）
4. 在 `backend/main.py:lifespan()` 中启动服务

## 关键约定

### 彭博终端风格 UI 标准（强制）
**参考**: `frontend/src/pages/BloombergStyleDashboard.tsx` + `PROJECT_UI_STANDARDS.md`

所有前端页面必须使用以下设计系统：
- **主背景**: `#0a0e17` (深蓝黑)
- **容器背景**: `#141a2a` (半透明深色)
- **边框**: `#2a3a5a` (深蓝)
- **上涨/绿色**: `#00ff88`
- **下跌/红色**: `#ff4444`
- **信息蓝**: `#00ccff`
- **字体**: 等宽字体（Courier New/Monaco）用于数值显示
- **布局**: 紧凑网格，最小边距 2-5px，高信息密度

```css
/* 标准价格卡片 - 参考 PROJECT_UI_STANDARDS.md:30-44 */
.price-card {
  background: #141a2a;
  border: 1px solid #2a3a5a;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}
```

### 环境变量配置
**配置文件**: `.env` (Git忽略，需手动创建)

**必填项（生产环境）**：
```env
# 安全配置
SECRET_KEY=your-secure-random-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/omnimarket

# 数据库连接
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
REDIS_URL=redis://localhost:6379
```

**可选项（增强功能）**：
```env
# 数据源API密钥（可选，无密钥时使用免费源或模拟数据）
TUSHARE_TOKEN=your-tushare-token
BINANCE_API_KEY=your-binance-key
BINANCE_SECRET_KEY=your-binance-secret

# 通知服务
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

所有配置项在 `backend/config.py` 中定义，支持环境变量覆盖默认值。

### 合规性检查（必须）
**参考**: `DEVELOPMENT_ROADMAP.md:1-50`

每次开发新功能前检查：
1. ✅ 所有交易功能标记"模拟交易"
2. ✅ API密钥通过环境变量配置（`.env` 文件，不提交到Git）
3. ✅ 虚拟交易系统不涉及真实资金
4. ✅ 用户密码使用 `passlib.hash` 哈希存储
5. ✅ 技术指标仅为数学计算，不提供投资建议

### 模型和Pydantic
- 所有数据模型在 `backend/models/` 定义
- API响应使用Pydantic模型验证
- 枚举类型（如 `MarketType`, `Timeframe`）集中在模型文件中

### 错误处理
- 数据源失败时降级到模拟数据，不抛出异常
- WebSocket断开时自动清理订阅（`websocket_manager.unregister()`）
- 使用 `logger.warning()` 而非 `logger.error()` 记录非关键故障

## 技术细节

### 窝轮（权证）分析
港股窝轮功能位于 `backend/services/warrants_*` 三个服务：
- `warrants_data_service`: 数据采集
- `warrants_analysis_service`: 定价和Greeks计算
- `warrants_monitoring_service`: 实时监控和预警

### 回测系统
集成三个回测引擎：
- **Backtesting.py**: 轻量级快速回测（默认使用）
- **VectorBT**: 矢量化高性能回测
- **LEAN**: QuantConnect开源引擎（需额外配置）

**LEAN 引擎配置**（可选）：
1. LEAN 依赖已在 `requirements.txt` 中注释（pythonnet 在 Windows 需额外配置）
2. 取消注释 `pythonnet==3.0.2` 和 `clr-loader==0.2.5`
3. Windows 用户需安装 .NET Framework 4.8+
4. 策略模板位于 `lean_backtest_service.py:67-120`
5. 默认使用 `backtesting.py` 库，无需 LEAN 配置即可运行

**回测服务使用**：
```python
# 创建回测请求
request = BacktestRequest(
    strategy_id="ma_cross",
    strategy_code="...",  # 策略代码
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2024-01-01",
    initial_capital=10000.0
)

# 执行回测
backtest_id = await lean_backtest_service.start_backtest(request)
```

### 虚拟交易引擎
`VirtualTradingEngine` 实现完整的订单生命周期：
- 虚拟资金账户管理（初始资金、保证金）
- 订单簿模拟（市价单、限价单、止损单）
- 成交撮合和持仓管理
- 交易历史和性能统计

## 常见任务

## 部署和运维

### 本地开发环境
```bash
# 1. 安装后端依赖
cd backend
pip install -r requirements.txt

# 2. 创建 .env 文件（参考环境变量配置）
cp .env.example .env  # 手动创建并配置

# 3. 启动后端
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. 安装前端依赖
cd ../frontend
npm install

# 5. 启动前端
npm run dev
```

### 生产环境部署
**当前状态**：项目缺少 `DEPLOYMENT.md`，以下为基础部署建议

**数据库准备**：
- PostgreSQL: 创建数据库和用户
- InfluxDB: 创建 org 和 bucket
- Redis: 确保服务运行

**后端部署**：
```bash
# 使用 Gunicorn + Uvicorn workers
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**前端部署**：
```bash
# 构建生产版本
npm run build

# 使用 Nginx 或其他静态服务器托管 dist/ 目录
```

**环境变量**：
- 生产环境必须配置 `SECRET_KEY`（使用强随机密钥）
- 数据库连接字符串指向生产数据库
- API 密钥根据需要配置

**Docker 部署**（待补充）：
- 项目暂无 Dockerfile，可自行创建
- 建议使用 docker-compose 管理多容器

### 测试策略

**当前状态**：项目无测试文件，以下为测试规范建议

**单元测试**（未实现）：
- 使用 pytest 框架
- 测试文件命名: `test_*.py` 或 `*_test.py`
- 放置位置: `backend/tests/` 目录
- 覆盖关键服务逻辑（数据源降级、预警触发等）

**集成测试**（未实现）：
- 测试 API 端点完整流程
- WebSocket 连接和消息传递
- 数据库读写操作

**测试示例**：
```python
# backend/tests/test_data_service.py
import pytest
from backend.services.data_service import DataService

@pytest.mark.asyncio
async def test_get_klines_with_fallback():
    """测试数据源降级机制"""
    service = DataService()
    klines = await service.get_klines(
        symbol="BTC/USDT",
        market_type=MarketType.CRYPTO,
        exchange="binance",
        timeframe=Timeframe.HOUR_1
    )
    assert len(klines) > 0
    assert klines[0].symbol == "BTC/USDT"
```

**运行测试**：
```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest backend/tests/

# 运行特定测试
pytest backend/tests/test_data_service.py -v
```

## 测试和诊断
- 运行 `python project_diagnostic.py` 检查项目完整性
- 检查服务文件大小判断功能完整度（>5KB为完整实现）
- 前端开发服务器自动热重载，无需重启
- 使用浏览器开发者工具调试 WebSocket 连接py` 的降级链中添加新源
4. 在 `_register_data_sources()` 中注册到质量监控

### 添加新技术指标
1. 在 `technical_analysis_service.py` 添加计算方法
2. 遵循 TA-Lib 接口模式（输入 DataFrame，返回 Series/DataFrame）
3. 在前端 `BloombergStyleDashboard.tsx` 的技术指标选择器中添加选项

### 调试 WebSocket
- WebSocket日志在 `backend/services/websocket_manager.py:73-108`
- 使用浏览器控制台查看客户端消息：`ws://localhost:8000/ws`
- 订阅/取消订阅消息格式见 `handle_message()` 方法

## 依赖管理
- 后端: `backend/requirements.txt` (35个依赖，无严格版本锁定)
- 前端: `frontend/package.json` (React 18 + Vite + Tailwind + ECharts)
- 数据库可选：InfluxDB和Redis失败时服务仍可运行

## 测试和诊断
- 运行 `python project_diagnostic.py` 检查项目完整性
- 检查服务文件大小判断功能完整度（>5KB为完整实现）
- 前端开发服务器自动热重载，无需重启
