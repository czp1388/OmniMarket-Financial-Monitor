@echo off
cd /d E:\OmniMarket-Financial-Monitor
echo ========================================
echo    OmniMarket 终极一键开发系统
echo ========================================
echo.
echo [1] 自动修复所有问题...
powershell -ExecutionPolicy Bypass -File "scripts\auto_fix.ps1" -FixType all
echo.
echo [2] 启动开发环境...
powershell -ExecutionPolicy Bypass -File "scripts\start_service.ps1"
echo.
echo [3] 生成智能DeepSeek话术...
powershell -ExecutionPolicy Bypass -File "scripts\generate_deepseek_message.ps1"
echo.
echo ========================================
echo   复制上面的话术给DeepSeek即可！
echo ========================================
echo.
pause
