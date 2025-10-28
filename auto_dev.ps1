# 全自动开发助手 - 智能版本
Write-Host "🤖 启动 OmniMarket 智能开发模式..." -ForegroundColor Magenta

Write-Host "`n🔧 执行标准开发流程..." -ForegroundColor Cyan

# 1. 环境设置
Write-Host "1. 环境检查..." -ForegroundColor Yellow
.\setup_dev_env.ps1

# 2. 启动服务
Write-Host "`n2. 启动服务..." -ForegroundColor Yellow
.\scripts\start_service.ps1

# 3. 生成智能DeepSeek话术
Write-Host "`n3. 生成智能对话话术..." -ForegroundColor Cyan
.\scripts\generate_deepseek_message.ps1

Write-Host "`n🎉 智能模式已启动！复制上面的话术给DeepSeek即可。" -ForegroundColor Green
