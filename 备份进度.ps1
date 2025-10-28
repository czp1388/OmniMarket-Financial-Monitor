# 💾 一键备份开发进度

Write-Host "=== 备份开发进度 ===" -ForegroundColor Cyan

# 步骤1: 切换到项目目录
Write-Host "`n1. 切换到项目目录..." -ForegroundColor Yellow
cd E:\OmniMarket-Financial-Monitor

# 步骤2: 备份到Git
Write-Host "`n2. 备份到Git..." -ForegroundColor Green
.\scripts\git_backup.ps1

# 步骤3: 显示备份结果
Write-Host "`n✅ 备份完成！" -ForegroundColor Green
Write-Host "💡 下次开发时运行: .\开始开发.ps1" -ForegroundColor Yellow

Write-Host "`n🎯 给DeepSeek的话术:" -ForegroundColor Magenta
Write-Host "开发进度已备份。请更新 现在在做什么.txt 文件记录下一步计划。" -ForegroundColor White
