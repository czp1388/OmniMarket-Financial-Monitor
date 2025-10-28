# 🔄 恢复开发 - PowerShell版本

Write-Host "恢复开发环境..." -ForegroundColor Green
cd E:\OmniMarket-Financial-Monitor

Write-Host "`n📋 当前进度：" -ForegroundColor Cyan
Get-Content "现在在做什么.txt"

Write-Host "`n🚀 启动服务..." -ForegroundColor Yellow
cd backend\app
Start-Process -FilePath "python" -ArgumentList "main_simple.py"

Write-Host "⏳ 等待10秒服务启动..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host "`n🧪 测试服务..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ 服务正常: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ 服务异常: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🌐 访问地址:" -ForegroundColor Magenta
Write-Host "文档: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "健康检查: http://localhost:8000/health" -ForegroundColor Blue

Write-Host "`n🎉 恢复完成！现在可以继续开发了。" -ForegroundColor Green
