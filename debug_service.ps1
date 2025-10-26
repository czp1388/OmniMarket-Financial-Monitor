# 寰宇多市场金融监控系统 - 调试启动工具
Write-Host "🔧 调试模式启动服务..." -ForegroundColor Cyan

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$LogFile = "$ProjectRoot\service_debug.log"

Write-Host "📝 日志文件: $LogFile" -ForegroundColor Yellow

# 启动服务并捕获输出
try {
    Write-Host "🚀 启动后端服务（调试模式）..." -ForegroundColor Green
    $process = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "$ProjectRoot\backend\app" -PassThru -NoNewWindow -Wait
    
    if ($process.ExitCode -ne 0) {
        Write-Host "❌ 服务异常退出，退出代码: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "💡 请查看上面的错误信息进行修复" -ForegroundColor Yellow
    } else {
        Write-Host "✅ 服务正常退出" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🔍 调试信息:" -ForegroundColor Cyan
Write-Host "   服务目录: $ProjectRoot\backend\app" -ForegroundColor White
Write-Host "   主文件: main.py" -ForegroundColor White
Write-Host "   当前时间: $(Get-Date)" -ForegroundColor White
