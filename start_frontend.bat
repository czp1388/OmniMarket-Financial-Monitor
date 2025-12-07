@echo off
echo.
echo ===============================================
echo    启动前端开发服务器
echo ===============================================
echo.
echo 访问地址: http://localhost:3000
echo 助手模式: http://localhost:3000/assistant
echo 专家模式: http://localhost:3000/expert
echo.
echo 按 Ctrl+C 可以停止服务
echo.

cd /d E:\OmniMarket-Financial-Monitor\frontend
call npm run dev

pause
