# 寰宇多市场金融监控系统 - 自主状态管理器
param([string]$Action = "status")

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$StatusFile = "$ProjectRoot\project_status.md"
$BackupDir = "$ProjectRoot\status_backups"

function Update-Status {
    # 创建备份目录
    if (!(Test-Path $BackupDir)) { 
        New-Item -ItemType Directory -Path $BackupDir -Force 
    }
    
    # 备份旧状态
    if (Test-Path $StatusFile) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item $StatusFile "$BackupDir\status_$timestamp.md"
    }
    
    # 获取Git状态
    $gitStatus = "无Git提交历史"
    try {
        $gitResult = git log --oneline -1 2>$null
        if ($gitResult) { $gitStatus = $gitResult }
    } catch {
        $gitStatus = "Git不可用"
    }
    
    # 获取项目结构
    $projectTree = "无法生成目录树"
    try {
        $treeResult = cmd /c "tree /F /A 2>nul"
        if ($treeResult) { $projectTree = $treeResult }
    } catch {
        # 使用备用方法
        $projectTree = "使用备用目录列表"
    }
    
    # 生成新状态
    $statusContent = @"
# 寰宇多市场金融监控系统 - 状态快照
# 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# Git状态: $gitStatus

## 🏗️ 项目结构
$projectTree

## 🔧 服务状态
**后端服务:** $(if (Get-Process -Name "python" -ErrorAction SilentlyContinue) { "✅ 运行中" } else { "❌ 未运行" })
**服务地址:** http://localhost:8000

## 📊 关键文件
$(Get-ChildItem -Recurse -Include *.py,*.ps1,*.md,*.json,*.txt | ForEach-Object { "- $($_.Name) (修改: $($_.LastWriteTime.ToString('MM/dd HH:mm')))" })

## 🚀 下一步操作
1. 启动服务: cd backend\app; python main.py
2. 测试API: http://localhost:8000/health
3. 查看文档: http://localhost:8000/docs

## 💾 恢复命令
cd E:\OmniMarket-Financial-Monitor
.\project_status.ps1 status
"@
    
    $statusContent | Out-File -FilePath $StatusFile -Encoding utf8
    Write-Host "✅ 状态已更新: $StatusFile" -ForegroundColor Green
}

function Show-Status {
    if (Test-Path $StatusFile) {
        Write-Host "📋 当前项目状态:" -ForegroundColor Cyan
        Get-Content $StatusFile
    } else {
        Write-Host "❌ 状态文件不存在，正在创建..." -ForegroundColor Yellow
        Update-Status
    }
}

# 执行动作
switch ($Action) {
    "update" { Update-Status }
    "status" { Show-Status }
    default { Show-Status }
}
