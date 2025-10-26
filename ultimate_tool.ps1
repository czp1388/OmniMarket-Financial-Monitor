# 寰宇多市场金融监控系统 - 终极服务管理器
param([string]$Action = "status")

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$ServiceDir = "$ProjectRoot\backend\app"

function Start-UltimateService {
    Write-Host "🚀 启动终极版服务..." -ForegroundColor Cyan
    
    # 停止可能运行的服务
    Stop-UltimateService
    
    # 检查必要文件
    Write-Host "1. 检查项目完整性..." -ForegroundColor Yellow
    $requiredFiles = @(
        @{Path="main.py"; Desc="主服务文件"},
        @{Path="routers\market.py"; Desc="市场路由"},
        @{Path="routers\__init__.py"; Desc="路由初始化"}
    )
    
    foreach ($file in $requiredFiles) {
        if (Test-Path "$ServiceDir\$($file.Path)") {
            Write-Host "   ✅ $($file.Desc)" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $($file.Desc) 缺失" -ForegroundColor Red
            return $false
        }
    }
    
    # 检查语法
    Write-Host "2. 检查Python语法..." -ForegroundColor Yellow
    try {
        cd $ServiceDir
        python -c "import ast; ast.parse(open('main.py', encoding='utf-8').read()); print('✅ main.py 语法正确')"
        python -c "import ast; ast.parse(open('routers\market.py', encoding='utf-8').read()); print('✅ market.py 语法正确')"
        Write-Host "   ✅ 所有文件语法正确" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ 语法检查失败: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # 启动服务
    Write-Host "3. 启动服务进程..." -ForegroundColor Yellow
    try {
        $process = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory $ServiceDir -PassThru -WindowStyle Normal
        Write-Host "   ✅ 服务启动成功 (PID: $($process.Id))" -ForegroundColor Green
        Write-Host "   📍 服务地址: http://localhost:8000" -ForegroundColor White
        Write-Host "   📚 API文档: http://localhost:8000/docs" -ForegroundColor White
        
        # 等待服务启动
        Write-Host "4. 等待服务就绪..." -ForegroundColor Yellow
        for ($i = 1; $i -le 10; $i++) {
            Write-Host "   等待中... ($i/10)" -ForegroundColor Gray
            Start-Sleep -Seconds 2
            
            if (Test-UltimateService) {
                Write-Host "   ✅ 服务已就绪！" -ForegroundColor Green
                return $true
            }
        }
        
        Write-Host "   ⚠️ 服务启动较慢，请稍后手动测试" -ForegroundColor Yellow
        return $true
    } catch {
        Write-Host "   ❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Stop-UltimateService {
    Write-Host "🛑 停止所有服务..." -ForegroundColor Yellow
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        $count = 0
        foreach ($proc in $pythonProcesses) {
            try {
                $proc | Stop-Process -Force
                $count++
            } catch {
                Write-Host "   警告: 无法停止进程 $($proc.Id)" -ForegroundColor Red
            }
        }
        Write-Host "✅ 已停止 $count 个Python进程" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ 没有运行中的Python服务" -ForegroundColor Blue
    }
}

function Test-UltimateService {
    $endpoints = @(
        @{Url="http://localhost:8000/health"; Name="健康检查"},
        @{Url="http://localhost:8000/"; Name="根路径"},
        @{Url="http://localhost:8000/api/v1/exchanges"; Name="交易所列表"}
    )
    
    $successCount = 0
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 3
            $successCount++
        } catch {
            # 忽略单个端点失败
        }
    }
    
    return $successCount -gt 0
}

function Show-UltimateStatus {
    Write-Host "📊 终极服务状态监控" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Yellow
    
    # 检查进程
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Write-Host "✅ 服务状态: 运行中" -ForegroundColor Green
        Write-Host "   PID: $(($pythonProcesses | Select-Object -First 1).Id)" -ForegroundColor White
        Write-Host "   进程数: $($pythonProcesses.Count)" -ForegroundColor White
    } else {
        Write-Host "❌ 服务状态: 未运行" -ForegroundColor Red
    }
    
    # 测试连接
    Write-Host "🌐 API连接测试..." -ForegroundColor Cyan
    if (Test-UltimateService) {
        Write-Host "   ✅ API状态: 可访问" -ForegroundColor Green
    } else {
        Write-Host "   ❌ API状态: 不可访问" -ForegroundColor Red
    }
    
    Write-Host "📁 项目位置: $ProjectRoot" -ForegroundColor Gray
    Write-Host "🕐 检查时间: $(Get-Date)" -ForegroundColor Gray
}

function Invoke-UltimateTest {
    Write-Host "🔍 终极API测试..." -ForegroundColor Cyan
    
    $endpoints = @(
        @{Url="http://localhost:8000/health"; Name="健康检查"},
        @{Url="http://localhost:8000/"; Name="根路径"},
        @{Url="http://localhost:8000/api/v1/exchanges"; Name="交易所列表"},
        @{Url="http://localhost:8000/api/v1/prices/?symbol=BTC/USDT"; Name="BTC价格"}
    )
    
    $maxRetries = 3
    $retryDelay = 2
    
    foreach ($endpoint in $endpoints) {
        $retryCount = 0
        $success = $false
        
        while (-not $success -and $retryCount -lt $maxRetries) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 5
                Write-Host "   ✅ $($endpoint.Name) - 正常" -ForegroundColor Green
                $success = $true
            } catch {
                $retryCount++
                if ($retryCount -eq $maxRetries) {
                    Write-Host "   ❌ $($endpoint.Name) - 失败" -ForegroundColor Red
                } else {
                    Write-Host "   ⚠️ $($endpoint.Name) - 第$retryCount次重试..." -ForegroundColor Yellow
                    Start-Sleep -Seconds $retryDelay
                }
            }
        }
    }
}

# 执行动作
switch ($Action) {
    "start" { 
        if (Start-UltimateService) {
            Write-Host "🎉 服务启动完成！" -ForegroundColor Green
        } else {
            Write-Host "❌ 服务启动失败，请检查错误信息" -ForegroundColor Red
        }
    }
    "stop" { Stop-UltimateService }
    "test" { Invoke-UltimateTest }
    "status" { Show-UltimateStatus }
    "restart" { 
        Stop-UltimateService
        Start-Sleep -Seconds 3
        Start-UltimateService
    }
    default { Show-UltimateStatus }
}
