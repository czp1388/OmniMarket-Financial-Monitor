# 寰宇多市场金融监控系统 - 全局终极工具
param([string]$Command = "help")

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$UltimateTool = "$ProjectRoot\ultimate_tool.ps1"

function Show-Help {
    Write-Host "🎯 寰宇多市场金融监控系统 - 全局工具" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Yellow
    Write-Host "使用方法: E:\OmniMarket-Financial-Monitor\omnimarket.ps1 [命令]" -ForegroundColor White
    Write-Host ""
    Write-Host "可用命令:" -ForegroundColor Green
    Write-Host "  start    - 启动服务" -ForegroundColor White
    Write-Host "  stop     - 停止服务" -ForegroundColor White
    Write-Host "  test     - 测试API" -ForegroundColor White
    Write-Host "  status   - 服务状态" -ForegroundColor White
    Write-Host "  restart  - 重启服务" -ForegroundColor White
    Write-Host "  docs     - 打开API文档" -ForegroundColor White
    Write-Host "  help     - 显示帮助" -ForegroundColor White
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Gray
    Write-Host "  E:\OmniMarket-Financial-Monitor\omnimarket.ps1 start" -ForegroundColor Gray
    Write-Host "  E:\OmniMarket-Financial-Monitor\omnimarket.ps1 test" -ForegroundColor Gray
}

function Open-Docs {
    Write-Host "📚 打开API文档..." -ForegroundColor Cyan
    Start-Process "http://localhost:8000/docs"
}

# 执行命令
switch ($Command.ToLower()) {
    "start" { & $UltimateTool start }
    "stop" { & $UltimateTool stop }
    "test" { & $UltimateTool test }
    "status" { & $UltimateTool status }
    "restart" { & $UltimateTool restart }
    "docs" { Open-Docs }
    "help" { Show-Help }
    default { 
        Write-Host "❌ 未知命令: $Command" -ForegroundColor Red
        Show-Help
    }
}
