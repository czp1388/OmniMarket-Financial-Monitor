# 最简单开发启动
Write-Host "🚀 启动开发..." -ForegroundColor Green
.\setup_dev_env.ps1
.\scripts\start_service.ps1
Write-Host "📋 当前进度：" -ForegroundColor Cyan
if (Test-Path "progress.txt") { Get-Content "progress.txt" }
Write-Host "💬 复制上面的进度信息给DeepSeek" -ForegroundColor Yellow
