# 双模架构 - 快速启动脚本
# 一键启动后端和前端，验证双模功能

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   双模架构 - 快速启动" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

# 检查必要文件
Write-Host "[1/5] 检查文件..." -ForegroundColor Yellow

$requiredFiles = @(
    "backend\services\intent_service.py",
    "backend\api\endpoints\assistant_api.py",
    "frontend\src\pages\AssistantDashboard.tsx"
)

$allExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file 不存在！" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host "`n错误：缺少必要文件，请检查实施是否完成" -ForegroundColor Red
    exit 1
}

# 检查端口占用
Write-Host "`n[2/5] 检查端口..." -ForegroundColor Yellow

$port8000 = netstat -ano | findstr ":8000"
$port3001 = netstat -ano | findstr ":3001"

if ($port8000) {
    Write-Host "  ⚠ 端口8000已被占用（后端可能已运行）" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ 端口8000空闲" -ForegroundColor Green
}

if ($port3001) {
    Write-Host "  ⚠ 端口3001已被占用（前端可能已运行）" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ 端口3001空闲" -ForegroundColor Green
}

# 运行快速验证
Write-Host "`n[3/5] 验证核心功能..." -ForegroundColor Yellow

python quick_verify_dual_mode.py > $null 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 意图理解服务正常" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 验证失败，但可能不影响运行" -ForegroundColor Yellow
}

# 询问是否启动
Write-Host "`n[4/5] 准备启动服务..." -ForegroundColor Yellow

$response = Read-Host "是否启动后端和前端？(y/n)"

if ($response -ne 'y') {
    Write-Host "`n已取消启动" -ForegroundColor Gray
    exit 0
}

# 启动后端
Write-Host "`n[5/5] 启动服务..." -ForegroundColor Yellow

Write-Host "`n正在启动后端（端口8000）..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PWD\backend'; Write-Host '后端服务启动中...' -ForegroundColor Green; uvicorn main:app --reload --host 0.0.0.0 --port 8000"
)

Start-Sleep -Seconds 3

# 启动前端
Write-Host "正在启动前端（端口3001）..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PWD\frontend'; Write-Host '前端服务启动中...' -ForegroundColor Green; npm run dev"
)

Start-Sleep -Seconds 2

# 等待服务启动
Write-Host "`n等待服务启动..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# 检查服务状态
Write-Host "`n检查服务状态..." -ForegroundColor Yellow

$backendRunning = $false
$frontendRunning = $false

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "  ✓ 后端服务运行正常" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ 后端服务未就绪（可能还在启动）" -ForegroundColor Yellow
}

$frontendCheck = netstat -ano | findstr ":3001"
if ($frontendCheck) {
    $frontendRunning = $true
    Write-Host "  ✓ 前端服务运行正常" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 前端服务未就绪（可能还在启动）" -ForegroundColor Yellow
}

# 打开浏览器
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   服务启动完成！" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "📱 助手模式（零基础用户）:" -ForegroundColor Yellow
Write-Host "   http://localhost:3001/assistant" -ForegroundColor White

Write-Host "`n🔬 专家模式（量化交易员）:" -ForegroundColor Yellow
Write-Host "   http://localhost:3001/expert" -ForegroundColor White

Write-Host "`n📚 API文档（查看 '智能助手' 标签）:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n🧪 测试助手API:" -ForegroundColor Yellow
Write-Host "   .\test_dual_mode_curl.ps1" -ForegroundColor Gray

Write-Host "`n💡 提示:" -ForegroundColor Cyan
Write-Host "   - 两个服务已在独立窗口中运行" -ForegroundColor Gray
Write-Host "   - 关闭窗口或按 Ctrl+C 可停止服务" -ForegroundColor Gray
Write-Host "   - 如服务未就绪，请等待10-15秒后刷新页面" -ForegroundColor Gray

# 自动打开浏览器
$openBrowser = Read-Host "`n是否自动打开浏览器？(y/n)"

if ($openBrowser -eq 'y') {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000/docs"
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:3001/assistant"
    
    Write-Host "`n浏览器已打开，开始体验双模架构！" -ForegroundColor Green
}

Write-Host "`n============================================`n" -ForegroundColor Cyan
