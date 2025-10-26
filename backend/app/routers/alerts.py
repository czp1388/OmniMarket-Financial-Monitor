from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import asyncio

router = APIRouter()

# 模拟预警规则存储（实际项目中应该用数据库）
alert_rules = []

@router.post("/alerts/")
async def create_alert(
    symbol: str,
    condition: str,  # "above", "below"
    price: float,
    email: str = None
):
    """创建价格预警"""
    alert_rule = {
        "id": len(alert_rules) + 1,
        "symbol": symbol,
        "condition": condition,
        "price": price,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "active": True
    }
    
    alert_rules.append(alert_rule)
    
    return {
        "message": "预警创建成功",
        "alert": alert_rule
    }

@router.get("/alerts/")
async def get_alerts():
    """获取所有预警规则"""
    return {
        "alerts": alert_rules,
        "count": len(alert_rules)
    }

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int):
    """删除预警规则"""
    global alert_rules
    alert_rules = [alert for alert in alert_rules if alert["id"] != alert_id]
    
    return {"message": f"预警 {alert_id} 已删除"}

@router.get("/alerts/status")
async def get_alerts_status():
    """获取预警系统状态"""
    active_alerts = [alert for alert in alert_rules if alert["active"]]
    
    return {
        "total_alerts": len(alert_rules),
        "active_alerts": len(active_alerts),
        "system_status": "运行中"
    }
