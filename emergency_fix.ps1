# 寰宇金融监控系统 - 紧急修复脚本
Write-Host "🚨 执行紧急修复..." -ForegroundColor Red

# 停止所有Python进程
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 清理端口
try {
    $process = netstat -ano | findstr :8000
    if ($process) {
        $pid = ($process -split '\s+')[-1]
        taskkill /PID $pid /F
        Write-Host "✅ 已清理端口8000进程: $pid" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ 端口清理失败: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 重新安装依赖
Write-Host "🔧 重新安装Python依赖..." -ForegroundColor Yellow
pip install -r requirements.txt --upgrade

# 启动服务
Write-Host "🚀 启动服务..." -ForegroundColor Green
cd backend\app
python main_pro.py
