# 数据库管理器
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        
    def set_engine(self, engine):
        """设置数据库引擎"""
        self.engine = engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("✅ 数据库引擎设置成功")
    
    def get_db(self):
        """获取数据库会话"""
        if not self.SessionLocal:
            raise Exception("数据库会话未初始化")
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("✅ 数据库连接已关闭")

# 创建全局数据库管理器实例
db_manager = DatabaseManager()
