# 启动前端开发服务器
Write-Host "`n=== 启动前端开发服务器 ===" -ForegroundColor Green
Write-Host "访问地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "助手模式: http://localhost:3000/assistant" -ForegroundColor Cyan
Write-Host "专家模式: http://localhost:3000/expert`n" -ForegroundColor Cyan

Set-Location E:\OmniMarket-Financial-Monitor\frontend

# 启动 Vite 开发服务器
npm run dev
