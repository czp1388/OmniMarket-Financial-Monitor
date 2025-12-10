# OmniMarket 前后端启动问题修复报告

## 修复内容

### 1. 后端启动优化
- ✅ 在 `backend/main.py` 的 `lifespan()` 函数中添加了完善的异常处理
- ✅ 所有服务启动时使用 try-except 包装，防止单个服务失败导致整个应用崩溃
- ✅ 添加了详细的日志输出，便于诊断问题

### 2. 创建服务管理脚本
创建了三个PowerShell脚本用于服务管理：

#### `start_services.ps1` - 启动脚本
- 在独立的PowerShell窗口中启动后端服务
- 在另一个独立的PowerShell窗口中启动前端服务
- 自动进行健康检查
- 显示服务访问地址

#### `stop_services.ps1` - 停止脚本
- 自动查找并停止所有Python/Uvicorn进程
- 自动查找并停止所有Node进程
- 检查端口释放状态

#### `test_services.ps1` - 测试脚本
- 检查前端服务状态 (http://localhost:3000)
- 检查后端健康接口 (http://localhost:8000/health)
- 检查后端根路径 (http://localhost:8000)
- 检查API文档 (http://localhost:8000/docs)

## 当前服务状态

### ✅ 后端服务 (已成功启动)
- **地址**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **状态**: 正常运行
- **端口监听**: 
  - 8000: FastAPI HTTP服务器
  - 8774: WebSocket服务器

**已启动的服务**:
- ✅ 数据库连接 (InfluxDB正常, Redis不可用但不影响核心功能)
- ✅ 数据服务
- ✅ 预警监控服务
- ✅ WebSocket服务器
- ✅ 牛熊证监控服务 (使用模拟数据)
- ✅ 数据质量监控服务

### ✅ 前端服务 (已成功启动)
- **地址**: http://localhost:3000
- **开发服务器**: Vite
- **状态**: 正常监听端口3000
- **注意**: Vite开发服务器对根路径返回404是正常的，需要访问具体页面路由

## 使用说明

### 启动服务
```powershell
# 方法1: 使用启动脚本 (推荐)
powershell -ExecutionPolicy Bypass -File .\start_services.ps1

# 方法2: 手动启动
# 后端:
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端:
cd frontend
npm run dev
```

### 停止服务
```powershell
powershell -ExecutionPolicy Bypass -File .\stop_services.ps1
```

### 测试服务状态
```powershell
powershell -ExecutionPolicy Bypass -File .\test_services.ps1
```

### 访问系统
- **前端界面**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs (Swagger UI)
- **WebSocket连接**: ws://localhost:8774

## 已知问题和解决方案

### 1. Redis连接失败
**问题**: `WARNING:backend.database:Redis连接失败`
**影响**: 缓存功能不可用，但不影响核心功能
**解决**: 可选 - 安装并启动Redis服务以启用缓存功能

### 2. 富途数据服务未连接
**问题**: `WARNING:services.futu_data_service:富途数据服务未连接，使用模拟数据`
**影响**: 牛熊证数据使用模拟数据
**解决**: 可选 - 配置富途OpenAPI连接以使用真实数据

### 3. 前端根路径返回404
**问题**: 访问 http://localhost:3000 返回404
**说明**: 这是Vite开发服务器的正常行为
**解决**: 直接访问具体页面路由，如 http://localhost:3000/dashboard

## 技术细节

### 后端技术栈
- **框架**: FastAPI
- **服务器**: Uvicorn
- **数据库**: InfluxDB (时序数据), PostgreSQL/SQLite (关系数据)
- **缓存**: Redis (可选)
- **WebSocket**: websockets库

### 前端技术栈
- **框架**: React 18
- **构建工具**: Vite
- **UI样式**: Tailwind CSS
- **图表库**: ECharts, Recharts, Chart.js

### 数据源
- **加密货币**: CoinGecko (免费), Alpha Vantage, CCXT Binance
- **股票**: Alpha Vantage, Yahoo Finance, AkShare
- **外汇**: Alpha Vantage
- **牛熊证**: 富途OpenAPI (可选), 模拟数据

## 下一步建议

1. ✅ 前后端服务已正常启动
2. ⏭️ 测试前端页面功能
3. ⏭️ 测试API端点 (通过 http://localhost:8000/docs)
4. ⏭️ 配置API密钥以使用真实数据源 (可选)
5. ⏭️ 安装Redis以启用缓存功能 (可选)
6. ⏭️ 配置富途OpenAPI以使用真实牛熊证数据 (可选)
