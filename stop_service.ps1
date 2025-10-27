# OmniMarket Financial Monitor 服务停止脚本
Write-Host "🛑 停止 OmniMarket Financial Monitor..." -ForegroundColor Yellow

# 停止Python进程
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "✅ 已停止所有Python进程" -ForegroundColor Green
} else {
    Write-Host "ℹ️ 没有找到运行的Python进程" -ForegroundColor Blue
}

# 检查端口释放
try {
    Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
    Write-Host "⚠️ 端口8000仍在占用，等待释放..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
} catch {
    Write-Host "✅ 端口8000已释放" -ForegroundColor Green
}
