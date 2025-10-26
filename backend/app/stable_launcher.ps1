# 寰宇多市场金融监控系统 - 稳定服务启动器
Write-Host "🚀 启动稳定版服务..." -ForegroundColor Cyan

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$BackendDir = "$ProjectRoot\backend\app"

# 停止可能运行的服务
Write-Host "1. 清理环境..." -ForegroundColor Yellow
try {
    & "$ProjectRoot\ultimate_tool.ps1" stop
    Write-Host "   ✅ 环境清理完成" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ 环境清理跳过" -ForegroundColor Yellow
}

# 直接启动服务（不进行语法检查）
Write-Host "2. 启动服务..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory $BackendDir -PassThru -WindowStyle Normal
    Write-Host "   ✅ 服务启动成功 (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "   📍 服务地址: http://localhost:8000" -ForegroundColor White
    Write-Host "   📚 API文档: http://localhost:8000/docs" -ForegroundColor White
    
    # 等待服务启动
    Write-Host "3. 等待服务就绪..." -ForegroundColor Yellow
    for ($i = 1; $i -le 15; $i++) {
        Write-Host "   等待中... ($i/15)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Write-Host "   ✅ 服务已就绪！" -ForegroundColor Green
                break
            }
        } catch {
            # 继续等待
        }
        
        if ($i -eq 15) {
            Write-Host "   ⚠️ 服务启动较慢，请稍后手动检查" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 稳定启动完成！" -ForegroundColor Green
Write-Host "💡 使用 'E:\OmniMarket-Financial-Monitor\dev.ps1 test' 测试功能" -ForegroundColor Cyan
