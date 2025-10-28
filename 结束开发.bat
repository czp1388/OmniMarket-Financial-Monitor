@echo off
cd /d E:\OmniMarket-Financial-Monitor
echo ========================================
echo    OmniMarket 开发结束 - 自动备份
echo ========================================
echo.
echo 正在执行自动备份...
powershell -ExecutionPolicy Bypass -File "scripts\auto_backup.ps1" -BackupMessage "开发会话结束备份"
echo.
echo ========================================
echo   备份完成！下次运行 终极开发.bat 继续
echo ========================================
echo.
pause
