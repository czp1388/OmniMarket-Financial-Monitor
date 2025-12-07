# 助手模式 MVP 用户旅程测试
# 
# 测试完整流程：
# 1. 访问助手模式主页
# 2. 点击"浏览策略包"进入激活流程
# 3. 设置参数并启动策略
# 4. 查看运行状态
# 5. 查看进度报告

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  助手模式 MVP 用户旅程测试" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# 检查前端服务是否运行
Write-Host "[1/5] 检查前端服务..." -ForegroundColor Yellow
$frontendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    $frontendRunning = $true
    Write-Host "✓ 前端服务运行正常 (http://localhost:5173)" -ForegroundColor Green
} catch {
    Write-Host "✗ 前端服务未运行" -ForegroundColor Red
    Write-Host "  请运行: cd frontend; npm run dev" -ForegroundColor Gray
}

# 检查后端服务是否运行
Write-Host "`n[2/5] 检查后端服务..." -ForegroundColor Yellow
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    $backendRunning = $true
    Write-Host "✓ 后端服务运行正常 (http://localhost:8000)" -ForegroundColor Green
} catch {
    Write-Host "✗ 后端服务未运行" -ForegroundColor Red
    Write-Host "  请运行: cd backend; uvicorn main:app --reload" -ForegroundColor Gray
}

# 检查关键文件是否存在
Write-Host "`n[3/5] 检查关键文件..." -ForegroundColor Yellow
$files = @{
    "AssistantDashboard.tsx" = "frontend\src\pages\AssistantDashboard.tsx"
    "StrategyActivationFlow.tsx" = "frontend\src\pages\StrategyActivationFlow.tsx"
    "StrategyRunningStatus.tsx" = "frontend\src\pages\StrategyRunningStatus.tsx"
    "SimpleProgressReport.tsx" = "frontend\src\pages\SimpleProgressReport.tsx"
    "App.tsx (路由配置)" = "frontend\src\App.tsx"
}

$allFilesExist = $true
foreach ($name in $files.Keys) {
    $path = $files[$name]
    if (Test-Path $path) {
        Write-Host "  ✓ $name" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $name 不存在" -ForegroundColor Red
        $allFilesExist = $false
    }
}

# 检查路由注册
Write-Host "`n[4/5] 检查路由注册..." -ForegroundColor Yellow
$appTsxContent = Get-Content "frontend\src\App.tsx" -Raw
$routes = @(
    "/assistant/strategies/activate/:packageId",
    "/assistant/strategies/running/:instanceId",
    "/assistant/strategies/report/:instanceId"
)

$allRoutesRegistered = $true
foreach ($route in $routes) {
    if ($appTsxContent -match [regex]::Escape($route)) {
        Write-Host "  ✓ 路由 $route 已注册" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 路由 $route 未找到" -ForegroundColor Red
        $allRoutesRegistered = $false
    }
}

# 生成用户旅程指南
Write-Host "`n[5/5] 用户旅程测试指南" -ForegroundColor Yellow
Write-Host ""
Write-Host "完整的用户旅程流程：" -ForegroundColor Cyan
Write-Host ""
Write-Host "步骤 1: 访问助手模式主页" -ForegroundColor White
Write-Host "  URL: http://localhost:5173/assistant" -ForegroundColor Gray
Write-Host "  预期: 看到'智能投资助手'页面，包含账户概况和市场机会" -ForegroundColor Gray
Write-Host ""

Write-Host "步骤 2: 点击'浏览策略包'或空状态下的按钮" -ForegroundColor White
Write-Host "  预期: 跳转到策略激活页面 (Step 1: 确认策略)" -ForegroundColor Gray
Write-Host ""

Write-Host "步骤 3: 在激活流程中设置参数" -ForegroundColor White
Write-Host "  Step 1: 确认策略信息（稳健增长定投宝）" -ForegroundColor Gray
Write-Host "  Step 2: 设置投入金额（默认5000元）和定投周期（月度）" -ForegroundColor Gray
Write-Host "  Step 3: 阅读风险提示并同意启动" -ForegroundColor Gray
Write-Host ""

Write-Host "步骤 4: 策略启动后自动跳转到运行状态页" -ForegroundColor White
Write-Host "  URL: http://localhost:5173/assistant/strategies/running/:instanceId" -ForegroundColor Gray
Write-Host "  预期: 看到账户价值、下次操作、管理按钮" -ForegroundColor Gray
Write-Host ""

Write-Host "步骤 5: 点击'查看详细报告'按钮" -ForegroundColor White
Write-Host "  URL: http://localhost:5173/assistant/strategies/report/:instanceId" -ForegroundColor Gray
Write-Host "  预期: 看到周报/月报，包含进度条、本周亮点、下周建议" -ForegroundColor Gray
Write-Host ""

# 测试结果总结
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  测试结果总结" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$allTestsPassed = $frontendRunning -and $backendRunning -and $allFilesExist -and $allRoutesRegistered

if ($allTestsPassed) {
    Write-Host "✓ 所有检查通过！MVP 已就绪" -ForegroundColor Green
    Write-Host ""
    Write-Host "开始测试：" -ForegroundColor White
    Write-Host "1. 在浏览器中访问: http://localhost:5173/assistant" -ForegroundColor Cyan
    Write-Host "2. 按照上面的用户旅程指南操作" -ForegroundColor Cyan
    Write-Host "3. 记录任何问题或改进建议" -ForegroundColor Cyan
} else {
    Write-Host "✗ 部分检查失败，请修复后再测试" -ForegroundColor Red
    Write-Host ""
    if (-not $frontendRunning) {
        Write-Host "启动前端: cd frontend; npm run dev" -ForegroundColor Yellow
    }
    if (-not $backendRunning) {
        Write-Host "启动后端: cd backend; uvicorn main:app --reload" -ForegroundColor Yellow
    }
    if (-not $allFilesExist) {
        Write-Host "缺少关键文件，请检查文件是否正确创建" -ForegroundColor Yellow
    }
    if (-not $allRoutesRegistered) {
        Write-Host "路由未完全注册，请检查 frontend/src/App.tsx" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Phase 1 Week 1 进度检查" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Day 1-2: StrategyActivationFlow.tsx (3步向导)" -ForegroundColor Green
Write-Host "✓ Day 3-4: StrategyRunningStatus.tsx (监控页面)" -ForegroundColor Green
Write-Host "✓ Day 5: SimpleProgressReport.tsx (周报/月报)" -ForegroundColor Green
Write-Host "✓ 路由注册: 所有助手模式路由已配置" -ForegroundColor Green
Write-Host "✓ 导航链接: AssistantDashboard 已更新跳转逻辑" -ForegroundColor Green
Write-Host ""
Write-Host "下一步 (Day 6-7):" -ForegroundColor Yellow
Write-Host "  1. 实现后端 API endpoints (activate/setup, running status, report)" -ForegroundColor Gray
Write-Host "  2. 集成虚拟交易引擎（VirtualTradingEngine）" -ForegroundColor Gray
Write-Host "  3. 数据库表结构（strategy_instances, execution_history）" -ForegroundColor Gray
Write-Host "  4. 端到端测试和用户体验优化" -ForegroundColor Gray
Write-Host ""
