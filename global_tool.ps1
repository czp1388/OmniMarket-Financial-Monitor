# 寰宇多市场金融监控系统 - 全局工具
param([string]$Command = "help")

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"

function Show-Help {
    Write-Host "🚀 寰宇多市场金融监控系统 - 全局工具" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "用法: .\global_tool.ps1 [命令]" -ForegroundColor White
    Write-Host ""
    Write-Host "可用命令:" -ForegroundColor Green
    Write-Host "  status     - 查看项目状态" -ForegroundColor White
    Write-Host "  diagnose   - 运行完整诊断" -ForegroundColor White
    Write-Host "  start      - 启动后端服务" -ForegroundColor White
    Write-Host "  stop       - 停止后端服务" -ForegroundColor White
    Write-Host "  docs       - 打开API文档" -ForegroundColor White
    Write-Host "  test       - 测试API功能" -ForegroundColor White
    Write-Host "  update     - 更新项目状态" -ForegroundColor White
    Write-Host "  help       - 显示此帮助" -ForegroundColor White
}

function Show-Status {
    Set-Location $ProjectRoot
    .\project_status.ps1 status
}

function Run-Diagnose {
    Set-Location $ProjectRoot
    .\diagnostic_tool.ps1 all
}

function Start-Service {
    Set-Location "$ProjectRoot\backend\app"
    Write-Host "🚀 启动后端服务..." -ForegroundColor Cyan
    python main.py
}

function Stop-Service {
    Write-Host "🛑 停止后端服务..." -ForegroundColor Yellow
    $process = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($process) {
        $process | Stop-Process -Force
        Write-Host "✅ 服务已停止" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  没有运行中的Python服务" -ForegroundColor Blue
    }
}

function Open-Docs {
    Start-Process "http://localhost:8000/docs"
}

function Test-API {
    Set-Location $ProjectRoot
    Write-Host "🔍 测试API功能..." -ForegroundColor Cyan
    
    $endpoints = @(
        @{Url="http://localhost:8000/health"; Name="健康检查"},
        @{Url="http://localhost:8000/"; Name="根路径"},
        @{Url="http://localhost:8000/api/v1/exchanges"; Name="交易所列表"},
        @{Url="http://localhost:8000/api/v1/prices/?symbol=BTC/USDT"; Name="BTC价格"}
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 5
            Write-Host "   ✅ $($endpoint.Name) - 正常" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ $($endpoint.Name) - 失败: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Update-Status {
    Set-Location $ProjectRoot
    .\project_status.ps1 update
}

# 执行命令
switch ($Command) {
    "status" { Show-Status }
    "diagnose" { Run-Diagnose }
    "start" { Start-Service }
    "stop" { Stop-Service }
    "docs" { Open-Docs }
    "test" { Test-API }
    "update" { Update-Status }
    "help" { Show-Help }
    default { Show-Help }
}
