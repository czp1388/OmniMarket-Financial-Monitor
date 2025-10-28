# OmniMarket 服务验证脚本
Write-Host "🔍 验证 OmniMarket 服务状态..." -ForegroundColor Cyan

# 检查文件
Write-Host "1. 检查必要文件..." -ForegroundColor Yellow
$files = @(
    "backend\app\main_simple.py",
    "backend\app\main_super_stable.py", 
    "scripts\start_service.ps1",
    "scripts\stop_service.ps1",
    "scripts\test_api.ps1"
)

$allFilesExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host " ✅ $file" -ForegroundColor Green
    } else {
        Write-Host " ❌ $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

# 检查服务状态
Write-Host "`n2. 检查服务状态..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
    Write-Host " ✅ 服务运行中: $($health.status)" -ForegroundColor Green
    $serviceRunning = $true
} catch {
    Write-Host " 🔴 服务未运行" -ForegroundColor Red
    $serviceRunning = $false
}

# 总结
Write-Host "`n📊 验证结果:" -ForegroundColor Magenta
if ($allFilesExist -and $serviceRunning) {
    Write-Host "🎉 所有检查通过！标准开发模式已恢复！" -ForegroundColor Green
} elseif ($allFilesExist -and !$serviceRunning) {
    Write-Host "⚠️  文件完整，但服务未运行" -ForegroundColor Yellow
    Write-Host "💡 运行 .\scripts\start_service.ps1 启动服务" -ForegroundColor Gray
} else {
    Write-Host "❌ 文件不完整，需要修复" -ForegroundColor Red
}

Write-Host "`n🎯 您的标准开发流程:" -ForegroundColor White
Write-Host "cd E:\OmniMarket-Financial-Monitor" -ForegroundColor Gray
Write-Host ".\setup_dev_env.ps1" -ForegroundColor Gray  
Write-Host ".\scripts\start_service.ps1" -ForegroundColor Gray
Write-Host ".\scripts\test_api.ps1" -ForegroundColor Gray
