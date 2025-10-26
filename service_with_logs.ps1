# 寰宇多市场金融监控系统 - 日志服务启动器
Write-Host "🚀 启动服务（带日志输出）..." -ForegroundColor Cyan

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$BackendDir = "$ProjectRoot\backend\app"
$LogFile = "$ProjectRoot\service.log"

# 停止可能运行的服务
Write-Host "1. 清理环境..." -ForegroundColor Yellow
try {
    & "$ProjectRoot\ultimate_tool.ps1" stop
    Write-Host "   ✅ 环境清理完成" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ 环境清理跳过" -ForegroundColor Yellow
}

# 等待端口释放
Start-Sleep -Seconds 3

# 启动服务并捕获输出
Write-Host "2. 启动服务..." -ForegroundColor Yellow
Write-Host "   日志文件: $LogFile" -ForegroundColor Gray

try {
    # 使用Start-Process启动服务并重定向输出
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "python"
    $processInfo.Arguments = "main.py"
    $processInfo.WorkingDirectory = $BackendDir
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $false

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    $process.Start() | Out-Null

    Write-Host "   ✅ 服务启动成功 (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "   📍 服务地址: http://localhost:8000" -ForegroundColor White
    Write-Host "   📚 API文档: http://localhost:8000/docs" -ForegroundColor White

    # 异步读取输出
    $outputJob = Start-Job -ScriptBlock {
        param($Process, $LogFile)
        while (!$Process.HasExited) {
            if (!$Process.StandardOutput.EndOfStream) {
                $line = $Process.StandardOutput.ReadLine()
                Write-Host "   [服务日志] $line" -ForegroundColor Gray
                Add-Content -Path $LogFile -Value "$(Get-Date): $line"
            }
            Start-Sleep -Milliseconds 100
        }
    } -ArgumentList $process, $LogFile

    # 等待服务就绪
    Write-Host "3. 等待服务就绪..." -ForegroundColor Yellow
    $serviceReady = $false
    for ($i = 1; $i -le 20; $i++) {
        Write-Host "   等待中... ($i/20)" -ForegroundColor Gray
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "   ✅ 服务已就绪！" -ForegroundColor Green
                $serviceReady = $true
                break
            }
        } catch {
            # 继续等待
        }
        
        Start-Sleep -Seconds 2
    }

    if (-not $serviceReady) {
        Write-Host "   ⚠️ 服务启动超时，请检查日志文件" -ForegroundColor Yellow
        Write-Host "   📄 日志文件: $LogFile" -ForegroundColor White
    }

    Write-Host "`n🎉 服务启动完成！" -ForegroundColor Green
    Write-Host "💡 PID: $($process.Id)" -ForegroundColor Cyan
    Write-Host "📄 实时日志: $LogFile" -ForegroundColor Cyan

    # 返回进程信息供后续使用
    return @{
        Process = $process
        OutputJob = $outputJob
        LogFile = $LogFile
    }

} catch {
    Write-Host "   ❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   📄 请检查日志文件: $LogFile" -ForegroundColor White
}
