# 寰宇多市场金融监控系统 - 用户管理API（增强版）
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 导入服务
try:
    from services.auth_service import auth_service
    from services.database_service import database_service
    from database import User
    logger.info("✅ 用户管理服务导入成功")
except ImportError as e:
    logger.error(f"❌ 用户管理服务导入失败: {e}")
    auth_service = None
    database_service = None

# 数据模型
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: str
    updated_at: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 安全方案
security = HTTPBearer()

# 创建路由
router = APIRouter()

# 依赖函数
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="认证服务不可用")
    
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户信息
    user = database_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# 用户注册
@router.post("/users/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """用户注册"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    if not auth_service:
        raise HTTPException(status_code=503, detail="认证服务不可用")
    
    try:
        # 检查用户名和邮箱
        if database_service.get_user_by_username(user.username):
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        if database_service.get_user_by_email(user.email):
            raise HTTPException(status_code=400, detail="邮箱已存在")
        
        # 创建用户
        hashed_password = auth_service.get_password_hash(user.password)
        user_data = {
            'username': user.username,
            'email': user.email,
            'hashed_password': hashed_password,
            'is_active': True,
            'is_superuser': False
        }
        
        new_user = database_service.create_user(user_data)
        if not new_user:
            raise HTTPException(status_code=500, detail="用户创建失败")
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "is_active": new_user.is_active,
            "is_superuser": new_user.is_superuser,
            "created_at": new_user.created_at.isoformat(),
            "updated_at": new_user.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户注册失败: {str(e)}")

# 用户登录
@router.post("/users/login", response_model=Token)
async def login_user(user: UserLogin):
    """用户登录"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="认证服务不可用")
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        # 从数据库获取用户
        db_user = database_service.get_user_by_username(user.username)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码
        if not auth_service.verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户是否激活
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账户已被禁用"
            )
        
        # 创建访问令牌
        access_token = auth_service.create_access_token(
            data={"sub": db_user.username}
        )
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

# 获取当前用户信息
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat()
    }

# 更新当前用户信息
@router.put("/users/me", response_model=UserResponse)
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新当前用户信息"""
    if not database_service:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        update_data = {}
        if user_update.email is not None:
            # 检查邮箱是否已被其他用户使用
            existing_user = database_service.get_user_by_email(user_update.email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(status_code=400, detail="邮箱已被其他用户使用")
            update_data['email'] = user_update.email
        
        if user_update.is_active is not None:
            update_data['is_active'] = user_update.is_active
        
        if update_data:
            success = database_service.update_user(current_user.id, update_data)
            if not success:
                raise HTTPException(status_code=500, detail="用户信息更新失败")
            
            # 重新获取更新后的用户信息
            updated_user = database_service.get_user_by_id(current_user.id)
            if not updated_user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            return {
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "is_active": updated_user.is_active,
                "is_superuser": updated_user.is_superuser,
                "created_at": updated_user.created_at.isoformat(),
                "updated_at": updated_user.updated_at.isoformat()
            }
        else:
            # 没有要更新的字段，返回原用户信息
            return {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "is_active": current_user.is_active,
                "is_superuser": current_user.is_superuser,
                "created_at": current_user.created_at.isoformat(),
                "updated_at": current_user.updated_at.isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

# 获取用户列表（需要管理员权限）
@router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user)):
    """获取用户列表（仅管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="权限不足")
    
    if not database_service:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        users = database_service.get_all_users()
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

# 健康检查
@router.get("/users/health")
async def users_health():
    """用户服务健康检查"""
    return {
        "status": "healthy",
        "auth_service": "available" if auth_service else "unavailable",
        "database_service": "available" if database_service and database_service.is_initialized else "unavailable",
        "user_count": len(database_service.get_all_users()) if database_service and database_service.is_initialized else 0
    }
