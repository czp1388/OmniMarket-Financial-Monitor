import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Set, Callable, Optional
from collections import deque, defaultdict
from dataclasses import dataclass, field
import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """WebSocket连接信息"""
    websocket: websockets.WebSocketServerProtocol
    connected_at: float
    last_ping: float
    last_pong: float
    subscriptions: Set[str] = field(default_factory=set)
    message_count: int = 0
    is_alive: bool = True


class MessageQueue:
    """消息队列管理器"""
    def __init__(self, maxlen: int = 1000):
        self.queue: deque = deque(maxlen=maxlen)
        self.processing = False
        
    async def enqueue(self, message: dict, target: Optional[str] = None):
        """将消息加入队列"""
        self.queue.append({
            'message': message,
            'target': target,
            'timestamp': time.time()
        })
        
    async def process_queue(self, broadcast_func: Callable):
        """处理队列中的消息"""
        while self.queue:
            item = self.queue.popleft()
            try:
                if item['target']:
                    await broadcast_func(item['target'], item['message'])
                else:
                    await broadcast_func(item['message'])
            except Exception as e:
                logger.error(f"处理消息队列时出错: {e}")

class WebSocketManager:
    """WebSocket管理器 - 增强版"""
    
    def __init__(self):
        # 连接管理
        self.connections: Dict[websockets.WebSocketServerProtocol, ConnectionInfo] = {}
        self.subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = defaultdict(set)
        
        # 消息队列
        self.message_queue = MessageQueue(maxlen=1000)
        
        # 心跳配置
        self.heartbeat_interval = 30  # 30秒发送一次心跳
        self.heartbeat_timeout = 60  # 60秒未响应则认为连接断开
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # 数据处理器
        self.data_handlers: Dict[str, Callable] = {}
        
        # 运行状态
        self.is_running = False
        
        # 统计信息
        self.total_connections = 0
        self.total_messages = 0
        
        logger.info("WebSocketManager 增强版初始化完成")
        
    async def register(self, websocket: websockets.WebSocketServerProtocol):
        """注册WebSocket连接 - 增强版"""
        current_time = time.time()
        conn_info = ConnectionInfo(
            websocket=websocket,
            connected_at=current_time,
            last_ping=current_time,
            last_pong=current_time
        )
        self.connections[websocket] = conn_info
        self.total_connections += 1
        
        logger.info(f"新WebSocket连接 (总连接: {len(self.connections)}, 历史: {self.total_connections})")
        
    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        """取消注册WebSocket连接 - 增强版"""
        if websocket not in self.connections:
            return
            
        conn_info = self.connections[websocket]
        
        # 从所有订阅中移除
        for symbol in conn_info.subscriptions:
            if symbol in self.subscriptions:
                self.subscriptions[symbol].discard(websocket)
                if not self.subscriptions[symbol]:
                    del self.subscriptions[symbol]
        
        # 移除连接
        del self.connections[websocket]
        
        duration = time.time() - conn_info.connected_at
        logger.info(f"WebSocket连接断开 (连接时长: {duration:.1f}s, 消息数: {conn_info.message_count}, 剩余: {len(self.connections)})")
        
    async def subscribe(self, websocket: websockets.WebSocketServerProtocol, symbol: str):
        """订阅特定符号的实时数据 - 增强版"""
        if websocket not in self.connections:
            logger.warning(f"尝试订阅但连接不存在: {symbol}")
            return
            
        self.subscriptions[symbol].add(websocket)
        self.connections[websocket].subscriptions.add(symbol)
        
        logger.info(f"订阅 {symbol} (订阅者: {len(self.subscriptions[symbol])})")
        
    async def unsubscribe(self, websocket: websockets.WebSocketServerProtocol, symbol: str):
        """取消订阅特定符号的实时数据 - 增强版"""
        if websocket in self.connections:
            self.connections[websocket].subscriptions.discard(symbol)
            
        if symbol in self.subscriptions:
            self.subscriptions[symbol].discard(websocket)
            if not self.subscriptions[symbol]:
                del self.subscriptions[symbol]
                
        logger.info(f"取消订阅 {symbol}")
            
    async def broadcast_to_subscribers(self, symbol: str, message: dict):
        """向订阅特定符号的所有连接广播消息 - 增强版"""
        if symbol not in self.subscriptions:
            return
            
        disconnected = set()
        success_count = 0
        
        for websocket in self.subscriptions[symbol]:
            if websocket not in self.connections:
                disconnected.add(websocket)
                continue
                
            try:
                await websocket.send(json.dumps(message))
                self.connections[websocket].message_count += 1
                self.total_messages += 1
                success_count += 1
            except ConnectionClosed:
                disconnected.add(websocket)
                self.connections[websocket].is_alive = False
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.add(websocket)
                
        # 清理断开的连接
        for websocket in disconnected:
            await self.unregister(websocket)
            
        if success_count > 0:
            logger.debug(f"广播到 {symbol}: {success_count} 个连接")
                    
    async def broadcast_to_all(self, message: dict):
        """向所有连接广播消息 - 增强版"""
        disconnected = set()
        success_count = 0
        
        for websocket in list(self.connections.keys()):
            try:
                await websocket.send(json.dumps(message))
                self.connections[websocket].message_count += 1
                self.total_messages += 1
                success_count += 1
            except ConnectionClosed:
                disconnected.add(websocket)
                self.connections[websocket].is_alive = False
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                
        # 清理断开的连接
        for websocket in disconnected:
            await self.unregister(websocket)
            
        logger.debug(f"全局广播: {success_count}/{len(self.connections)} 个连接")
                
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """处理从客户端接收的消息 - 增强版"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            # 更新消息计数
            if websocket in self.connections:
                self.connections[websocket].message_count += 1
            
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
                # 更新pong时间
                if websocket in self.connections:
                    self.connections[websocket].last_pong = time.time()
                    
                await websocket.send(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
                
            elif message_type == 'get_status':
                # 返回连接状态
                conn_info = self.connections.get(websocket)
                if conn_info:
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'connected_at': conn_info.connected_at,
                        'subscriptions': list(conn_info.subscriptions),
                        'message_count': conn_info.message_count,
                        'timestamp': datetime.now().isoformat()
                    }))
                    
        except json.JSONDecodeError:
            logger.error("无法解析WebSocket消息")
        except Exception as e:
            logger.error(f"处理WebSocket消息时出错: {e}")
            
    async def _heartbeat_loop(self):
        """心跳检测循环"""
        logger.info(f"启动心跳检测 (间隔: {self.heartbeat_interval}s, 超时: {self.heartbeat_timeout}s)")
        
        while self.is_running:
            try:
                current_time = time.time()
                disconnected = set()
                
                for websocket, conn_info in list(self.connections.items()):
                    # 检查是否超时
                    time_since_pong = current_time - conn_info.last_pong
                    
                    if time_since_pong > self.heartbeat_timeout:
                        logger.warning(f"连接超时 (无响应: {time_since_pong:.1f}s)")
                        conn_info.is_alive = False
                        disconnected.add(websocket)
                        continue
                    
                    # 发送心跳
                    if current_time - conn_info.last_ping >= self.heartbeat_interval:
                        try:
                            await websocket.send(json.dumps({
                                'type': 'ping',
                                'timestamp': datetime.now().isoformat()
                            }))
                            conn_info.last_ping = current_time
                        except Exception as e:
                            logger.error(f"发送心跳失败: {e}")
                            disconnected.add(websocket)
                
                # 清理超时连接
                for websocket in disconnected:
                    await self.unregister(websocket)
                    try:
                        await websocket.close()
                    except:
                        pass
                
                # 等待下一次检测
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"心跳检测循环错误: {e}")
                await asyncio.sleep(10)
    
    async def start_websocket_server(self, host: str = "localhost", port: int = 8774, max_retries: int = 5):
        """启动WebSocket服务器 - 增强版（支持端口冲突自动重试）"""
        self.is_running = True
        
        async def handler(websocket, path):
            await self.register(websocket)
            try:
                async for message in websocket:
                    await self.handle_message(websocket, message)
            except ConnectionClosed:
                logger.debug("WebSocket连接关闭")
            except Exception as e:
                logger.error(f"WebSocket处理器错误: {e}")
            finally:
                await self.unregister(websocket)
        
        # 尝试启动服务器，端口冲突时自动递增
        for attempt in range(max_retries):
            try:
                current_port = port + attempt
                logger.info(f"尝试启动WebSocket服务器在 {host}:{current_port}")
                
                # 启动WebSocket服务器
                server = await websockets.serve(handler, host, current_port)
                
                # 启动心跳检测
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                logger.info(f"✅ WebSocket服务器启动成功: {host}:{current_port}")
                return server
                
            except OSError as e:
                if "10048" in str(e) or "address already in use" in str(e).lower():
                    logger.warning(f"端口 {current_port} 已被占用，尝试下一个端口...")
                    if attempt == max_retries - 1:
                        logger.error(f"尝试了 {max_retries} 个端口仍无法启动WebSocket服务器")
                        raise
                else:
                    raise
            except Exception as e:
                logger.error(f"启动WebSocket服务器失败: {e}")
                raise
        
    async def stop(self):
        """停止WebSocket管理器 - 增强版"""
        logger.info("开始停止WebSocket管理器...")
        self.is_running = False
        
        # 停止心跳检测
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # 关闭所有连接
        for websocket in list(self.connections.keys()):
            try:
                await websocket.close()
            except:
                pass
            await self.unregister(websocket)
            
        logger.info(f"WebSocket管理器已停止 (总连接: {self.total_connections}, 总消息: {self.total_messages})")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "active_connections": len(self.connections),
            "total_connections": self.total_connections,
            "total_messages": self.total_messages,
            "subscriptions": {
                symbol: len(subscribers)
                for symbol, subscribers in self.subscriptions.items()
            },
            "is_running": self.is_running
        }


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
