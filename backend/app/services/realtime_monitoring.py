# 实时监控服务
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class RealTimeMonitoringService:
    def __init__(self):
        self.is_running = False
        self.monitoring_tasks = {}
        self.alert_rules = {}
        self.alert_history = []
        
    async def initialize(self):
        """初始化监控服务"""
        try:
            logger.info("🔄 初始化实时监控服务...")
            self.is_running = True
            logger.info("✅ 实时监控服务初始化完成")
            return True
        except Exception as e:
            logger.error(f"❌ 实时监控服务初始化失败: {e}")
            return False
    
    async def start_symbol_monitoring(self, symbol: str, interval: str = "1m"):
        """开始监控指定交易对"""
        try:
            if symbol in self.monitoring_tasks:
                logger.info(f"🔁 {symbol} 已在监控中")
                return True
                
            task = asyncio.create_task(self._monitor_symbol(symbol, interval))
            self.monitoring_tasks[symbol] = task
            logger.info(f"✅ 开始监控 {symbol} ({interval})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 开始监控 {symbol} 失败: {e}")
            return False
    
    async def stop_symbol_monitoring(self, symbol: str):
        """停止监控指定交易对"""
        try:
            if symbol in self.monitoring_tasks:
                self.monitoring_tasks[symbol].cancel()
                del self.monitoring_tasks[symbol]
                logger.info(f"✅ 停止监控 {symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 停止监控 {symbol} 失败: {e}")
            return False
    
    async def _monitor_symbol(self, symbol: str, interval: str):
        """监控指定交易对的核心循环"""
        from services.market_data_service import market_data_service
        
        while self.is_running:
            try:
                # 获取最新数据
                klines = await market_data_service.get_crypto_klines(symbol, interval, 10)
                if klines and len(klines) > 0:
                    latest_data = klines[-1]
                    
                    # 检查预警规则
                    await self._check_alert_rules(symbol, latest_data, klines)
                
                # 根据间隔等待
                await asyncio.sleep(self._get_interval_seconds(interval))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控 {symbol} 异常: {e}")
                await asyncio.sleep(60)  # 出错时等待1分钟
    
    def _get_interval_seconds(self, interval: str) -> int:
        """将时间间隔转换为秒数"""
        interval_map = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400
        }
        return interval_map.get(interval, 60)
    
    async def _check_alert_rules(self, symbol: str, latest_data: Dict, klines: List[Dict]):
        """检查预警规则"""
        # 这里实现具体的预警规则检查逻辑
        # 例如：价格突破、技术指标信号等
        pass
    
    async def add_alert_rule(self, rule: Dict):
        """添加预警规则"""
        rule_id = len(self.alert_rules) + 1
        self.alert_rules[rule_id] = rule
        logger.info(f"✅ 添加预警规则: {rule_id}")
        return rule_id
    
    async def remove_alert_rule(self, rule_id: int):
        """移除预警规则"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"✅ 移除预警规则: {rule_id}")
            return True
        return False
    
    async def stop_all_monitoring(self):
        """停止所有监控"""
        self.is_running = False
        for symbol, task in self.monitoring_tasks.items():
            task.cancel()
        self.monitoring_tasks.clear()
        logger.info("✅ 停止所有监控任务")

# 创建全局实时监控服务实例
realtime_monitoring_service = RealTimeMonitoringService()
