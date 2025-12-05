# API 密钥获取指南

本文档介绍如何获取各数据源的 API 密钥以提升 OmniMarket 系统的数据质量。

**重要说明**：所有 API 密钥都是**可选的**。未配置时，系统会自动使用免费数据源或模拟数据。

---

## 📊 数据源概览

| 数据源 | 数据类型 | 注册难度 | 免费额度 | 推荐度 |
|--------|---------|---------|---------|-------|
| **CoinGecko** | 加密货币 | ❌ 无需注册 | 无限制 | ⭐⭐⭐⭐⭐ |
| **Yahoo Finance** | 全球股票 | ❌ 无需注册 | 无限制 | ⭐⭐⭐⭐⭐ |
| **Alpha Vantage** | 股票+外汇 | ✅ 简单 | 500次/天 | ⭐⭐⭐⭐ |
| **Tushare** | A股数据 | ✅ 需实名 | 基础数据 | ⭐⭐⭐⭐ |
| **AkShare** | A股数据 | ❌ 无需注册 | 无限制 | ⭐⭐⭐ |
| **Binance** | 加密货币 | ✅ 中等 | 1200次/分 | ⭐⭐⭐⭐ |
| **富途OpenD** | 港股实时 | ⭐⭐⭐ 需账户 | 需客户端 | ⭐⭐⭐ |

---

## 1. Alpha Vantage（股票和外汇数据）

### 数据类型
- ✅ 美股实时和历史数据
- ✅ 全球股票数据
- ✅ 外汇汇率（实时）
- ✅ 加密货币数据
- ✅ 技术指标

### 获取步骤

1. **访问官网**
   - URL: https://www.alphavantage.co/support/#api-key

2. **填写申请表单**
   - Email: 填写你的邮箱
   - Organization: `Individual` 或你的公司名
   - Purpose: `Personal Use` 或 `Academic Research`

3. **获取密钥**
   - 提交后立即显示 API Key
   - 同时会发送到邮箱

4. **配置到 OmniMarket**
   编辑 `backend/.env` 文件：
   ```env
   ALPHA_VANTAGE_API_KEY=YOUR_API_KEY_HERE
   ```

### 免费额度
- **每分钟**: 5 次请求
- **每天**: 500 次请求

### 示例 API Key 格式
```
ALPHA_VANTAGE_API_KEY=ABC123XYZ789DEF456GHI
```

### 使用建议
- 适合查询美股和外汇数据
- 请求频率较低时使用
- 可注册多个账号获取多个密钥

---

## 2. Tushare（A股数据）

### 数据类型
- ✅ A股实时和历史行情
- ✅ 指数数据
- ✅ 财务数据
- ✅ 基金数据
- ✅ 期货数据

### 获取步骤

1. **注册账号**
   - URL: https://tushare.pro/register
   - 需要手机号验证

2. **实名认证（可选，提升权限）**
   - 登录后进入：https://tushare.pro/user/token
   - 完成实名认证可获得更高积分

3. **获取 Token**
   - 注册后自动生成 Token
   - 在个人中心 → 接口TOKEN 查看

4. **配置到 OmniMarket**
   编辑 `backend/.env` 文件：
   ```env
   TUSHARE_TOKEN=YOUR_TOKEN_HERE
   ```

### 积分系统
Tushare 使用积分制，积分越高，可用接口越多：

| 积分 | 获取方式 | 权限 |
|------|---------|------|
| 120分 | 注册 | 基础行情 |
| 200分 | 实名认证 | 日线数据 |
| 300分 | 分享推广 | 分钟数据 |
| 500分 | 捐赠 | 实时数据 |

**获取积分方法**：
- ✅ 每日签到：2-5 分
- ✅ 分享给好友注册：50 分/人
- ✅ 社区贡献（回答问题）：10-50 分
- ✅ 捐赠支持：50 分/100 元

### 示例 Token 格式
```
TUSHARE_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

### 使用建议
- 主要用于 A股数据
- 积分 200+ 可满足大部分需求
- 定期签到积累积分

---

## 3. Binance（加密货币交易所）

### 数据类型
- ✅ 加密货币实时价格
- ✅ K线数据
- ✅ 深度数据
- ✅ 交易对信息

### 获取步骤

1. **注册账号**
   - URL: https://www.binance.com
   - 需要邮箱或手机验证

2. **创建 API 密钥**
   - 登录后进入：个人中心 → API管理
   - 点击"创建API"
   - 完成身份验证（谷歌认证器或手机验证码）

3. **设置 API 权限**
   - ✅ 勾选：**读取**（Read）
   - ❌ 不勾选：交易、提现等权限
   - 这样最安全，只能查询数据

4. **白名单设置（可选）**
   - 绑定可信IP地址
   - 增强安全性

5. **配置到 OmniMarket**
   编辑 `backend/.env` 文件：
   ```env
   BINANCE_API_KEY=your-api-key-here
   BINANCE_SECRET_KEY=your-secret-key-here
   ```

### 免费额度
- **重量级限制**: 1200/分钟
- **订单限制**: 10/秒
- **WebSocket**: 无限制

### 示例 API Key 格式
```
BINANCE_API_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
BINANCE_SECRET_KEY=1234567890aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

### 安全建议
- ⚠️ **仅启用"读取"权限**，不要启用交易权限
- ⚠️ 定期更换 API 密钥
- ⚠️ 不要将密钥提交到 Git 仓库
- ⚠️ 设置 IP 白名单

---

## 4. 富途证券 OpenD（港股实时数据）

### 数据类型
- ✅ 港股实时行情
- ✅ 窝轮（权证）数据
- ✅ 牛熊证数据
- ✅ K线数据
- ✅ 深度数据

### 获取步骤

1. **注册富途账号**
   - URL: https://www.futunn.com
   - 需要实名认证

2. **下载富途牛牛客户端**
   - Windows/Mac: https://www.futunn.com/download
   - 安装并登录

3. **启用 OpenD 服务**
   - 在富途牛牛中：设置 → API → 启用 OpenD
   - 默认端口：11111
   - 记录解锁密码（如果设置）

4. **安装 Python SDK**（已包含在 requirements.txt）
   ```bash
   pip install futu-api
   ```

5. **配置到 OmniMarket**
   编辑 `backend/.env` 文件：
   ```env
   FUTU_HOST=127.0.0.1
   FUTU_PORT=11111
   FUTU_UNLOCK_PASSWORD=your-password-if-set
   ```

### 使用限制
- 需要富途牛牛客户端保持运行
- 需要登录富途账号
- 港股实时行情需要账户有相应权限

### 故障排查
如果连接失败，系统会自动使用模拟数据，不影响其他功能。

---

## 5. Telegram 通知（可选）

### 获取 Bot Token 和 Chat ID

1. **创建 Telegram Bot**
   - 在 Telegram 中搜索 `@BotFather`
   - 发送 `/newbot`
   - 按提示设置 Bot 名称和用户名
   - 复制返回的 Bot Token

2. **获取 Chat ID**
   - 在 Telegram 中搜索 `@userinfobot`
   - 发送任意消息
   - Bot 会返回你的 Chat ID

3. **配置到 OmniMarket**
   编辑 `backend/.env` 文件：
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=987654321
   ```

4. **测试通知**
   启动 OmniMarket 后，预警触发时会自动发送 Telegram 消息。

---

## 6. SMTP 邮件通知（可选）

### Gmail 示例

1. **开启两步验证**
   - 访问：https://myaccount.google.com/security
   - 启用"两步验证"

2. **生成应用专用密码**
   - 访问：https://myaccount.google.com/apppasswords
   - 选择"邮件"和"其他设备"
   - 生成密码（16位，无空格）

3. **配置到 OmniMarket**
   编辑 `backend/.env` 文件：
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-digit-app-password
   EMAIL_FROM=your-email@gmail.com
   ```

### 其他邮件服务商

| 服务商 | SMTP 服务器 | 端口 | 安全 |
|--------|------------|------|------|
| Gmail | smtp.gmail.com | 587 | TLS |
| Outlook | smtp-mail.outlook.com | 587 | TLS |
| QQ邮箱 | smtp.qq.com | 587 | TLS |
| 163邮箱 | smtp.163.com | 465 | SSL |
| 126邮箱 | smtp.126.com | 465 | SSL |

---

## 配置验证

### 检查配置是否生效

1. **重启后端服务**
   ```powershell
   cd E:\OmniMarket-Financial-Monitor\backend
   python -m uvicorn main:app --reload
   ```

2. **查看启动日志**
   - ✅ 数据源初始化成功
   - ⚠️ 未配置的服务会使用降级方案

3. **测试 API**
   访问 http://localhost:8000/docs 测试各个端点

### 日志示例

**配置成功**：
```
INFO:backend.services.alpha_vantage_service:Alpha Vantage API 已配置
INFO:backend.services.data_service:使用 Alpha Vantage 作为股票数据源
```

**未配置（降级）**：
```
INFO:backend.services.data_service:未配置 Alpha Vantage API，使用 Yahoo Finance
```

---

## 安全最佳实践

### 1. 环境变量管理
- ✅ 使用 `.env` 文件存储密钥
- ✅ `.env` 已在 `.gitignore` 中，不会提交到 Git
- ❌ 不要在代码中硬编码密钥

### 2. 权限控制
- ✅ API 密钥仅赋予必要的权限（如只读）
- ✅ Binance API 不要开启交易权限
- ✅ 定期更换密钥

### 3. 访问限制
- ✅ 设置 IP 白名单（如 Binance）
- ✅ 监控 API 使用量
- ✅ 发现异常立即禁用密钥

### 4. 备份
- ✅ 备份 `.env` 文件到安全位置
- ✅ 使用密码管理器存储密钥
- ❌ 不要将密钥发送到云端（除非加密）

---

## 故障排除

### 问题 1: API 密钥配置后无效

**可能原因**：
- `.env` 文件位置错误（应在 `backend/.env`）
- 未重启服务
- 密钥包含多余的空格或引号

**解决方案**：
```powershell
# 检查 .env 文件位置
Test-Path E:\OmniMarket-Financial-Monitor\backend\.env

# 重启服务
# 按 Ctrl+C 停止，然后重新启动
python -m uvicorn main:app --reload
```

### 问题 2: API 请求超过限额

**解决方案**：
- 增加缓存时间（修改 `.env` 中的 `CACHE_TTL`）
- 减少数据更新频率（修改 `DATA_UPDATE_INTERVAL`）
- 使用多个 API 密钥轮换

### 问题 3: Tushare 权限不足

**解决方案**：
- 查看积分：https://tushare.pro/user/token
- 每日签到获取积分
- 邀请好友注册（50分/人）

---

## 总结

### 推荐配置优先级

**最小配置（推荐新手）**：
```env
# 无需任何 API 密钥，系统自动使用免费数据源
# CoinGecko（加密货币） + Yahoo Finance（股票） + AkShare（A股）
```

**基础配置（推荐一般用户）**：
```env
ALPHA_VANTAGE_API_KEY=your_key  # 提升美股和外汇数据质量
```

**进阶配置（推荐高级用户）**：
```env
ALPHA_VANTAGE_API_KEY=your_key
TUSHARE_TOKEN=your_token        # 提升A股数据质量
BINANCE_API_KEY=your_key        # 提升加密货币数据质量
BINANCE_SECRET_KEY=your_secret
```

**完整配置（推荐专业用户）**：
```env
# 所有数据源 + 通知服务 + 富途港股
ALPHA_VANTAGE_API_KEY=your_key
TUSHARE_TOKEN=your_token
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id
FUTU_HOST=127.0.0.1
FUTU_PORT=11111
```

### 效果对比

| 配置级别 | 数据延迟 | 数据覆盖 | 请求限制 | 适用场景 |
|---------|---------|---------|---------|---------|
| 无配置 | 5-15分钟 | 主流品种 | 无限制 | 学习测试 |
| 基础配置 | 1-5分钟 | 全球主要市场 | 500次/天 | 个人投资 |
| 进阶配置 | 实时 | 全市场覆盖 | 1000+次/天 | 活跃交易 |
| 完整配置 | 实时 | 全市场+港股 | 无限制 | 专业交易 |

---

需要帮助？查看 [部署文档](DEPLOYMENT.md) 或提交 Issue。
