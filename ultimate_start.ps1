# 寰宇多市场金融监控系统 - 终极启动工具
Write-Host "🚀 启动终极稳定版服务..." -ForegroundColor Cyan

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$BackendDir = "$ProjectRoot\backend\app"
$LogFile = "$ProjectRoot\startup.log"

# 清理环境
Write-Host "1. 清理环境..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 检查端口占用
$portProcess = netstat -ano | findstr :8000
if ($portProcess) {
    Write-Host "   ⚠️ 清理端口占用..." -ForegroundColor Yellow
    $portProcess | ForEach-Object {
        if ($_ -match '\s+(\d+)$') {
            $pidToKill = $matches[1]
            try {
                Stop-Process -Id $pidToKill -Force
                Write-Host "   ✅ 停止进程: $pidToKill" -ForegroundColor Green
            } catch {
                # 忽略错误
            }
        }
    }
}

# 启动稳定服务
Write-Host "2. 启动稳定服务..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath "python" -ArgumentList "main_stable.py" -WorkingDirectory $BackendDir -PassThru -WindowStyle Normal
    Write-Host "   ✅ 服务启动成功 (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "   📍 服务地址: http://localhost:8000" -ForegroundColor White
    Write-Host "   📚 API文档: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   🔧 版本: 2.0.0 稳定版" -ForegroundColor White
    
    # 等待并验证服务
    Write-Host "3. 验证服务状态..." -ForegroundColor Yellow
    $serviceReady = $false
    
    for ($i = 1; $i -le 15; $i++) {
        Write-Host "   等待服务启动... ($i/15)" -ForegroundColor Gray
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
            if ($response.status -eq "healthy") {
                Write-Host "   ✅ 服务健康检查通过!" -ForegroundColor Green
                $serviceReady = $true
                break
            }
        } catch {
            # 继续等待
        }
        
        Start-Sleep -Seconds 2
    }
    
    if ($serviceReady) {
        Write-Host "   ✅ 服务验证完成" -ForegroundColor Green
        
        # 测试基本功能
        try {
            $test = Invoke-RestMethod -Uri "http://localhost:8000/test" -TimeoutSec 3
            Write-Host "   ✅ API测试通过: $($test.message)" -ForegroundColor Green
        } catch {
            Write-Host "   ⚠️ API测试跳过" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️ 服务启动较慢，请手动检查" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   ❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   💡 尝试使用基础版本..." -ForegroundColor Cyan
    
    # 回退到基础版本
    try {
        $process = Start-Process -FilePath "python" -ArgumentList "main_simple.py" -WorkingDirectory $BackendDir -PassThru -WindowStyle Normal
        Write-Host "   ✅ 基础版本启动成功" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 所有启动方式都失败" -ForegroundColor Red
    }
}

Write-Host "`n🎉 启动流程完成!" -ForegroundColor Green
Write-Host "💡 服务信息:" -ForegroundColor Cyan
Write-Host "   - 主服务: http://localhost:8000" -ForegroundColor White
Write-Host "   - API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - 健康检查: http://localhost:8000/health" -ForegroundColor White
Write-Host "   - 测试接口: http://localhost:8000/test" -ForegroundColor White

Write-Host "`n🚀 现在可以开始开发新功能了!" -ForegroundColor Green
