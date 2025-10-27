# OmniMarket 服务停止脚本
Write-Host "🛑 停止 OmniMarket 服务..." -ForegroundColor Yellow

$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "✅ 已停止 $($pythonProcesses.Count) 个Python进程" -ForegroundColor Green
} else {
    Write-Host "ℹ️ 没有运行中的Python进程" -ForegroundColor Blue
}

# 清理端口占用
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portProcess) {
    $portProcess | ForEach-Object {
        try {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        } catch {
            # 忽略错误
        }
    }
    Write-Host "✅ 清理端口8000占用" -ForegroundColor Green
}

Write-Host "服务已停止" -ForegroundColor Green
