# 寰宇多市场金融监控系统 - 最终数据库初始化测试
Write-Host "🗃️ 最终数据库初始化测试..." -ForegroundColor Cyan

cd E:\OmniMarket-Financial-Monitor\backend\app

# 创建测试脚本
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
        
        # 检查数据库文件
        db_file = "E:\\OmniMarket-Financial-Monitor\\financial_monitor.db"
        if os.path.exists(db_file):
            file_size = os.path.getsize(db_file)
            print(f"📁 数据库文件: {db_file}")
            print(f"📏 文件大小: {file_size} 字节")
        else:
            print("❌ 数据库文件未找到")
    else:
        print("❌ 数据库初始化失败")

if __name__ == "__main__":
    asyncio.run(init_database())
"@ | Out-File -FilePath "test_database.py" -Encoding utf8

# 运行测试脚本
python test_database.py

# 清理临时文件
Remove-Item "test_database.py" -Force

Write-Host "✅ 数据库初始化测试完成" -ForegroundColor Green
