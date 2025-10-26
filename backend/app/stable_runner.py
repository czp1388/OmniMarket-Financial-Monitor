import asyncio
import logging
import sys
import os
import signal

# 添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_pro import app
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('service.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """处理退出信号"""
    logger.info("收到关闭信号，正在优雅关闭服务...")
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("🚀 启动稳定的寰宇多市场金融监控系统服务...")
        print("=" * 60)
        print("🚀 寰宇多市场金融监控系统 - 稳定版 v2.4.1")
        print("📊 服务运行在: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs") 
        print("🔗 实时数据: ws://localhost:8000/ws/realtime")
        print("🌐 Web界面: http://localhost:8000/")
        print("💎 数据源: 真实交易所 + 模拟数据")
        print("=" * 60)
        
        # 启动服务
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
            reload=False  # 生产环境关闭热重载
        )
        
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)
