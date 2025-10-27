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

# 导入邮件服务
try:
    from services.email_service import email_service
    logger.info("✅ 邮件通知服务导入成功")
except ImportError as e:
    logger.error(f"❌ 邮件通知服务导入失败: {e}")
    email_service = None

# 数据模型
class AlertRuleCreate(BaseModel):
    symbol: str
    condition: str  # "above", "below", "change_up", "change_down"
    threshold: float
    notification_type: str = "log"
    email_recipients: Optional[List[str]] = None

class AlertRuleResponse(BaseModel):
    symbol: str
    condition: str
    threshold: float
    notification_type: str
    email_recipients: List[str]
    triggered: bool
    created_at: str
    last_triggered: Optional[str]

class AlertHistoryResponse(BaseModel):
    id: int
    symbol: str
    condition: str
    threshold: float
    current_price: float
    previous_price: float
    message: str
    triggered_time: str

class EmailConfigResponse(BaseModel):
    enabled: bool
    smtp_server: str
    sender_email: str
    configured: bool

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
            notification_type=rule.notification_type,
            email_recipients=rule.email_recipients or []
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

@router.get("/alerts/history", response_model=List[AlertHistoryResponse], operation_id="get_alert_history")
async def get_alert_history(limit: int = 50, symbol: Optional[str] = None):
    """获取预警历史记录"""
    if not advanced_alert_service:
        raise HTTPException(status_code=503, detail="预警服务不可用")
    
    return advanced_alert_service.get_alert_history(limit, symbol)

@router.get("/alerts/email/config", response_model=EmailConfigResponse, operation_id="get_email_config")
async def get_email_config():
    """获取邮件配置状态"""
    if not email_service:
        raise HTTPException(status_code=503, detail="邮件服务不可用")
    
    return email_service.get_config_status()

@router.post("/alerts/test-email", operation_id="test_email_notification")
async def test_email_notification(email: str):
    """测试邮件通知"""
    if not email_service:
        raise HTTPException(status_code=503, detail="邮件服务不可用")
    
    try:
        test_alert = {
            'symbol': 'BTC/USDT',
            'condition': 'above',
            'threshold': 100000,
            'current_price': 113423.90,
            'previous_price': 111500.00,
            'message': '这是测试预警消息',
            'triggered_time': '2024-01-01T12:00:00'
        }
        
        success = await email_service.send_alert_notification(test_alert, [email])
        if success:
            return {"message": f"测试邮件已发送到 {email}", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="发送测试邮件失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送测试邮件失败: {str(e)}")

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
            "rule_count": 0,
            "history_count": 0
        }
    
    # 获取历史记录数量
    history_count = len(advanced_alert_service.get_alert_history(limit=1000))
    
    return {
        "status": "available",
        "message": "预警服务运行正常",
        "monitoring": advanced_alert_service.is_monitoring,
        "rule_count": len(advanced_alert_service.alert_rules),
        "history_count": history_count
    }
