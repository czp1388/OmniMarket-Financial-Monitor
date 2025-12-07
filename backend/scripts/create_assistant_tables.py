"""
创建助手模式相关数据库表
运行: python backend/scripts/create_assistant_tables.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database import Base, engine
from backend.models.assistant import StrategyInstance, ExecutionHistory, SimpleReport
from backend.models.users import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """创建所有助手模式相关表"""
    try:
        logger.info("开始创建助手模式数据库表...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ 数据库表创建成功！")
        logger.info("创建的表：")
        logger.info("  - strategy_instances (策略实例)")
        logger.info("  - execution_history (执行历史)")
        logger.info("  - simple_reports (简化报告)")
        
    except Exception as e:
        logger.error(f"❌ 创建表失败: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    create_tables()
