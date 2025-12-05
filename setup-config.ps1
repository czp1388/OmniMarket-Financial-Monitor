#!/usr/bin/env pwsh
# OmniMarket 配置向导
# 用于快速配置 .env 文件

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  OmniMarket 配置向导" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$envPath = "E:\OmniMarket-Financial-Monitor\backend\.env"

# 检查 .env 文件是否存在
if (Test-Path $envPath) {
    Write-Host "✅ 发现现有配置文件: $envPath" -ForegroundColor Green
    $overwrite = Read-Host "是否要更新配置？(y/n)"
    if ($overwrite -ne "y") {
        Write-Host "配置已取消" -ForegroundColor Yellow
        exit
    }
}

Write-Host ""
Write-Host "📝 开始配置向导..." -ForegroundColor Yellow
Write-Host "提示: 直接按回车跳过可选配置" -ForegroundColor Gray
Write-Host ""

# Alpha Vantage
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "1. Alpha Vantage API (股票和外汇数据)" -ForegroundColor Cyan
Write-Host "   获取地址: https://www.alphavantage.co/support/#api-key" -ForegroundColor Gray
$alphaKey = Read-Host "请输入 Alpha Vantage API Key (可选)"

# Tushare
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "2. Tushare Token (A股数据)" -ForegroundColor Cyan
Write-Host "   获取地址: https://tushare.pro/register" -ForegroundColor Gray
$tushareToken = Read-Host "请输入 Tushare Token (可选)"

# Binance
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "3. Binance API (加密货币数据)" -ForegroundColor Cyan
Write-Host "   获取地址: https://www.binance.com → API管理" -ForegroundColor Gray
Write-Host "   ⚠️  仅启用'读取'权限，不要启用交易权限！" -ForegroundColor Yellow
$binanceKey = Read-Host "请输入 Binance API Key (可选)"
$binanceSecret = ""
if ($binanceKey) {
    $binanceSecret = Read-Host "请输入 Binance Secret Key"
}

# Telegram
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "4. Telegram 通知 (预警通知)" -ForegroundColor Cyan
Write-Host "   创建机器人: 与 @BotFather 对话" -ForegroundColor Gray
Write-Host "   获取 Chat ID: 与 @userinfobot 对话" -ForegroundColor Gray
$telegramToken = Read-Host "请输入 Telegram Bot Token (可选)"
$telegramChatId = ""
if ($telegramToken) {
    $telegramChatId = Read-Host "请输入 Telegram Chat ID"
}

# Email
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "5. 邮件通知 (预警通知)" -ForegroundColor Cyan
Write-Host "   Gmail 用户需要使用应用专用密码" -ForegroundColor Gray
Write-Host "   获取地址: https://myaccount.google.com/apppasswords" -ForegroundColor Gray
$smtpUsername = Read-Host "请输入邮箱地址 (可选)"
$smtpPassword = ""
if ($smtpUsername) {
    $smtpPassword = Read-Host "请输入邮箱密码/应用专用密码" -AsSecureString
    $smtpPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($smtpPassword)
    )
}

# Redis
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "6. Redis 配置 (缓存服务，可选)" -ForegroundColor Cyan
$redisUrl = "redis://localhost:6379"
$configRedis = Read-Host "是否配置 Redis? (y/n)"
if ($configRedis -eq "y") {
    Write-Host "   默认地址: redis://localhost:6379" -ForegroundColor Gray
    $customRedis = Read-Host "使用自定义 Redis 地址? (直接回车使用默认)"
    if ($customRedis) {
        $redisUrl = $customRedis
    }
}

# 生成 .env 文件
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "📝 生成配置文件..." -ForegroundColor Yellow

$envContent = @"
# OmniMarket 金融监控系统 - 环境变量配置
# 自动生成时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# ============================================
# 应用基础配置
# ============================================

APP_NAME=OmniMarket Financial Monitor
VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# ============================================
# 安全配置
# ============================================

SECRET_KEY=omnimarket-dev-secret-key-change-in-production-2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# 数据库配置
# ============================================

# InfluxDB 配置（时序数据）
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token-here
INFLUXDB_ORG=omnimarket
INFLUXDB_BUCKET=market_data

# Redis 配置（缓存，可选）
REDIS_URL=$redisUrl

# ============================================
# 数据源 API 密钥
# ============================================

"@

# 添加 API 密钥
if ($alphaKey) {
    $envContent += "`nALPHA_VANTAGE_API_KEY=$alphaKey"
} else {
    $envContent += "`n# ALPHA_VANTAGE_API_KEY="
}

if ($tushareToken) {
    $envContent += "`nTUSHARE_TOKEN=$tushareToken"
} else {
    $envContent += "`n# TUSHARE_TOKEN="
}

if ($binanceKey) {
    $envContent += "`nBINANCE_API_KEY=$binanceKey"
    $envContent += "`nBINANCE_SECRET_KEY=$binanceSecret"
} else {
    $envContent += "`n# BINANCE_API_KEY="
    $envContent += "`n# BINANCE_SECRET_KEY="
}

$envContent += @"


# ============================================
# 通知服务配置
# ============================================

"@

if ($telegramToken) {
    $envContent += "`nTELEGRAM_BOT_TOKEN=$telegramToken"
    $envContent += "`nTELEGRAM_CHAT_ID=$telegramChatId"
} else {
    $envContent += "`n# TELEGRAM_BOT_TOKEN="
    $envContent += "`n# TELEGRAM_CHAT_ID="
}

if ($smtpUsername) {
    $envContent += "`nSMTP_SERVER=smtp.gmail.com"
    $envContent += "`nSMTP_PORT=587"
    $envContent += "`nSMTP_USERNAME=$smtpUsername"
    $envContent += "`nSMTP_PASSWORD=$smtpPassword"
    $envContent += "`nEMAIL_FROM=$smtpUsername"
} else {
    $envContent += "`n# SMTP_SERVER=smtp.gmail.com"
    $envContent += "`n# SMTP_PORT=587"
    $envContent += "`n# SMTP_USERNAME="
    $envContent += "`n# SMTP_PASSWORD="
    $envContent += "`n# EMAIL_FROM="
}

$envContent += @"


# ============================================
# 富途证券配置（港股实时数据，可选）
# ============================================

FUTU_HOST=127.0.0.1
FUTU_PORT=11111
# FUTU_UNLOCK_PASSWORD=

# ============================================
# 性能配置
# ============================================

DATA_UPDATE_INTERVAL=60
MAX_HISTORICAL_DAYS=365
CACHE_TTL=300
API_RATE_LIMIT_PER_MINUTE=300
MAX_WS_CONNECTIONS_PER_USER=5

# ============================================
# 日志配置
# ============================================

LOG_LEVEL=INFO
LOG_FILE=logs/omnimarket.log
"@

# 保存文件
Set-Content -Path $envPath -Value $envContent -Encoding UTF8

Write-Host "✅ 配置文件已生成: $envPath" -ForegroundColor Green
Write-Host ""

# 显示配置摘要
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "📊 配置摘要" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$configCount = 0
if ($alphaKey) { 
    Write-Host "  ✅ Alpha Vantage API" -ForegroundColor Green
    $configCount++
} else {
    Write-Host "  ⚪ Alpha Vantage API (未配置)" -ForegroundColor Gray
}

if ($tushareToken) { 
    Write-Host "  ✅ Tushare Token" -ForegroundColor Green
    $configCount++
} else {
    Write-Host "  ⚪ Tushare Token (未配置)" -ForegroundColor Gray
}

if ($binanceKey) { 
    Write-Host "  ✅ Binance API" -ForegroundColor Green
    $configCount++
} else {
    Write-Host "  ⚪ Binance API (未配置)" -ForegroundColor Gray
}

if ($telegramToken) { 
    Write-Host "  ✅ Telegram 通知" -ForegroundColor Green
    $configCount++
} else {
    Write-Host "  ⚪ Telegram 通知 (未配置)" -ForegroundColor Gray
}

if ($smtpUsername) { 
    Write-Host "  ✅ 邮件通知" -ForegroundColor Green
    $configCount++
} else {
    Write-Host "  ⚪ 邮件通知 (未配置)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "已配置 $configCount 个服务" -ForegroundColor Yellow
Write-Host ""

# 后续步骤
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "🚀 下一步" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "1. (可选) 安装 Redis 缓存服务" -ForegroundColor White
Write-Host "   查看文档: REDIS_SETUP.md" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 启动后端服务" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python -m uvicorn main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 启动前端服务" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 访问系统" -ForegroundColor White
Write-Host "   前端: http://localhost:3000" -ForegroundColor Gray
Write-Host "   API文档: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "需要帮助？查看文档:" -ForegroundColor Yellow
Write-Host "  • API_KEYS_GUIDE.md - API密钥获取指南" -ForegroundColor Gray
Write-Host "  • REDIS_SETUP.md - Redis安装指南" -ForegroundColor Gray
Write-Host "  • DEPLOYMENT.md - 完整部署文档" -ForegroundColor Gray
Write-Host ""
