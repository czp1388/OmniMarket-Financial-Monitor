from fastapi import APIRouter, HTTPException
from typing import List, Dict
import sys
import os

# 添加服务路径
sys.path.append(os.path.dirname(__file__))
try:
    from services.alert_service import alert_service, AlertRule
    print("✅ 预警路由成功导入预警服务")
except ImportError as e:
    print(f"❌ 预警路由导入失败: {e}")
    alert_service = None

router = APIRouter(prefix="/alerts", tags=["预警管理"])

@router.get("/")
async def get_alerts():
    """获取所有预警规则"""
    if alert_service:
        return list(alert_service.rules.values())
    return []

@router.post("/")
async def create_alert(rule_data: Dict):
    """创建预警规则"""
    if not alert_service:
        raise HTTPException(status_code=500, detail="预警服务未就绪")
    
    try:
        rule = AlertRule(
            id=rule_data.get("id", str(len(alert_service.rules) + 1)),
            name=rule_data["name"],
            condition=rule_data["condition"],
            target=rule_data["target"],
            enabled=rule_data.get("enabled", True)
        )
        alert_service.add_rule(rule)
        return {"message": "预警规则创建成功", "rule": rule.__dict__}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建预警规则失败: {e}")

@router.delete("/{rule_id}")
async def delete_alert(rule_id: str):
    """删除预警规则"""
    if alert_service:
        alert_service.remove_rule(rule_id)
    return {"message": "预警规则删除成功"}

@router.put("/{rule_id}/toggle")
async def toggle_alert(rule_id: str):
    """切换预警规则状态"""
    if alert_service and rule_id in alert_service.rules:
        rule = alert_service.rules[rule_id]
        rule.enabled = not rule.enabled
        return {"message": "预警规则状态已更新", "enabled": rule.enabled}
    else:
        raise HTTPException(status_code=404, detail="预警规则不存在")

@router.get("/status")
async def get_alert_status():
    """获取预警服务状态"""
    if alert_service:
        return {
            "is_monitoring": alert_service.is_monitoring,
            "total_rules": len(alert_service.rules),
            "active_rules": len([r for r in alert_service.rules.values() if r.enabled])
        }
    return {
        "is_monitoring": False,
        "total_rules": 0,
        "active_rules": 0
    }
