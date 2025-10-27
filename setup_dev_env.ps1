# OmniMarket 开发环境设置
# 每次新开PowerShell窗口时运行

Write-Host "🔧 设置 OmniMarket 开发环境..." -ForegroundColor Green

# 自动切换到项目目录
$projectPath = "E:\OmniMarket-Financial-Monitor"
if ((Get-Location).Path -ne $projectPath) {
    Set-Location $projectPath
    Write-Host "📁 切换到项目目录: $projectPath" -ForegroundColor Green
}

Write-Host "`n📊 项目状态检查:" -ForegroundColor Cyan

# 检查核心文件
Write-Host "核心文件:" -ForegroundColor Yellow
$coreFiles = @(
    "scripts\start_service.ps1",
    "scripts\stop_service.ps1", 
    "scripts\test_api.ps1",
    "backend\app\main_super_stable.py",
    "backend\app\main_simple.py"
)

foreach ($file in $coreFiles) {
    if (Test-Path $file) {
        Write-Host " ✅ $file" -ForegroundColor Green
    } else {
        Write-Host " ❌ $file" -ForegroundColor Red
    }
}

# 检查Python环境
Write-Host "`n🐍 Python环境:" -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host " ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host " ❌ Python未安装" -ForegroundColor Red
}

# 检查服务状态
Write-Host "`n🌐 服务状态:" -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host " ✅ 服务运行中 (PID: $($pythonProcesses.Id))" -ForegroundColor Green
} else {
    Write-Host " 🔴 服务未运行" -ForegroundColor Red
}

Write-Host "`n🎯 标准化开发命令:" -ForegroundColor Magenta
Write-Host " .\scripts\start_service.ps1 # 启动服务" -ForegroundColor White
Write-Host " .\scripts\stop_service.ps1 # 停止服务" -ForegroundColor White
Write-Host " .\scripts\test_api.ps1 # 测试API" -ForegroundColor White
Write-Host " git status # Git状态" -ForegroundColor White

Write-Host "`n💡 提示: 每次新开窗口先运行此脚本" -ForegroundColor Gray
Write-Host "🚀 环境设置完成！开始开发吧！" -ForegroundColor Green
