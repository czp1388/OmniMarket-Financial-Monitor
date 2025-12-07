# 寰宇多市场金融监控系统 (OmniMarket Financial Monitor)

## 🌟 产品定位：双模智能投资平台

**一个平台，两种体验，服务所有投资者**

- 🎓 **助手模式**: 零基础小白用户 - "我想稳健增长" → 系统自动配置
- 🔬 **专家模式**: 量化交易员 - 完全控制所有技术参数

### 核心创新
- **意图理解引擎**: 将白话目标翻译为量化策略
- **策略包系统**: 预配置策略，一键激活
- **渐进式透明**: 从小白逐步成长为专家

---

## 项目特性

### 🆕 双模架构（2025.12.7）
- 🤖 **助手模式**: 通俗化表达，隐藏技术细节，目标驱动
- 🔬 **专家模式**: 彭博终端风格，完整技术指标，参数完全控制
- 🔄 **无缝切换**: 同一引擎，两种交互，数据共享

### 多市场支持
- 📊 **多市场**: A股、港股、外汇、加密货币、商品期货（16种）
- ⏰ **多时间周期**: 1分钟到年线的完整K线数据
- 🔔 **智能预警**: 价格、技术指标、形态识别（21种）预警
- 💰 **虚拟交易**: 投资组合监控、风险控制、回测系统
- 📈 **专业图表**: TradingView级别图表 + 7种绘图工具

### 量化引擎
- 🎯 **LEAN集成**: QuantConnect开源引擎
- 📊 **回测系统**: 3个引擎（Backtesting.py, VectorBT, LEAN）
- 🤖 **自动交易**: 半自动/全自动交易策略
- 📈 **技术分析**: 50+技术指标，21种形态识别

### 通知渠道
- 📧 **5种渠道**: Email、Telegram、钉钉、飞书、Webhook
- 🔔 **实时推送**: 预警触发即时通知
- 🎨 **自定义**: 通知模板、频率、优先级可配置

## 🚀 快速开始

### 双模体验（推荐）
```bash
# 一键启动双模架构
.\start_dual_mode.ps1

# 或手动启动
# 终端1：后端
cd backend
uvicorn main:app --reload --port 8000

# 终端2：前端
cd frontend
npm run dev
```

**访问地址**:
- 🤖 助手模式（零基础）: http://localhost:3001/assistant
- 🔬 专家模式（量化交易）: http://localhost:3001/expert
- 📚 API文档: http://localhost:8000/docs

### 测试双模API
```bash
# Python验证
python quick_verify_dual_mode.py

# PowerShell curl测试
.\test_dual_mode_curl.ps1
```

---

## 技术架构

### 后端技术栈
- **语言**: Python 3.9+
- **框架**: FastAPI + WebSocket
- **数据库**: InfluxDB (时序), PostgreSQL (关系), Redis (缓存)
- **量化引擎**: LEAN (QuantConnect) + Backtesting.py + VectorBT
- **数据源**: CoinGecko, Alpha Vantage, yfinance, AkShare

### 前端技术栈
- **框架**: React 18 + TypeScript
- **图表**: Lightweight Charts (TradingView) + ECharts
- **构建工具**: Vite
- **样式**: Tailwind CSS + 彭博终端深色主题

### 双模架构
```
用户层
  ├─ 助手模式: 通俗化UI + 意图理解
  └─ 专家模式: 技术化UI + 参数暴露
        ↓
   意图理解层 (intent_service)
        ↓
   统一LEAN引擎
        ↓
   数据服务层（容错降级）
```

---

## 开发阶段

### ✅ 已完成（96%+）
- [x] 加密货币、A股、港股、外汇数据接入
- [x] 基础K线图表 + 7种绘图工具
- [x] 50+技术指标 + 21种形态识别
- [x] 5种通知渠道（Email, Telegram, 钉钉, 飞书, Webhook）
- [x] 投资组合管理 + 虚拟交易
- [x] LEAN量化引擎集成
- [x] 16种商品期货数据
- [x] **🆕 双模架构（助手+专家）**

### 🚧 进行中
- [ ] 市场机会推荐算法（当前模拟数据）
- [ ] 用户目标持久化
- [ ] 策略运行状态实时更新

### 📅 计划中
- [ ] 目标跟踪功能（进度条）
- [ ] 策略对比工具
- [ ] 助手聊天界面（ChatGPT式交互）
- [ ] 移动端适配

## 快速开始

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 项目结构
```
OmniMarket-Financial-Monitor/
├── backend/          # FastAPI后端
├── frontend/         # React前端
├── docs/             # 项目文档
├── scripts/          # 部署脚本
└── data/             # 数据文件
```

## 许可证
MIT License
