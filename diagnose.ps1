# OmniMarket 服务诊断脚本
Write-Host "🔍 OmniMarket 服务诊断..." -ForegroundColor Green

cd E:\OmniMarket-Financial-Monitor\backend\app

# 1. 检查Python环境
Write-Host "`n1. 检查Python环境..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python不可用" -ForegroundColor Red
    exit 1
}

# 2. 检查依赖
Write-Host "`n2. 检查依赖..." -ForegroundColor Cyan
$dependencies = @("fastapi", "uvicorn", "sqlalchemy", "aiohttp", "pandas", "numpy", "talib")
foreach ($dep in $dependencies) {
    try {
        python -c "import $dep" 2>$null
        Write-Host "   ✅ $dep" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ $dep" -ForegroundColor Red
    }
}

# 3. 检查服务状态
Write-Host "`n3. 检查服务状态..." -ForegroundColor Cyan
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "   ✅ Python进程运行中: $($pythonProcesses.Count) 个" -ForegroundColor Green
} else {
    Write-Host "   ❌ 没有Python进程运行" -ForegroundColor Red
}

# 4. 检查端口占用
Write-Host "`n4. 检查端口8000..." -ForegroundColor Cyan
try {
    $connection = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
    if ($connection) {
        Write-Host "   ✅ 端口8000已被占用" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 端口8000未被占用" -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠️ 无法检查端口状态" -ForegroundColor Yellow
}

# 5. 检查文件结构
Write-Host "`n5. 检查关键文件..." -ForegroundColor Cyan
$criticalFiles = @(
    "main_simple.py",
    "main_enhanced.py", 
    "main_complete.py",
    "services\market_data_service.py",
    "services\alert_engine.py",
    "routers\alert_management.py",
    "models\alert_models.py"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file" -ForegroundColor Red
    }
}

Write-Host "`n🎯 诊断完成" -ForegroundColor Green
Write-Host "如果发现问题，请根据上述检查结果进行修复" -ForegroundColor Yellow
