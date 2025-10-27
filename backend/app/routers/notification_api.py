"""
通知系统API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
import logging
from services.notification_service import notification_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/notification", tags=["通知系统"])

@router.get("/health")
async def notification_health():
    """通知服务健康检查"""
    status = notification_service.get_status()
    return {
        "service": "notification",
        "status": "healthy" if notification_service.is_initialized else "initializing",
        "config": status
    }

@router.post("/email")
async def send_email_notification(
    to_email: str,
    subject: str,
    content: str,
    is_html: bool = False
):
    """发送邮件通知"""
    try:
        result = await notification_service.send_email(to_email, subject, content, is_html)
        return {
            "service": "email",
            "result": result
        }
    except Exception as e:
        logger.error(f"发送邮件通知异常: {e}")
        raise HTTPException(status_code=500, detail=f"发送邮件失败: {str(e)}")

@router.post("/telegram")
async def send_telegram_notification(
    message: str,
    parse_mode: str = "HTML"
):
    """发送Telegram通知"""
    try:
        result = await notification_service.send_telegram(message, parse_mode)
        return {
            "service": "telegram", 
            "result": result
        }
    except Exception as e:
        logger.error(f"发送Telegram通知异常: {e}")
        raise HTTPException(status_code=500, detail=f"发送Telegram失败: {str(e)}")

@router.post("/market-alert")
async def send_market_alert(
    symbol: str,
    price: float,
    change_percent: float,
    alert_type: str = "price_alert"
):
    """发送市场警报"""
    try:
        results = await notification_service.send_market_alert(symbol, price, change_percent, alert_type)
        return {
            "service": "market_alert",
            "alert_type": alert_type,
            "symbol": symbol,
            "results": results
        }
    except Exception as e:
        logger.error(f"发送市场警报异常: {e}")
        raise HTTPException(status_code=500, detail=f"发送市场警报失败: {str(e)}")

@router.post("/system-alert")
async def send_system_alert(
    title: str,
    message: str,
    level: str = "info"
):
    """发送系统警报"""
    try:
        results = await notification_service.send_system_alert(title, message, level)
        return {
            "service": "system_alert",
            "level": level,
            "title": title,
            "results": results
        }
    except Exception as e:
        logger.error(f"发送系统警报异常: {e}")
        raise HTTPException(status_code=500, detail=f"发送系统警报失败: {str(e)}")

@router.get("/test")
async def test_notification():
    """测试通知系统"""
    try:
        # 测试邮件
        email_result = await notification_service.send_email(
            notification_service.smtp_config["from_email"],
            "OmniMarket 测试邮件",
            "这是一封来自 OmniMarket 金融监控系统的测试邮件。\n\n如果收到此邮件，说明邮件通知配置正确！",
            is_html=False
        )
        
        # 测试Telegram
        telegram_result = await notification_service.send_telegram(
            "🔔 <b>OmniMarket 测试消息</b>\n\n这是一条来自 OmniMarket 金融监控系统的测试消息。\n\n如果收到此消息，说明 Telegram 通知配置正确！"
        )
        
        return {
            "service": "notification_test",
            "results": {
                "email": email_result,
                "telegram": telegram_result
            }
        }
    except Exception as e:
        logger.error(f"测试通知系统异常: {e}")
        raise HTTPException(status_code=500, detail=f"测试通知系统失败: {str(e)}")

@router.get("/status")
async def get_notification_status():
    """获取通知系统状态"""
    return {
        "service": "notification",
        "status": notification_service.get_status()
    }
