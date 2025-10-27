# OmniMarket Financial Monitor - 最终启动脚本
Write-Host "🚀 启动 OmniMarket Financial Monitor..." -ForegroundColor Green

# 进入项目目录
Set-Location "E:\OmniMarket-Financial-Monitor\backend\app"

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python 版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 不可用" -ForegroundColor Red
    exit 1
}

# 停止现有服务
Write-Host "停止现有服务..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 选择启动版本
Write-Host "选择启动版本:" -ForegroundColor Cyan
Write-Host "1. 简化版本 (快速启动)" -ForegroundColor White
Write-Host "2. 完整版本 (包含所有功能)" -ForegroundColor White
Write-Host "3. 原始版本 (main_pro_fixed.py)" -ForegroundColor White

$choice = Read-Host "`n请输入选择 (1-3, 默认1)"

switch ($choice) {
    "2" { 
        $script = "main_complete.py" 
        Write-Host "启动完整版本..." -ForegroundColor Green 
    }
    "3" { 
        $script = "main_pro_fixed.py" 
        Write-Host "启动原始版本..." -ForegroundColor Yellow 
    }
    default { 
        $script = "main_simple.py" 
        Write-Host "启动简化版本..." -ForegroundColor Cyan 
    }
}

# 启动服务
Write-Host "`n启动服务: $script" -ForegroundColor Green
$process = Start-Process -FilePath "python" -ArgumentList $script -PassThru -WindowStyle Normal

Write-Host "⏳ 等待服务启动（10秒）..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# 检查服务状态
try {
    Write-Host "测试服务状态..." -ForegroundColor Cyan
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ 服务启动成功！" -ForegroundColor Green
    
    Write-Host "`n🌐 访问信息:" -ForegroundColor Yellow
    Write-Host "   API文档: http://localhost:8000/docs" -ForegroundColor Magenta
    Write-Host "   健康检查: http://localhost:8000/health" -ForegroundColor Magenta
    Write-Host "   服务首页: http://localhost:8000/" -ForegroundColor Magenta
    
    Write-Host "`n📊 服务状态:" -ForegroundColor White
    Write-Host "   版本: $($health.version)" -ForegroundColor Gray
    Write-Host "   状态: $($health.status)" -ForegroundColor Gray
    Write-Host "   数据库: $($health.database_initialized)" -ForegroundColor Gray
    
    Write-Host "`n💡 提示: 服务窗口保持打开状态，不要关闭" -ForegroundColor Cyan
    Write-Host "   按 Ctrl+C 可以停止服务" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请检查服务窗口中的错误信息" -ForegroundColor Yellow
    
    # 显示Python进程状态
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Write-Host "Python进程正在运行，但服务可能未正确绑定到端口" -ForegroundColor Yellow
        Write-Host "请检查服务窗口中的错误日志" -ForegroundColor Yellow
    }
}

Write-Host "`n脚本执行完成" -ForegroundColor Green
