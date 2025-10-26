Write-Host "🚀 寰宇多市场金融监控系统 - 新窗口启动" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "项目路径: E:\OmniMarket-Financial-Monitor" -ForegroundColor White
Write-Host "当前时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White

# 显示快速状态
Write-Host "`n📊 快速状态检查:" -ForegroundColor Green

# 检查服务
try {
    $null = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2
    Write-Host "   ✅ 后端服务: 运行中" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 后端服务: 未运行" -ForegroundColor Red
}

# 检查文件
if (Test-Path "backend\app\main.py") {
    Write-Host "   ✅ 项目文件: 正常" -ForegroundColor Green
} else {
    Write-Host "   ❌ 项目文件: 异常" -ForegroundColor Red
}

Write-Host "`n🔧 可用命令:" -ForegroundColor Cyan
Write-Host "   .\project_status.ps1 status    # 查看详细状态" -ForegroundColor White
Write-Host "   .\diagnostic_tool.ps1 all      # 完整系统检查" -ForegroundColor White

Write-Host "`n🎯 开发命令:" -ForegroundColor Magenta
Write-Host "   启动服务: cd backend\app; python main.py" -ForegroundColor White
Write-Host "   API文档: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n💡 提示: 使用上述命令诊断和修复问题" -ForegroundColor Yellow
