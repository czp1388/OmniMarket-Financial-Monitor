import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class DataSourceStatus(Enum):
    """数据源状态枚举"""
    HEALTHY = "healthy"  # 健康
    DEGRADED = "degraded"  # 性能下降
    UNRELIABLE = "unreliable"  # 不可靠
    OFFLINE = "offline"  # 离线

class DataQualityMetrics:
    """数据质量指标"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.error_count = 0
        self.success_count = 0
        self.last_success_time: Optional[datetime] = None
        self.last_error_time: Optional[datetime] = None
        self.data_freshness: List[float] = []  # 数据新鲜度（秒）
        
    def record_success(self, response_time: float, data_freshness: float = 0.0):
        """记录成功请求"""
        self.response_times.append(response_time)
        self.data_freshness.append(data_freshness)
        self.success_count += 1
        self.last_success_time = datetime.now()
        
    def record_error(self):
        """记录错误请求"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        
    def get_metrics(self) -> Dict[str, Any]:
        """获取质量指标"""
        total_requests = self.success_count + self.error_count
        error_rate = self.error_count / total_requests if total_requests > 0 else 0
        
        avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
        avg_freshness = statistics.mean(self.data_freshness) if self.data_freshness else 0
        
        # 保留最近100个数据点
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
        if len(self.data_freshness) > 100:
            self.data_freshness = self.data_freshness[-100:]
            
        return {
            "total_requests": total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "avg_data_freshness": avg_freshness,
            "last_success_time": self.last_success_time,
            "last_error_time": self.last_error_time
        }

class DataSourceMonitor:
    """数据源监控器"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.metrics = DataQualityMetrics()
        self.status = DataSourceStatus.HEALTHY
        self.status_since = datetime.now()
        
    def update_status(self, new_status: DataSourceStatus):
        """更新状态"""
        if self.status != new_status:
            logger.info(f"数据源 {self.source_name} 状态从 {self.status.value} 变为 {new_status.value}")
            self.status = new_status
            self.status_since = datetime.now()
            
    def evaluate_health(self) -> DataSourceStatus:
        """评估健康状态"""
        metrics = self.metrics.get_metrics()
        
        if metrics["total_requests"] == 0:
            return DataSourceStatus.HEALTHY
            
        # 评估标准
        error_rate = metrics["error_rate"]
        avg_response_time = metrics["avg_response_time"]
        
        if error_rate > 0.5:  # 错误率超过50%
            return DataSourceStatus.OFFLINE
        elif error_rate > 0.2:  # 错误率超过20%
            return DataSourceStatus.UNRELIABLE
        elif avg_response_time > 10.0:  # 平均响应时间超过10秒
            return DataSourceStatus.DEGRADED
        else:
            return DataSourceStatus.HEALTHY

class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self):
        self.sources: Dict[str, DataSourceMonitor] = {}
        self.evaluation_interval = 60  # 评估间隔（秒）
        self.is_running = False
        
    def register_source(self, source_name: str):
        """注册数据源"""
        if source_name not in self.sources:
            self.sources[source_name] = DataSourceMonitor(source_name)
            logger.info(f"注册数据源监控: {source_name}")
            
    def record_success(self, source_name: str, response_time: float, data_freshness: float = 0.0):
        """记录成功请求"""
        if source_name in self.sources:
            self.sources[source_name].metrics.record_success(response_time, data_freshness)
            
    def record_error(self, source_name: str):
        """记录错误请求"""
        if source_name in self.sources:
            self.sources[source_name].metrics.record_error()
            
    def get_source_status(self, source_name: str) -> Optional[DataSourceStatus]:
        """获取数据源状态"""
        if source_name in self.sources:
            return self.sources[source_name].status
        return None
        
    def get_healthy_sources(self, source_names: List[str]) -> List[str]:
        """获取健康的数据源列表"""
        healthy_sources = []
        for source_name in source_names:
            status = self.get_source_status(source_name)
            if status in [DataSourceStatus.HEALTHY, DataSourceStatus.DEGRADED]:
                healthy_sources.append(source_name)
        return healthy_sources
        
    def get_best_source(self, source_names: List[str]) -> Optional[str]:
        """获取最佳数据源"""
        healthy_sources = self.get_healthy_sources(source_names)
        if not healthy_sources:
            return None
            
        # 根据错误率和响应时间排序
        best_source = None
        best_score = float('inf')
        
        for source_name in healthy_sources:
            source = self.sources[source_name]
            metrics = source.metrics.get_metrics()
            
            # 评分公式：错误率权重 + 响应时间权重
            score = (metrics["error_rate"] * 100) + (metrics["avg_response_time"] * 10)
            if score < best_score:
                best_score = score
                best_source = source_name
                
        return best_source
        
    async def start_monitoring(self):
        """开始监控"""
        self.is_running = True
        logger.info("启动数据质量监控服务")
        
        while self.is_running:
            try:
                await self._evaluate_sources()
                await asyncio.sleep(self.evaluation_interval)
            except Exception as e:
                logger.error(f"数据质量监控错误: {e}")
                await asyncio.sleep(10)
                
    async def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        logger.info("停止数据质量监控服务")
        
    async def _evaluate_sources(self):
        """评估所有数据源"""
        for source_name, monitor in self.sources.items():
            try:
                new_status = monitor.evaluate_health()
                monitor.update_status(new_status)
                
                # 记录状态变化
                metrics = monitor.metrics.get_metrics()
                logger.debug(f"数据源 {source_name} 状态: {new_status.value}, "
                           f"错误率: {metrics['error_rate']:.2%}, "
                           f"平均响应时间: {metrics['avg_response_time']:.2f}s")
                           
            except Exception as e:
                logger.error(f"评估数据源 {source_name} 时出错: {e}")
                
    def get_overview(self) -> Dict[str, Any]:
        """获取监控概览"""
        overview = {
            "total_sources": len(self.sources),
            "sources": {}
        }
        
        for source_name, monitor in self.sources.items():
            overview["sources"][source_name] = {
                "status": monitor.status.value,
                "status_since": monitor.status_since.isoformat(),
                "metrics": monitor.metrics.get_metrics()
            }
            
        return overview

# 全局数据质量监控器实例
data_quality_monitor = DataQualityMonitor()
