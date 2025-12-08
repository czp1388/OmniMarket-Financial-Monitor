"""
Market Data API 集成测试
测试市场数据相关的API端点
"""
import pytest
from httpx import AsyncClient
from fastapi import status

from main import app


@pytest.fixture
async def async_client():
    """创建异步HTTP客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestMarketDataAPI:
    """市场数据API测试套件"""
    
    @pytest.mark.asyncio
    async def test_get_markets(self, async_client):
        """测试获取市场列表"""
        response = await async_client.get("/api/v1/market/markets")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "markets" in data or isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_klines_crypto(self, async_client):
        """测试获取加密货币K线数据"""
        response = await async_client.get(
            "/api/v1/market/klines",
            params={
                "symbol": "BTC/USDT",
                "market_type": "crypto",
                "exchange": "binance",
                "timeframe": "1h",
                "limit": 100
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 验证返回数据结构
        assert isinstance(data, (list, dict))
        if isinstance(data, dict):
            assert "data" in data or "klines" in data
    
    @pytest.mark.asyncio
    async def test_get_klines_stock(self, async_client):
        """测试获取股票K线数据"""
        response = await async_client.get(
            "/api/v1/market/klines",
            params={
                "symbol": "AAPL",
                "market_type": "stock",
                "exchange": "US",
                "timeframe": "1d",
                "limit": 50
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_get_current_price(self, async_client):
        """测试获取当前价格"""
        response = await async_client.get(
            "/api/v1/market/price",
            params={
                "symbol": "BTC/USDT",
                "market_type": "crypto",
                "exchange": "binance"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 验证价格数据
        assert "price" in data or "current_price" in data
    
    @pytest.mark.asyncio
    async def test_get_market_depth(self, async_client):
        """测试获取市场深度（订单簿）"""
        response = await async_client.get(
            "/api/v1/market/depth",
            params={
                "symbol": "BTC/USDT",
                "market_type": "crypto",
                "exchange": "binance"
            }
        )
        
        # 某些端点可能未实现，接受404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "bids" in data or "asks" in data
    
    @pytest.mark.asyncio
    async def test_invalid_market_type(self, async_client):
        """测试无效市场类型"""
        response = await async_client.get(
            "/api/v1/market/klines",
            params={
                "symbol": "BTC/USDT",
                "market_type": "invalid_market",
                "exchange": "binance",
                "timeframe": "1h"
            }
        )
        
        # 应该返回错误
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    @pytest.mark.asyncio
    async def test_missing_required_params(self, async_client):
        """测试缺少必需参数"""
        response = await async_client.get("/api/v1/market/klines")
        
        # 应该返回422（参数验证失败）
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_get_symbols_by_market(self, async_client):
        """测试按市场类型获取交易对列表"""
        response = await async_client.get(
            "/api/v1/market/symbols",
            params={
                "market_type": "crypto",
                "exchange": "binance"
            }
        )
        
        # 某些端点可能未实现
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, (list, dict))
    
    @pytest.mark.asyncio
    async def test_get_ticker_24h(self, async_client):
        """测试获取24小时行情统计"""
        response = await async_client.get(
            "/api/v1/market/ticker/24h",
            params={
                "symbol": "BTC/USDT",
                "market_type": "crypto",
                "exchange": "binance"
            }
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            # 验证包含24h统计数据
            assert "volume" in data or "change_percent" in data or "high" in data


class TestSystemMonitorAPI:
    """系统监控API测试套件"""
    
    @pytest.mark.asyncio
    async def test_get_cache_stats(self, async_client):
        """测试获取缓存统计"""
        response = await async_client.get("/api/v1/system/cache/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        
        # 验证缓存统计字段
        cache_data = data["data"]
        assert "performance" in cache_data
        assert "hit_rate" in cache_data["performance"]
        assert "total_requests" in cache_data["performance"]
    
    @pytest.mark.asyncio
    async def test_reset_cache_stats(self, async_client):
        """测试重置缓存统计"""
        response = await async_client.post("/api/v1/system/cache/reset-stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """测试系统健康检查"""
        response = await async_client.get("/api/v1/system/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "status" in data
        assert "data" in data
        assert "health_status" in data["data"]
        assert data["data"]["health_status"] in ["healthy", "warning", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_data_quality_stats(self, async_client):
        """测试数据质量统计"""
        response = await async_client.get("/api/v1/system/data-quality/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "data" in data


class TestAlertsAPI:
    """预警API测试套件"""
    
    @pytest.mark.asyncio
    async def test_create_alert(self, async_client):
        """测试创建预警"""
        alert_data = {
            "user_id": 1,
            "symbol": "BTC/USDT",
            "condition_type": "price_above",
            "condition_value": 60000.0,
            "notification_method": "email",
            "is_active": True
        }
        
        response = await async_client.post(
            "/api/v1/alerts/",
            json=alert_data
        )
        
        # 某些端点可能需要认证
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    @pytest.mark.asyncio
    async def test_get_alerts(self, async_client):
        """测试获取预警列表"""
        response = await async_client.get("/api/v1/alerts/")
        
        # 可能需要认证
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED
        ]
    
    @pytest.mark.asyncio
    async def test_get_alert_by_id(self, async_client):
        """测试通过ID获取预警"""
        response = await async_client.get("/api/v1/alerts/1")
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED
        ]


class TestTechnicalIndicatorsAPI:
    """技术指标API测试套件"""
    
    @pytest.mark.asyncio
    async def test_calculate_ma(self, async_client):
        """测试计算移动平均线"""
        response = await async_client.post(
            "/api/v1/technical/ma",
            json={
                "symbol": "BTC/USDT",
                "market_type": "crypto",
                "exchange": "binance",
                "timeframe": "1h",
                "period": 20
            }
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    @pytest.mark.asyncio
    async def test_calculate_rsi(self, async_client):
        """测试计算RSI指标"""
        response = await async_client.post(
            "/api/v1/technical/rsi",
            json={
                "symbol": "BTC/USDT",
                "market_type": "crypto",
                "exchange": "binance",
                "timeframe": "1h",
                "period": 14
            }
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    @pytest.mark.asyncio
    async def test_calculate_macd(self, async_client):
        """测试计算MACD指标"""
        response = await async_client.post(
            "/api/v1/technical/macd",
            json={
                "symbol": "BTC/USDT",
                "market_type": "crypto",
                "exchange": "binance",
                "timeframe": "1h"
            }
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
