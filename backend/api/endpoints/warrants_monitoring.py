"""
牛熊证实时监控API端点
提供牛熊证监控数据的实时获取和管理功能
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import logging
import asyncio
import json

from backend.services.warrants_monitoring_service import (
    warrants_monitoring_service
)
from backend.services.warrants_data_service import (
    warrants_data_service
)
from backend.models.warrants import (
    WarrantData,
    WarrantMonitoringAlert,
    WarrantType,
    WarrantStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["warrants-monitoring"])


@router.get("/warrants", response_model=List[WarrantData])
async def get_all_warrants():
    """
    获取所有牛熊证监控数据
    """
    try:
        # 使用牛熊证数据服务获取真实数据
        warrants_list = await warrants_data_service.get_warrants_list()
        return warrants_list
    except Exception as e:
        logger.error(f"获取牛熊证数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取牛熊证数据失败: {str(e)}")


@router.get("/warrants/{warrant_code}", response_model=WarrantData)
async def get_warrant_by_code(warrant_code: str):
    """
    根据代码获取牛熊证数据
    """
    try:
        warrant = await warrants_monitoring_service.get_warrant(warrant_code)
        if not warrant:
            raise HTTPException(status_code=404, detail="牛熊证不存在")
        return warrant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取牛熊证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取牛熊证失败: {str(e)}")


@router.get("/alerts", response_model=List[WarrantMonitoringAlert])
async def get_active_alerts():
    """
    获取活跃预警列表
    """
    try:
        alerts = await warrants_monitoring_service.get_active_alerts()
        return alerts
    except Exception as e:
        logger.error(f"获取预警列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取预警列表失败: {str(e)}")


@router.post("/alerts/{warrant_code}/acknowledge")
async def acknowledge_alert(warrant_code: str):
    """
    确认预警
    """
    try:
        success = await warrants_monitoring_service.acknowledge_alert(warrant_code)
        if not success:
            raise HTTPException(status_code=404, detail="预警不存在")
        return {"message": "预警已确认"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"确认预警失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"确认预警失败: {str(e)}")


@router.get("/metrics/{warrant_code}")
async def get_warrant_metrics(warrant_code: str):
    """
    获取牛熊证关键指标
    """
    try:
        warrant = await warrants_monitoring_service.get_warrant(warrant_code)
        if not warrant:
            raise HTTPException(status_code=404, detail="牛熊证不存在")
        
        # 计算关键指标
        distance_to_knock_out = warrants_monitoring_service.calculate_distance_to_knock_out(
            warrant.warrant_type, warrant.underlying_price, warrant.knock_out_price
        )
        
        effective_leverage = warrants_monitoring_service.calculate_effective_leverage(
            warrant.warrant_price, warrant.conversion_ratio, warrant.underlying_price
        )
        
        # 获取当前预警级别
        alert_level = warrants_monitoring_service._get_alert_level(distance_to_knock_out)
        
        return {
            "warrant_code": warrant_code,
            "distance_to_knock_out": distance_to_knock_out,
            "effective_leverage": effective_leverage,
            "alert_level": alert_level.value,
            "underlying_price": warrant.underlying_price,
            "warrant_price": warrant.warrant_price,
            "knock_out_price": warrant.knock_out_price,
            "time_to_expiry": warrant.time_to_expiry
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取牛熊证指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取牛熊证指标失败: {str(e)}")


@router.post("/monitoring/start")
async def start_monitoring():
    """
    启动牛熊证监控
    """
    try:
        await warrants_monitoring_service.initialize_monitoring()
        return {"message": "牛熊证监控已启动"}
    except Exception as e:
        logger.error(f"启动监控失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动监控失败: {str(e)}")


@router.post("/monitoring/stop")
async def stop_monitoring():
    """
    停止牛熊证监控
    """
    try:
        # 这里需要实现停止监控的逻辑
        return {"message": "牛熊证监控已停止"}
    except Exception as e:
        logger.error(f"停止监控失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止监控失败: {str(e)}")


@router.get("/status")
async def get_monitoring_status():
    """
    获取监控系统状态
    """
    try:
        warrants_count = len(await warrants_monitoring_service.get_all_warrants())
        active_alerts_count = len(await warrants_monitoring_service.get_all_active_alerts())
        
        return {
            "status": "running",
            "warrants_monitored": warrants_count,
            "active_alerts": active_alerts_count,
            "last_update": warrants_monitoring_service.last_update_time.isoformat() if hasattr(warrants_monitoring_service, 'last_update_time') and warrants_monitoring_service.last_update_time else None
        }
    except Exception as e:
        logger.error(f"获取监控状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取监控状态失败: {str(e)}")


# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 定期发送监控数据更新
            await asyncio.sleep(2)  # 每2秒更新一次
            
            warrants = await warrants_monitoring_service.get_all_warrants()
            alerts = await warrants_monitoring_service.get_active_alerts()
            
            update_data = {
                "type": "monitoring_update",
                "warrants": [warrant.dict() for warrant in warrants],
                "alerts": [alert.dict() for alert in alerts],
                "timestamp": warrants_monitoring_service.last_update_time.isoformat() if warrants_monitoring_service.last_update_time else None
            }
            
            await websocket.send_text(json.dumps(update_data))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 示例数据端点
@router.get("/sample-warrants", response_model=List[WarrantData])
async def get_sample_warrants():
    """
    获取示例牛熊证数据用于测试
    """
    try:
        # 修复字段名称以匹配WarrantData模型
        sample_warrants = [
            WarrantData(
                symbol="12345.HK",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BULL,
                strike_price=180.0,
                knock_out_price=200.0,
                current_price=0.25,
                leverage=8.5,
                time_to_maturity=180,
                status=WarrantStatus.ACTIVE,
                volume=1500000,
                average_volume=800000
            ),
            WarrantData(
                symbol="12346.HK",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BEAR,
                strike_price=190.0,
                knock_out_price=170.0,
                current_price=0.18,
                leverage=7.2,
                time_to_maturity=180,
                status=WarrantStatus.ACTIVE,
                volume=800000,
                average_volume=500000
            ),
            WarrantData(
                symbol="12347.HK",
                underlying_symbol="00941.HK",
                warrant_type=WarrantType.BULL,
                strike_price=55.0,
                knock_out_price=60.0,
                current_price=0.32,
                leverage=6.8,
                time_to_maturity=120,
                status=WarrantStatus.ACTIVE,
                volume=1200000,
                average_volume=900000
            ),
            WarrantData(
                symbol="12348.HK",
                underlying_symbol="00941.HK",
                warrant_type=WarrantType.BEAR,
                strike_price=58.0,
                knock_out_price=52.0,
                current_price=0.28,
                leverage=5.9,
                time_to_maturity=120,
                status=WarrantStatus.ACTIVE,
                volume=600000,
                average_volume=400000
            )
        ]
        return sample_warrants
    except Exception as e:
        logger.error(f"获取示例数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取示例数据失败: {str(e)}")
