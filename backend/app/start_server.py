import uvicorn
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.getcwd())

try:
    print("🚀 启动寰宇多市场金融监控系统...")
    uvicorn.run(
        "main_pro:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    input("按Enter键退出...")
