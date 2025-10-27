from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String(100), default="OmniMarket Financial Monitor")
    version = Column(String(20), default="2.9.3")
    market_data_provider = Column(String(50), default="default")
    alert_check_interval = Column(Integer, default=60)  # 秒
    max_alert_rules_per_user = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserRole(Base):
    """用户角色表"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default=[])  # 存储权限列表
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserRoleAssignment(Base):
    """用户角色分配表"""
    __tablename__ = "user_role_assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    role_id = Column(Integer, index=True, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer)  # 分配者的用户ID

class Permission(Base):
    """权限定义表"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # 权限分类
    created_at = Column(DateTime, default=datetime.utcnow)

class AlertRule(Base):
    """预警规则表"""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)  # 所属用户
    name = Column(String(100), nullable=False)  # 规则名称
    description = Column(Text)  # 规则描述
    market_symbol = Column(String(50), nullable=False)  # 市场符号
    condition_type = Column(String(50), nullable=False)  # 条件类型: price_above, price_below, percentage_change等
    condition_value = Column(Float, nullable=False)  # 条件值
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AlertHistory(Base):
    """预警历史表"""
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_rule_id = Column(Integer, index=True, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    market_symbol = Column(String(50), nullable=False)
    current_value = Column(Float, nullable=False)
    condition_value = Column(Float, nullable=False)
    message = Column(Text)  # 预警消息
