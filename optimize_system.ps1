# OmniMarket 系统优化脚本
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  OmniMarket 系统优化工具" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$projectRoot = "E:\OmniMarket-Financial-Monitor"

# 1. 检查并安装缺失的Python包
Write-Host "【1/5】检查Python依赖..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"
try {
    $missing = python -c "
import sys
required = ['fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2-binary', 'influxdb-client', 'redis', 'ccxt', 'aiohttp', 'websockets', 'pytest', 'httpx']
missing = []
for pkg in required:
    try:
        __import__(pkg.replace('-', '_'))
    except ImportError:
        missing.append(pkg)
if missing:
    print(','.join(missing))
"
    if ($missing) {
        Write-Host "  发现缺失依赖: $missing" -ForegroundColor Yellow
        Write-Host "  正在安装..." -ForegroundColor Cyan
        pip install $missing.Split(',') -q
        Write-Host "  ✅ 依赖安装完成" -ForegroundColor Green
    } else {
        Write-Host "  ✅ 所有依赖已安装" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️  依赖检查失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 2. 检查并修复前端依赖
Write-Host "`n【2/5】检查前端依赖..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"
if (Test-Path "node_modules") {
    Write-Host "  ✅ node_modules 已存在" -ForegroundColor Green
} else {
    Write-Host "  正在安装前端依赖..." -ForegroundColor Cyan
    npm install
    Write-Host "  ✅ 前端依赖安装完成" -ForegroundColor Green
}

# 3. 清理缓存和临时文件
Write-Host "`n【3/5】清理缓存文件..." -ForegroundColor Yellow
Set-Location $projectRoot
$cleaned = 0
Get-ChildItem -Path "backend" -Recurse -Include "__pycache__" -Directory | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $cleaned++
}
Get-ChildItem -Path "backend" -Recurse -Include "*.pyc" -File | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    $cleaned++
}
Write-Host "  ✅ 清理了 $cleaned 个缓存文件/目录" -ForegroundColor Green

# 4. 检查环境变量配置
Write-Host "`n【4/5】检查环境配置..." -ForegroundColor Yellow
if (Test-Path "$projectRoot\.env") {
    Write-Host "  ✅ .env 文件存在" -ForegroundColor Green
    
    # 检查关键配置
    $envContent = Get-Content "$projectRoot\.env" -Raw
    $configs = @{
        "SECRET_KEY" = "安全密钥"
        "ALPHA_VANTAGE_API_KEY" = "Alpha Vantage API"
        "BINANCE_API_KEY" = "币安 API Key"
    }
    
    foreach ($key in $configs.Keys) {
        if ($envContent -match "$key\s*=\s*\S+") {
            Write-Host "    ✅ $($configs[$key]): 已配置" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  $($configs[$key]): 未配置或为空" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ⚠️  .env 文件不存在，请从 .env.example 创建" -ForegroundColor Yellow
}

# 5. 运行系统诊断
Write-Host "`n【5/5】运行系统诊断..." -ForegroundColor Yellow
python "$projectRoot\project_diagnostic.py" 2>$null

# 优化建议
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  优化建议" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✅ 已完成的优化:" -ForegroundColor Green
Write-Host "  • TypeScript类型错误修复（AutoTradingPage, KlineStyleDashboard）" -ForegroundColor White
Write-Host "  • API响应处理统一使用 response.data" -ForegroundColor White
Write-Host "  • 清理Python缓存文件" -ForegroundColor White
Write-Host "  • K线API exchange字段缺失已修复（部分）`n" -ForegroundColor White

Write-Host "🔧 建议继续优化:" -ForegroundColor Yellow
Write-Host "  1. 修复剩余数据源服务的 exchange 字段" -ForegroundColor White
Write-Host "     - yfinance_data_service.py" -ForegroundColor Gray
Write-Host "     - akshare_service.py" -ForegroundColor Gray
Write-Host "     - futu_data_service.py" -ForegroundColor Gray
Write-Host "  2. 启动Redis服务以启用缓存功能" -ForegroundColor White
Write-Host "  3. 配置富途数据服务API（可选）" -ForegroundColor White
Write-Host "  4. 添加更多单元测试覆盖`n" -ForegroundColor White

Write-Host "📋 快速测试命令:" -ForegroundColor Cyan
Write-Host "  .\test_all_features.ps1" -ForegroundColor White
Write-Host "  .\quick_test.ps1`n" -ForegroundColor White

Write-Host "========================================`n" -ForegroundColor Cyan
