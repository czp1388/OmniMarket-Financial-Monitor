# 🚀 一键启动开发环境

Write-Host "=== OmniMarket 开发环境启动 ===" -ForegroundColor Cyan

# 步骤1: 切换到项目目录
Write-Host "`n1. 切换到项目目录..." -ForegroundColor Yellow
cd E:\OmniMarket-Financial-Monitor

# 步骤2: 显示当前进度
Write-Host "`n2. 当前开发进度:" -ForegroundColor Cyan
if (Test-Path "现在在做什么.txt") {
    Get-Content "现在在做什么.txt"
} else {
    Write-Host "❌ 进度文件不存在，正在创建..." -ForegroundColor Red
    "📝 请在这里记录开发进度" | Set-Content "现在在做什么.txt" -Encoding utf8
}

# 步骤3: 启动服务
Write-Host "`n3. 启动服务..." -ForegroundColor Green
.\scripts\stop_service.ps1
Start-Sleep -Seconds 2
.\scripts\start_service.ps1

# 步骤4: 显示重要信息
Write-Host "`n🎯 给DeepSeek的话术:" -ForegroundColor Magenta
Write-Host "请继续开发OmniMarket项目。当前进度如上所示。" -ForegroundColor White
Write-Host "服务已启动，可以访问: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n💡 提示: 复制上面的进度信息给DeepSeek" -ForegroundColor Yellow
Write-Host "🔧 要停止服务，运行: .\scripts\stop_service.ps1" -ForegroundColor Gray
