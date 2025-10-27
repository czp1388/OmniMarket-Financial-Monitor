# OmniMarket 绝对可靠服务启动器
# 在任何情况下都能启动服务

Write-Host "🚀 启动 OmniMarket 服务 (绝对可靠版)..." -ForegroundColor Green

# 强制切换到正确目录
$correctPath = "E:\OmniMarket-Financial-Monitor"
if ((Get-Location).Path -ne $correctPath) {
    Write-Host "切换到项目目录: $correctPath" -ForegroundColor Yellow
    Set-Location $correctPath
}

# 1. 彻底清理环境
Write-Host "1. 彻底清理环境..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python3 -ErrorAction SilentlyContinue | Stop-Process -Force

# 清理端口占用
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portProcess) {
    Write-Host "清理端口8000占用..." -ForegroundColor Cyan
    $portProcess | ForEach-Object {
        try {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        } catch {
            # 忽略无法停止的进程
        }
    }
}

Start-Sleep -Seconds 3

# 2. 检查Python环境
Write-Host "2. 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host " ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python未安装或不在PATH中" -ForegroundColor Red
    Write-Host "请安装Python并确保在PATH中" -ForegroundColor Yellow
    exit 1
}

# 3. 检查项目文件
Write-Host "3. 检查项目文件..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend\app\main_super_stable.py",
    "backend\app\main_simple.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host " ✅ $file" -ForegroundColor Green
    } else {
        Write-Host " ❌ $file 不存在" -ForegroundColor Red
    }
}

# 4. 检查依赖
Write-Host "4. 检查依赖..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn" 2>$null
    Write-Host " ✅ 核心依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ 缺少依赖，正在安装..." -ForegroundColor Yellow
    pip install fastapi uvicorn
    Write-Host " ✅ 依赖安装完成" -ForegroundColor Green
}

# 5. 启动服务
Write-Host "5. 启动服务..." -ForegroundColor Green
Set-Location "backend\app"

Write-Host "使用超级稳定版本启动..." -ForegroundColor Cyan
$process = Start-Process -FilePath "python" -ArgumentList "main_super_stable.py" -PassThru

# 6. 等待并测试
Write-Host "6. 等待服务启动（15秒）..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

Write-Host "7. 测试服务连接..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "✅ 服务启动成功!" -ForegroundColor Green
    Write-Host " 版本: $($health.version)" -ForegroundColor White
    Write-Host " 状态: $($health.status)" -ForegroundColor White
    Write-Host "`n🎉 服务运行正常!" -ForegroundColor Magenta
    Write-Host "🌐 访问地址:" -ForegroundColor Cyan
    Write-Host " API文档: http://localhost:8000/docs" -ForegroundColor Blue
    Write-Host " 健康检查: http://localhost:8000/health" -ForegroundColor Blue
} catch {
    Write-Host "❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "尝试使用简化版本..." -ForegroundColor Yellow
    # 停止当前进程
    try { $process | Stop-Process -Force } catch { }
    # 使用简化版本
    Write-Host "启动简化版本..." -ForegroundColor Cyan
    $simpleProcess = Start-Process -FilePath "python" -ArgumentList "main_simple.py" -PassThru
    Start-Sleep -Seconds 8
    try {
        $simpleHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Host "✅ 简化版服务启动成功!" -ForegroundColor Green
        Write-Host " 状态: $($simpleHealth.status)" -ForegroundColor White
    } catch {
        Write-Host "❌ 所有启动尝试都失败" -ForegroundColor Red
        Write-Host "请手动检查: cd backend\app && python main_simple.py" -ForegroundColor Yellow
    }
}

# 回到项目根目录
Set-Location "E:\OmniMarket-Financial-Monitor"
