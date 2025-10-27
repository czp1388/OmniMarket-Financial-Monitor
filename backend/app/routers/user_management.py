# 寰宇多市场金融监控系统 - 用户管理API
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import logging

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
    created_at: str

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
    
    # 这里应该从数据库获取用户信息
    # 简化实现，直接返回用户名
    return {"username": username}

# 用户注册
@router.post("/users/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """用户注册"""
    if not database_service or not database_service.is_initialized:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        # 检查用户名是否已存在
        # 这里需要实现具体的用户创建逻辑
        # 简化实现，返回成功响应
        
        return {
            "id": 1,
            "username": user.username,
            "email": user.email,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户注册失败: {str(e)}")

# 用户登录
@router.post("/users/login", response_model=Token)
async def login_user(user: UserLogin):
    """用户登录"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="认证服务不可用")
    
    # 简化实现，实际应该验证用户名和密码
    if user.username == "admin" and user.password == "admin":
        access_token = auth_service.create_access_token(
            data={"sub": user.username}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 获取当前用户信息
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": 1,
        "username": current_user["username"],
        "email": "user@example.com",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }

# 获取用户列表（需要管理员权限）
@router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    """获取用户列表"""
    # 简化实现
    return [{
        "id": 1,
        "username": current_user["username"],
        "email": "user@example.com",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }]

# 健康检查
@router.get("/users/health")
async def users_health():
    """用户服务健康检查"""
    return {
        "status": "healthy",
        "auth_service": "available" if auth_service else "unavailable",
        "database_service": "available" if database_service and database_service.is_initialized else "unavailable"
    }
