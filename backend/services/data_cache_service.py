import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class DataCacheService:
    """数据缓存服务 - 由于Redis连接失败，使用内存缓存作为临时方案
    
    性能优化：
    - 缓存命中率监控
    - TTL调整为180秒（更新鲜的市场数据）
    - 线程安全的统计计数器
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl: Dict[str, float] = {}  # TTL时间戳
        self.default_ttl = 180  # 默认缓存时间3分钟（优化：从300s降低到180s以获取更新鲜数据）
        self.cleanup_interval = 60  # 清理间隔60秒
        self.is_running = False
        self.cleanup_task = None
        
        # 性能监控统计（线程安全）
        self._stats_lock = threading.Lock()
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_requests = 0
    
    async def start(self):
        """启动缓存服务"""
        self.is_running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("数据缓存服务已启动（内存缓存）")
    
    async def stop(self):
        """停止缓存服务"""
        self.is_running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("数据缓存服务已停止")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            cache_ttl = ttl if ttl is not None else self.default_ttl
            self.cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
            self.cache_ttl[key] = time.time() + cache_ttl
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            with self._stats_lock:
                self._total_requests += 1
            
            # 检查是否过期
            if key in self.cache_ttl and time.time() > self.cache_ttl[key]:
                self._delete_key(key)
                with self._stats_lock:
                    self._cache_misses += 1
                logger.debug(f"缓存过期: {key}")
                return None
            
            if key in self.cache:
                with self._stats_lock:
                    self._cache_hits += 1
                logger.debug(f"缓存命中: {key}")
                return self.cache[key]['value']
            
            with self._stats_lock:
                self._cache_misses += 1
            logger.debug(f"缓存未命中: {key}")
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            with self._stats_lock:
                self._cache_misses += 1
            return None
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            self._delete_key(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def _delete_key(self, key: str):
        """删除缓存键"""
        if key in self.cache:
            del self.cache[key]
        if key in self.cache_ttl:
            del self.cache_ttl[key]
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            if key not in self.cache:
                return False
            
            # 检查是否过期
            if key in self.cache_ttl and time.time() > self.cache_ttl[key]:
                self._delete_key(key)
                return False
            
            return True
        except Exception as e:
            logger.error(f"检查缓存存在失败: {e}")
            return False
    
    async def ttl(self, key: str) -> Optional[int]:
        """获取缓存剩余时间"""
        try:
            if key not in self.cache_ttl:
                return None
            
            remaining = self.cache_ttl[key] - time.time()
            return max(0, int(remaining))
        except Exception as e:
            logger.error(f"获取缓存TTL失败: {e}")
            return None
    
    async def keys(self, pattern: str = "*") -> list:
        """获取匹配模式的缓存键"""
        try:
            import fnmatch
            current_keys = list(self.cache.keys())
            matching_keys = []
            
            for key in current_keys:
                # 检查是否过期
                if key in self.cache_ttl and time.time() > self.cache_ttl[key]:
                    self._delete_key(key)
                    continue
                
                if fnmatch.fnmatch(key, pattern):
                    matching_keys.append(key)
            
            return matching_keys
        except Exception as e:
            logger.error(f"获取缓存键失败: {e}")
            return []
    
    async def flush_all(self) -> bool:
        """清空所有缓存"""
        try:
            self.cache.clear()
            self.cache_ttl.clear()
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False
    
    async def _cleanup_loop(self):
        """清理过期缓存的循环"""
        while self.is_running:
            try:
                await self._cleanup_expired()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存清理循环出错: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_expired(self):
        """清理过期缓存"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, expiry in self.cache_ttl.items():
                if current_time > expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._delete_key(key)
            
            if expired_keys:
                logger.debug(f"清理了 {len(expired_keys)} 个过期缓存")
                
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息（包括命中率监控）"""
        current_time = time.time()
        valid_keys = 0
        expired_keys = 0
        
        for key in list(self.cache.keys()):
            if key in self.cache_ttl and current_time > self.cache_ttl[key]:
                expired_keys += 1
            else:
                valid_keys += 1
        
        with self._stats_lock:
            total_requests = self._total_requests
            cache_hits = self._cache_hits
            cache_misses = self._cache_misses
            hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            'total_keys': len(self.cache),
            'valid_keys': valid_keys,
            'expired_keys': expired_keys,
            'cache_size': len(self.cache),
            'memory_usage': f"{len(str(self.cache))} bytes",
            # 性能监控指标
            'performance': {
                'total_requests': total_requests,
                'cache_hits': cache_hits,
                'cache_misses': cache_misses,
                'hit_rate': f"{hit_rate:.2f}%",
                'default_ttl': self.default_ttl
            }
        }
    
    def reset_stats(self):
        """重置性能统计（用于调试或定期重置）"""
        with self._stats_lock:
            self._cache_hits = 0
            self._cache_misses = 0
            self._total_requests = 0
        logger.info("缓存性能统计已重置")


# 全局数据缓存服务实例
data_cache_service = DataCacheService()
