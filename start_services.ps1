# OmniMarket 金融监控系统 - 启动脚本
# 用法: .\start_services.ps1

Write-Host "=== OmniMarket 金融监控系统 ===" -ForegroundColor Cyan
Write-Host "正在启动前后端服务..." -ForegroundColor Yellow
Write-Host ""

# 检查虚拟环境
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "激活Python虚拟环境..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "警告: 未找到虚拟环境，使用全局Python环境" -ForegroundColor Yellow
}

# 启动后端
Write-Host "`n启动后端服务 (端口 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# 等待后端启动
Write-Host "等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# 启动前端
Write-Host "`n启动前端服务 (端口 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

# 等待前端启动
Write-Host "等待前端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 测试服务
Write-Host "`n=== 服务状态检查 ===" -ForegroundColor Cyan

# 测试后端
Write-Host "`n检查后端健康状态..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -UseBasicParsing
    $healthData = $health.Content | ConvertFrom-Json
    Write-Host "✓ 后端服务运行正常" -ForegroundColor Green
    Write-Host "  状态: $($healthData.status)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 后端服务检查失败，可能仍在启动中" -ForegroundColor Yellow
    Write-Host "  请手动访问: http://localhost:8000/docs" -ForegroundColor Gray
}

# 测试前端
Write-Host "`n检查前端服务..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✓ 前端服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "✗ 前端服务检查失败，可能仍在启动中" -ForegroundColor Yellow
    Write-Host "  请手动访问: http://localhost:3000" -ForegroundColor Gray
}

Write-Host "`n=== 服务已启动 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "前端地址: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "后端地址: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "API文档: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 两个服务在独立的PowerShell窗口中运行" -ForegroundColor Yellow
Write-Host "      关闭对应窗口即可停止服务" -ForegroundColor Yellow
