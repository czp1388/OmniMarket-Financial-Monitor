import logging
import asyncio
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
import json
import websockets
from websockets.exceptions import ConnectionClosed

from backend.models.market_data import MarketType, Timeframe
from backend.services.data_service import data_service

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: Set[websockets.WebSocketServerProtocol] = set()
        self.subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.market_data_connections: Dict[str, Any] = {}
        
    async def connect(self, websocket: websockets.WebSocketServerProtocol):
        """处理新的WebSocket连接"""
        self.connections.add(websocket)
        logger.info(f"新的WebSocket连接建立，当前连接数: {len(self.connections)}")
        
        try:
            await websocket.send(json.dumps({
                "type": "connection_established",
                "message": "WebSocket连接已建立",
                "timestamp": datetime.now().isoformat()
            }))
            
            # 保持连接活跃
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except ConnectionClosed:
            pass
        finally:
            await self.disconnect(websocket)
    
    async def disconnect(self, websocket: websockets.WebSocketServerProtocol):
        """处理WebSocket连接断开"""
        if websocket in self.connections:
            self.connections.remove(websocket)
            
        # 从所有订阅中移除连接
        for symbol in list(self.subscriptions.keys()):
            if websocket in self.subscriptions[symbol]:
                self.subscriptions[symbol].remove(websocket)
                if not self.subscriptions[symbol]:
                    del self.subscriptions[symbol]
        
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.connections)}")
    
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """处理WebSocket消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                await self.handle_subscribe(websocket, data)
            elif message_type == "unsubscribe":
                await self.handle_unsubscribe(websocket, data)
            elif message_type == "ping":
                await self.handle_ping(websocket)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"未知的消息类型: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "无效的JSON格式",
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"处理WebSocket消息时出错: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"处理消息时出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }))
    
    async def handle_subscribe(self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]):
        """处理订阅请求"""
        symbol = data.get("symbol")
        market_type = data.get("market_type")
        exchange = data.get("exchange")
        timeframe = data.get("timeframe", "1m")
        
        if not symbol or not market_type or not exchange:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "订阅请求缺少必要参数: symbol, market_type, exchange",
                "timestamp": datetime.now().isoformat()
            }))
            return
        
        subscription_key = f"{exchange}:{market_type}:{symbol}:{timeframe}"
        
        if subscription_key not in self.subscriptions:
            self.subscriptions[subscription_key] = set()
        
        self.subscriptions[subscription_key].add(websocket)
        
        # 发送确认消息
        await websocket.send(json.dumps({
            "type": "subscription_confirmed",
            "symbol": symbol,
            "market_type": market_type,
            "exchange": exchange,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat()
        }))
        
        logger.info(f"客户端订阅: {subscription_key}")
    
    async def handle_unsubscribe(self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]):
        """处理取消订阅请求"""
        symbol = data.get("symbol")
        market_type = data.get("market_type")
        exchange = data.get("exchange")
        timeframe = data.get("timeframe", "1m")
        
        if not symbol or not market_type or not exchange:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "取消订阅请求缺少必要参数: symbol, market_type, exchange",
                "timestamp": datetime.now().isoformat()
            }))
            return
        
        subscription_key = f"{exchange}:{market_type}:{symbol}:{timeframe}"
        
        if subscription_key in self.subscriptions and websocket in self.subscriptions[subscription_key]:
            self.subscriptions[subscription_key].remove(websocket)
            if not self.subscriptions[subscription_key]:
                del self.subscriptions[subscription_key]
        
        await websocket.send(json.dumps({
            "type": "unsubscription_confirmed",
            "symbol": symbol,
            "market_type": market_type,
            "exchange": exchange,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat()
        }))
        
        logger.info(f"客户端取消订阅: {subscription_key}")
    
    async def handle_ping(self, websocket: websockets.WebSocketServerProtocol):
        """处理ping消息"""
        await websocket.send(json.dumps({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }))
    
    async def broadcast_market_data(self, symbol: str, market_type: str, exchange: str, 
                                   timeframe: str, data: Dict[str, Any]):
        """广播市场数据到所有订阅者"""
        subscription_key = f"{exchange}:{market_type}:{symbol}:{timeframe}"
        
        if subscription_key not in self.subscriptions:
            return
        
        message = {
            "type": "market_data",
            "symbol": symbol,
            "market_type": market_type,
            "exchange": exchange,
            "timeframe": timeframe,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected_connections = []
        
        for websocket in self.subscriptions[subscription_key]:
            try:
                await websocket.send(json.dumps(message))
            except ConnectionClosed:
                disconnected_connections.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            await self.disconnect(websocket)
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """广播预警信息到所有连接"""
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected_connections = []
        
        for websocket in self.connections:
            try:
                await websocket.send(json.dumps(message))
            except ConnectionClosed:
                disconnected_connections.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            await self.disconnect(websocket)
    
    async def broadcast_system_status(self, status: str, message: str = ""):
        """广播系统状态信息"""
        system_message = {
            "type": "system_status",
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected_connections = []
        
        for websocket in self.connections:
            try:
                await websocket.send(json.dumps(system_message))
            except ConnectionClosed:
                disconnected_connections.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            await self.disconnect(websocket)
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.connections)
    
    def get_subscription_count(self) -> int:
        """获取订阅总数"""
        return sum(len(connections) for connections in self.subscriptions.values())


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
