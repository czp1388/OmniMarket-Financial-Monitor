# 测试财报 API 端点
# 使用方法: .\test_financial_report_api.ps1

Write-Host "🧪 财报 API 测试脚本" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# 配置
$baseUrl = "http://localhost:8000/api/v1"
$testSymbols = @("AAPL", "MSFT", "GOOGL", "INVALID_SYMBOL")

# 检查后端服务是否运行
Write-Host "📡 检查后端服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "✅ 后端服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ 后端服务未运行，请先启动后端服务:" -ForegroundColor Red
    Write-Host "   cd backend ; uvicorn main:app --reload" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# 测试 1: 获取财报数据
Write-Host "📊 测试 1: 获取财报数据" -ForegroundColor Cyan
Write-Host "-" * 60 -ForegroundColor Gray
foreach ($symbol in $testSymbols) {
    Write-Host "查询股票: $symbol" -ForegroundColor White
    try {
        $url = "$baseUrl/financial-reports/?symbol=$symbol"
        $response = Invoke-RestMethod -Uri $url -Method GET -ErrorAction Stop
        
        if ($response.symbol) {
            Write-Host "  ✅ 成功获取 $($response.symbol) 财报数据" -ForegroundColor Green
            Write-Host "     公司: $($response.companyName)" -ForegroundColor Gray
            Write-Host "     季度: $($response.quarter)" -ForegroundColor Gray
            Write-Host "     营收: `$$($response.revenue)B" -ForegroundColor Gray
            Write-Host "     净利润: `$$($response.netIncome)B" -ForegroundColor Gray
            Write-Host "     EPS: `$$($response.eps)" -ForegroundColor Gray
        } else {
            Write-Host "  ⚠️  未返回数据（可能是 API 限流或无效代码）" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ 请求失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 测试 2: 获取历史数据
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""
Write-Host "📈 测试 2: 获取历史数据" -ForegroundColor Cyan
Write-Host "-" * 60 -ForegroundColor Gray
$historySymbol = "AAPL"
try {
    $url = "$baseUrl/financial-reports/historical?symbol=$historySymbol&periods=4"
    $response = Invoke-RestMethod -Uri $url -Method GET -ErrorAction Stop
    
    Write-Host "  ✅ 成功获取 $historySymbol 历史数据（$($response.Count) 个季度）" -ForegroundColor Green
    foreach ($quarter in $response) {
        Write-Host "    📅 $($quarter.quarter)" -ForegroundColor Gray
        Write-Host "       营收: `$$($quarter.revenue)B | 净利润: `$$($quarter.netIncome)B | EPS: `$$($quarter.eps)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ❌ 请求失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# 测试 3: 搜索股票代码
Write-Host "🔍 测试 3: 搜索股票代码" -ForegroundColor Cyan
Write-Host "-" * 60 -ForegroundColor Gray
$searchKeywords = @("apple", "microsoft", "tech")
foreach ($keyword in $searchKeywords) {
    Write-Host "搜索关键词: $keyword" -ForegroundColor White
    try {
        $url = "$baseUrl/financial-reports/search?keyword=$keyword"
        $response = Invoke-RestMethod -Uri $url -Method GET -ErrorAction Stop
        
        if ($response.Count -gt 0) {
            Write-Host "  ✅ 找到 $($response.Count) 个匹配结果" -ForegroundColor Green
            foreach ($stock in $response | Select-Object -First 3) {
                Write-Host "    📌 $($stock.symbol) - $($stock.name)" -ForegroundColor Gray
            }
        } else {
            Write-Host "  ⚠️  无匹配结果" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ 请求失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 测试总结
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""
Write-Host "✅ API 测试完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📝 提示:" -ForegroundColor Yellow
Write-Host "  - 首次请求可能较慢（需要从 Alpha Vantage 获取数据）" -ForegroundColor White
Write-Host "  - 后续请求会使用缓存（1小时有效期）" -ForegroundColor White
Write-Host "  - 如果 API 请求失败，系统会自动降级到模拟数据" -ForegroundColor White
Write-Host "  - 配置 ALPHA_VANTAGE_API_KEY 环境变量以使用真实 API" -ForegroundColor White
Write-Host ""
Write-Host "🔧 环境变量配置:" -ForegroundColor Cyan
Write-Host '  $env:ALPHA_VANTAGE_API_KEY="your_api_key_here"' -ForegroundColor White
Write-Host ""
