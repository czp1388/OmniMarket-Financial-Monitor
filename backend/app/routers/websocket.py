# 寰宇多市场金融监控系统 - WebSocket实时数据服务
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
import asyncio
import json
import logging
from typing import Dict, List
import time

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.price_data = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket客户端连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket客户端断开，剩余连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"发送消息失败，连接可能已断开: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)

    def update_price_data(self, symbol: str, price: float, change: float, volume: float):
        """更新价格数据"""
        self.price_data[symbol] = {
            'symbol': symbol,
            'price': price,
            'change': change,
            'change_percent': (change / price * 100) if price else 0,
            'volume': volume,
            'timestamp': time.time()
        }

    async def broadcast_market_data(self):
        """广播市场数据给所有客户端"""
        if self.price_data:
            message = {
                'type': 'market_data',
                'data': self.price_data,
                'timestamp': time.time()
            }
            await self.broadcast(json.dumps(message))

# 创建连接管理器实例
manager = ConnectionManager()

# 创建WebSocket路由
router = APIRouter()

@router.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # 发送欢迎消息
        welcome_msg = {
            'type': 'connection',
            'message': '连接到寰宇多市场金融监控系统实时数据',
            'timestamp': time.time()
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # 保持连接，等待客户端消息
        while True:
            data = await websocket.receive_text()
            # 可以处理客户端发送的指令
            try:
                command = json.loads(data)
                if command.get('type') == 'subscribe':
                    await manager.send_personal_message(json.dumps({
                        'type': 'subscription',
                        'message': f"已订阅 {command.get('symbols', [])}",
                        'timestamp': time.time()
                    }), websocket)
            except:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 模拟实时数据生成任务
async def generate_realtime_data():
    """生成模拟实时数据"""
    import random
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'DOT/USDT']
    base_prices = {
        'BTC/USDT': 50000,
        'ETH/USDT': 3000, 
        'BNB/USDT': 400,
        'ADA/USDT': 1.2,
        'DOT/USDT': 25
    }
    
    while True:
        for symbol in symbols:
            base_price = base_prices[symbol]
            # 模拟价格波动 (-2% 到 +2%)
            change_percent = random.uniform(-0.02, 0.02)
            new_price = base_price * (1 + change_percent)
            change = new_price - base_price
            volume = random.randint(1000, 100000)
            
            # 更新价格数据
            manager.update_price_data(symbol, new_price, change, volume)
        
        # 广播数据给所有客户端
        await manager.broadcast_market_data()
        
        # 每秒更新一次
        await asyncio.sleep(1)

@router.on_event("startup")
async def startup_event():
    """启动时开始生成实时数据"""
    asyncio.create_task(generate_realtime_data())
    logger.info("✅ WebSocket实时数据服务已启动")

# REST API 端点用于获取当前实时数据
@router.get("/realtime/prices")
async def get_realtime_prices():
    """获取当前实时价格数据"""
    return {
        'data': manager.price_data,
        'timestamp': time.time(),
        'total_symbols': len(manager.price_data)
    }

@router.get("/realtime/connections")
async def get_connection_status():
    """获取WebSocket连接状态"""
    return {
        'active_connections': len(manager.active_connections),
        'tracked_symbols': list(manager.price_data.keys()),
        'last_update': time.time()
    }
