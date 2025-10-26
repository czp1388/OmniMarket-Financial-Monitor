# 寰宇多市场金融监控系统 - 深度诊断工具
Write-Host "🔧 深度诊断系统问题..." -ForegroundColor Cyan

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$BackendDir = "$ProjectRoot\backend\app"

Write-Host "1. 检查系统环境..." -ForegroundColor Yellow

# 检查Python
try {
    $pythonVersion = python --version
    Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python未安装或不在PATH中" -ForegroundColor Red
}

# 检查必要模块
Write-Host "2. 检查Python依赖..." -ForegroundColor Yellow
try {
    python -c "import fastapi; print('   ✅ FastAPI')"
    python -c "import uvicorn; print('   ✅ Uvicorn')" 
    python -c "import ccxt; print('   ✅ CCXT')"
    Write-Host "   ✅ 所有依赖正常" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 依赖缺失: $($_.Exception.Message)" -ForegroundColor Red
}

# 检查项目文件
Write-Host "3. 检查项目文件..." -ForegroundColor Yellow
$requiredFiles = @(
    "main.py",
    "routers/market.py",
    "routers/alerts.py", 
    "services/data_service.py",
    "services/alert_service.py",
    "services/__init__.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path "$BackendDir\$file") {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file 缺失" -ForegroundColor Red
    }
}

# 检查语法
Write-Host "4. 检查Python语法..." -ForegroundColor Yellow
cd $BackendDir
try {
    python -c "exec(open('main.py', encoding='utf-8').read())"
    Write-Host "   ✅ main.py 可执行" -ForegroundColor Green
} catch {
    Write-Host "   ❌ main.py 执行错误: $($_.Exception.Message)" -ForegroundColor Red
}

# 检查端口占用
Write-Host "5. 检查端口占用..." -ForegroundColor Yellow
$portProcess = netstat -ano | findstr :8000
if ($portProcess) {
    Write-Host "   ⚠️ 端口8000被占用:" -ForegroundColor Yellow
    $portProcess | ForEach-Object { Write-Host "      $_" -ForegroundColor White }
} else {
    Write-Host "   ✅ 端口8000可用" -ForegroundColor Green
}

Write-Host "`n🎯 诊断完成" -ForegroundColor Cyan
