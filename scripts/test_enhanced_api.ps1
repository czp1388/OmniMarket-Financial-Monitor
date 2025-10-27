# 增强版A股数据API测试
Write-Host "🧪 测试增强版A股数据API..." -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"

$enhancedEndpoints = @(
    "/api/v1/market/stock_cn_enhanced/health",
    "/api/v1/market/stock_cn_enhanced/stocks",
    "/api/v1/market/stock_cn_enhanced/000001.SZ/realtime",
    "/api/v1/market/stock_cn_enhanced/000001.SZ/historical?days=5",
    "/api/v1/market/stock_cn_enhanced/industry/银行",
    "/api/v1/market/stock_cn_enhanced/search/平安",
    "/api/v1/market/stock_cn_enhanced/market/overview"
)

Write-Host "测试 $($enhancedEndpoints.Count) 个增强API端点..." -ForegroundColor Yellow

$successCount = 0
foreach ($endpoint in $enhancedEndpoints) {
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl$endpoint" -TimeoutSec 5
        Write-Host "✅ $endpoint - 成功" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "❌ $endpoint - 失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📊 增强版API测试结果: $successCount/$($enhancedEndpoints.Count) 通过" -ForegroundColor Cyan

if ($successCount -eq $enhancedEndpoints.Count) {
    Write-Host "🎉 增强版A股数据功能全部正常！" -ForegroundColor Magenta
    Write-Host "🌐 新增功能已可用，访问API文档查看详情: http://localhost:8000/docs" -ForegroundColor Blue
} else {
    Write-Host "⚠️  部分增强功能需要调试" -ForegroundColor Yellow
}
