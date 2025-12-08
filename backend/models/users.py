from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    
    # 用户配置
    preferences = Column(JSON, default={})  # 存储用户个性化配置
    notification_settings = Column(JSON, default={})  # 通知设置
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # 关系
    strategy_instances = relationship("StrategyInstance", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, role={self.role})>"

class UserSession(Base):
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, expires_at={self.expires_at})>"

# Pydantic models for API
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    preferences: Optional[dict] = None
    notification_settings: Optional[dict] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None
