import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Set, Callable, Optional
import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: Set[websockets.WebSocketServerProtocol] = set()
        self.subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.data_handlers: Dict[str, Callable] = {}
        self.is_running = False
        
    async def register(self, websocket: websockets.WebSocketServerProtocol):
        """注册WebSocket连接"""
        self.connections.add(websocket)
        logger.info(f"新的WebSocket连接已注册，当前连接数: {len(self.connections)}")
        
    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        """取消注册WebSocket连接"""
        self.connections.remove(websocket)
        # 同时从所有订阅中移除
        for symbol in list(self.subscriptions.keys()):
            if websocket in self.subscriptions[symbol]:
                self.subscriptions[symbol].remove(websocket)
        logger.info(f"WebSocket连接已取消注册，当前连接数: {len(self.connections)}")
        
    async def subscribe(self, websocket: websockets.WebSocketServerProtocol, symbol: str):
        """订阅特定符号的实时数据"""
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = set()
        self.subscriptions[symbol].add(websocket)
        logger.info(f"WebSocket连接已订阅 {symbol}，当前订阅数: {len(self.subscriptions[symbol])}")
        
    async def unsubscribe(self, websocket: websockets.WebSocketServerProtocol, symbol: str):
        """取消订阅特定符号的实时数据"""
        if symbol in self.subscriptions and websocket in self.subscriptions[symbol]:
            self.subscriptions[symbol].remove(websocket)
            logger.info(f"WebSocket连接已取消订阅 {symbol}，当前订阅数: {len(self.subscriptions[symbol])}")
            
    async def broadcast_to_subscribers(self, symbol: str, message: dict):
        """向订阅特定符号的所有连接广播消息"""
        if symbol in self.subscriptions:
            disconnected = set()
            for websocket in self.subscriptions[symbol]:
                try:
                    await websocket.send(json.dumps(message))
                except ConnectionClosed:
                    disconnected.add(websocket)
            # 清理断开连接的WebSocket
            for websocket in disconnected:
                await self.unsubscribe(websocket, symbol)
                if websocket in self.connections:
                    await self.unregister(websocket)
                    
    async def broadcast_to_all(self, message: dict):
        """向所有连接广播消息"""
        disconnected = set()
        for websocket in self.connections:
            try:
                await websocket.send(json.dumps(message))
            except ConnectionClosed:
                disconnected.add(websocket)
        # 清理断开连接的WebSocket
        for websocket in disconnected:
            if websocket in self.connections:
                await self.unregister(websocket)
                
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """处理从客户端接收的消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                symbol = data.get('symbol')
                if symbol:
                    await self.subscribe(websocket, symbol)
                    await websocket.send(json.dumps({
                        'type': 'subscribed',
                        'symbol': symbol,
                        'timestamp': datetime.now().isoformat()
                    }))
                    
            elif message_type == 'unsubscribe':
                symbol = data.get('symbol')
                if symbol:
                    await self.unsubscribe(websocket, symbol)
                    await websocket.send(json.dumps({
                        'type': 'unsubscribed',
                        'symbol': symbol,
                        'timestamp': datetime.now().isoformat()
                    }))
                    
            elif message_type == 'ping':
                await websocket.send(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            logger.error("无法解析WebSocket消息")
        except Exception as e:
            logger.error(f"处理WebSocket消息时出错: {e}")
            
    async def start_websocket_server(self, host: str = "localhost", port: int = 8777):
        """启动WebSocket服务器"""
        self.is_running = True
        logger.info(f"启动WebSocket服务器在 {host}:{port}")
        
        async def handler(websocket, path):
            await self.register(websocket)
            try:
                async for message in websocket:
                    await self.handle_message(websocket, message)
            except ConnectionClosed:
                pass
            finally:
                await self.unregister(websocket)
                
        server = await websockets.serve(handler, host, port)
        return server
        
    async def stop(self):
        """停止WebSocket管理器"""
        self.is_running = False
        # 关闭所有连接
        for websocket in list(self.connections):
            await self.unregister(websocket)
        logger.info("WebSocket管理器已停止")


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
