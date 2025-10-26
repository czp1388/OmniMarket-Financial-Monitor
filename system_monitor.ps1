# 寰宇多市场金融监控系统 - 系统监控
param([string]$Action = "status")

function Get-SystemStatus {
    Write-Host "🔍 系统状态监控" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Yellow
    
    # 检查服务状态
    $serviceRunning = $false
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3
        Write-Host "✅ 后端服务: 运行正常" -ForegroundColor Green
        $serviceRunning = $true
    } catch {
        Write-Host "❌ 后端服务: 未运行" -ForegroundColor Red
    }
    
    # 检查关键进程
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    Write-Host "📊 Python进程: $($pythonProcesses.Count) 个" -ForegroundColor $(if ($pythonProcesses.Count -gt 0) { "Green" } else { "Red" })
    
    # 检查磁盘空间
    $drive = Get-PSDrive -Name "E" -ErrorAction SilentlyContinue
    if ($drive) {
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        $totalGB = [math]::Round($drive.Used / 1GB + $drive.Free / 1GB, 2)
        Write-Host "💾 磁盘空间: $freeGB GB 可用 / $totalGB GB 总量" -ForegroundColor Green
    }
    
    # 检查网络连接
    try {
        $ping = Test-NetConnection -ComputerName "www.google.com" -Port 80 -InformationLevel Quiet
        Write-Host "🌐 网络连接: $(if ($ping) { '正常' } else { '异常' })" -ForegroundColor $(if ($ping) { "Green" } else { "Red" })
    } catch {
        Write-Host "🌐 网络连接: 检查失败" -ForegroundColor Yellow
    }
    
    # 显示项目信息
    Write-Host "`n📁 项目信息:" -ForegroundColor Cyan
    Write-Host "   路径: E:\OmniMarket-Financial-Monitor" -ForegroundColor White
    Write-Host "   服务: http://localhost:8000" -ForegroundColor White
    Write-Host "   文档: http://localhost:8000/docs" -ForegroundColor White
    
    if ($serviceRunning) {
        # 测试API功能
        Write-Host "`n🔧 API功能测试:" -ForegroundColor Cyan
        try {
            $exchanges = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/exchanges" -TimeoutSec 5
            Write-Host "   ✅ 交易所API: 正常 ($($exchanges.count) 个交易所)" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ 交易所API: 异常" -ForegroundColor Red
        }
    }
}

function Show-QuickActions {
    Write-Host "`n🚀 快速操作:" -ForegroundColor Magenta
    Write-Host "   1. 启动服务: .\global_tool.ps1 start" -ForegroundColor White
    Write-Host "   2. 停止服务: .\global_tool.ps1 stop" -ForegroundColor White
    Write-Host "   3. 诊断问题: .\global_tool.ps1 diagnose" -ForegroundColor White
    Write-Host "   4. 测试API: .\global_tool.ps1 test" -ForegroundColor White
    Write-Host "   5. 查看文档: .\global_tool.ps1 docs" -ForegroundColor White
}

# 执行动作
switch ($Action) {
    "status" { Get-SystemStatus; Show-QuickActions }
    "monitor" { 
        while ($true) {
            Clear-Host
            Get-SystemStatus
            Start-Sleep -Seconds 10
        }
    }
    default { Get-SystemStatus; Show-QuickActions }
}
