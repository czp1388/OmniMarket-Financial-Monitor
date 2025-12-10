# OmniMarket 环境检测和自动修复工具
# 用途：一键检测系统环境并自动修复常见问题

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OmniMarket 环境检测和修复工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()

# 1. 检测 Python 环境
Write-Host "[1/8] 检测 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$matches[1]
        if ($minorVersion -ge 8) {
            Write-Host "  ✅ Python 版本: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Python 版本过低: $pythonVersion (建议 3.8+)" -ForegroundColor Red
            $issues += "Python 版本需要 3.8 或更高"
        }
    }
} catch {
    Write-Host "  ❌ Python 未安装或未加入PATH" -ForegroundColor Red
    $issues += "Python 未安装"
}

# 2. 检测虚拟环境
Write-Host "[2/8] 检测虚拟环境..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  ✅ 虚拟环境存在: .venv" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  虚拟环境不存在" -ForegroundColor Yellow
    $warnings += "虚拟环境未创建"
    
    $create = Read-Host "是否立即创建虚拟环境? (y/n)"
    if ($create -eq "y") {
        python -m venv .venv
        Write-Host "  ✅ 虚拟环境创建成功" -ForegroundColor Green
    }
}

# 3. 检测 Node.js
Write-Host "[3/8] 检测 Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✅ Node.js 版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Node.js 未安装" -ForegroundColor Red
    $issues += "Node.js 未安装"
}

# 4. 检测 Redis
Write-Host "[4/8] 检测 Redis..." -ForegroundColor Yellow
try {
    $redisProcess = Get-Process redis-server -ErrorAction SilentlyContinue
    if ($redisProcess) {
        Write-Host "  ✅ Redis 正在运行 (PID: $($redisProcess.Id))" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Redis 未运行" -ForegroundColor Yellow
        $warnings += "Redis 服务未启动"
        
        # 尝试启动 Redis
        if (Test-Path "C:\Program Files\Redis\redis-server.exe") {
            $start = Read-Host "是否启动 Redis? (y/n)"
            if ($start -eq "y") {
                Start-Process "C:\Program Files\Redis\redis-server.exe" -WindowStyle Minimized
                Start-Sleep -Seconds 2
                Write-Host "  ✅ Redis 启动成功" -ForegroundColor Green
            }
        } else {
            Write-Host "  ℹ️  Redis 未安装，系统将使用模拟缓存" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "  ⚠️  无法检测 Redis 状态" -ForegroundColor Yellow
    $warnings += "Redis 状态未知"
}

# 5. 检测 InfluxDB
Write-Host "[5/8] 检测 InfluxDB..." -ForegroundColor Yellow
try {
    $influxProcess = Get-Process influxd -ErrorAction SilentlyContinue
    if ($influxProcess) {
        Write-Host "  ✅ InfluxDB 正在运行 (PID: $($influxProcess.Id))" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  InfluxDB 未运行" -ForegroundColor Yellow
        $warnings += "InfluxDB 服务未启动"
        
        # 提示启动
        Write-Host "  ℹ️  请手动启动 InfluxDB 或使用模拟数据" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ⚠️  无法检测 InfluxDB 状态" -ForegroundColor Yellow
}

# 6. 检测端口占用
Write-Host "[6/8] 检测端口占用..." -ForegroundColor Yellow

function Test-Port {
    param($Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connection -ne $null
}

# 检测 8000 (后端)
if (Test-Port 8000) {
    Write-Host "  ⚠️  端口 8000 已被占用" -ForegroundColor Yellow
    $warnings += "后端端口 8000 被占用"
} else {
    Write-Host "  ✅ 端口 8000 可用 (后端)" -ForegroundColor Green
}

# 检测 5173 (前端)
if (Test-Port 5173) {
    Write-Host "  ⚠️  端口 5173 已被占用" -ForegroundColor Yellow
    $warnings += "前端端口 5173 被占用"
} else {
    Write-Host "  ✅ 端口 5173 可用 (前端)" -ForegroundColor Green
}

# 7. 检测后端依赖
Write-Host "[7/8] 检测后端依赖..." -ForegroundColor Yellow
if (Test-Path "backend/requirements.txt") {
    Write-Host "  ✅ requirements.txt 存在" -ForegroundColor Green
    
    # 检测关键依赖
    & .venv\Scripts\Activate.ps1
    $missingDeps = @()
    
    try {
        python -c "import fastapi" 2>&1 | Out-Null
    } catch {
        $missingDeps += "fastapi"
    }
    
    try {
        python -c "import uvicorn" 2>&1 | Out-Null
    } catch {
        $missingDeps += "uvicorn"
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Host "  ⚠️  缺少依赖: $($missingDeps -join ', ')" -ForegroundColor Yellow
        $install = Read-Host "是否安装缺失的依赖? (y/n)"
        if ($install -eq "y") {
            pip install -r backend/requirements.txt
            Write-Host "  ✅ 依赖安装完成" -ForegroundColor Green
        }
    } else {
        Write-Host "  ✅ 关键依赖已安装" -ForegroundColor Green
    }
} else {
    Write-Host "  ❌ requirements.txt 不存在" -ForegroundColor Red
    $issues += "缺少 requirements.txt"
}

# 8. 检测前端依赖
Write-Host "[8/8] 检测前端依赖..." -ForegroundColor Yellow
if (Test-Path "frontend/node_modules") {
    Write-Host "  ✅ node_modules 存在" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  node_modules 不存在" -ForegroundColor Yellow
    $warnings += "前端依赖未安装"
    
    $install = Read-Host "是否安装前端依赖? (y/n)"
    if ($install -eq "y") {
        Set-Location frontend
        npm install
        Set-Location ..
        Write-Host "  ✅ 前端依赖安装完成" -ForegroundColor Green
    }
}

# 总结报告
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  检测结果总结" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "🎉 恭喜！所有检测通过，环境就绪！" -ForegroundColor Green
    Write-Host ""
    Write-Host "启动命令:" -ForegroundColor Cyan
    Write-Host "  后端: cd backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host "  前端: cd frontend; npm run dev" -ForegroundColor White
} else {
    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-Host "❌ 发现 $($issues.Count) 个关键问题:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "  - $issue" -ForegroundColor Red
        }
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️  发现 $($warnings.Count) 个警告:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  - $warning" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "ℹ️  这些警告不会阻止系统运行，但可能影响部分功能" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "检测完成！按任意键退出..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
