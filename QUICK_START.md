# 寰宇多市场金融监控系统 - 快速启动指南

## 🚀 一键启动（推荐）
.\global_tool.ps1 start     # 启动服务
.\global_tool.ps1 test      # 测试API
.\global_tool.ps1 docs      # 打开文档

## 📊 系统监控
.\system_monitor.ps1        # 查看系统状态
.\system_monitor.ps1 monitor # 实时监控模式

## 🔧 问题诊断
.\global_tool.ps1 diagnose  # 完整诊断
.\diagnostic_tool.ps1 all   # 基础诊断

## 📋 状态管理
.\project_status.ps1 status # 查看项目状态
.\new_window.ps1           # 新窗口快速开始

## 🌐 API测试端点
http://localhost:8000/              # 根路径
http://localhost:8000/health        # 健康检查
http://localhost:8000/api/v1/exchanges # 交易所列表
http://localhost:8000/api/v1/prices/?symbol=BTC/USDT # BTC价格
http://localhost:8000/docs          # API文档

## 💡 故障排除
1. 服务未运行? -> .\global_tool.ps1 start
2. API测试失败? -> 检查网络连接，稍后重试
3. 脚本找不到? -> 确保在项目根目录运行
4. 依赖问题? -> cd backend; pip install -r requirements_simple.txt
