"""
系统监控API端点
提供系统性能、健康状态、日志查询等功能
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from backend.services.performance_monitor import performance_monitor
from backend.services.data_quality_monitor import data_quality_monitor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", summary="系统健康检查")
async def health_check() -> Dict[str, Any]:
    """
    系统健康检查端点
    返回所有服务的健康状态
    """
    try:
        services_health = performance_monitor.get_all_services_health()
        system_metrics = performance_monitor.get_system_metrics()
        
        # 判断整体状态
        unhealthy_count = sum(1 for s in services_health if s['status'] == 'unhealthy')
        degraded_count = sum(1 for s in services_health if s['status'] == 'degraded')
        
        if unhealthy_count > 0:
            overall_status = "unhealthy"
        elif degraded_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": services_health,
            "system": system_metrics,
            "summary": {
                "total_services": len(services_health),
                "healthy": sum(1 for s in services_health if s['status'] == 'healthy'),
                "degraded": degraded_count,
                "unhealthy": unhealthy_count
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail="健康检查失败")


@router.get("/metrics", summary="系统指标")
async def get_metrics(
    metric_name: Optional[str] = Query(None, description="指标名称"),
    window_seconds: int = Query(300, ge=60, le=3600, description="时间窗口(秒)")
) -> Dict[str, Any]:
    """
    获取系统性能指标
    
    - **metric_name**: 指定指标名称，不指定则返回所有
    - **window_seconds**: 时间窗口，默认300秒
    """
    try:
        if metric_name:
            summary = performance_monitor.get_metric_summary(metric_name, window_seconds)
            return {
                "metric_name": metric_name,
                "window_seconds": window_seconds,
                "summary": summary
            }
        else:
            # 返回仪表板数据
            return performance_monitor.get_dashboard_data()
    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        raise HTTPException(status_code=500, detail="获取指标失败")


@router.get("/data-quality", summary="数据质量报告")
async def get_data_quality() -> Dict[str, Any]:
    """
    获取数据质量报告
    包含所有数据源的状态、错误率、响应时间等
    """
    try:
        report = data_quality_monitor.get_quality_report()
        return {
            "timestamp": datetime.now().isoformat(),
            "sources": report
        }
    except Exception as e:
        logger.error(f"获取数据质量报告失败: {e}")
        raise HTTPException(status_code=500, detail="获取数据质量报告失败")


@router.get("/services/{service_name}/health", summary="单个服务健康状态")
async def get_service_health(service_name: str) -> Dict[str, Any]:
    """获取指定服务的健康状态"""
    try:
        health = performance_monitor.get_service_health(service_name)
        if health is None:
            raise HTTPException(status_code=404, detail=f"服务 {service_name} 未找到")
        
        return {
            "service_name": service_name,
            "health": health,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取服务健康状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取服务健康状态失败")


@router.get("/stats/summary", summary="统计摘要")
async def get_stats_summary() -> Dict[str, Any]:
    """
    获取系统统计摘要
    包含请求总数、错误率、平均响应时间等关键指标
    """
    try:
        services = performance_monitor.get_all_services_health()
        
        total_requests = sum(s['success_count'] + s['error_count'] for s in services)
        total_errors = sum(s['error_count'] for s in services)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "services_count": len(services),
            "avg_response_time": sum(s['avg_response_time'] for s in services) / len(services) if services else 0
        }
    except Exception as e:
        logger.error(f"获取统计摘要失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计摘要失败")


@router.post("/services/{service_name}/reset", summary="重置服务统计")
async def reset_service_stats(service_name: str) -> Dict[str, str]:
    """重置指定服务的统计数据"""
    try:
        if service_name in performance_monitor.services:
            health = performance_monitor.services[service_name]
            health.error_count = 0
            health.success_count = 0
            health.avg_response_time = 0
            health.last_error = None
            health.status = "healthy"
            
            return {
                "status": "success",
                "message": f"服务 {service_name} 统计已重置"
            }
        else:
            raise HTTPException(status_code=404, detail=f"服务 {service_name} 未找到")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置服务统计失败: {e}")
        raise HTTPException(status_code=500, detail="重置服务统计失败")
