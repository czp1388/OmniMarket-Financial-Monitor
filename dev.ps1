# 寰宇多市场金融监控系统 - 开发工具
param([string]$Command = "help")

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"

function Start-Development {
    Write-Host "🚀 启动开发模式..." -ForegroundColor Cyan
    & "$ProjectRoot\omnimarket.ps1" start
    Write-Host "📊 开发服务器已启动: http://localhost:8000" -ForegroundColor Green
    Write-Host "📚 API文档: http://localhost:8000/docs" -ForegroundColor Green
}

function Test-All {
    Write-Host "🔍 运行完整测试套件..." -ForegroundColor Cyan
    & "$ProjectRoot\omnimarket.ps1" test
}

function Show-Status {
    & "$ProjectRoot\omnimarket.ps1" status
}

function Backup-Code {
    Write-Host "💾 备份代码到Git..." -ForegroundColor Cyan
    cd $ProjectRoot
    git add .
    git commit -m "开发进度备份 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git push origin main
    Write-Host "✅ 代码备份完成" -ForegroundColor Green
}

function Open-Project {
    Write-Host "📁 打开项目目录..." -ForegroundColor Cyan
    explorer $ProjectRoot
}

function Show-DevHelp {
    Write-Host "🎯 开发工具命令" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Yellow
    Write-Host "dev start    - 启动开发服务器" -ForegroundColor White
    Write-Host "dev test     - 运行完整测试" -ForegroundColor White
    Write-Host "dev status   - 查看服务状态" -ForegroundColor White
    Write-Host "dev backup   - 备份代码到Git" -ForegroundColor White
    Write-Host "dev open     - 打开项目目录" -ForegroundColor White
    Write-Host "dev help     - 显示帮助" -ForegroundColor White
}

# 执行命令
switch ($Command.ToLower()) {
    "start" { Start-Development }
    "test" { Test-All }
    "status" { Show-Status }
    "backup" { Backup-Code }
    "open" { Open-Project }
    "help" { Show-DevHelp }
    default { 
        Write-Host "使用: dev.ps1 [命令]" -ForegroundColor Yellow
        Show-DevHelp
    }
}
