# OmniMarket Financial Monitor 服务启动脚本
Write-Host "🚀 启动 OmniMarket Financial Monitor..." -ForegroundColor Green

cd E:\OmniMarket-Financial-Monitor\backend\app

# 检查Python是否可用
try {
    python --version > $null 2>&1
    Write-Host "✅ Python 可用" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 不可用，请检查Python安装" -ForegroundColor Red
    exit 1
}

# 停止现有服务
Write-Host "停止现有服务..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force
Start-Sleep -Seconds 2

# 启动服务
Write-Host "启动服务..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "main_pro_fixed.py" -WindowStyle Normal

Write-Host "⏳ 等待服务启动..." -ForegroundColor Cyan
Start-Sleep -Seconds 8

# 检查服务状态
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ 服务启动成功！" -ForegroundColor Green
    Write-Host "`n🌐 访问信息:" -ForegroundColor Yellow
    Write-Host "   API文档: http://localhost:8000/docs" -ForegroundColor Magenta
    Write-Host "   健康检查: http://localhost:8000/health" -ForegroundColor Magenta
    Write-Host "   服务状态: $($health.status)" -ForegroundColor White
    Write-Host "   版本: $($health.version)" -ForegroundColor White
} catch {
    Write-Host "❌ 服务启动失败，请检查日志" -ForegroundColor Red
}
