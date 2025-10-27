# 寰宇多市场金融监控系统 - 数据库初始化脚本（修复版）
Write-Host "🗃️ 初始化数据库..." -ForegroundColor Cyan

cd E:\OmniMarket-Financial-Monitor\backend\app

# 创建正确的测试脚本来初始化数据库
@"
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.database_service import database_service

async def init_database():
    print("🔧 初始化数据库...")
    
    # 初始化数据库服务
    await database_service.initialize()
    
    if database_service.is_initialized:
        print("✅ 数据库初始化成功")
        
        # 测试数据库连接
        if database_service.test_connection():
            print("✅ 数据库连接测试成功")
        else:
            print("❌ 数据库连接测试失败")
            
        # 显示数据库统计
        stats = database_service.get_database_stats()
        print(f"📊 数据库统计:")
        print(f"   预警规则: {stats['alert_rules_count']}")
        print(f"   预警历史: {stats['alert_history_count']}")
        print(f"   市场数据: {stats['market_data_count']}")
        print(f"   系统配置: {stats['system_config_count']}")
    else:
        print("❌ 数据库初始化失败")

if __name__ == "__main__":
    asyncio.run(init_database())
"@ | Out-File -FilePath "init_database.py" -Encoding utf8

# 运行初始化脚本
python init_database.py

# 清理临时文件
Remove-Item "init_database.py" -Force

Write-Host "✅ 数据库初始化完成" -ForegroundColor Green
