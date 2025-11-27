from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.users import User, UserCreate, UserUpdate, UserResponse, UserLogin, Token
from services.user_service import user_service
from services.auth_service import auth_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册
    """
    try:
        new_user = user_service.create_user(user.username, user.email, user.password)
        if not new_user:
            raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户注册失败: {str(e)}")

@router.post("/login", response_model=Token)
async def login_user(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录
    """
    try:
        token = await auth_service.authenticate_user(
            username=user_login.username,
            password=user_login.password
        )
        if not token:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户登录失败: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户信息
    """
    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    """
    try:
        updated_user = user_service.update_user_profile(user_id, user_update.dict(exclude_unset=True))
        if not updated_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    删除用户（暂时禁用，实际项目中需要更复杂的逻辑）
    """
    raise HTTPException(status_code=501, detail="用户删除功能暂未实现")

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, description="跳过数量", ge=0),
    limit: int = Query(100, description="返回数量", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（仅管理员）
    """
    # 实际项目中需要权限验证
    raise HTTPException(status_code=501, detail="用户列表功能暂未实现")

@router.post("/{user_id}/preferences")
async def update_user_preferences(
    user_id: int,
    preferences: dict,
    db: Session = Depends(get_db)
):
    """
    更新用户偏好设置
    """
    try:
        updated_user = user_service.update_user_profile(user_id, {"preferences": preferences})
        if not updated_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return {"message": "偏好设置更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新偏好设置失败: {str(e)}")

@router.post("/{user_id}/notification-settings")
async def update_notification_settings(
    user_id: int,
    settings: dict,
    db: Session = Depends(get_db)
):
    """
    更新用户通知设置
    """
    try:
        updated_user = user_service.update_user_profile(user_id, {"notification_settings": settings})
        if not updated_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return {"message": "通知设置更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新通知设置失败: {str(e)}")

@router.get("/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户仪表板数据
    """
    # 实际项目中需要实现具体的仪表板数据逻辑
    raise HTTPException(status_code=501, detail="用户仪表板功能暂未实现")
