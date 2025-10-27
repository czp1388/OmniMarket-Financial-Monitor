# 寰宇多市场金融监控系统 - 数据库服务
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from database import db_manager, AlertRule, AlertHistory, SystemConfig, MarketData

logger = logging.getLogger(__name__)

class DatabaseService:
    """数据库服务"""
    
    def __init__(self):
        self.is_initialized = False
        
    async def initialize(self):
        """初始化数据库服务"""
        try:
            if db_manager.init_db():
                self.is_initialized = True
                logger.info("✅ 数据库服务初始化成功")
                
                # 初始化默认系统配置
                self._init_default_config()
            else:
                logger.error("❌ 数据库服务初始化失败")
        except Exception as e:
            logger.error(f"❌ 数据库服务初始化异常: {e}")

    def _init_default_config(self):
        """初始化默认系统配置"""
        try:
            db = next(db_manager.get_db())
            
            # 检查是否已有配置
            existing_config = db.query(SystemConfig).first()
            if not existing_config:
                # 创建默认配置
                default_configs = [
                    SystemConfig(
                        config_key="system.version",
                        config_value="2.8.0",
                        description="系统版本号"
                    ),
                    SystemConfig(
                        config_key="alert.max_history_days",
                        config_value="30",
                        description="预警历史保留天数"
                    ),
                    SystemConfig(
                        config_key="market_data.cache_ttl",
                        config_value="300",
                        description="市场数据缓存时间（秒）"
                    )
                ]
                
                db.add_all(default_configs)
                db.commit()
                logger.info("✅ 默认系统配置初始化完成")
            
            db.close()
        except Exception as e:
            logger.error(f"❌ 默认配置初始化失败: {e}")

    # 预警规则管理
    def create_alert_rule(self, rule_data: Dict) -> Optional[AlertRule]:
        """创建预警规则"""
        try:
            db = next(db_manager.get_db())
            
            rule = AlertRule(
                user_id=rule_data.get('user_id', 0),
                symbol=rule_data['symbol'],
                condition=rule_data['condition'],
                threshold=rule_data['threshold'],
                notification_type=rule_data.get('notification_type', 'log'),
                email_recipients=rule_data.get('email_recipients', []),
                telegram_chat_ids=rule_data.get('telegram_chat_ids', []),
                is_active=rule_data.get('is_active', True)
            )
            
            db.add(rule)
            db.commit()
            db.refresh(rule)
            db.close()
            
            logger.info(f"✅ 预警规则已创建: {rule.symbol} {rule.condition} {rule.threshold}")
            return rule
            
        except Exception as e:
            logger.error(f"❌ 创建预警规则失败: {e}")
            return None

    def get_alert_rules(self, user_id: int = 0, active_only: bool = True) -> List[AlertRule]:
        """获取预警规则列表"""
        try:
            db = next(db_manager.get_db())
            
            query = db.query(AlertRule).filter(AlertRule.user_id == user_id)
            if active_only:
                query = query.filter(AlertRule.is_active == True)
                
            rules = query.order_by(desc(AlertRule.created_at)).all()
            db.close()
            
            return rules
            
        except Exception as e:
            logger.error(f"❌ 获取预警规则失败: {e}")
            return []

    def get_alert_rule_by_id(self, rule_id: int) -> Optional[AlertRule]:
        """根据ID获取预警规则"""
        try:
            db = next(db_manager.get_db())
            rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
            db.close()
            return rule
        except Exception as e:
            logger.error(f"❌ 获取预警规则失败: {e}")
            return None

    def update_alert_rule(self, rule_id: int, update_data: Dict) -> bool:
        """更新预警规则"""
        try:
            db = next(db_manager.get_db())
            rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
            
            if not rule:
                db.close()
                return False
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.utcnow()
            db.commit()
            db.close()
            
            logger.info(f"✅ 预警规则已更新: ID {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新预警规则失败: {e}")
            return False

    def delete_alert_rule(self, rule_id: int) -> bool:
        """删除预警规则"""
        try:
            db = next(db_manager.get_db())
            rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
            
            if not rule:
                db.close()
                return False
            
            db.delete(rule)
            db.commit()
            db.close()
            
            logger.info(f"✅ 预警规则已删除: ID {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除预警规则失败: {e}")
            return False

    # 预警历史管理
    def create_alert_history(self, alert_data: Dict) -> Optional[AlertHistory]:
        """创建预警历史记录"""
        try:
            db = next(db_manager.get_db())
            
            history = AlertHistory(
                rule_id=alert_data['rule_id'],
                symbol=alert_data['symbol'],
                condition=alert_data['condition'],
                threshold=alert_data['threshold'],
                current_price=alert_data['current_price'],
                previous_price=alert_data.get('previous_price', 0),
                message=alert_data['message'],
                notification_type=alert_data.get('notification_type', 'log'),
                triggered_at=alert_data.get('triggered_at', datetime.utcnow())
            )
            
            db.add(history)
            db.commit()
            db.refresh(history)
            db.close()
            
            return history
            
        except Exception as e:
            logger.error(f"❌ 创建预警历史失败: {e}")
            return None

    def get_alert_history(self, limit: int = 50, symbol: str = None, days: int = 7) -> List[AlertHistory]:
        """获取预警历史记录"""
        try:
            db = next(db_manager.get_db())
            
            query = db.query(AlertHistory)
            
            # 时间过滤
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AlertHistory.triggered_at >= start_date)
            
            # 交易对过滤
            if symbol:
                query = query.filter(AlertHistory.symbol == symbol)
            
            history = query.order_by(desc(AlertHistory.triggered_at)).limit(limit).all()
            db.close()
            
            return history
            
        except Exception as e:
            logger.error(f"❌ 获取预警历史失败: {e}")
            return []

    def get_alert_stats(self, days: int = 7) -> Dict:
        """获取预警统计信息"""
        try:
            db = next(db_manager.get_db())
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 总触发次数
            total_count = db.query(AlertHistory).filter(
                AlertHistory.triggered_at >= start_date
            ).count()
            
            # 按交易对分组统计
            symbol_stats = db.query(
                AlertHistory.symbol,
                db.func.count(AlertHistory.id)
            ).filter(
                AlertHistory.triggered_at >= start_date
            ).group_by(AlertHistory.symbol).all()
            
            # 按通知类型分组统计
            notification_stats = db.query(
                AlertHistory.notification_type,
                db.func.count(AlertHistory.id)
            ).filter(
                AlertHistory.triggered_at >= start_date
            ).group_by(AlertHistory.notification_type).all()
            
            db.close()
            
            return {
                'total_count': total_count,
                'symbol_stats': dict(symbol_stats),
                'notification_stats': dict(notification_stats),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"❌ 获取预警统计失败: {e}")
            return {}

    # 市场数据缓存
    def update_market_data(self, symbol: str, price_data: Dict) -> bool:
        """更新市场数据缓存"""
        try:
            db = next(db_manager.get_db())
            
            # 查找现有记录
            market_data = db.query(MarketData).filter(MarketData.symbol == symbol).first()
            
            if market_data:
                # 更新现有记录
                market_data.price = price_data.get('price', 0)
                market_data.change_24h = price_data.get('change_24h')
                market_data.volume_24h = price_data.get('volume_24h')
                market_data.high_24h = price_data.get('high_24h')
                market_data.low_24h = price_data.get('low_24h')
                market_data.last_updated = datetime.utcnow()
            else:
                # 创建新记录
                market_data = MarketData(
                    symbol=symbol,
                    price=price_data.get('price', 0),
                    change_24h=price_data.get('change_24h'),
                    volume_24h=price_data.get('volume_24h'),
                    high_24h=price_data.get('high_24h'),
                    low_24h=price_data.get('low_24h'),
                    last_updated=datetime.utcnow()
                )
                db.add(market_data)
            
            db.commit()
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新市场数据缓存失败: {e}")
            return False

    def get_market_data(self, symbol: str = None) -> List[MarketData]:
        """获取市场数据缓存"""
        try:
            db = next(db_manager.get_db())
            
            if symbol:
                data = db.query(MarketData).filter(MarketData.symbol == symbol).all()
            else:
                data = db.query(MarketData).order_by(MarketData.symbol).all()
            
            db.close()
            return data
            
        except Exception as e:
            logger.error(f"❌ 获取市场数据缓存失败: {e}")
            return []

    # 系统配置管理
    def get_config(self, key: str, default: str = None) -> str:
        """获取系统配置"""
        try:
            db = next(db_manager.get_db())
            config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            db.close()
            
            return config.config_value if config else default
            
        except Exception as e:
            logger.error(f"❌ 获取系统配置失败: {e}")
            return default

    def set_config(self, key: str, value: str, description: str = None) -> bool:
        """设置系统配置"""
        try:
            db = next(db_manager.get_db())
            config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            
            if config:
                config.config_value = value
                if description:
                    config.description = description
                config.updated_at = datetime.utcnow()
            else:
                config = SystemConfig(
                    config_key=key,
                    config_value=value,
                    description=description or f"系统配置: {key}"
                )
                db.add(config)
            
            db.commit()
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ 设置系统配置失败: {e}")
            return False

    def get_all_configs(self) -> Dict:
        """获取所有系统配置"""
        try:
            db = next(db_manager.get_db())
            configs = db.query(SystemConfig).all()
            db.close()
            
            return {config.config_key: config.config_value for config in configs}
            
        except Exception as e:
            logger.error(f"❌ 获取所有系统配置失败: {e}")
            return {}

    # 数据库维护
    def cleanup_old_history(self, days: int = 30) -> int:
        """清理旧的历史记录"""
        try:
            db = next(db_manager.get_db())
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = db.query(AlertHistory).filter(
                AlertHistory.triggered_at < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            logger.info(f"✅ 清理了 {deleted_count} 条旧历史记录")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 清理历史记录失败: {e}")
            return 0

    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        try:
            db = next(db_manager.get_db())
            
            stats = {
                'alert_rules_count': db.query(AlertRule).count(),
                'alert_history_count': db.query(AlertHistory).count(),
                'market_data_count': db.query(MarketData).count(),
                'system_config_count': db.query(SystemConfig).count(),
                'database_size': 'N/A'  # SQLite可以通过文件大小获取
            }
            
            db.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取数据库统计失败: {e}")
            return {}

    def test_connection(self):
        """测试数据库连接"""
        try:
            db = next(db_manager.get_db())
            db.execute("SELECT 1")
            db.close()
            logger.info("✅ 数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接测试失败: {e}")
            return False

# 创建全局数据库服务实例
database_service = DatabaseService()

