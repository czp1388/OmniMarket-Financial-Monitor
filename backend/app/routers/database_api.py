# 寰宇多市场金融监控系统 - 数据库管理API
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 导入数据库服务
try:
    from services.database_service import database_service
    logger.info("✅ 数据库服务导入成功")
except ImportError as e:
    logger.error(f"❌ 数据库服务导入失败: {e}")
    database_service = None

# 数据模型
class AlertRuleCreate(BaseModel):
    symbol: str
    condition: str
    threshold: float
    notification_type: str = "log"
    email_recipients: Optional[List[str]] = None
    telegram_chat_ids: Optional[List[str]] = None
    is_active: bool = True

class AlertRuleResponse(BaseModel):
    id: int
    symbol: str
    condition: str
    threshold: float
    notification_type: str
    email_recipients: List[str]
    telegram_chat_ids: List[str]
    is_active: bool
    created_at: str
    updated_at: Optional[str]

class AlertHistoryResponse(BaseModel):
    id: int
    rule_id: int
    symbol: str
    condition: str
    threshold: float
    current_price: float
    previous_price: float
    message: str
    notification_type: str
    triggered_time: str

class AlertStatsResponse(BaseModel):
    total_count: int
    symbol_stats: Dict[str, int]
    notification_stats: Dict[str, int]
    period_days: int

class DatabaseStatsResponse(BaseModel):
    alert_rules_count: int
    alert_history_count: int
    market_data_count: int
    system_config_count: int
    database_size: str

class SystemConfigResponse(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str]
    updated_at: str

# 创建路由
router = APIRouter()

# 预警规则管理API
@router.post("/database/alert-rules", response_model=AlertRuleResponse, operation_id="create_alert_rule_db")
async def create_alert_rule(rule: AlertRuleCreate):
    """创建预警规则（数据库版本）"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        rule_data = {
            'symbol': rule.symbol,
            'condition': rule.condition,
            'threshold': rule.threshold,
            'notification_type': rule.notification_type,
            'email_recipients': rule.email_recipients or [],
            'telegram_chat_ids': rule.telegram_chat_ids or [],
            'is_active': rule.is_active
        }
        
        db_rule = database_service.create_alert_rule(rule_data)
        if not db_rule:
            raise HTTPException(status_code=500, detail="创建预警规则失败")
        
        return {
            "id": db_rule.id,
            "symbol": db_rule.symbol,
            "condition": db_rule.condition,
            "threshold": db_rule.threshold,
            "notification_type": db_rule.notification_type,
            "email_recipients": db_rule.email_recipients or [],
            "telegram_chat_ids": db_rule.telegram_chat_ids or [],
            "is_active": db_rule.is_active,
            "created_at": db_rule.created_at.isoformat(),
            "updated_at": db_rule.updated_at.isoformat() if db_rule.updated_at else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建预警规则失败: {str(e)}")

@router.get("/database/alert-rules", response_model=List[AlertRuleResponse], operation_id="get_alert_rules_db")
async def get_alert_rules(active_only: bool = True):
    """获取所有预警规则（数据库版本）"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        db_rules = database_service.get_alert_rules(active_only=active_only)
        
        return [{
            "id": rule.id,
            "symbol": rule.symbol,
            "condition": rule.condition,
            "threshold": rule.threshold,
            "notification_type": rule.notification_type,
            "email_recipients": rule.email_recipients or [],
            "telegram_chat_ids": rule.telegram_chat_ids or [],
            "is_active": rule.is_active,
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
        } for rule in db_rules]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警规则失败: {str(e)}")

@router.get("/database/alert-rules/{rule_id}", response_model=AlertRuleResponse, operation_id="get_alert_rule_by_id")
async def get_alert_rule_by_id(rule_id: int):
    """根据ID获取预警规则"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        rule = database_service.get_alert_rule_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="预警规则不存在")
        
        return {
            "id": rule.id,
            "symbol": rule.symbol,
            "condition": rule.condition,
            "threshold": rule.threshold,
            "notification_type": rule.notification_type,
            "email_recipients": rule.email_recipients or [],
            "telegram_chat_ids": rule.telegram_chat_ids or [],
            "is_active": rule.is_active,
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警规则失败: {str(e)}")

@router.put("/database/alert-rules/{rule_id}", operation_id="update_alert_rule")
async def update_alert_rule(rule_id: int, rule_update: AlertRuleCreate):
    """更新预警规则"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        update_data = {
            'symbol': rule_update.symbol,
            'condition': rule_update.condition,
            'threshold': rule_update.threshold,
            'notification_type': rule_update.notification_type,
            'email_recipients': rule_update.email_recipients or [],
            'telegram_chat_ids': rule_update.telegram_chat_ids or [],
            'is_active': rule_update.is_active
        }
        
        success = database_service.update_alert_rule(rule_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="预警规则不存在或更新失败")
        
        return {"message": "预警规则更新成功", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新预警规则失败: {str(e)}")

@router.delete("/database/alert-rules/{rule_id}", operation_id="delete_alert_rule_db")
async def delete_alert_rule(rule_id: int):
    """删除预警规则"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        success = database_service.delete_alert_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail="预警规则不存在")
        
        return {"message": "预警规则删除成功", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除预警规则失败: {str(e)}")

# 预警历史API
@router.get("/database/alert-history", response_model=List[AlertHistoryResponse], operation_id="get_alert_history_db")
async def get_alert_history(limit: int = 50, symbol: Optional[str] = None, days: int = 7):
    """获取预警历史记录（数据库版本）"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        history = database_service.get_alert_history(limit=limit, symbol=symbol, days=days)
        
        return [{
            "id": record.id,
            "rule_id": record.rule_id,
            "symbol": record.symbol,
            "condition": record.condition,
            "threshold": record.threshold,
            "current_price": record.current_price,
            "previous_price": record.previous_price,
            "message": record.message,
            "notification_type": record.notification_type,
            "triggered_time": record.triggered_at.isoformat()
        } for record in history]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警历史失败: {str(e)}")

@router.get("/database/alert-stats", response_model=AlertStatsResponse, operation_id="get_alert_stats")
async def get_alert_stats(days: int = 7):
    """获取预警统计信息"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        stats = database_service.get_alert_stats(days=days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警统计失败: {str(e)}")

# 数据库管理API
@router.get("/database/stats", response_model=DatabaseStatsResponse, operation_id="get_database_stats")
async def get_database_stats():
    """获取数据库统计信息"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        stats = database_service.get_database_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库统计失败: {str(e)}")

@router.post("/database/cleanup", operation_id="cleanup_database")
async def cleanup_database(days: int = 30):
    """清理旧的历史记录"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        deleted_count = database_service.cleanup_old_history(days=days)
        return {
            "message": f"清理了 {deleted_count} 条旧历史记录",
            "deleted_count": deleted_count,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理数据库失败: {str(e)}")

# 系统配置API
@router.get("/database/config", response_model=Dict[str, str], operation_id="get_all_configs")
async def get_all_configs():
    """获取所有系统配置"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        configs = database_service.get_all_configs()
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")

@router.get("/database/config/{config_key}", operation_id="get_config")
async def get_config(config_key: str, default: Optional[str] = None):
    """获取特定系统配置"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        value = database_service.get_config(config_key, default)
        return {"config_key": config_key, "config_value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")

@router.put("/database/config/{config_key}", operation_id="set_config")
async def set_config(config_key: str, config_value: str, description: Optional[str] = None):
    """设置系统配置"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        success = database_service.set_config(config_key, config_value, description)
        if not success:
            raise HTTPException(status_code=500, detail="设置系统配置失败")
        
        return {"message": "系统配置更新成功", "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置系统配置失败: {str(e)}")

# 数据库状态检查
@router.get("/database/status", operation_id="get_database_status")
async def get_database_status():
    """获取数据库状态"""
    if not database_service:
        return {
            "status": "unavailable",
            "message": "数据库服务不可用",
            "initialized": False
        }
    
    return {
        "status": "available",
        "message": "数据库服务运行正常",
        "initialized": database_service.is_initialized,
        "using_database": database_service.is_initialized
    }
