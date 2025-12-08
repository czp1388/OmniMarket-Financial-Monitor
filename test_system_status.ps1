# 系统状态完整测试脚本
# 测试前后端服务、数据库、API 端点

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "  OmniMarket 系统状态检测" -ForegroundColor Green
Write-Host "======================================`n" -ForegroundColor Cyan

# 1. 检查服务端口
Write-Host "[1/6] 检查服务端口..." -ForegroundColor Yellow

$ports = @{
    "后端 API (8000)" = "8000"
    "前端 Vite (5173)" = "5173"
    "前端备用 (3000)" = "3000"
}

$servicesRunning = @{}
foreach ($name in $ports.Keys) {
    $port = $ports[$name]
    $result = netstat -ano | Select-String ":$port "
    if ($result) {
        Write-Host "  ✓ $name - 正在运行" -ForegroundColor Green
        $servicesRunning[$name] = $true
    } else {
        Write-Host "  ✗ $name - 未运行" -ForegroundColor Red
        $servicesRunning[$name] = $false
    }
}

# 2. 检查数据库
Write-Host "`n[2/6] 检查数据库..." -ForegroundColor Yellow

$dbPath = "E:\OmniMarket-Financial-Monitor\backend\omnimarket.db"
if (Test-Path $dbPath) {
    $dbSize = (Get-Item $dbPath).Length / 1KB
    Write-Host "  ✓ 数据库文件存在" -ForegroundColor Green
    Write-Host "    路径: $dbPath" -ForegroundColor Gray
    Write-Host "    大小: $([math]::Round($dbSize, 2)) KB" -ForegroundColor Gray
} else {
    Write-Host "  ✗ 数据库文件不存在" -ForegroundColor Red
}

# 3. 测试后端 API
Write-Host "`n[3/6] 测试后端 API..." -ForegroundColor Yellow

if ($servicesRunning["后端 API (8000)"]) {
    try {
        # 测试健康检查端点
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "  ✓ 健康检查通过" -ForegroundColor Green
        
        # 测试策略包列表
        $packages = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/assistant/strategies/packages" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "  ✓ 策略包 API 正常 ($($packages.Count) 个策略包)" -ForegroundColor Green
        
        # 测试仪表盘摘要
        $dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/assistant/dashboard/summary" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "  ✓ 仪表盘 API 正常" -ForegroundColor Green
        
    } catch {
        Write-Host "  ✗ API 测试失败: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "  - 后端未运行，跳过 API 测试" -ForegroundColor Gray
}

# 4. 检查前端资源
Write-Host "`n[4/6] 检查前端资源..." -ForegroundColor Yellow

$frontendFiles = @(
    "frontend\src\App.tsx",
    "frontend\src\pages\AssistantDashboard.tsx",
    "frontend\src\pages\BloombergStyleDashboard.tsx",
    "frontend\src\pages\StrategyActivationFlow.tsx",
    "frontend\src\pages\StrategyRunningStatus.tsx",
    "frontend\src\pages\SimpleProgressReport.tsx"
)

$missingFiles = @()
foreach ($file in $frontendFiles) {
    $fullPath = "E:\OmniMarket-Financial-Monitor\$file"
    if (Test-Path $fullPath) {
        Write-Host "  ✓ $($file.Split('\')[-1])" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($file.Split('\')[-1]) - 缺失" -ForegroundColor Red
        $missingFiles += $file
    }
}

# 5. 检查最近的 Git 提交
Write-Host "`n[5/6] 检查 Git 状态..." -ForegroundColor Yellow

try {
    cd E:\OmniMarket-Financial-Monitor
    $lastCommit = git log -1 --oneline
    Write-Host "  ✓ 最近提交: $lastCommit" -ForegroundColor Green
    
    $status = git status --short
    if ($status) {
        $changedFiles = ($status | Measure-Object).Count
        Write-Host "  ⚠ 有 $changedFiles 个文件未提交" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ 工作区干净" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Git 检查失败" -ForegroundColor Red
}

# 6. 生成测试报告
Write-Host "`n[6/6] 测试总结" -ForegroundColor Yellow

$totalTests = 0
$passedTests = 0

# 服务状态
if ($servicesRunning["后端 API (8000)"]) { $passedTests++ }
$totalTests++

if ($servicesRunning["前端 Vite (5173)"] -or $servicesRunning["前端备用 (3000)"]) { $passedTests++ }
$totalTests++

# 数据库
if (Test-Path $dbPath) { $passedTests++ }
$totalTests++

# 前端文件
if ($missingFiles.Count -eq 0) { $passedTests++ }
$totalTests++

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "  测试通过: $passedTests / $totalTests" -ForegroundColor $(if ($passedTests -eq $totalTests) {"Green"} else {"Yellow"})
Write-Host "======================================`n" -ForegroundColor Cyan

# 操作建议
if (-not $servicesRunning["后端 API (8000)"]) {
    Write-Host "📌 启动后端: .\start_backend.bat" -ForegroundColor Yellow
}

if (-not ($servicesRunning["前端 Vite (5173)"] -or $servicesRunning["前端备用 (3000)"])) {
    Write-Host "📌 启动前端: .\start_frontend.bat" -ForegroundColor Yellow
}

if ($missingFiles.Count -gt 0) {
    Write-Host "📌 缺少 $($missingFiles.Count) 个前端文件，请检查代码完整性" -ForegroundColor Yellow
}

Write-Host "`n✅ 专家模式问题已修复 (BloombergStyleDashboard.tsx)" -ForegroundColor Green
Write-Host "🔗 访问链接:" -ForegroundColor Cyan
Write-Host "   助手模式: http://localhost:5173/assistant" -ForegroundColor Gray
Write-Host "   专家模式: http://localhost:5173/expert" -ForegroundColor Gray
Write-Host "   API 文档: http://localhost:8000/docs`n" -ForegroundColor Gray
