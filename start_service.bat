@echo off
chcp 65001 > nul
title 寰宇多市场金融监控系统 - 专业版

echo ========================================
echo   寰宇多市场金融监控系统 - 专业版 v2.4.1
echo ========================================
echo.
echo 启动服务中...

cd /d E:\OmniMarket-Financial-Monitor\backend\app

:: 检查Python是否可用
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python未找到，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

:: 启动服务
echo 🚀 启动稳定的服务...
python stable_runner.py

if errorlevel 1 (
    echo ❌ 服务启动失败
    echo 💡 请检查错误信息并确保所有依赖已安装
    pause
) else (
    echo ✅ 服务已正常退出
)

pause
