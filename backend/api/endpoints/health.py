"""
健康检查 API 端点
用于 Docker 健康检查和系统监控
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

router = APIRouter(tags=["Health"])


@router.get("/health", summary="健康检查")
async def health_check() -> Dict[str, Any]:
    """
    系统健康检查端点
    
    返回:
        - status: 服务状态 (healthy/unhealthy)
        - timestamp: 当前时间戳
        - version: API版本
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "OmniMarket Financial Monitor"
    }


@router.get("/health/ready", summary="就绪检查")
async def readiness_check() -> Dict[str, Any]:
    """
    服务就绪检查
    
    检查服务是否准备好接收请求
    """
    # TODO: 添加数据库连接检查
    # TODO: 添加缓存连接检查
    
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok",  # 简化版本，实际应检查连接
            "cache": "ok",
            "services": "ok"
        }
    }


@router.get("/health/live", summary="存活检查")
async def liveness_check() -> Dict[str, Any]:
    """
    服务存活检查
    
    检查服务是否存活（简单响应）
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
