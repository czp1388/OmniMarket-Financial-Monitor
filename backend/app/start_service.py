import uvicorn
import sys
import os
import time

# 添加当前目录到Python路径
sys.path.append(os.getcwd())

def main():
    try:
        print("🚀 启动寰宇多市场金融监控系统...")
        print(f"📁 工作目录: {os.getcwd()}")
        print(f"🐍 Python路径: {sys.executable}")
        
        # 检查必要模块
        try:
            from main_pro_fixed import app
            print("✅ FastAPI应用导入成功")
        except Exception as e:
            print(f"❌ FastAPI应用导入失败: {e}")
            input("按Enter键退出...")
            return
        
        # 启动服务
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")

if __name__ == "__main__":
    main()
