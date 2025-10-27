# OmniMarket 可靠服务启动器
# 确保服务在各种情况下都能启动

Write-Host "🚀 启动 OmniMarket 服务 (可靠版)..." -ForegroundColor Green

# 1. 环境检查
Write-Host "1. 环境检查..." -ForegroundColor Yellow
if (!(Test-Path "E:\OmniMarket-Financial-Monitor")) {
    Write-Host "❌ 项目目录不存在" -ForegroundColor Red
    exit 1
}

Set-Location "E:\OmniMarket-Financial-Monitor\backend\app"

# 2. 彻底清理环境
Write-Host "2. 清理环境..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python3 -ErrorAction SilentlyContinue | Stop-Process -Force

# 清理端口占用
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portProcess) {
    $portProcess | ForEach-Object { 
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue 
    }
}

Start-Sleep -Seconds 3

# 3. 检查Python环境
Write-Host "3. 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python未安装或不在PATH中" -ForegroundColor Red
    exit 1
}

# 4. 检查依赖
Write-Host "4. 检查依赖..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn" 2>$null
    Write-Host "   ✅ 核心依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ 缺少依赖，正在安装..." -ForegroundColor Yellow
    pip install fastapi uvicorn
}

# 5. 启动服务（使用超级稳定版本）
Write-Host "5. 启动超级稳定版服务..." -ForegroundColor Green
$process = Start-Process -FilePath "python" -ArgumentList "main_super_stable.py" -PassThru -WindowStyle Normal

# 6. 等待服务启动
Write-Host "6. 等待服务启动（10秒）..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# 7. 测试服务
Write-Host "7. 测试服务连接..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ 服务启动成功!" -ForegroundColor Green
    Write-Host "   版本: $($health.version)" -ForegroundColor White
    Write-Host "   状态: $($health.status)" -ForegroundColor White
    
    Write-Host "`n🌐 服务已就绪:" -ForegroundColor Magenta
    Write-Host "   API文档: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "   健康检查: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host "`n📊 现在可以运行测试脚本验证所有API" -ForegroundColor White
    
} catch {
    Write-Host "❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 解决方案:" -ForegroundColor Yellow
    Write-Host "   1. 检查服务日志: 查看 backend\app\service.log" -ForegroundColor Gray
    Write-Host "   2. 手动启动调试: cd backend\app && python main_super_stable.py" -ForegroundColor Gray
    Write-Host "   3. 查看详细错误信息" -ForegroundColor Gray
}
