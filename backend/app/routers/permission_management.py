# 🔐 用户权限管理API
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# 导入服务
try:
    from services.database_service import database_service
    from database import User, UserRole, UserRoleAssignment
    logger.info("✅ 权限管理服务导入成功")
except ImportError as e:
    logger.error(f"❌ 权限管理服务导入失败: {e}")
    database_service = None

# 安全方案
security = HTTPBearer()

# 数据模型
class RoleCreate(BaseModel):
    name: str
    description: str
    permissions: List[str]
    is_default: bool = False

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    permissions: List[str]
    is_default: bool
    created_at: str

class RoleAssignment(BaseModel):
    user_id: int
    role_id: int

class PermissionResponse(BaseModel):
    code: str
    name: str
    description: str
    category: str

class UserWithRoles(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    roles: List[RoleResponse]

# 依赖函数
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    from services.auth_service import auth_service
    
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
    
    user = database_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def require_permission(permission_code: str, current_user: User = Depends(get_current_user)):
    """权限检查依赖"""
    if not database_service.user_has_permission(current_user.id, permission_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user

# 创建路由
router = APIRouter()

# 角色管理端点
@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(lambda: require_permission("user.write"))
):
    """创建角色"""
    if not database_service:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        # 检查角色名是否已存在
        existing_role = database_service.get_role_by_name(role.name)
        if existing_role:
            raise HTTPException(status_code=400, detail="角色名已存在")
        
        new_role = database_service.create_role({
            'name': role.name,
            'description': role.description,
            'permissions': role.permissions,
            'is_default': role.is_default
        })
        
        if not new_role:
            raise HTTPException(status_code=500, detail="角色创建失败")
        
        return {
            "id": new_role.id,
            "name": new_role.name,
            "description": new_role.description,
            "permissions": new_role.permissions,
            "is_default": new_role.is_default,
            "created_at": new_role.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建角色失败: {str(e)}")

@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(current_user: User = Depends(lambda: require_permission("user.read"))):
    """获取所有角色"""
    if not database_service:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        # 这里应该从数据库获取角色列表
        # 简化实现，返回空列表
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色列表失败: {str(e)}")

# 权限管理端点
@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(current_user: User = Depends(lambda: require_permission("user.read"))):
    """获取所有权限"""
    try:
        permissions = database_service.get_all_permissions()
        return [
            {
                "code": perm["code"],
                "name": perm["name"],
                "description": perm["description"],
                "category": perm["category"]
            }
            for perm in permissions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取权限列表失败: {str(e)}")

# 用户角色管理端点
@router.post("/users/{user_id}/roles")
async def assign_role_to_user(
    user_id: int,
    assignment: RoleAssignment,
    current_user: User = Depends(lambda: require_permission("user.write"))
):
    """为用户分配角色"""
    if not database_service:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        success = database_service.assign_role_to_user(
            user_id=user_id,
            role_id=assignment.role_id,
            assigned_by=current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="角色分配失败")
        
        return {"message": "角色分配成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"角色分配失败: {str(e)}")

@router.get("/users/{user_id}/roles", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(lambda: require_permission("user.read"))
):
    """获取用户的角色"""
    if not database_service:
        raise HTTPException(status_code=503, detail="数据库服务不可用")
    
    try:
        roles = database_service.get_user_roles(user_id)
        return [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.permissions,
                "is_default": role.is_default,
                "created_at": role.created_at.isoformat()
            }
            for role in roles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户角色失败: {str(e)}")

# 健康检查
@router.get("/permissions/health")
async def permissions_health():
    """权限服务健康检查"""
    return {
        "status": "healthy",
        "database_service": "available" if database_service and database_service.is_initialized else "unavailable",
        "permission_count": len(database_service.get_all_permissions()) if database_service else 0
    }
