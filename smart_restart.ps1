# 寰宇多市场金融监控系统 - 智能重启工具
Write-Host "🔄 智能重启系统..." -ForegroundColor Cyan

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$BackendDir = "$ProjectRoot\backend\app"

function Test-Service {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3
        return $true
    } catch {
        return $false
    }
}

# 1. 检查当前服务状态
Write-Host "1. 检查当前服务状态..." -ForegroundColor Yellow
if (Test-Service) {
    Write-Host "   ✅ 服务正在运行" -ForegroundColor Green
    $restart = Read-Host "   是否重启服务? (y/n, 默认n)"
    if ($restart -ne 'y') {
        Write-Host "   ℹ️ 保持服务运行" -ForegroundColor Gray
        exit
    }
} else {
    Write-Host "   ❌ 服务未运行" -ForegroundColor Red
}

# 2. 清理环境
Write-Host "2. 清理环境..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "   ✅ 已停止 $($pythonProcesses.Count) 个Python进程" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

# 3. 检查端口占用
Write-Host "3. 检查端口占用..." -ForegroundColor Yellow
$portProcess = netstat -ano | findstr :8000
if ($portProcess) {
    Write-Host "   ⚠️ 端口8000仍被占用，尝试清理..." -ForegroundColor Yellow
    $portProcess | ForEach-Object {
        if ($_ -match '\s+(\d+)$') {
            $pidToKill = $matches[1]
            try {
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                Write-Host "   ✅ 停止进程: $pidToKill" -ForegroundColor Green
            } catch {
                # 忽略错误
            }
        }
    }
    Start-Sleep -Seconds 2
}

# 4. 启动服务
Write-Host "4. 启动服务..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath "python" -ArgumentList "stable_runner.py" -WorkingDirectory $BackendDir -PassThru -WindowStyle Normal
    Write-Host "   ✅ 服务启动成功 (PID: $($process.Id))" -ForegroundColor Green
    
    # 5. 等待服务就绪
    Write-Host "5. 等待服务就绪..." -ForegroundColor Yellow
    $serviceReady = $false
    for ($i = 1; $i -le 20; $i++) {
        Write-Host "   等待服务启动... ($i/20)" -ForegroundColor Gray
        if (Test-Service) {
            Write-Host "   ✅ 服务健康检查通过!" -ForegroundColor Green
            $serviceReady = $true
            break
        }
        Start-Sleep -Seconds 3
    }
    
    if ($serviceReady) {
        Write-Host "   ✅ 服务验证完成" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ 服务启动较慢，请稍后手动检查" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   ❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 重启流程完成!" -ForegroundColor Green
Write-Host "💡 服务信息:" -ForegroundColor Cyan
Write-Host "   - 主服务: http://localhost:8000" -ForegroundColor White
Write-Host "   - API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Web界面: http://localhost:8000/" -ForegroundColor White

if (Test-Service) {
    Write-Host "`n✅ 系统现在正常运行!" -ForegroundColor Green
} else {
    Write-Host "`n❌ 系统可能未正确启动，请检查日志" -ForegroundColor Red
}
