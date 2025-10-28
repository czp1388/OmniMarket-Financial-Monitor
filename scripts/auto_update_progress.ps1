param(
    [string]$CurrentTask,
    [string]$Completed,
    [string]$NextStep, 
    [string]$Remarks
)

Write-Host "🤖 自动更新开发进度..." -ForegroundColor Green

$newProgress = @"
📋 OmniMarket 开发进度记录

🎯 当前任务：$CurrentTask
✅ 已完成：$Completed
🔧 下一步：$NextStep
💡 重要提醒：$Remarks

最近更新：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

$newProgress | Set-Content "..\progress.txt" -Encoding utf8
Write-Host "✅ 进度已自动更新" -ForegroundColor Green

Write-Host "`n📋 更新后的进度：" -ForegroundColor Cyan
Get-Content "..\progress.txt"
