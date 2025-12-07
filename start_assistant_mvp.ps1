# OmniMarket 助手模式启动脚本
# 用于快速启动前后端服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OmniMarket \u667a\u80fd\u6295\u8d44\u52a9\u624b" -ForegroundColor Cyan
Write-Host "  \u52a9\u624b\u6a21\u5f0f MVP - \u5feb\u901f\u542f\u52a8" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# \u68c0\u67e5\u5e76\u6e05\u7406\u65e7\u8fdb\u7a0b
Write-Host "[1/4] \u6e05\u7406\u65e7\u8fdb\u7a0b..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "node"} | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "\u2713 \u6e05\u7406\u5b8c\u6210`n" -ForegroundColor Green

# \u542f\u52a8\u540e\u7aef\u670d\u52a1
Write-Host "[2/4] \u542f\u52a8\u540e\u7aef API \u670d\u52a1..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '\u540e\u7aef API \u670d\u52a1 (FastAPI)' -ForegroundColor Green; Write-Host '==================' -ForegroundColor Green; Write-Host 'API \u6587\u6863: http://localhost:8000/docs`n' -ForegroundColor Cyan; uvicorn main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal
Start-Sleep -Seconds 3
Write-Host "\u2713 \u540e\u7aef\u670d\u52a1\u542f\u52a8\u4e2d...`n" -ForegroundColor Green

# \u542f\u52a8\u524d\u7aef\u670d\u52a1
Write-Host "[3/4] \u542f\u52a8\u524d\u7aef\u5f00\u53d1\u670d\u52a1\u5668..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\frontend"
    npm run dev
}
Write-Host "\u2713 \u524d\u7aef\u670d\u52a1\u542f\u52a8\u4e2d... (Job ID: $($frontendJob.Id))`n" -ForegroundColor Green

# \u7b49\u5f85\u670d\u52a1\u5c31\u7eea
Write-Host "[4/4] \u7b49\u5f85\u670d\u52a1\u5c31\u7eea..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# \u68c0\u67e5\u670d\u52a1\u72b6\u6001
Write-Host "`n\u68c0\u67e5\u670d\u52a1\u72b6\u6001\uff1a" -ForegroundColor Cyan
$backendPort = netstat -ano | findstr ":8000 "
$frontendPort = $null
$checkPorts = @(5173, 3000, 3001, 3002, 3003)
foreach ($port in $checkPorts) {
    $conn = netstat -ano | findstr ":$port "
    if ($conn) {
        $frontendPort = $port
        break
    }
}

if ($backendPort) {
    Write-Host "\u2713 \u540e\u7aef API: http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "\u2717 \u540e\u7aef\u670d\u52a1\u672a\u542f\u52a8" -ForegroundColor Red
}

if ($frontendPort) {
    Write-Host "\u2713 \u524d\u7aef\u670d\u52a1: http://localhost:$frontendPort`n" -ForegroundColor Green
} else {
    Write-Host "\u2717 \u524d\u7aef\u670d\u52a1\u672a\u542f\u52a8`n" -ForegroundColor Red
    Write-Host "\u8bf7\u68c0\u67e5\u540e\u7aef PowerShell \u7a97\u53e3\u4e2d\u7684\u9519\u8bef\u4fe1\u606f`n" -ForegroundColor Yellow
    exit
}

# \u6253\u5f00\u6d4f\u89c8\u5668
Write-Host "\u6b63\u5728\u6253\u5f00\u6d4f\u89c8\u5668..." -ForegroundColor Cyan
Start-Process "http://localhost:$frontendPort/assistant"

# \u663e\u793a\u8bbf\u95ee\u4fe1\u606f
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  \u670d\u52a1\u5df2\u542f\u52a8\u6210\u529f\uff01" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "\ud83d\udcf1 \u52a9\u624b\u6a21\u5f0f\uff08\u96f6\u57fa\u7840\u7528\u6237\uff09\uff1a" -ForegroundColor White
Write-Host "   http://localhost:$frontendPort/assistant`n" -ForegroundColor Cyan

Write-Host "\ud83d\udd27 \u4e13\u5bb6\u6a21\u5f0f\uff08\u4e13\u4e1a\u4ea4\u6613\uff09\uff1a" -ForegroundColor White
Write-Host "   http://localhost:$frontendPort/expert`n" -ForegroundColor Cyan

Write-Host "\ud83d\udce1 \u540e\u7aef API \u6587\u6863\uff1a" -ForegroundColor White
Write-Host "   http://localhost:8000/docs`n" -ForegroundColor Cyan

Write-Host "\ud83d\udca1 \u5f00\u59cb\u6d4b\u8bd5 MVP\uff1a" -ForegroundColor Yellow
Write-Host "   1. \u70b9\u51fb\u201c\u6d4f\u89c8\u7b56\u7565\u5305\u201d\u6309\u94ae" -ForegroundColor Gray
Write-Host "   2. \u5b8c\u62103\u6b65\u6fc0\u6d3b\u6d41\u7a0b" -ForegroundColor Gray
Write-Host "   3. \u67e5\u770b\u8fd0\u884c\u72b6\u6001\u548c\u8fdb\u5ea6\u62a5\u544a`n" -ForegroundColor Gray

Write-Host "\u2139\ufe0f  \u670d\u52a1\u7ba1\u7406\u547d\u4ee4\uff1a" -ForegroundColor Yellow
Write-Host "   \u67e5\u770b\u524d\u7aef\u65e5\u5fd7: Get-Job | Receive-Job" -ForegroundColor Gray
Write-Host "   \u505c\u6b62\u670d\u52a1: Get-Job | Stop-Job; Get-Job | Remove-Job`n" -ForegroundColor Gray

Write-Host "========================================`n" -ForegroundColor Cyan
