# 寰宇多市场金融监控系统 - Telegram管理API
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# 导入Telegram服务
try:
    from services.telegram_service import telegram_service
    logger.info("✅ Telegram机器人服务导入成功")
except ImportError as e:
    logger.error(f"❌ Telegram机器人服务导入失败: {e}")
    telegram_service = None

# 数据模型
class TelegramConfigResponse(BaseModel):
    enabled: bool
    bot_token_configured: bool
    chat_ids_configured: bool
    chat_ids_count: int

class TelegramBotInfoResponse(BaseModel):
    enabled: bool
    bot_username: Optional[str] = None
    bot_name: Optional[str] = None
    chat_ids_count: int
    configured: bool
    error: Optional[str] = None

class TelegramTestMessage(BaseModel):
    message: str = "这是一条测试消息"
    chat_ids: Optional[List[str]] = None

# 创建路由
router = APIRouter()

@router.get("/alerts/telegram/config", response_model=TelegramConfigResponse, operation_id="get_telegram_config")
async def get_telegram_config():
    """获取Telegram配置状态"""
    if not telegram_service:
        raise HTTPException(status_code=503, detail="Telegram服务不可用")
    
    return telegram_service.get_config_status()

@router.get("/alerts/telegram/bot-info", response_model=TelegramBotInfoResponse, operation_id="get_telegram_bot_info")
async def get_telegram_bot_info():
    """获取Telegram机器人信息"""
    if not telegram_service:
        raise HTTPException(status_code=503, detail="Telegram服务不可用")
    
    return await telegram_service.get_bot_info()

@router.post("/alerts/telegram/test", operation_id="test_telegram_notification")
async def test_telegram_notification(test_data: TelegramTestMessage):
    """测试Telegram通知"""
    if not telegram_service:
        raise HTTPException(status_code=503, detail="Telegram服务不可用")
    
    try:
        success = await telegram_service.send_system_notification(
            test_data.message, 
            test_data.chat_ids
        )
        
        if success:
            return {"message": "Telegram测试消息发送成功", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="发送Telegram测试消息失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送Telegram测试消息失败: {str(e)}")

@router.post("/alerts/telegram/test-alert", operation_id="test_telegram_alert")
async def test_telegram_alert(chat_ids: Optional[str] = None):
    """测试Telegram预警通知"""
    if not telegram_service:
        raise HTTPException(status_code=503, detail="Telegram服务不可用")
    
    try:
        test_alert = {
            'symbol': 'BTC/USDT',
            'condition': 'above',
            'threshold': 100000,
            'current_price': 113423.90,
            'previous_price': 111500.00,
            'message': '这是测试预警消息 - Telegram通知测试',
            'triggered_time': '2024-01-01T12:00:00'
        }

        target_chat_ids = chat_ids.split(',') if chat_ids else None
        success = await telegram_service.send_alert_notification(test_alert, target_chat_ids)
        
        if success:
            return {"message": "Telegram预警测试消息发送成功", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="发送Telegram预警测试消息失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送Telegram预警测试消息失败: {str(e)}")
