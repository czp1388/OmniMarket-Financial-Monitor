import logging
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import redis
import asyncio
import time

from config import settings

logger = logging.getLogger(__name__)

# 优化的SQLAlchemy配置
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,              # 常驻连接数
    max_overflow=20,           # 最大溢出连接
    pool_timeout=30,           # 获取连接超时（秒）
    pool_recycle=3600,         # 连接回收时间（1小时）
    pool_pre_ping=True,        # 使用前测试连接
    echo=False,                # 生产环境不打印SQL
    connect_args={
        "connect_timeout": 10
    }
)

# 监听连接池事件（性能监控）
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    connection_record.info['connect_time'] = time.time()
    logger.debug(f"新建数据库连接: {id(dbapi_conn)}")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    connection_record.info['checkout_time'] = time.time()

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    checkout_time = connection_record.info.get('checkout_time')
    if checkout_time:
        duration = time.time() - checkout_time
        if duration > 1.0:
            logger.warning(f"长时间占用连接: {duration:.2f}秒")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# InfluxDB客户端
influx_client = None
influx_write_api = None
influx_query_api = None

# Redis客户端
redis_client = None

async def init_db():
    """初始化数据库连接"""
    global influx_client, influx_write_api, influx_query_api, redis_client
    
    try:
        # 初始化InfluxDB
        influx_client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        influx_query_api = influx_client.query_api()
        logger.info("InfluxDB连接成功")
        
    except Exception as e:
        logger.warning(f"InfluxDB连接失败: {e}。服务将继续运行，但时序数据功能不可用。")
        influx_client = None
        influx_write_api = None
        influx_query_api = None
    
    try:
        # 初始化Redis
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()  # 测试连接
        logger.info("Redis连接成功")
        
    except Exception as e:
        logger.warning(f"Redis连接失败: {e}。服务将继续运行，但缓存功能不可用。")
        redis_client = None

# 数据库会话依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_influxdb():
    return influx_client, influx_write_api, influx_query_api

def get_redis():
    return redis_client

# 数据模型基类
class MarketDataBase:
    """市场数据基类"""
    
    @classmethod
    def create_table_if_not_exists(cls):
        """创建表（如果不存在）"""
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logger.error(f"创建表失败: {e}")

# 创建所有表
async def create_tables():
    """创建所有数据库表"""
    try:
        # 延迟导入所有模型以避免循环导入
        from models.market_data import MarketData, KlineData
        from models.alerts import Alert
        from models.users import User
        
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")
