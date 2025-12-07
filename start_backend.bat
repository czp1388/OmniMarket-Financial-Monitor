@echo off
echo.
echo ===============================================
echo    启动后端 API 服务
echo ===============================================
echo.
echo API 地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 可以停止服务
echo.

cd /d E:\OmniMarket-Financial-Monitor\backend
call ..\.venv\Scripts\python.exe main_simple.py

pause
