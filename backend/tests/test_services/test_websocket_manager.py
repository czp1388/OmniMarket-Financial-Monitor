"""
WebSocket Manager 单元测试
测试实时通信管理器的注册、订阅、广播等功能
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from backend.services.websocket_manager import WebSocketManager


@pytest.fixture
def ws_manager():
    """创建 WebSocketManager 实例"""
    manager = WebSocketManager()
    yield manager
    # 清理
    manager.connections.clear()
    manager.subscriptions.clear()


@pytest.fixture
def mock_websocket():
    """创建模拟 WebSocket 连接"""
    mock_ws = Mock()
    mock_ws.send_json = AsyncMock()
    mock_ws.send_text = AsyncMock()
    return mock_ws


class TestWebSocketManager:
    """WebSocket管理器测试套件"""
    
    @pytest.mark.asyncio
    async def test_register_connection(self, ws_manager, mock_websocket):
        """测试连接注册"""
        # 注册连接
        await ws_manager.register(mock_websocket)
        
        # 验证连接已注册
        assert mock_websocket in ws_manager.connections
        assert len(ws_manager.connections) == 1
    
    @pytest.mark.asyncio
    async def test_unregister_connection(self, ws_manager, mock_websocket):
        """测试连接注销"""
        # 先注册
        await ws_manager.register(mock_websocket)
        assert len(ws_manager.connections) == 1
        
        # 注销连接
        await ws_manager.unregister(mock_websocket)
        
        # 验证连接已移除
        assert mock_websocket not in ws_manager.connections
        assert len(ws_manager.connections) == 0
    
    @pytest.mark.asyncio
    async def test_subscribe_to_symbol(self, ws_manager, mock_websocket):
        """测试订阅品种"""
        connection_id = await ws_manager.register(mock_websocket)
        symbol = "BTC/USDT"
        
        # 订阅品种
        await ws_manager.subscribe(connection_id, symbol)
        
        # 验证订阅关系
        assert symbol in ws_manager.subscriptions
        assert connection_id in ws_manager.subscriptions[symbol]
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_symbol(self, ws_manager, mock_websocket):
        """测试取消订阅"""
        connection_id = await ws_manager.register(mock_websocket)
        symbol = "BTC/USDT"
        
        # 订阅后取消订阅
        await ws_manager.subscribe(connection_id, symbol)
        await ws_manager.unsubscribe(connection_id, symbol)
        
        # 验证订阅已移除
        if symbol in ws_manager.subscriptions:
            assert connection_id not in ws_manager.subscriptions[symbol]
    
    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, ws_manager):
        """测试广播消息到所有连接"""
        # 注册3个连接
        mock_ws1 = Mock()
        mock_ws1.send = AsyncMock()
        mock_ws2 = Mock()
        mock_ws2.send = AsyncMock()
        mock_ws3 = Mock()
        mock_ws3.send = AsyncMock()
        
        await ws_manager.register(mock_ws1)
        await ws_manager.register(mock_ws2)
        await ws_manager.register(mock_ws3)
        
        # 广播消息
        message = {"type": "test", "data": "broadcast"}
        await ws_manager.broadcast_to_all(message)
        
        # 验证所有连接都收到消息 (实际发送的是 JSON 字符串)
        import json
        expected_message = json.dumps(message)
        mock_ws1.send.assert_called_once_with(expected_message)
        mock_ws2.send.assert_called_once_with(expected_message)
        mock_ws3.send.assert_called_once_with(expected_message)
    
    @pytest.mark.asyncio
    async def test_broadcast_to_symbol_subscribers(self, ws_manager):
        """测试广播消息到特定品种订阅者"""
        # 注册3个连接
        mock_ws1 = Mock()
        mock_ws1.send = AsyncMock()
        mock_ws2 = Mock()
        mock_ws2.send = AsyncMock()
        mock_ws3 = Mock()
        mock_ws3.send = AsyncMock()
        
        await ws_manager.register(mock_ws1)
        await ws_manager.register(mock_ws2)
        await ws_manager.register(mock_ws3)
        
        # 只有连接1和2订阅BTC/USDT
        symbol = "BTC/USDT"
        await ws_manager.subscribe(mock_ws1, symbol)
        await ws_manager.subscribe(mock_ws2, symbol)
        
        # 广播到BTC/USDT订阅者
        message = {"symbol": symbol, "price": 50000}
        await ws_manager.broadcast_to_subscribers(symbol, message)
        
        # 验证订阅者收到消息
        import json
        expected_message = json.dumps(message)
        mock_ws1.send.assert_called_once_with(expected_message)
        mock_ws2.send.assert_called_once_with(expected_message)
        mock_ws3.send.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_multiple_subscriptions_per_connection(self, ws_manager, mock_websocket):
        """测试单个连接订阅多个品种"""
        await ws_manager.register(mock_websocket)
        
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        
        # 订阅多个品种
        for symbol in symbols:
            await ws_manager.subscribe(mock_websocket, symbol)
        
        # 验证所有订阅
        for symbol in symbols:
            assert symbol in ws_manager.subscriptions
            assert mock_websocket in ws_manager.subscriptions[symbol]
    
    @pytest.mark.asyncio
    async def test_unregister_removes_all_subscriptions(self, ws_manager, mock_websocket):
        """测试注销连接时自动清理所有订阅"""
        await ws_manager.register(mock_websocket)
        
        symbols = ["BTC/USDT", "ETH/USDT"]
        for symbol in symbols:
            await ws_manager.subscribe(mock_websocket, symbol)
        
        # 注销连接
        await ws_manager.unregister(mock_websocket)
        
        # 验证所有订阅都被清理
        for symbol in symbols:
            if symbol in ws_manager.subscriptions:
                assert mock_websocket not in ws_manager.subscriptions[symbol]
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="send_personal_message 方法不存在于实际 API 中")
    async def test_send_personal_message(self, ws_manager, mock_websocket):
        """测试发送个人消息"""
        await ws_manager.register(mock_websocket)
        
        message = {"type": "personal", "data": "only for you"}
        # 实际 API 不支持直接发送个人消息
        pass
    
    @pytest.mark.asyncio
    async def test_handle_disconnected_websocket(self, ws_manager):
        """测试处理断开的WebSocket连接"""
        from websockets.exceptions import ConnectionClosed
        
        mock_ws = Mock()
        # 模拟发送失败（连接已断开）
        mock_ws.send = AsyncMock(side_effect=ConnectionClosed(None, None))
        
        await ws_manager.register(mock_ws)
        
        # 尝试广播（应该捕获异常而不崩溃）
        message = {"type": "test"}
        try:
            await ws_manager.broadcast_to_all(message)
            # 应该成功处理，不抛出异常
        except Exception as e:
            pytest.fail(f"broadcast_to_all() should handle disconnected websockets gracefully, got {e}")
    
    @pytest.mark.asyncio
    async def test_get_active_connections_count(self, ws_manager):
        """测试获取活跃连接数"""
        # 注册3个连接
        for _ in range(3):
            mock_ws = Mock()
            mock_ws.send = AsyncMock()
            await ws_manager.register(mock_ws)
        
        # 实际 API 通过 len(connections) 获取连接数
        assert len(ws_manager.connections) == 3
    
    @pytest.mark.asyncio
    async def test_get_subscriptions_for_symbol(self, ws_manager):
        """测试获取特定品种的订阅数"""
        symbol = "BTC/USDT"
        
        # 注册并订阅
        for _ in range(5):
            mock_ws = Mock()
            mock_ws.send = AsyncMock()
            await ws_manager.register(mock_ws)
            await ws_manager.subscribe(mock_ws, symbol)
        
        # 实际 API 通过 subscriptions[symbol] 访问订阅者
        subscribers = ws_manager.subscriptions.get(symbol, set())
        assert len(subscribers) == 5
