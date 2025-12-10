"""
数据库优化工具模块
提供连接池管理、批量操作、索引优化等功能
"""
import logging
from typing import List, Dict, Any, Optional, TypeVar, Generic
from contextlib import contextmanager
from sqlalchemy import create_engine, event, Index, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.engine import Engine
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================
# 连接池优化配置
# ============================================

def create_optimized_engine(
    database_url: str,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
    echo: bool = False,
    pool_pre_ping: bool = True
) -> Engine:
    """
    创建优化的数据库引擎
    
    参数:
        pool_size: 连接池大小（常驻连接数）
        max_overflow: 最大溢出连接数
        pool_timeout: 获取连接超时时间（秒）
        pool_recycle: 连接回收时间（秒），防止MySQL 8小时超时
        echo: 是否打印SQL语句
        pool_pre_ping: 使用前测试连接有效性
    """
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=pool_pre_ping,
        echo=echo,
        echo_pool=False,  # 不打印连接池日志
        # 性能优化
        connect_args={
            "connect_timeout": 10,
            # PostgreSQL特定
            # "options": "-c statement_timeout=30000"  # 30秒查询超时
        }
    )
    
    # 监听连接事件
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """连接建立时的回调"""
        connection_record.info['connect_time'] = time.time()
        logger.debug(f"新建数据库连接: {id(dbapi_conn)}")
    
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """连接检出时的回调"""
        connection_record.info['checkout_time'] = time.time()
    
    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_conn, connection_record):
        """连接归还时的回调"""
        checkout_time = connection_record.info.get('checkout_time')
        if checkout_time:
            duration = time.time() - checkout_time
            if duration > 1.0:  # 超过1秒的查询记录警告
                logger.warning(f"长时间占用连接: {duration:.2f}秒")
    
    logger.info(f"数据库引擎创建成功 - pool_size={pool_size}, max_overflow={max_overflow}")
    
    return engine


# ============================================
# 批量操作工具
# ============================================

class BatchOperator(Generic[T]):
    """批量操作工具类"""
    
    def __init__(self, session: Session, batch_size: int = 1000):
        self.session = session
        self.batch_size = batch_size
        self.buffer: List[T] = []
    
    def add(self, item: T):
        """添加项到批量缓冲区"""
        self.buffer.append(item)
        
        if len(self.buffer) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """刷新缓冲区，执行批量插入"""
        if not self.buffer:
            return
        
        try:
            self.session.bulk_save_objects(self.buffer)
            self.session.commit()
            count = len(self.buffer)
            self.buffer.clear()
            logger.debug(f"批量插入 {count} 条记录")
        except Exception as e:
            self.session.rollback()
            logger.error(f"批量插入失败: {e}")
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.flush()
        else:
            self.session.rollback()


def bulk_insert_mappings(
    session: Session,
    model_class: type,
    mappings: List[Dict[str, Any]],
    batch_size: int = 1000
) -> int:
    """
    批量插入字典数据（性能更优）
    
    返回:
        插入的记录数
    """
    total = 0
    
    try:
        for i in range(0, len(mappings), batch_size):
            batch = mappings[i:i + batch_size]
            session.bulk_insert_mappings(model_class, batch)
            session.commit()
            total += len(batch)
            logger.debug(f"批量插入 {len(batch)} 条记录 (总计: {total}/{len(mappings)})")
        
        logger.info(f"批量插入完成: {total} 条记录")
        return total
        
    except Exception as e:
        session.rollback()
        logger.error(f"批量插入失败: {e}")
        raise


def bulk_update_mappings(
    session: Session,
    model_class: type,
    mappings: List[Dict[str, Any]],
    batch_size: int = 1000
) -> int:
    """
    批量更新字典数据
    
    注意: mappings中必须包含主键字段
    """
    total = 0
    
    try:
        for i in range(0, len(mappings), batch_size):
            batch = mappings[i:i + batch_size]
            session.bulk_update_mappings(model_class, batch)
            session.commit()
            total += len(batch)
            logger.debug(f"批量更新 {len(batch)} 条记录 (总计: {total}/{len(mappings)})")
        
        logger.info(f"批量更新完成: {total} 条记录")
        return total
        
    except Exception as e:
        session.rollback()
        logger.error(f"批量更新失败: {e}")
        raise


# ============================================
# 索引管理
# ============================================

class IndexManager:
    """索引管理器"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def create_index(
        self,
        table_name: str,
        index_name: str,
        columns: List[str],
        unique: bool = False
    ):
        """创建索引"""
        try:
            unique_str = "UNIQUE " if unique else ""
            columns_str = ", ".join(columns)
            
            with self.engine.connect() as conn:
                conn.execute(text(
                    f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} "
                    f"ON {table_name} ({columns_str})"
                ))
                conn.commit()
            
            logger.info(f"索引创建成功: {index_name} on {table_name}({columns_str})")
            
        except Exception as e:
            logger.error(f"索引创建失败: {e}")
            raise
    
    def drop_index(self, index_name: str):
        """删除索引"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
                conn.commit()
            
            logger.info(f"索引删除成功: {index_name}")
            
        except Exception as e:
            logger.error(f"索引删除失败: {e}")
            raise
    
    def list_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """列出表的所有索引"""
        try:
            with self.engine.connect() as conn:
                # PostgreSQL查询
                result = conn.execute(text("""
                    SELECT 
                        indexname as name,
                        indexdef as definition
                    FROM pg_indexes
                    WHERE tablename = :table_name
                """), {"table_name": table_name})
                
                indexes = [dict(row) for row in result]
                return indexes
                
        except Exception as e:
            logger.error(f"查询索引失败: {e}")
            return []
    
    def analyze_table(self, table_name: str):
        """分析表统计信息（优化查询计划）"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"ANALYZE {table_name}"))
                conn.commit()
            
            logger.info(f"表分析完成: {table_name}")
            
        except Exception as e:
            logger.error(f"表分析失败: {e}")


# ============================================
# 查询优化工具
# ============================================

@contextmanager
def query_timer(query_name: str, slow_threshold: float = 1.0):
    """
    查询计时器上下文管理器
    
    用法:
        with query_timer("获取用户列表"):
            users = session.query(User).all()
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        if duration > slow_threshold:
            logger.warning(f"慢查询 [{query_name}]: {duration:.3f}秒")
        else:
            logger.debug(f"查询 [{query_name}]: {duration:.3f}秒")


def paginate_query(
    query,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    分页查询
    
    返回:
        {
            'items': [...],
            'total': 100,
            'page': 1,
            'page_size': 20,
            'total_pages': 5
        }
    """
    # 限制page_size
    page_size = min(page_size, max_page_size)
    
    # 计算总数（优化：使用count()而非len()）
    total = query.count()
    
    # 计算分页
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }


class LazyQuery:
    """懒加载查询（仅在需要时执行）"""
    
    def __init__(self, query):
        self.query = query
        self._result = None
        self._executed = False
    
    def execute(self):
        """执行查询"""
        if not self._executed:
            with query_timer("LazyQuery"):
                self._result = self.query.all()
                self._executed = True
        return self._result
    
    def __iter__(self):
        return iter(self.execute())
    
    def __len__(self):
        return len(self.execute())


# ============================================
# 连接池监控
# ============================================

class PoolMonitor:
    """连接池监控器"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def get_pool_status(self) -> Dict[str, Any]:
        """获取连接池状态"""
        pool = self.engine.pool
        
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'total_connections': pool.size() + pool.overflow(),
        }
    
    def log_pool_status(self):
        """记录连接池状态"""
        status = self.get_pool_status()
        logger.info(
            f"连接池状态 - "
            f"总连接: {status['total_connections']}, "
            f"使用中: {status['checked_out']}, "
            f"空闲: {status['checked_in']}, "
            f"溢出: {status['overflow']}"
        )


# ============================================
# 推荐的索引配置
# ============================================

RECOMMENDED_INDEXES = {
    'alerts': [
        ('idx_alerts_user_id', ['user_id']),
        ('idx_alerts_status', ['status']),
        ('idx_alerts_symbol', ['symbol']),
        ('idx_alerts_user_status', ['user_id', 'status']),
        ('idx_alerts_created_at', ['created_at']),
    ],
    'alert_triggers': [
        ('idx_triggers_alert_id', ['alert_id']),
        ('idx_triggers_triggered_at', ['triggered_at']),
    ],
    'users': [
        ('idx_users_email', ['email'], True),  # unique
        ('idx_users_username', ['username'], True),  # unique
    ],
    'virtual_trades': [
        ('idx_trades_user_id', ['user_id']),
        ('idx_trades_symbol', ['symbol']),
        ('idx_trades_created_at', ['created_at']),
        ('idx_trades_user_symbol', ['user_id', 'symbol']),
    ],
}


def create_recommended_indexes(engine: Engine):
    """创建推荐的索引"""
    manager = IndexManager(engine)
    
    for table_name, indexes in RECOMMENDED_INDEXES.items():
        for index_config in indexes:
            index_name = index_config[0]
            columns = index_config[1]
            unique = index_config[2] if len(index_config) > 2 else False
            
            try:
                manager.create_index(table_name, index_name, columns, unique)
            except Exception as e:
                logger.warning(f"索引创建失败（可能已存在）: {index_name} - {e}")
