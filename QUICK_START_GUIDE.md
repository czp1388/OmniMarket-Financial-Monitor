# OmniMarket 金融监控系统 - 快速启动指南

## 🎯 系统状态

✅ **核心功能验证通过**
- 意图理解服务正常（5 个策略包）
- 意图翻译功能正常
- 白话解读生成正常

✅ **依赖已安装**
- 后端：50+ Python 包
- 前端：node_modules 完整

## 🚀 启动步骤

### 1. 启动后端服务

打开 **新的 PowerShell 窗口**，运行：

```powershell
cd E:\OmniMarket-Financial-Monitor\backend
..\.venv\Scripts\python.exe main_simple.py
```

或者使用 uvicorn：

```powershell
cd E:\OmniMarket-Financial-Monitor
.\.venv\Scripts\python.exe -m uvicorn backend.main_simple:app --host 0.0.0.0 --port 8000
```

**后端服务信息：**
- 📍 API 地址: http://localhost:8000
- 📚 API 文档: http://localhost:8000/docs
- 🤖 助手模式 API: http://localhost:8000/api/v1/assistant

### 2. 启动前端服务

打开 **另一个 PowerShell 窗口**，运行：

```powershell
cd E:\OmniMarket-Financial-Monitor\frontend
npm run dev
```

**前端服务信息：**
- 📍 主页面: http://localhost:3000
- 🤖 助手模式: http://localhost:3000/assistant
- 🎯 专家模式: http://localhost:3000/expert

## 📋 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端主页 | http://localhost:3000 | 系统首页 |
| 助手模式 | http://localhost:3000/assistant | 智能策略推荐 |
| 专家模式 | http://localhost:3000/expert | 高级策略配置 |
| API 文档 | http://localhost:8000/docs | FastAPI Swagger UI |
| API 根路径 | http://localhost:8000 | 服务状态信息 |
| 助手 API | http://localhost:8000/api/v1/assistant | 助手模式端点 |

## ⚠️ 已知问题

### 后端服务自动关闭问题
**问题描述：** 使用 `--reload` 模式启动时，服务在初始化完成后立即关闭。

**临时解决方案：**
1. 使用简化版 `main_simple.py`（已创建）
2. 不使用 `--reload` 参数：
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn backend.main_simple:app --host 0.0.0.0 --port 8000
   ```
3. 或直接运行 Python 脚本：
   ```powershell
   cd backend
   ..\.venv\Scripts\python.exe main_simple.py
   ```

### Redis 连接警告
**警告信息：** `Redis连接失败: Error 10061`

**说明：** 这是正常的。Redis 用于缓存，未启动时系统会使用内存缓存继续运行。

### 富途数据服务警告
**警告信息：** `富途数据服务未连接，使用模拟数据`

**说明：** 这是正常的。未配置富途 API 时，系统使用模拟数据进行开发测试。

## 💡 开发建议

### 数据库
- 当前使用 SQLite (`backend/omnimarket.db`)
- 生产环境需切换到 PostgreSQL

### API 测试
使用 cURL 测试 API 端点：

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 获取策略包列表
curl http://localhost:8000/api/v1/assistant/strategies/packages

# 激活策略（POST）
curl -X POST http://localhost:8000/api/v1/assistant/strategies/activate \
  -H "Content-Type: application/json" \
  -d '{
    "user_goal": "stable_growth",
    "risk_tolerance": "low",
    "investment_amount": 5000,
    "investment_horizon": "long_term"
  }'
```

### 前端开发
- 热重载已启用（自动刷新）
- 修改代码后自动编译
- 浏览器开发者工具查看网络请求

## 📚 相关文档

- **项目总览**: `README.md`
- **API 文档**: `API_DOCS.md`
- **双模架构**: `DUAL_MODE_ARCHITECTURE.md`
- **助手模式进度**: `ASSISTANT_MODE_BACKEND_PROGRESS.md`
- **UI 标准**: `PROJECT_UI_STANDARDS.md`

## 🔧 故障排查

### 后端无法启动
1. 检查虚拟环境是否激活
2. 检查依赖是否完整：`pip list | grep fastapi`
3. 查看数据库文件是否存在：`backend/omnimarket.db`

### 前端无法启动
1. 检查 Node.js 版本：`node --version`（需要 >= 16）
2. 重新安装依赖：`npm install`
3. 清除缓存：`npm run build --force`

### API 请求失败
1. 确认后端服务正在运行
2. 检查端口占用：`netstat -ano | findstr :8000`
3. 查看浏览器控制台错误信息

---

**最后更新**: 2025-12-08 04:30  
**系统版本**: 1.0.0 (Phase 1 Week 1 MVP)
