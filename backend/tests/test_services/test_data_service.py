"""
测试 DataService 数据服务
包含数据源降级、缓存策略、K线数据获取等功能的测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from services.data_service import DataService
from models.market_data import KlineData, MarketType, Timeframe


class TestDataService:
    """DataService 测试类"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_klines_from_cache(self, mock_redis, sample_kline_data):
        """测试从缓存获取 K 线数据"""
        # 模拟缓存命中
        with patch('backend.services.data_service.data_cache_service') as mock_cache:
            mock_cache.get = AsyncMock(return_value=sample_kline_data)
            
            service = DataService()
            result = await service.get_klines(
                symbol="BTC/USDT",
                market_type=MarketType.CRYPTO,
                exchange="binance",
                timeframe=Timeframe.H1,
                limit=100
            )
            
            assert result == sample_kline_data
            mock_cache.get.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_klines_crypto_fallback_chain(self):
        """测试加密货币数据源降级链"""
        service = DataService()
        
        # 模拟所有数据源失败，最终使用模拟数据
        with patch('backend.services.data_service.coingecko_service') as mock_coingecko, \
             patch('backend.services.data_service.alpha_vantage_service') as mock_av, \
             patch('backend.services.data_service.data_cache_service') as mock_cache:
            
            # 模拟缓存未命中
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            
            # 模拟 CoinGecko 失败
            mock_coingecko.get_crypto_klines = AsyncMock(side_effect=Exception("CoinGecko error"))
            
            # 模拟 Alpha Vantage 失败
            mock_av.get_crypto_klines = AsyncMock(side_effect=Exception("AV error"))
            
            # 执行测试
            result = await service.get_klines(
                symbol="BTC/USDT",
                market_type=MarketType.CRYPTO,
                exchange="binance",
                timeframe=Timeframe.H1,
                limit=10
            )
            
            # 验证返回了模拟数据（降级到最后）
            assert len(result) > 0
            assert result[0].symbol == "BTC/USDT"
            assert result[0].market_type == MarketType.CRYPTO
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_klines_stock_success(self):
        """测试成功获取股票 K 线数据"""
        service = DataService()
        
        with patch('backend.services.data_service.alpha_vantage_service') as mock_av, \
             patch('backend.services.data_service.data_cache_service') as mock_cache:
            
            # 模拟缓存未命中
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            
            # 模拟 Alpha Vantage 成功返回数据
            mock_data = [
                KlineData(
                    symbol="AAPL",
                    timeframe=Timeframe.D1,
                    market_type=MarketType.STOCK,
                    timestamp=datetime.now(),
                    open=150.0,
                    high=152.0,
                    low=149.0,
                    close=151.0,
                    volume=1000000.0
                )
            ]
            mock_av.get_stock_klines = AsyncMock(return_value=mock_data)
            
            # 执行测试
            result = await service.get_klines(
                symbol="AAPL",
                market_type=MarketType.STOCK,
                exchange="nasdaq",
                timeframe=Timeframe.D1,
                limit=10
            )
            
            # 验证结果
            assert len(result) == 1
            assert result[0].symbol == "AAPL"
            assert result[0].close == 151.0
            mock_av.get_stock_klines.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_klines_forex_success(self):
        """测试成功获取外汇 K 线数据"""
        service = DataService()
        
        with patch('backend.services.data_service.alpha_vantage_service') as mock_av, \
             patch('backend.services.data_service.data_cache_service') as mock_cache:
            
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            
            mock_data = [
                KlineData(
                    symbol="EUR/USD",
                    timeframe=Timeframe.H1,
                    market_type=MarketType.FOREX,
                    timestamp=datetime.now(),
                    open=1.0850,
                    high=1.0870,
                    low=1.0840,
                    close=1.0860,
                    volume=0
                )
            ]
            mock_av.get_forex_klines = AsyncMock(return_value=mock_data)
            
            result = await service.get_klines(
                symbol="EUR/USD",
                market_type=MarketType.FOREX,
                exchange="forex",
                timeframe=Timeframe.H1,
                limit=10
            )
            
            assert len(result) == 1
            assert result[0].symbol == "EUR/USD"
            assert result[0].market_type == MarketType.FOREX
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mock_data_generation(self):
        """测试模拟数据生成功能"""
        service = DataService()
        
        result = await service._get_mock_data(
            symbol="TEST/USDT",
            timeframe=Timeframe.H1,
            market_type=MarketType.CRYPTO,
            limit=10
        )
        
        # 验证模拟数据
        assert len(result) == 10
        assert all(isinstance(k, KlineData) for k in result)
        assert all(k.symbol == "TEST/USDT" for k in result)
        assert all(k.market_type == MarketType.CRYPTO for k in result)
        
        # 验证价格合理性（相邻K线价格变化不应该太大）
        for i in range(1, len(result)):
            price_change_percent = abs(result[i].close - result[i-1].close) / result[i-1].close
            assert price_change_percent < 0.1, "模拟数据价格变化过大"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_strategy(self):
        """测试缓存策略"""
        service = DataService()
        
        with patch('backend.services.data_service.data_cache_service') as mock_cache, \
             patch('backend.services.data_service.coingecko_service') as mock_cg:
            
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            
            mock_data = [KlineData(
                symbol="BTC/USDT",
                timeframe=Timeframe.H1,
                market_type=MarketType.CRYPTO,
                timestamp=datetime.now(),
                open=42000.0,
                high=42500.0,
                low=41800.0,
                close=42300.0,
                volume=1000.0
            )]
            mock_cg.get_crypto_klines = AsyncMock(return_value=mock_data)
            
            # 第一次调用应该从 API 获取数据并缓存
            result = await service.get_klines(
                symbol="BTC/USDT",
                market_type=MarketType.CRYPTO,
                exchange="binance",
                timeframe=Timeframe.H1
            )
            
            # 验证缓存被调用
            mock_cache.set.assert_called_once()
            assert len(result) > 0
    
    @pytest.mark.unit
    def test_setup_exchanges(self):
        """测试交易所初始化"""
        service = DataService()
        
        # 验证交易所已初始化
        assert 'binance' in service.exchanges
        assert service.exchanges['binance'] is not None
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_coingecko_api(self):
        """测试真实 CoinGecko API（集成测试，需要网络）"""
        # 跳过此测试，除非明确指定
        pytest.skip("需要真实网络连接")
        
        service = DataService()
        result = await service.get_klines(
            symbol="BTC/USDT",
            market_type=MarketType.CRYPTO,
            exchange="binance",
            timeframe=Timeframe.H1,
            limit=5
        )
        
        assert len(result) > 0
        assert result[0].symbol == "BTC/USDT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
