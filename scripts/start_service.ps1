# OmniMarket 修复版启动脚本
Write-Host "🚀 启动 OmniMarket 服务 (修复版)..." -ForegroundColor Green

# 强制切换到正确目录
$correctPath = "E:\OmniMarket-Financial-Monitor"
if ((Get-Location).Path -ne $correctPath) {
    Write-Host "切换到项目目录: $correctPath" -ForegroundColor Yellow
    Set-Location $correctPath
}

# 1. 彻底清理环境
Write-Host "1. 彻底清理环境..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 2. 检查必要文件
Write-Host "2. 检查必要文件..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend\app\main_simple.py",
    "backend\app\main_super_stable.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host " ✅ $file" -ForegroundColor Green
    } else {
        Write-Host " ❌ $file 不存在" -ForegroundColor Red
        Write-Host "正在创建缺失文件..." -ForegroundColor Yellow
        # 这里可以添加创建缺失文件的代码
    }
}

# 3. 启动服务（使用简化版本，确保可靠）
Write-Host "3. 启动服务..." -ForegroundColor Green
cd backend\app
Write-Host "使用简化版本启动..." -ForegroundColor Cyan
$process = Start-Process -FilePath "python" -ArgumentList "main_simple.py" -PassThru

# 保存进程ID
$process.Id | Out-File "..\..\logs\backend_pid.txt" -Encoding utf8

# 4. 等待并测试
Write-Host "4. 等待服务启动（12秒）..." -ForegroundColor Cyan
Start-Sleep -Seconds 12

Write-Host "5. 测试服务连接..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 8
    Write-Host "✅ 服务启动成功!" -ForegroundColor Green
    Write-Host " 状态: $($health.status)" -ForegroundColor White
    Write-Host " 服务: $($health.service)" -ForegroundColor White
    
    Write-Host "`n🎉 服务运行正常!" -ForegroundColor Magenta
    Write-Host "🌐 访问地址:" -ForegroundColor Cyan
    Write-Host " API文档: http://localhost:8000/docs" -ForegroundColor Blue
    Write-Host " 健康检查: http://localhost:8000/health" -ForegroundColor Blue
    Write-Host " 系统信息: http://localhost:8000/api/v1/system/info" -ForegroundColor Blue
    
    Write-Host "`n💡 服务PID: $($process.Id)" -ForegroundColor Gray
    Write-Host "要停止服务，请运行: .\scripts\stop_service.ps1" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "尝试手动启动..." -ForegroundColor Yellow
    Write-Host "请运行: cd backend\app && python main_simple.py" -ForegroundColor White
}

# 回到项目根目录
Set-Location "E:\OmniMarket-Financial-Monitor"
