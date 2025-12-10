"""
性能监控服务
用于跟踪系统性能指标、服务健康状态和资源使用情况
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """单个指标数据点"""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """服务健康状态"""
    service_name: str
    status: str  # healthy, degraded, unhealthy
    last_check: float
    error_count: int = 0
    success_count: int = 0
    avg_response_time: float = 0
    last_error: Optional[str] = None


class PerformanceMonitor:
    """性能监控器 - 单例"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # 指标存储 (使用deque限制内存使用)
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # 服务健康状态
        self.services: Dict[str, ServiceHealth] = {}
        
        # 系统资源监控
        self.system_metrics = {
            'cpu_percent': deque(maxlen=100),
            'memory_percent': deque(maxlen=100),
            'disk_usage': deque(maxlen=100),
            'network_io': deque(maxlen=100)
        }
        
        # 监控任务
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        logger.info("PerformanceMonitor 初始化完成")
    
    async def start(self):
        """启动性能监控"""
        if self.is_running:
            logger.warning("性能监控已在运行中")
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("性能监控已启动")
    
    async def stop(self):
        """停止性能监控"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("性能监控已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 收集系统指标
                await self._collect_system_metrics()
                
                # 检查服务健康状态
                self._check_services_health()
                
                # 每5秒执行一次
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            timestamp = time.time()
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.system_metrics['cpu_percent'].append(
                MetricPoint(timestamp, cpu_percent)
            )
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self.system_metrics['memory_percent'].append(
                MetricPoint(timestamp, memory.percent)
            )
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            self.system_metrics['disk_usage'].append(
                MetricPoint(timestamp, disk.percent)
            )
            
            # 网络IO
            net_io = psutil.net_io_counters()
            self.system_metrics['network_io'].append(
                MetricPoint(timestamp, net_io.bytes_sent + net_io.bytes_recv)
            )
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
    
    def _check_services_health(self):
        """检查所有服务健康状态"""
        current_time = time.time()
        
        for service_name, health in self.services.items():
            # 如果最近有错误，标记为降级或不健康
            if health.error_count > 0:
                total = health.error_count + health.success_count
                error_rate = health.error_count / total if total > 0 else 0
                
                if error_rate > 0.5:
                    health.status = "unhealthy"
                elif error_rate > 0.2:
                    health.status = "degraded"
                else:
                    health.status = "healthy"
            else:
                health.status = "healthy"
            
            health.last_check = current_time
    
    def record_metric(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """记录指标"""
        metric_point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels or {}
        )
        self.metrics[metric_name].append(metric_point)
    
    def record_request(self, service_name: str, duration: float, success: bool = True, error: Optional[str] = None):
        """记录服务请求"""
        if service_name not in self.services:
            self.services[service_name] = ServiceHealth(
                service_name=service_name,
                status="healthy",
                last_check=time.time()
            )
        
        health = self.services[service_name]
        
        if success:
            health.success_count += 1
        else:
            health.error_count += 1
            health.last_error = error
        
        # 更新平均响应时间
        total = health.success_count + health.error_count
        health.avg_response_time = (
            (health.avg_response_time * (total - 1) + duration) / total
        )
        
        # 记录响应时间指标
        self.record_metric(
            f"{service_name}_response_time",
            duration,
            {"service": service_name, "success": str(success)}
        )
    
    def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """获取服务健康状态"""
        if service_name not in self.services:
            return None
        
        health = self.services[service_name]
        return asdict(health)
    
    def get_all_services_health(self) -> List[Dict[str, Any]]:
        """获取所有服务健康状态"""
        return [asdict(health) for health in self.services.values()]
    
    def get_metric_summary(self, metric_name: str, window_seconds: int = 300) -> Dict[str, float]:
        """获取指标摘要 (最近N秒)"""
        if metric_name not in self.metrics:
            return {}
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # 过滤时间窗口内的数据点
        recent_points = [
            point for point in self.metrics[metric_name]
            if point.timestamp >= cutoff_time
        ]
        
        if not recent_points:
            return {}
        
        values = [p.value for p in recent_points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else 0
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标摘要"""
        return {
            "cpu": self.get_metric_summary_from_deque(self.system_metrics['cpu_percent']),
            "memory": self.get_metric_summary_from_deque(self.system_metrics['memory_percent']),
            "disk": self.get_metric_summary_from_deque(self.system_metrics['disk_usage']),
        }
    
    def get_metric_summary_from_deque(self, metric_deque: deque) -> Dict[str, float]:
        """从deque获取指标摘要"""
        if not metric_deque:
            return {}
        
        values = [p.value for p in metric_deque]
        
        return {
            "current": values[-1] if values else 0,
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        return {
            "timestamp": time.time(),
            "system": self.get_system_metrics(),
            "services": self.get_all_services_health(),
            "uptime": time.time() - (self.services.get('system', ServiceHealth('system', 'healthy', time.time())).last_check if self.services else time.time())
        }


# 全局单例
performance_monitor = PerformanceMonitor()
