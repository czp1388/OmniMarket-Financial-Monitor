import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database import Base, User, SystemConfig, UserRole, UserRoleAssignment, AlertRule, AlertHistory
from db_manager import db_manager

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.is_initialized = False
        self.engine = None
        self.SessionLocal = None
        
    def initialize(self, database_url: str = "sqlite:///./test.db"):
        """初始化数据库连接和表"""
        try:
            self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            
            # 设置数据库管理器
            db_manager.set_engine(self.engine)
            
            # 初始化默认数据
            self._init_default_data()
            
            self.is_initialized = True
            logger.info("✅ 数据库初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            return False

    def _init_default_data(self):
        """初始化默认数据"""
        try:
            # 初始化默认配置
            self._init_default_config()
            
            # 初始化默认角色和权限
            self.initialize_default_roles()
            
            logger.info("✅ 默认数据初始化完成")
        except Exception as e:
            logger.error(f"❌ 默认数据初始化失败: {e}")

    def _init_default_config(self):
        """初始化默认系统配置"""
        try:
            db = next(db_manager.get_db())
            
            # 检查是否已存在配置
            existing_config = db.query(SystemConfig).first()
            if existing_config:
                db.close()
                return
            
            # 创建默认配置
            default_config = SystemConfig(
                app_name="OmniMarket Financial Monitor",
                version="2.9.3",
                market_data_provider="default",
                alert_check_interval=60,
                max_alert_rules_per_user=50,
                created_at=datetime.utcnow()
            )
            
            db.add(default_config)
            db.commit()
            db.close()
            
            logger.info("✅ 默认系统配置初始化完成")
        except Exception as e:
            logger.error(f"❌ 默认系统配置初始化失败: {e}")

    # 用户管理方法
    def create_user(self, user_data: Dict) -> Optional[User]:
        """创建用户"""
        try:
            db = next(db_manager.get_db())
            
            # 检查用户名是否已存在
            existing_user = db.query(User).filter(User.username == user_data['username']).first()
            if existing_user:
                db.close()
                return None
            
            # 检查邮箱是否已存在
            existing_email = db.query(User).filter(User.email == user_data['email']).first()
            if existing_email:
                db.close()
                return None
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                hashed_password=user_data['hashed_password'],
                is_active=user_data.get('is_active', True),
                is_superuser=user_data.get('is_superuser', False),
                created_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            db.close()
            
            logger.info(f"✅ 用户创建成功: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"❌ 创建用户失败: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            db = next(db_manager.get_db())
            user = db.query(User).filter(User.username == username).first()
            db.close()
            return user
        except Exception as e:
            logger.error(f"❌ 获取用户失败: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        try:
            db = next(db_manager.get_db())
            user = db.query(User).filter(User.id == user_id).first()
            db.close()
            return user
        except Exception as e:
            logger.error(f"❌ 获取用户失败: {e}")
            return None

    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        try:
            db = next(db_manager.get_db())
            users = db.query(User).all()
            db.close()
            return users
        except Exception as e:
            logger.error(f"❌ 获取用户列表失败: {e}")
            return []

    def update_user(self, user_id: int, update_data: Dict) -> bool:
        """更新用户信息"""
        try:
            db = next(db_manager.get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                db.close()
                return False
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.close()
            
            logger.info(f"✅ 用户更新成功: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新用户失败: {e}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            db = next(db_manager.get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                db.close()
                return False
            
            db.delete(user)
            db.commit()
            db.close()
            
            logger.info(f"✅ 用户删除成功: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除用户失败: {e}")
            return False

    # 权限管理方法
    def create_role(self, role_data: Dict) -> Optional[UserRole]:
        """创建角色"""
        try:
            db = next(db_manager.get_db())
            
            role = UserRole(
                name=role_data['name'],
                description=role_data.get('description', ''),
                permissions=role_data.get('permissions', []),
                is_default=role_data.get('is_default', False)
            )
            
            db.add(role)
            db.commit()
            db.refresh(role)
            db.close()
            
            logger.info(f"✅ 角色创建成功: {role.name}")
            return role
            
        except Exception as e:
            logger.error(f"❌ 创建角色失败: {e}")
            return None

    def get_role_by_name(self, name: str) -> Optional[UserRole]:
        """根据名称获取角色"""
        try:
            db = next(db_manager.get_db())
            role = db.query(UserRole).filter(UserRole.name == name).first()
            db.close()
            return role
        except Exception as e:
            logger.error(f"❌ 获取角色失败: {e}")
            return None

    def get_user_roles(self, user_id: int) -> List[UserRole]:
        """获取用户的所有角色"""
        try:
            db = next(db_manager.get_db())
            role_assignments = db.query(UserRoleAssignment).filter(UserRoleAssignment.user_id == user_id).all()
            role_ids = [ra.role_id for ra in role_assignments]
            roles = db.query(UserRole).filter(UserRole.id.in_(role_ids)).all()
            db.close()
            return roles
        except Exception as e:
            logger.error(f"❌ 获取用户角色失败: {e}")
            return []

    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by: int = None) -> bool:
        """为用户分配角色"""
        try:
            db = next(db_manager.get_db())
            
            # 检查是否已分配
            existing = db.query(UserRoleAssignment).filter(
                UserRoleAssignment.user_id == user_id,
                UserRoleAssignment.role_id == role_id
            ).first()
            
            if existing:
                db.close()
                return True  # 已经分配，返回成功
            
            assignment = UserRoleAssignment(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by
            )
            
            db.add(assignment)
            db.commit()
            db.close()
            
            logger.info(f"✅ 角色分配成功: 用户 {user_id} -> 角色 {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 分配角色失败: {e}")
            return False

    def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """移除用户的角色"""
        try:
            db = next(db_manager.get_db())
            
            assignment = db.query(UserRoleAssignment).filter(
                UserRoleAssignment.user_id == user_id,
                UserRoleAssignment.role_id == role_id
            ).first()
            
            if not assignment:
                db.close()
                return True  # 没有分配，返回成功
            
            db.delete(assignment)
            db.commit()
            db.close()
            
            logger.info(f"✅ 角色移除成功: 用户 {user_id} -> 角色 {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 移除角色失败: {e}")
            return False

    def user_has_permission(self, user_id: int, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        try:
            db = next(db_manager.get_db())
            
            # 获取用户的所有角色
            role_assignments = db.query(UserRoleAssignment).filter(UserRoleAssignment.user_id == user_id).all()
            role_ids = [ra.role_id for ra in role_assignments]
            
            if not role_ids:
                db.close()
                return False
            
            # 检查所有角色的权限
            roles = db.query(UserRole).filter(UserRole.id.in_(role_ids)).all()
            for role in roles:
                if permission_code in role.permissions:
                    db.close()
                    return True
            
            db.close()
            return False
            
        except Exception as e:
            logger.error(f"❌ 检查权限失败: {e}")
            return False

    def get_all_permissions(self) -> List[Dict]:
        """获取所有可用的权限"""
        # 这里定义系统所有权限
        permissions = [
            {"code": "user.read", "name": "查看用户", "description": "查看用户信息", "category": "user"},
            {"code": "user.write", "name": "管理用户", "description": "创建、编辑、删除用户", "category": "user"},
            {"code": "alert_rule.read", "name": "查看预警规则", "description": "查看预警规则", "category": "alert"},
            {"code": "alert_rule.write", "name": "管理预警规则", "description": "创建、编辑、删除预警规则", "category": "alert"},
            {"code": "alert_rule.own", "name": "管理个人预警规则", "description": "管理自己的预警规则", "category": "alert"},
            {"code": "market_data.read", "name": "查看市场数据", "description": "查看市场数据", "category": "market"},
            {"code": "system.config", "name": "系统配置", "description": "管理系统配置", "category": "system"},
            {"code": "system.monitor", "name": "系统监控", "description": "查看系统监控信息", "category": "system"}
        ]
        return permissions

    def initialize_default_roles(self):
        """初始化默认角色"""
        try:
            db = next(db_manager.get_db())
            
            # 检查是否已初始化
            existing_roles = db.query(UserRole).count()
            if existing_roles > 0:
                db.close()
                return
            
            # 创建默认角色
            default_roles = [
                {
                    "name": "admin",
                    "description": "系统管理员",
                    "permissions": ["user.read", "user.write", "alert_rule.read", "alert_rule.write", "market_data.read", "system.config", "system.monitor"],
                    "is_default": False
                },
                {
                    "name": "user",
                    "description": "普通用户",
                    "permissions": ["alert_rule.own", "market_data.read"],
                    "is_default": True
                },
                {
                    "name": "viewer",
                    "description": "只读用户",
                    "permissions": ["alert_rule.read", "market_data.read"],
                    "is_default": False
                }
            ]
            
            for role_data in default_roles:
                role = UserRole(
                    name=role_data['name'],
                    description=role_data['description'],
                    permissions=role_data['permissions'],
                    is_default=role_data['is_default']
                )
                db.add(role)
            
            db.commit()
            db.close()
            logger.info("✅ 默认角色初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 初始化默认角色失败: {e}")

    # 预警规则管理方法
    def create_alert_rule(self, rule_data: Dict) -> Optional[AlertRule]:
        """创建预警规则"""
        try:
            db = next(db_manager.get_db())
            
            rule = AlertRule(
                user_id=rule_data['user_id'],
                name=rule_data['name'],
                description=rule_data.get('description', ''),
                market_symbol=rule_data['market_symbol'],
                condition_type=rule_data['condition_type'],
                condition_value=rule_data['condition_value'],
                is_active=rule_data.get('is_active', True)
            )
            
            db.add(rule)
            db.commit()
            db.refresh(rule)
            db.close()
            
            logger.info(f"✅ 预警规则创建成功: {rule.name} (用户: {rule.user_id})")
            return rule
            
        except Exception as e:
            logger.error(f"❌ 创建预警规则失败: {e}")
            return None

    def get_user_alert_rules(self, user_id: int) -> List[AlertRule]:
        """获取用户的所有预警规则"""
        try:
            db = next(db_manager.get_db())
            rules = db.query(AlertRule).filter(AlertRule.user_id == user_id).all()
            db.close()
            return rules
        except Exception as e:
            logger.error(f"❌ 获取用户预警规则失败: {e}")
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
            
            logger.info(f"✅ 预警规则更新成功: {rule_id}")
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
            
            logger.info(f"✅ 预警规则删除成功: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除预警规则失败: {e}")
            return False

    def add_alert_history(self, history_data: Dict) -> bool:
        """添加预警历史记录"""
        try:
            db = next(db_manager.get_db())
            
            history = AlertHistory(
                alert_rule_id=history_data['alert_rule_id'],
                market_symbol=history_data['market_symbol'],
                current_value=history_data['current_value'],
                condition_value=history_data['condition_value'],
                message=history_data.get('message', '')
            )
            
            db.add(history)
            db.commit()
            db.close()
            
            logger.info(f"✅ 预警历史记录添加成功: 规则 {history_data['alert_rule_id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加预警历史记录失败: {e}")
            return False

    def get_alert_history(self, rule_id: int, limit: int = 50) -> List[AlertHistory]:
        """获取预警规则的历史记录"""
        try:
            db = next(db_manager.get_db())
            history = db.query(AlertHistory).filter(
                AlertHistory.alert_rule_id == rule_id
            ).order_by(AlertHistory.triggered_at.desc()).limit(limit).all()
            db.close()
            return history
        except Exception as e:
            logger.error(f"❌ 获取预警历史失败: {e}")
            return []

# 创建全局数据库服务实例
database_service = DatabaseService()
