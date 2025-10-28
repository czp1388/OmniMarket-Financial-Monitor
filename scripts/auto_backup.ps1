# 智能自动备份系统
param(
    [string]$BackupMessage = "自动备份开发进度"
)

Write-Host "💾 执行智能自动备份..." -ForegroundColor Magenta

# 1. 更新进度文件时间戳
if (Test-Path "progress.txt") {
    $progress = Get-Content "progress.txt" -Raw
    $updatedProgress = $progress -replace "最近更新：.*", "最近更新：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $updatedProgress | Set-Content "progress.txt" -Encoding utf8
}

# 2. 执行Git备份
Write-Host "1. 备份到Git..." -ForegroundColor Yellow
.\scripts\backup_to_git.ps1

# 3. 创建备份快照
$backupFile = "backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
if (!(Test-Path "backups")) {
    New-Item -ItemType Directory -Path "backups" -Force
}

@"
📋 开发备份快照
备份时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
备份说明: $BackupMessage

当前进度:
$(if (Test-Path "progress.txt") { Get-Content "progress.txt" } else { "无进度文件" })

项目状态:
$(git status --short 2>$null)

最近提交:
$(git log --oneline -3 2>$null)
"@ | Set-Content $backupFile -Encoding utf8

Write-Host "2. 创建备份快照: $backupFile" -ForegroundColor Yellow

# 4. 显示备份结果
Write-Host "`n✅ 自动备份完成！" -ForegroundColor Green
Write-Host "📁 备份位置: $backupFile" -ForegroundColor Cyan
Write-Host "💡 下次开发时运行: .\终极开发.bat" -ForegroundColor Yellow

# 5. 显示最近备份
Write-Host "`n📅 最近备份文件:" -ForegroundColor Cyan
Get-ChildItem "backups\*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 3 Name, LastWriteTime | Format-Table -AutoSize
