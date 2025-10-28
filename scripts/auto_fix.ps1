# 自动问题修复脚本 - 解决常见开发问题
param(
    [string]$FixType = "all"
)

Write-Host "🔧 执行自动问题修复..." -ForegroundColor Magenta

switch ($FixType) {
    "crypto" {
        Write-Host "修复加密货币API..." -ForegroundColor Cyan
        # 这里放置上面修复加密货币的代码
    }
    "logs" {
        Write-Host "修复日志目录问题..." -ForegroundColor Cyan
        if (!(Test-Path "logs")) {
            New-Item -ItemType Directory -Path "logs" -Force
            Write-Host "✅ 创建logs目录" -ForegroundColor Green
        }
    }
    "deps" {
        Write-Host "安装依赖..." -ForegroundColor Cyan
        pip install ccxt pandas requests fastapi uvicorn
        Write-Host "✅ 依赖安装完成" -ForegroundColor Green
    }
    "all" {
        Write-Host "执行所有修复..." -ForegroundColor Cyan
        
        # 修复日志目录
        if (!(Test-Path "logs")) {
            New-Item -ItemType Directory -Path "logs" -Force
            Write-Host "✅ 创建logs目录" -ForegroundColor Green
        }
        
        # 修复加密货币路由
        $content = Get-Content "backend\app\main_simple.py" -Raw
        if ($content -notmatch "crypto") {
            $newContent = $content -replace "from app\.routers import stock_cn, stock_hk", "from app.routers import stock_cn, stock_hk, crypto"
            $newContent = $newContent -replace "app\.include_router\(stock_hk\.router\)", "app.include_router(stock_hk.router)`napp.include_router(crypto.router)"
            $newContent | Set-Content "backend\app\main_simple.py" -Encoding utf8
            Write-Host "✅ 注册加密货币路由" -ForegroundColor Green
        }
        
        # 安装依赖
        pip install ccxt pandas requests fastapi uvicorn | Out-Null
        Write-Host "✅ 检查依赖" -ForegroundColor Green
        
        Write-Host "`n🎉 所有问题修复完成！" -ForegroundColor Green
    }
}
