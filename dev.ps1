# 一键开发命令
Write-Host "🚀 启动 OmniMarket 开发..." -ForegroundColor Magenta

# 自动修复所有问题
.\scripts\auto_fix.ps1 -FixType all

# 启动标准开发流程
.\auto_dev.ps1
