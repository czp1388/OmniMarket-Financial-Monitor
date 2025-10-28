# 生成给DeepSeek的智能话术 - 包含备份提醒
Write-Host "🤖 生成智能DeepSeek话术..." -ForegroundColor Magenta

# 读取当前进度
if (Test-Path "progress.txt") {
    $progress = Get-Content "progress.txt" -Raw
} else {
    $progress = "进度文件不存在，请先运行自动开发系统"
}

# 从进度中提取当前任务
$currentTask = "未知任务"
if ($progress -match "🎯 当前任务：(.*)") {
    $currentTask = $matches[1].Trim()
}

# 生成智能话术
$smartMessage = @"
🎯 项目状态同步 - OmniMarket金融监控系统

## 📊 当前开发状态：
$progress

## 🚀 请协助我：
1. 基于上面的进度继续开发
2. 告诉我需要运行什么命令
3. 帮我更新开发进度

## 💡 重要上下文：
- 我正在使用全自动开发模式
- 您只需要告诉我命令，我会自动执行
- 项目路径：E:\OmniMarket-Financial-Monitor
- 已配置的脚本：启动服务、测试API、更新进度、Git备份

## 🔄 开发连续性保障：
- 开始开发：双击桌面上的"开始开发.bat"
- 结束开发：双击桌面上的"结束开发.bat"（自动备份）

请基于当前任务"$currentTask"，告诉我下一步具体要运行什么命令。
"@

Write-Host "💬 复制下面这段话给DeepSeek：" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host $smartMessage -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n📋 这个话术包含：" -ForegroundColor Yellow
Write-Host "  ✅ 完整项目状态" -ForegroundColor Green
Write-Host "  ✅ 明确的操作指引" -ForegroundColor Green  
Write-Host "  ✅ 开发上下文信息" -ForegroundColor Green
Write-Host "  ✅ 具体的技术任务: $currentTask" -ForegroundColor Green
Write-Host "  ✅ 自动备份提醒" -ForegroundColor Green
