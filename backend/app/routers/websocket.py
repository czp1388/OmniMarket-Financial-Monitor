# 寰宇多市场金融监控系统 - WebSocket实时数据服务（混合数据版）
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
import asyncio
import json
import logging
from typing import Dict, List
import time
import random

logger = logging.getLogger(__name__)

class RealTimeConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket客户端连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
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

    async def broadcast_market_data(self, market_data: Dict):
        """广播市场数据给所有客户端"""
        message = {
            'type': 'market_data',
            'data': market_data,
            'timestamp': time.time()
        }
        await self.broadcast(json.dumps(message))

# 创建连接管理器实例
manager = RealTimeConnectionManager()

# 创建WebSocket路由
router = APIRouter()

@router.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # 发送欢迎消息
        welcome_msg = {
            'type': 'connection',
            'message': '连接到寰宇多市场金融监控系统',
            'timestamp': time.time(),
            'version': '2.4.0',
            'data_source': 'hybrid'
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # 立即发送当前市场数据
        try:
            market_data = await get_market_data()
            if market_data:
                await manager.send_personal_message(json.dumps({
                    'type': 'market_data',
                    'data': market_data,
                    'timestamp': time.time()
                }), websocket)
        except Exception as e:
            logger.warning(f"发送初始数据失败: {e}")
        
        # 保持连接，等待客户端消息
        while True:
            try:
                data = await websocket.receive_text()
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
                break
            except Exception as e:
                logger.error(f"WebSocket错误: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def get_market_data():
    """获取市场数据 - 优先真实数据，回退到模拟数据"""
    try:
        # 尝试获取真实数据
        from services.real_exchange_service import real_data_service
        real_prices = real_data_service.get_realtime_prices()
        if real_prices:
            logger.debug("使用真实交易所数据")
            return real_prices
    except Exception as e:
        logger.debug(f"真实数据不可用: {e}")
    
    # 回退到模拟数据
    try:
        from services.safe_data_service import data_service
        if data_service and hasattr(data_service, 'get_all_prices'):
            simulated_prices = data_service.get_all_prices()
            logger.debug("使用模拟数据")
            return simulated_prices
    except Exception as e:
        logger.debug(f"模拟数据不可用: {e}")
    
    # 最后回退到基础模拟数据
    base_prices = {
        "BTC/USDT": {
            "symbol": "BTC/USDT",
            "price": 45000 + random.uniform(-1000, 1000),
            "change": random.uniform(-5, 5),
            "percentage": random.uniform(-3, 3),
            "volume": random.uniform(1000000, 5000000)
        },
        "ETH/USDT": {
            "symbol": "ETH/USDT", 
            "price": 3000 + random.uniform(-100, 100),
            "change": random.uniform(-3, 3),
            "percentage": random.uniform(-2, 2),
            "volume": random.uniform(500000, 2000000)
        }
    }
    logger.debug("使用基础模拟数据")
    return base_prices

# 混合数据广播任务
async def broadcast_hybrid_market_data():
    """广播混合市场数据"""
    logger.info("🔄 开始混合数据广播循环...")
    
    while True:
        try:
            market_data = await get_market_data()
            if market_data:
                await manager.broadcast_market_data(market_data)
                logger.debug(f"广播 {len(market_data)} 个交易对数据")
            else:
                logger.debug("暂无市场数据可广播")
                
            # 每3秒广播一次
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"广播市场数据错误: {e}")
            await asyncio.sleep(5)

@router.on_event("startup")
async def startup_event():
    """启动时开始广播数据"""
    asyncio.create_task(broadcast_hybrid_market_data())
    logger.info("✅ 混合数据WebSocket服务已启动")

# REST API 端点
@router.get("/realtime/prices")
async def get_realtime_prices():
    """获取当前实时价格数据"""
    market_data = await get_market_data()
    return {
        'data': market_data,
        'timestamp': time.time(),
        'total_symbols': len(market_data) if market_data else 0,
        'data_source': 'hybrid',
        'service_version': '2.4.0'
    }

@router.get("/realtime/connections")
async def get_connection_status():
    """获取WebSocket连接状态"""
    return {
        'active_connections': len(manager.active_connections),
        'service_version': '2.4.0',
        'data_source': 'hybrid',
        'last_update': time.time()
    }
