# 启动简化版后端服务
Write-Host "`n=== 启动后端 API 服务 ===" -ForegroundColor Green
Write-Host "API 地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API 文档: http://localhost:8000/docs`n" -ForegroundColor Cyan

Set-Location E:\OmniMarket-Financial-Monitor\backend

# 启动 FastAPI 服务
..\.venv\Scripts\python.exe main_simple.py
