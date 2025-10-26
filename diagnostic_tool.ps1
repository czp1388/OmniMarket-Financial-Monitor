# 寰宇多市场金融监控系统 - 诊断工具
param([string]$CheckType = "all")

function Test-Service {
    Write-Host "🔍 检查服务状态..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3
        Write-Host "   ✅ 服务运行正常" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   ❌ 服务未运行" -ForegroundColor Red
        return $false
    }
}

function Test-Environment {
    Write-Host "`n🔍 检查环境..." -ForegroundColor Cyan
    
    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Python未安装" -ForegroundColor Red
    }
    
    # 检查关键目录
    $directories = @("backend", "backend\app", "backend\app\routers")
    foreach ($dir in $directories) {
        if (Test-Path $dir) {
            Write-Host "   ✅ 目录存在: $dir" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 目录缺失: $dir" -ForegroundColor Red
        }
    }
}

function Show-Fixes {
    Write-Host "`n🚀 快速修复命令:" -ForegroundColor Magenta
    Write-Host "1. 启动服务: cd backend\app; python main.py" -ForegroundColor White
    Write-Host "2. 安装依赖: cd backend; pip install -r requirements_simple.txt" -ForegroundColor White
    Write-Host "3. 更新状态: .\project_status.ps1 update" -ForegroundColor White
}

# 执行检查
switch ($CheckType) {
    "service" { Test-Service }
    "env" { Test-Environment }
    "all" { 
        Test-Service
        Test-Environment
        Show-Fixes
    }
    default { 
        Write-Host "用法: .\diagnostic_tool.ps1 [all|service|env]" -ForegroundColor Yellow
    }
}
