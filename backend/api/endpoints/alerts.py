from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.alerts import (
    Alert, AlertCreate, AlertUpdate, AlertResponse, 
    AlertTriggerResponse, AlertStatus, AlertConditionType,
    NotificationType
)
from services.alert_service import alert_service as global_alert_service
from api.validators import (
    PaginationParams, 
    create_paginated_response,
    create_success_response,
    create_error_response,
    APIResponse,
    SymbolValidator
)

router = APIRouter()

@router.get("/", response_model=APIResponse)
async def get_alerts(
    user_id: int = Query(..., description="用户ID", gt=0),
    status: Optional[AlertStatus] = Query(None, description="预警状态"),
    symbol: Optional[str] = Query(None, description="交易对符号", min_length=1, max_length=20),
    market_type: Optional[str] = Query(None, description="市场类型"),
    pagination: PaginationParams = Depends()
):
    """
    获取用户预警列表（分页）
    
    - 支持按状态、交易对、市场类型过滤
    - 支持分页和排序
    - 返回统一响应格式
    """
    try:
        # 使用全局alert_service实例
        alerts = global_alert_service.get_all_alerts()
        
        # 过滤
        filtered = []
        for alert in alerts:
            if alert.user_id != user_id:
                continue
            if status and alert.status != status.value:
                continue
            if symbol and alert.symbol != symbol:
                continue
            if market_type and alert.market_type.value != market_type:
                continue
            filtered.append(alert)
        
        # 排序
        if pagination.sort_by:
            reverse = pagination.sort_order == "desc"
            filtered.sort(
                key=lambda x: getattr(x, pagination.sort_by, None) or "",
                reverse=reverse
            )
        
        # 分页
        total = len(filtered)
        start = pagination.offset
        end = start + pagination.page_size
        items = filtered[start:end]
        
        # 转换为响应模型
        alert_responses = [
            AlertResponse(
                id=alert.id,
                user_id=alert.user_id,
                name=alert.name,
                description=alert.description,
                symbol=alert.symbol,
                market_type=alert.market_type,
                exchange=alert.exchange,
                timeframe=alert.timeframe,
                condition_type=alert.condition_type,
                condition_config=alert.condition_config,
                status=alert.status,
                is_recurring=alert.is_recurring,
                triggered_count=alert.triggered_count or 0,
                last_triggered_at=alert.last_triggered_at,
                notification_types=alert.notification_types or [],
                notification_config=alert.notification_config or {},
                valid_from=alert.valid_from,
                valid_until=alert.valid_until,
                created_at=alert.created_at,
                updated_at=alert.updated_at
            )
            for alert in items
        ]
        
        # 创建分页响应
        paginated_data = create_paginated_response(
            items=alert_responses,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
        
        return create_success_response(
            data=paginated_data.dict(),
            message=f"成功获取 {len(items)} 条预警记录"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="参数验证失败",
                errors=[{"field": "params", "message": str(e)}]
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="获取预警列表失败",
                errors=[{"error": str(e)}]
            ).dict()
        )

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
    user_id: int = Path(..., gt=0, description="用户ID")
):
    """
    获取用户活跃预警数量
    """
    try:
        count = await global_alert_service.count_active_alerts(user_id)
        return create_success_response(
            data={"user_id": user_id, "active_alerts_count": count},
            message="成功获取活跃预警数量"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="获取活跃预警数量失败",
                errors=[{"error": str(e)}]
            ).dict()
        )


@router.get("/statistics", response_model=APIResponse)
async def get_alert_statistics():
    """
    获取预警系统统计信息
    
    - 总预警数、活跃数、触发数
    - Top 5 触发类型
    - Top 5 触发交易对
    - 历史记录数量
    """
    try:
        stats = global_alert_service.get_alert_statistics()
        return create_success_response(
            data=stats,
            message="成功获取预警统计信息"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="获取统计信息失败",
                errors=[{"error": str(e)}]
            ).dict()
        )


@router.get("/triggers/recent", response_model=APIResponse)
async def get_recent_triggers(
    limit: int = Query(20, ge=1, le=100, description="返回数量")
):
    """
    获取最近的预警触发记录
    """
    try:
        triggers = global_alert_service.get_recent_triggers(limit)
        return create_success_response(
            data={"triggers": triggers, "count": len(triggers)},
            message=f"成功获取最近 {len(triggers)} 条触发记录"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="获取触发记录失败",
                errors=[{"error": str(e)}]
            ).dict()
        )


@router.get("/{alert_id}/performance", response_model=APIResponse)
async def get_alert_performance(
    alert_id: int = Path(..., gt=0, description="预警ID")
):
    """
    获取单个预警的性能指标
    
    - 总触发次数
    - 平均触发间隔
    - 首次/最后触发时间
    """
    try:
        performance = await global_alert_service.get_alert_performance(alert_id)
        return create_success_response(
            data=performance,
            message="成功获取预警性能指标"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="获取性能指标失败",
                errors=[{"error": str(e)}]
            ).dict()
        )


@router.post("/triggers/{trigger_id}/mark-false", response_model=APIResponse)
async def mark_false_trigger(
    trigger_id: int = Path(..., gt=0, description="触发记录ID")
):
    """
    标记误报
    """
    try:
        await global_alert_service.mark_false_trigger(trigger_id)
        return create_success_response(
            data={"trigger_id": trigger_id},
            message="成功标记误报"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                message="标记误报失败",
                errors=[{"error": str(e)}]
            ).dict()
        )

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
