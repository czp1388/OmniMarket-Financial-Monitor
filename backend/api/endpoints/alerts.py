from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.alerts import (
    Alert, AlertCreate, AlertUpdate, AlertResponse, 
    AlertTriggerResponse, AlertStatus, AlertConditionType,
    NotificationType
)
from services.alert_service import AlertService

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    user_id: int = Query(..., description="用户ID"),
    status: Optional[AlertStatus] = Query(None, description="预警状态"),
    symbol: Optional[str] = Query(None, description="交易对符号"),
    market_type: Optional[str] = Query(None, description="市场类型"),
    skip: int = Query(0, description="跳过数量", ge=0),
    limit: int = Query(100, description="返回数量", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    获取用户预警列表
    """
    try:
        alert_service = AlertService(db)
        alerts = await alert_service.get_user_alerts(
            user_id=user_id,
            status=status,
            symbol=symbol,
            market_type=market_type,
            skip=skip,
            limit=limit
        )
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警列表失败: {str(e)}")

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):
    """
    创建新预警
    """
    try:
        alert_service = AlertService(db)
        new_alert = await alert_service.create_alert(alert)
        return new_alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建预警失败: {str(e)}")

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    获取预警详情
    """
    try:
        alert_service = AlertService(db)
        alert = await alert_service.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="预警不存在")
        return alert
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警详情失败: {str(e)}")

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    更新预警
    """
    try:
        alert_service = AlertService(db)
        updated_alert = await alert_service.update_alert(alert_id, alert_update)
        if not updated_alert:
            raise HTTPException(status_code=404, detail="预警不存在")
        return updated_alert
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新预警失败: {str(e)}")

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    删除预警
    """
    try:
        alert_service = AlertService(db)
        success = await alert_service.delete_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="预警不存在")
        return {"message": "预警删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除预警失败: {str(e)}")

@router.post("/{alert_id}/enable")
async def enable_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    启用预警
    """
    try:
        alert_service = AlertService(db)
        success = await alert_service.enable_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="预警不存在")
        return {"message": "预警已启用"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启用预警失败: {str(e)}")

@router.post("/{alert_id}/disable")
async def disable_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    禁用预警
    """
    try:
        alert_service = AlertService(db)
        success = await alert_service.disable_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="预警不存在")
        return {"message": "预警已禁用"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"禁用预警失败: {str(e)}")

@router.get("/{alert_id}/triggers", response_model=List[AlertTriggerResponse])
async def get_alert_triggers(
    alert_id: int,
    skip: int = Query(0, description="跳过数量", ge=0),
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    获取预警触发记录
    """
    try:
        alert_service = AlertService(db)
        triggers = await alert_service.get_alert_triggers(
            alert_id=alert_id,
            skip=skip,
            limit=limit
        )
        return triggers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取触发记录失败: {str(e)}")

@router.get("/user/{user_id}/active-count")
async def get_active_alerts_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户活跃预警数量
    """
    try:
        alert_service = AlertService(db)
        count = await alert_service.get_active_alerts_count(user_id)
        return {"user_id": user_id, "active_alerts_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活跃预警数量失败: {str(e)}")

@router.post("/test-condition")
async def test_alert_condition(
    condition_type: AlertConditionType,
    condition_config: dict,
    symbol: str,
    market_type: str,
    exchange: str,
    timeframe: str,
    db: Session = Depends(get_db)
):
    """
    测试预警条件
    """
    try:
        alert_service = AlertService(db)
        result = await alert_service.test_alert_condition(
            condition_type=condition_type,
            condition_config=condition_config,
            symbol=symbol,
            market_type=market_type,
            exchange=exchange,
            timeframe=timeframe
        )
        return {
            "condition_met": result,
            "message": "条件测试完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试预警条件失败: {str(e)}")
