# 寰宇多市场金融监控系统 - WebSocket实时数据服务（真实数据版）
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
import asyncio
import json
import logging
from typing import Dict, List
import time

logger = logging.getLogger(__name__)

class RealTimeConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
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
            'message': '连接到寰宇多市场金融监控系统真实数据',
            'timestamp': time.time(),
            'version': '2.3.0'
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # 立即发送当前市场数据
        try:
            from services.real_exchange_service import real_data_service
            current_prices = real_data_service.get_realtime_prices()
            if current_prices:
                await manager.send_personal_message(json.dumps({
                    'type': 'market_data',
                    'data': current_prices,
                    'timestamp': time.time()
                }), websocket)
        except Exception as e:
            logger.warning(f"发送初始数据失败: {e}")
        
        # 保持连接，等待客户端消息
        while True:
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

# 真实数据广播任务
async def broadcast_real_market_data():
    """广播真实市场数据"""
    try:
        from services.real_exchange_service import real_data_service
    except ImportError:
        logger.error("真实数据服务未找到，使用模拟数据")
        return
    
    while True:
        try:
            # 获取真实市场数据
            market_data = real_data_service.get_realtime_prices()
            if market_data:
                await manager.broadcast_market_data(market_data)
            else:
                logger.debug("暂无市场数据可广播")
                
            # 每2秒广播一次
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"广播市场数据错误: {e}")
            await asyncio.sleep(5)

@router.on_event("startup")
async def startup_event():
    """启动时开始广播真实数据"""
    asyncio.create_task(broadcast_real_market_data())
    logger.info("✅ 真实数据WebSocket服务已启动")

# REST API 端点
@router.get("/realtime/prices")
async def get_realtime_prices():
    """获取当前实时价格数据"""
    try:
        from services.real_exchange_service import real_data_service
        prices = real_data_service.get_realtime_prices()
        return {
            'data': prices,
            'timestamp': time.time(),
            'total_symbols': len(prices),
            'data_source': 'real_exchange'
        }
    except:
        # 回退到模拟数据
        return {
            'data': {},
            'timestamp': time.time(),
            'total_symbols': 0,
            'data_source': 'simulated',
            'message': '真实数据服务未就绪'
        }

@router.get("/realtime/connections")
async def get_connection_status():
    """获取WebSocket连接状态"""
    return {
        'active_connections': len(manager.active_connections),
        'service_version': '2.3.0',
        'data_source': 'real_exchange',
        'last_update': time.time()
    }
