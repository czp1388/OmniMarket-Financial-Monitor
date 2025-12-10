# 🚀 OmniMarket 快速开始指南

## 一键启动

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\start_services.ps1
```

等待10-15秒后，服务将在独立窗口中运行。

## 访问系统

| 服务 | 地址 | 说明 |
|------|------|------|
| 📊 **前端界面** | http://localhost:3000 | React应用主界面 |
| 📚 **API文档** | http://localhost:8000/docs | Swagger交互式API文档 |
| 🔧 **后端API** | http://localhost:8000 | RESTful API服务 |
| 📡 **WebSocket** | ws://localhost:8774 | 实时数据推送 |

## 停止服务

```powershell
powershell -ExecutionPolicy Bypass -File .\stop_services.ps1
```

## 测试服务状态

```powershell
powershell -ExecutionPolicy Bypass -File .\test_services.ps1
```

## 手动启动 (可选)

### 后端
```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端
```powershell
cd frontend
npm run dev
```

## 首次使用

1. **启动服务** (使用上面的一键启动命令)
2. **打开浏览器** 访问 http://localhost:3000
3. **浏览功能** 系统支持多个金融市场监控
4. **查看API** 访问 http://localhost:8000/docs 了解API功能

## 核心功能

- ✅ 加密货币实时行情监控
- ✅ A股、港股市场数据
- ✅ 外汇汇率监控
- ✅ 技术指标分析
- ✅ 价格预警系统
- ✅ 虚拟交易模拟
- ✅ 牛熊证监控 (港股窝轮)
- ✅ 回测系统

## 数据源说明

系统使用多数据源降级策略，无需API密钥即可运行：

- **加密货币**: CoinGecko (免费) → Alpha Vantage → Binance → 模拟数据
- **股票**: Alpha Vantage → Yahoo Finance → AkShare → 模拟数据
- **外汇**: Alpha Vantage → 模拟数据

如需使用付费数据源，可在 `.env` 文件中配置API密钥。

## 故障排除

### 端口被占用
```powershell
# 查看端口占用
Get-NetTCPConnection -LocalPort 3000,8000,8774 -State Listen

# 停止所有服务
.\stop_services.ps1
```

### Python模块缺失
```powershell
cd backend
pip install -r requirements.txt
```

### 前端依赖缺失
```powershell
cd frontend
npm install
```

## 更多信息

- **完整文档**: 查看 `README.md`
- **启动问题修复报告**: 查看 `STARTUP_FIX_REPORT.md`
- **API配置**: 查看 `API_KEYS_GUIDE.md`
- **部署指南**: 查看 `DEPLOYMENT.md`
