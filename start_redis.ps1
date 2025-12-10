# Redis 快速启动脚本
# 用途：一键启动 Redis 服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Redis 快速启动工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检测 Redis 是否已运行
$redisProcess = Get-Process redis-server -ErrorAction SilentlyContinue

if ($redisProcess) {
    Write-Host "✅ Redis 已经在运行中 (PID: $($redisProcess.Id))" -ForegroundColor Green
    Write-Host ""
    
    $restart = Read-Host "是否重启 Redis? (y/n)"
    if ($restart -eq "y") {
        Write-Host "正在停止 Redis..." -ForegroundColor Yellow
        Stop-Process -Id $redisProcess.Id -Force
        Start-Sleep -Seconds 2
        Write-Host "✅ Redis 已停止" -ForegroundColor Green
    } else {
        exit 0
    }
}

# 查找 Redis 安装路径
$redisPaths = @(
    "C:\Program Files\Redis\redis-server.exe",
    "C:\Program Files (x86)\Redis\redis-server.exe",
    "$env:LOCALAPPDATA\Redis\redis-server.exe",
    "redis-server.exe"  # 环境变量PATH中
)

$redisExe = $null
foreach ($path in $redisPaths) {
    if (Test-Path $path) {
        $redisExe = $path
        break
    }
}

if (-not $redisExe) {
    # 尝试从PATH中找
    try {
        $redisExe = (Get-Command redis-server -ErrorAction SilentlyContinue).Source
    } catch {}
}

if ($redisExe) {
    Write-Host "找到 Redis: $redisExe" -ForegroundColor Cyan
    Write-Host "正在启动 Redis..." -ForegroundColor Yellow
    
    try {
        # 启动 Redis（最小化窗口）
        Start-Process -FilePath $redisExe -WindowStyle Minimized
        Start-Sleep -Seconds 2
        
        # 验证启动
        $newProcess = Get-Process redis-server -ErrorAction SilentlyContinue
        if ($newProcess) {
            Write-Host "✅ Redis 启动成功 (PID: $($newProcess.Id))" -ForegroundColor Green
            Write-Host ""
            Write-Host "Redis 运行信息:" -ForegroundColor Cyan
            Write-Host "  - 主机: localhost" -ForegroundColor White
            Write-Host "  - 端口: 6379" -ForegroundColor White
            Write-Host "  - 状态: 运行中" -ForegroundColor Green
            Write-Host ""
            Write-Host "提示: Redis 将在后台运行，关闭此窗口不影响服务" -ForegroundColor Yellow
        } else {
            Write-Host "❌ Redis 启动失败" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ 启动 Redis 时出错: $_" -ForegroundColor Red
    }
} else {
    Write-Host "❌ 未找到 Redis 安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "安装 Redis (Windows):" -ForegroundColor Cyan
    Write-Host "  1. 下载: https://github.com/microsoftarchive/redis/releases" -ForegroundColor White
    Write-Host "  2. 安装到: C:\Program Files\Redis\" -ForegroundColor White
    Write-Host "  3. 重新运行此脚本" -ForegroundColor White
    Write-Host ""
    Write-Host "或使用 Chocolatey 安装:" -ForegroundColor Cyan
    Write-Host "  choco install redis-64" -ForegroundColor White
    Write-Host ""
    Write-Host "注意: 系统可以在没有 Redis 的情况下运行（使用模拟缓存）" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
