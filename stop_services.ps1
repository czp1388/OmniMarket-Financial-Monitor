# OmniMarket 金融监控系统 - 停止所有服务
# 用法: .\stop_services.ps1

Write-Host "=== 停止 OmniMarket 服务 ===" -ForegroundColor Cyan

# 停止后端 (Python/Uvicorn)
Write-Host "`n停止后端服务..." -ForegroundColor Yellow
$backendProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*" }
if ($backendProcesses) {
    $backendProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "✓ 已停止进程: $($_.Id)" -ForegroundColor Green
    }
} else {
    Write-Host "未找到运行中的后端进程" -ForegroundColor Gray
}

# 停止前端 (Node/Vite)
Write-Host "`n停止前端服务..." -ForegroundColor Yellow
$frontendProcesses = Get-Process | Where-Object { $_.ProcessName -like "*node*" }
if ($frontendProcesses) {
    $frontendProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "✓ 已停止进程: $($_.Id)" -ForegroundColor Green
    }
} else {
    Write-Host "未找到运行中的前端进程" -ForegroundColor Gray
}

# 检查端口占用
Write-Host "`n检查端口状态..." -ForegroundColor Yellow
$ports = @(3000, 8000, 8774)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "警告: 端口 $port 仍被占用" -ForegroundColor Yellow
    } else {
        Write-Host "✓ 端口 $port 已释放" -ForegroundColor Green
    }
}

Write-Host "`n=== 所有服务已停止 ===" -ForegroundColor Cyan
