# OmniMarket 可靠API测试脚本
Write-Host "🧪 测试 OmniMarket API (可靠版)..." -ForegroundColor Green

# 确保在正确目录
$projectRoot = "E:\OmniMarket-Financial-Monitor"
if ((Get-Location).Path -ne $projectRoot) {
    Write-Host "切换到项目目录..." -ForegroundColor Yellow
    Set-Location $projectRoot
}

$baseUrl = "http://localhost:8000"
$endpoints = @(
    "/health",
    "/api/v1/system/info",
    "/api/v1/market/stock_cn/health", 
    "/api/v1/market/stock_cn/symbols",
    "/api/v1/market/stock_hk/health",
    "/api/v1/market/stock_hk/symbols"
)

Write-Host "测试 $($endpoints.Count) 个API端点..." -ForegroundColor Cyan

$successCount = 0
$totalCount = $endpoints.Count

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl$endpoint" -TimeoutSec 5
        Write-Host "✅ $endpoint - 成功" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "❌ $endpoint - 失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📊 测试结果: $successCount/$totalCount 个API端点正常" -ForegroundColor Cyan

if ($successCount -eq $totalCount) {
    Write-Host "🎉 所有API测试通过！服务运行正常！" -ForegroundColor Magenta
    Write-Host "🌐 您可以访问: http://localhost:8000/docs" -ForegroundColor Blue
} elseif ($successCount -gt 0) {
    Write-Host "⚠️  部分API测试失败 ($successCount/$totalCount)" -ForegroundColor Yellow
    Write-Host "💡 基础服务运行中，但部分功能需要完善" -ForegroundColor Gray
} else {
    Write-Host "❌ 所有API测试失败，服务未运行" -ForegroundColor Red
    Write-Host "💡 请先运行: .\scripts\start_service.ps1" -ForegroundColor Yellow
}
