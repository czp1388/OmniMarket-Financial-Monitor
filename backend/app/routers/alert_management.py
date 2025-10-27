# 预警管理API路由
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
import logging
from services.alert_engine import alert_engine
from models.alert_models import (
    AlertRuleCreate, AlertRuleResponse, AlertHistoryResponse, AlertTriggerRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/alerts", tags=["alert_management"])

@router.get("/health")
async def alert_service_health():
    """预警服务健康检查"""
    return {
        "service": "alert_engine",
        "status": "healthy",
        "active_rules": len(alert_engine.alert_rules),
        "total_triggers": len(alert_engine.alert_history)
    }

@router.post("/rules", response_model=dict)
async def create_alert_rule(rule: AlertRuleCreate):
    """创建预警规则"""
    try:
        rule_data = rule.dict()
        rule_id = await alert_engine.add_alert_rule(rule_data)
        
        if rule_id > 0:
            return {
                "success": True,
                "rule_id": rule_id,
                "message": "预警规则创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail="创建预警规则失败")
            
    except Exception as e:
        logger.error(f"创建预警规则API异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/rules", response_model=dict)
async def get_alert_rules(
    symbol: Optional[str] = Query(None, description="筛选指定交易对"),
    enabled: Optional[bool] = Query(None, description="筛选启用状态")
):
    """获取预警规则列表"""
    try:
        rules = await alert_engine.get_alert_rules(symbol)
        
        # 过滤启用状态
        if enabled is not None:
            rules = [rule for rule in rules if rule["enabled"] == enabled]
            
        return {
            "count": len(rules),
            "rules": rules
        }
        
    except Exception as e:
        logger.error(f"获取预警规则列表异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/rules/{rule_id}", response_model=dict)
async def get_alert_rule(rule_id: int):
    """获取特定预警规则"""
    try:
        rules = await alert_engine.get_alert_rules()
        rule = next((r for r in rules if r["id"] == rule_id), None)
        
        if rule:
            return {"rule": rule}
        else:
            raise HTTPException(status_code=404, detail="预警规则不存在")
            
    except Exception as e:
        logger.error(f"获取预警规则异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.put("/rules/{rule_id}", response_model=dict)
async def update_alert_rule(rule_id: int, updates: dict = Body(...)):
    """更新预警规则"""
    try:
        success = await alert_engine.update_alert_rule(rule_id, updates)
        
        if success:
            return {
                "success": True,
                "message": "预警规则更新成功"
            }
        else:
            raise HTTPException(status_code=404, detail="预警规则不存在")
            
    except Exception as e:
        logger.error(f"更新预警规则异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.delete("/rules/{rule_id}", response_model=dict)
async def delete_alert_rule(rule_id: int):
    """删除预警规则"""
    try:
        success = await alert_engine.delete_alert_rule(rule_id)
        
        if success:
            return {
                "success": True,
                "message": "预警规则删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="预警规则不存在")
            
    except Exception as e:
        logger.error(f"删除预警规则异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/history", response_model=dict)
async def get_alert_history(
    rule_id: Optional[int] = Query(None, description="筛选特定规则"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制")
):
    """获取预警历史"""
    try:
        history = await alert_engine.get_alert_history(rule_id, limit)
        
        return {
            "count": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"获取预警历史异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.post("/test-trigger", response_model=dict)
async def test_alert_trigger(request: AlertTriggerRequest):
    """测试预警触发（开发用途）"""
    try:
        market_data = {
            "close_price": request.current_price,
            "volume": request.volume
        }
        
        triggered_alerts = await alert_engine.evaluate_alert_conditions(
            request.symbol, market_data, request.indicators
        )
        
        return {
            "triggered_count": len(triggered_alerts),
            "triggered_alerts": triggered_alerts
        }
        
    except Exception as e:
        logger.error(f"测试预警触发异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.post("/rules/{rule_id}/enable", response_model=dict)
async def enable_alert_rule(rule_id: int):
    """启用预警规则"""
    return await update_alert_rule(rule_id, {"enabled": True})

@router.post("/rules/{rule_id}/disable", response_model=dict)
async def disable_alert_rule(rule_id: int):
    """禁用预警规则"""
    return await update_alert_rule(rule_id, {"enabled": False})
