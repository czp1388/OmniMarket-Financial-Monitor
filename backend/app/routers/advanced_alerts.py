# 寰宇多市场金融监控系统 - 高级预警管理API
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# 导入高级预警服务
try:
    from services.advanced_alert_service import advanced_alert_service
    logger.info("✅ 高级预警服务导入成功")
except ImportError as e:
    logger.error(f"❌ 高级预警服务导入失败: {e}")
    advanced_alert_service = None

# 数据模型
class AlertRuleCreate(BaseModel):
    symbol: str
    condition: str  # "above", "below", "change_up", "change_down"
    threshold: float
    notification_type: str = "log"

class AlertRuleResponse(BaseModel):
    symbol: str
    condition: str
    threshold: float
    notification_type: str
    triggered: bool
    created_at: str
    last_triggered: Optional[str]

# 创建路由
router = APIRouter()

@router.post("/alerts/rules", response_model=dict, operation_id="create_alert_rule_advanced")
async def create_alert_rule(rule: AlertRuleCreate):
    """创建预警规则"""
    if not advanced_alert_service:
        raise HTTPException(status_code=503, detail="预警服务不可用")
    
    try:
        result = advanced_alert_service.add_alert_rule(
            symbol=rule.symbol,
            condition=rule.condition,
            threshold=rule.threshold,
            notification_type=rule.notification_type
        )
        return {"message": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建预警规则失败: {str(e)}")

@router.delete("/alerts/rules", operation_id="delete_alert_rule_advanced")
async def delete_alert_rule(symbol: str, condition: str, threshold: float):
    """删除预警规则"""
    if not advanced_alert_service:
        raise HTTPException(status_code=503, detail="预警服务不可用")
    
    success = advanced_alert_service.remove_alert_rule(symbol, condition, threshold)
    if success:
        return {"message": "预警规则已删除", "status": "success"}
    else:
        raise HTTPException(status_code=404, detail="未找到匹配的预警规则")

@router.get("/alerts/rules", response_model=List[AlertRuleResponse], operation_id="get_alert_rules_advanced")
async def get_alert_rules():
    """获取所有预警规则"""
    if not advanced_alert_service:
        raise HTTPException(status_code=503, detail="预警服务不可用")
    
    return advanced_alert_service.get_alert_rules()

@router.post("/alerts/start-monitoring", operation_id="start_alert_monitoring_advanced")
async def start_alert_monitoring():
    """开始预警监控"""
    if not advanced_alert_service:
        raise HTTPException(status_code=503, detail="预警服务不可用")
    
    try:
        from services.real_exchange_service import real_data_service
        await advanced_alert_service.start_monitoring(real_data_service)
        return {"message": "预警监控已启动", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动预警监控失败: {str(e)}")

@router.post("/alerts/stop-monitoring", operation_id="stop_alert_monitoring_advanced")
async def stop_alert_monitoring():
    """停止预警监控"""
    if not advanced_alert_service:
        raise HTTPException(status_code=503, detail="预警服务不可用")
    
    try:
        await advanced_alert_service.stop_monitoring()
        return {"message": "预警监控已停止", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止预警监控失败: {str(e)}")

@router.get("/alerts/status", operation_id="get_alert_status_advanced")
async def get_alert_status():
    """获取预警服务状态"""
    if not advanced_alert_service:
        return {
            "status": "unavailable",
            "message": "预警服务不可用",
            "monitoring": False,
            "rule_count": 0
        }
    
    return {
        "status": "available",
        "message": "预警服务运行正常",
        "monitoring": advanced_alert_service.is_monitoring,
        "rule_count": len(advanced_alert_service.alert_rules)
    }
