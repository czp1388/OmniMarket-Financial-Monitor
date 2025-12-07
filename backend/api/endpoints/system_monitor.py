"""
系统监控API端点
提供缓存性能、服务健康状态等监控信息
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from services.data_cache_service import data_cache_service
from services.data_quality_monitor import data_quality_monitor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """
    获取缓存性能统计
    
    Returns:
        缓存统计信息，包括命中率、总请求数、缓存键数量等
    """
    try:
        stats = data_cache_service.get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/reset-stats")
async def reset_cache_stats():
    """
    重置缓存性能统计（用于调试或定期重置）
    
    Returns:
        操作结果
    """
    try:
        data_cache_service.reset_stats()
        return {
            "status": "success",
            "message": "缓存统计已重置"
        }
    except Exception as e:
        logger.error(f"重置缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-quality/stats", response_model=Dict[str, Any])
async def get_data_quality_stats():
    """
    获取数据质量监控统计
    
    Returns:
        数据源质量统计，包括成功率、错误数、平均延迟等
    """
    try:
        stats = data_quality_monitor.get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取数据质量统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    系统健康检查端点
    
    Returns:
        系统健康状态
    """
    try:
        cache_stats = data_cache_service.get_stats()
        data_quality_stats = data_quality_monitor.get_stats()
        
        # 判断健康状态
        cache_hit_rate = cache_stats.get('performance', {}).get('hit_rate', '0%')
        hit_rate_value = float(cache_hit_rate.rstrip('%'))
        
        health_status = "healthy"
        issues = []
        
        # 检查缓存命中率（低于30%可能需要调整）
        if hit_rate_value < 30.0 and cache_stats['performance']['total_requests'] > 100:
            issues.append("缓存命中率偏低，建议检查缓存策略")
            health_status = "warning"
        
        # 检查过期缓存数量
        if cache_stats['expired_keys'] > cache_stats['valid_keys']:
            issues.append("过期缓存数量过多，清理机制可能需要优化")
            health_status = "warning"
        
        return {
            "status": "success",
            "data": {
                "health_status": health_status,
                "timestamp": cache_stats.get('timestamp', 'N/A'),
                "cache": {
                    "total_keys": cache_stats['total_keys'],
                    "hit_rate": cache_hit_rate,
                    "total_requests": cache_stats['performance']['total_requests']
                },
                "data_quality": {
                    "total_sources": len(data_quality_stats),
                    "sources": data_quality_stats
                },
                "issues": issues
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "error",
            "data": {
                "health_status": "unhealthy",
                "error": str(e)
            }
        }
