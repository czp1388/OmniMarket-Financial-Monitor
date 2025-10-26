# 寰宇多市场金融监控系统 - 稳定服务管理器
param([string]$Action = "status")

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$ServiceDir = "$ProjectRoot\backend\app"

function Start-StableService {
    Write-Host "🔧 启动稳定版服务..." -ForegroundColor Cyan
    
    # 先检查依赖
    Write-Host "1. 检查Python环境..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version
        Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Python未正确安装" -ForegroundColor Red
        return
    }
    
    # 检查必要文件
    Write-Host "2. 检查项目文件..." -ForegroundColor Yellow
    $requiredFiles = @("main.py", "routers\market.py", "routers\__init__.py")
    foreach ($file in $requiredFiles) {
        if (Test-Path "$ServiceDir\$file") {
            Write-Host "   ✅ $file" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $file 缺失" -ForegroundColor Red
            return
        }
    }
    
    # 检查语法
    Write-Host "3. 检查Python语法..." -ForegroundColor Yellow
    try {
        cd $ServiceDir
        python -m py_compile main.py
        python -m py_compile routers\market.py
        Write-Host "   ✅ 语法检查通过" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 语法错误: $($_.Exception.Message)" -ForegroundColor Red
        return
    }
    
    # 启动服务
    Write-Host "4. 启动服务..." -ForegroundColor Yellow
    try {
        $process = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory $ServiceDir -PassThru
        Write-Host "   ✅ 服务启动成功 (PID: $($process.Id))" -ForegroundColor Green
        Write-Host "   📍 服务地址: http://localhost:8000" -ForegroundColor White
        Write-Host "   📚 API文档: http://localhost:8000/docs" -ForegroundColor White
        Write-Host "   💡 提示: 服务窗口将保持打开，请不要关闭" -ForegroundColor Cyan
        
        # 等待服务启动
        Write-Host "5. 等待服务就绪..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        return $process.Id
    } catch {
        Write-Host "   ❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-StableService {
    Write-Host "🛑 停止服务..." -ForegroundColor Yellow
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($processes) {
        $processes | Stop-Process -Force
        Write-Host "✅ 已停止 $($processes.Count) 个Python进程" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ 没有运行中的Python服务" -ForegroundColor Blue
    }
}

function Test-StableService {
    Write-Host "🔍 测试服务状态..." -ForegroundColor Cyan
    
    $endpoints = @(
        @{Url="http://localhost:8000/health"; Name="健康检查"},
        @{Url="http://localhost:8000/"; Name="根路径"}
    )
    
    $success = $true
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 3
            Write-Host "   ✅ $($endpoint.Name) - 正常" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ $($endpoint.Name) - 失败" -ForegroundColor Red
            $success = $false
        }
    }
    
    return $success
}

function Show-ServiceStatus {
    Write-Host "📊 服务状态监控" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Yellow
    
    # 检查进程
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Write-Host "✅ 服务状态: 运行中 ($($pythonProcesses.Count) 个进程)" -ForegroundColor Green
        Write-Host "   PID: $(($pythonProcesses | Select-Object -First 1).Id)" -ForegroundColor White
    } else {
        Write-Host "❌ 服务状态: 未运行" -ForegroundColor Red
    }
    
    # 测试连接
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2
        Write-Host "🌐 API状态: 可访问" -ForegroundColor Green
    } catch {
        Write-Host "🌐 API状态: 不可访问" -ForegroundColor Red
    }
}

# 执行动作
switch ($Action) {
    "start" { Start-StableService }
    "stop" { Stop-StableService }
    "test" { Test-StableService }
    "status" { Show-ServiceStatus }
    "restart" { 
        Stop-StableService
        Start-Sleep -Seconds 2
        Start-StableService
    }
    default { Show-ServiceStatus }
}
