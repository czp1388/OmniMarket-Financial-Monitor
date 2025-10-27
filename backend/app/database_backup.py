# 寰宇多市场金融监控系统 - 数据库模型
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# 数据库配置 - 使用绝对路径
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./financial_monitor.db')

# 如果是SQLite，确保使用绝对路径
if DATABASE_URL.startswith('sqlite'):
    # 获取项目根目录的绝对路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'financial_monitor.db')
    DATABASE_URL = f'sqlite:///{db_path}'

logger.info(f"📁 数据库路径: {DATABASE_URL}")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class AlertRule(Base):
    """预警规则表"""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, default=0)  # 0表示系统规则
    symbol = Column(String(50), nullable=False, index=True)
    condition = Column(String(20), nullable=False)  # above, below, change_up, change_down
    threshold = Column(Float, nullable=False)
    notification_type = Column(String(20), default="log")  # log, console, email, telegram, all
    email_recipients = Column(JSON, default=[])  # 存储邮箱列表
    telegram_chat_ids = Column(JSON, default=[])  # 存储Telegram聊天ID列表
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AlertHistory(Base):
    """预警历史表"""
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, index=True, nullable=False)
    symbol = Column(String(50), nullable=False, index=True)
    condition = Column(String(20), nullable=False)
    threshold = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    previous_price = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(20), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketData(Base):
    """市场数据缓存表"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    change_24h = Column(Float)
    volume_24h = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow, index=True)

# 数据库工具类
class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def init_db(self):
        """初始化数据库，创建所有表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ 数据库表创建成功")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            return False

    def get_db(self):
        """获取数据库会话"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def test_connection(self):
        """测试数据库连接"""
        try:
            db = self.SessionLocal()
            db.execute("SELECT 1")
            db.close()
            logger.info("✅ 数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接测试失败: {e}")
            return False

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

