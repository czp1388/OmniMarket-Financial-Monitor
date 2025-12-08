"""
Pytest 配置文件
定义全局 fixtures 和测试配置
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock
import sys
from pathlib import Path

# 添加backend目录到 Python 路径
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from models.market_data import KlineData, MarketType, Timeframe
from config import settings


# ============================================
# Pytest 配置
# ============================================

def pytest_configure(config):
    """配置 pytest"""
    # 注册自定义标记
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "slow: 慢速测试")


# ============================================
# 事件循环 Fixture
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================
# 数据库 Fixtures
# ============================================

@pytest.fixture
def mock_postgres_db():
    """模拟 PostgreSQL 数据库连接"""
    db = Mock()
    db.execute = AsyncMock()
    db.fetch = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


@pytest.fixture
def mock_influxdb():
    """模拟 InfluxDB 连接"""
    client = Mock()
    write_api = Mock()
    query_api = Mock()
    
    write_api.write = Mock()
    query_api.query = Mock(return_value=[])
    
    return client, write_api, query_api


@pytest.fixture
def mock_redis():
    """模拟 Redis 连接"""
    redis = Mock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.exists = AsyncMock(return_value=False)
    redis.expire = AsyncMock()
    return redis


# ============================================
# 服务 Fixtures
# ============================================

@pytest.fixture
def mock_data_service():
    """模拟数据服务"""
    service = Mock()
    service.get_klines = AsyncMock()
    service.get_quote = AsyncMock()
    return service


@pytest.fixture
def mock_alert_service():
    """模拟预警服务"""
    service = Mock()
    service.create_alert = AsyncMock()
    service.get_alerts = AsyncMock(return_value=[])
    service.update_alert = AsyncMock()
    service.delete_alert = AsyncMock()
    service.test_condition = AsyncMock(return_value={"triggered": False})
    return service


@pytest.fixture
def mock_websocket_manager():
    """模拟 WebSocket 管理器"""
    manager = Mock()
    manager.register = AsyncMock()
    manager.unregister = AsyncMock()
    manager.subscribe = AsyncMock()
    manager.unsubscribe = AsyncMock()
    manager.broadcast_to_subscribers = AsyncMock()
    return manager


# ============================================
# 外部 API Fixtures
# ============================================

@pytest.fixture
def mock_coingecko():
    """模拟 CoinGecko API"""
    mock = Mock()
    mock.get_crypto_klines = AsyncMock(return_value=[
        KlineData(
            symbol="BTC/USDT",
            timeframe=Timeframe.H1,
            market_type=MarketType.CRYPTO,
            timestamp="2024-01-01T00:00:00Z",
            open=42000.0,
            high=42500.0,
            low=41800.0,
            close=42300.0,
            volume=1234.56
        )
    ])
    return mock


@pytest.fixture
def mock_alpha_vantage():
    """模拟 Alpha Vantage API"""
    mock = Mock()
    mock.get_stock_klines = AsyncMock(return_value=[])
    mock.get_crypto_klines = AsyncMock(return_value=[])
    mock.get_forex_klines = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_yfinance():
    """模拟 yfinance API"""
    mock = Mock()
    mock.get_stock_klines = AsyncMock(return_value=[])
    mock.get_stock_quote = AsyncMock(return_value={
        "symbol": "AAPL",
        "price": 150.0,
        "change": 2.5,
        "change_percent": 1.69
    })
    return mock


# ============================================
# 测试数据 Fixtures
# ============================================

@pytest.fixture
def sample_kline_data():
    """示例 K 线数据"""
    return [
        KlineData(
            symbol="BTC/USDT",
            timeframe=Timeframe.H1,
            market_type=MarketType.CRYPTO,
            timestamp="2024-01-01T00:00:00Z",
            open=42000.0,
            high=42500.0,
            low=41800.0,
            close=42300.0,
            volume=1234.56
        ),
        KlineData(
            symbol="BTC/USDT",
            timeframe=Timeframe.H1,
            market_type=MarketType.CRYPTO,
            timestamp="2024-01-01T01:00:00Z",
            open=42300.0,
            high=42800.0,
            low=42100.0,
            close=42600.0,
            volume=1456.78
        )
    ]


@pytest.fixture
def sample_alert_config():
    """示例预警配置"""
    from models.alerts import AlertStatus
    return {
        "name": "BTC 价格预警",
        "symbol": "BTC/USDT",
        "market_type": "CRYPTO",
        "condition_type": "PRICE_ABOVE",
        "condition_config": {
            "target_price": 45000.0
        },
        "notification_types": ["in_app", "email"],
        "status": AlertStatus.ACTIVE
    }


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture
def sample_virtual_order():
    """示例虚拟订单"""
    return {
        "account_id": "va_123",
        "symbol": "BTC/USDT",
        "order_type": "LIMIT",
        "side": "BUY",
        "quantity": 0.1,
        "price": 42000.0
    }


# ============================================
# API Client Fixtures
# ============================================

@pytest.fixture
async def async_client():
    """异步 HTTP 客户端"""
    from httpx import AsyncClient
    from main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers():
    """认证请求头"""
    return {
        "Authorization": "Bearer test_token_here"
    }


# ============================================
# 环境配置 Fixtures
# ============================================

@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """测试环境配置（自动应用）"""
    # 使用测试数据库
    monkeypatch.setattr(settings, "DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setattr(settings, "DEBUG", True)
    
    # 禁用外部 API 调用
    monkeypatch.setattr(settings, "BINANCE_API_KEY", "")
    monkeypatch.setattr(settings, "ALPHA_VANTAGE_API_KEY", "")
    
    return settings


# ============================================
# 清理 Fixtures
# ============================================

@pytest.fixture(autouse=True)
async def cleanup():
    """测试后清理"""
    yield
    # 在这里添加清理逻辑
    # 例如：清理测试数据库、关闭连接等
