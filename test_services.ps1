# 测试前后端服务状态
Write-Host "=== OmniMarket 服务状态检查 ===" -ForegroundColor Cyan

# 测试前端
Write-Host "`n检查前端服务 (http://localhost:3000)..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ 前端服务运行正常 (状态码: $($frontend.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "✗ 前端服务未运行" -ForegroundColor Red
}

# 测试后端健康检查
Write-Host "`n检查后端健康接口 (http://localhost:8000/health)..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    $healthData = $health.Content | ConvertFrom-Json
    Write-Host "✓ 后端健康检查通过" -ForegroundColor Green
    Write-Host "  状态: $($healthData.status)" -ForegroundColor Gray
    Write-Host "  时间戳: $($healthData.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 后端健康检查失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试后端根路径
Write-Host "`n检查后端根路径 (http://localhost:8000)..." -ForegroundColor Yellow
try {
    $root = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5 -UseBasicParsing
    $rootData = $root.Content | ConvertFrom-Json
    Write-Host "✓ 后端根路径访问成功" -ForegroundColor Green
    Write-Host "  消息: $($rootData.message)" -ForegroundColor Gray
    Write-Host "  版本: $($rootData.version)" -ForegroundColor Gray
    Write-Host "  状态: $($rootData.status)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 后端根路径访问失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试API文档
Write-Host "`n检查API文档 (http://localhost:8000/docs)..." -ForegroundColor Yellow
try {
    $docs = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ API文档可访问 (状态码: $($docs.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "✗ API文档不可访问" -ForegroundColor Red
}

Write-Host "`n=== 检查完成 ===" -ForegroundColor Cyan
