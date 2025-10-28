# DeepSeek命令自动执行器
param(
    [string]$Command
)

Write-Host "🤖 执行DeepSeek指令..." -ForegroundColor Magenta

if ($Command) {
    Write-Host "执行命令: $Command" -ForegroundColor Cyan
    Invoke-Expression $Command
} else {
    Write-Host "❌ 没有提供命令" -ForegroundColor Red
    Write-Host "💡 用法: .\scripts\execute_deepseek.ps1 -Command '您的命令'" -ForegroundColor Yellow
}
