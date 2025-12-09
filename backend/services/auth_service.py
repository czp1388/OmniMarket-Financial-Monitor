import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException

from .user_service import user_service
from config import settings

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        pass
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户认证并生成JWT令牌"""
        try:
            # 使用UserService进行用户认证
            user = user_service.authenticate_user(username, password)
            if not user:
                return None
            
            # 生成JWT令牌
            access_token = self._create_access_token(
                data={"sub": user.username, "user_id": user.id}
            )
            
            # 生成刷新令牌
            refresh_token = self._create_refresh_token(
                data={"sub": user.username, "user_id": user.id}
            )
            
            logger.info(f"用户认证成功: {username}")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.full_name or user.username
                }
            }
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.JWTError:  # 修复：使用 JWTError 替代 InvalidTokenError
            logger.warning("无效令牌")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """刷新访问令牌"""
        try:
            # 验证刷新令牌
            payload = self.verify_token(refresh_token)
            if not payload:
                return None
            
            # 生成新的访问令牌
            access_token = self._create_access_token(
                data={"sub": payload["sub"], "user_id": payload["user_id"]}
            )
            
            logger.info(f"令牌刷新成功: {payload['sub']}")
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"令牌刷新失败: {e}")
            return None
    
    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    def _create_refresh_token(self, data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """刷新访问令牌（异步版本）"""
        return self.refresh_token(refresh_token)
    
    async def get_current_user(self, token: str):
        """从令牌获取当前用户信息（返回User对象）"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            # 从数据库获取用户信息，返回User对象
            user = user_service.get_user_by_id(user_id)
            return user
            
        except Exception as e:
            logger.error(f"获取当前用户失败: {e}")
            return None
    
    async def logout_user(self, token: str) -> bool:
        """用户登出（可选：将令牌加入黑名单）"""
        try:
            # 验证令牌
            payload = self.verify_token(token)
            if not payload:
                return False
            
            # TODO: 可以在这里将令牌加入黑名单（Redis）
            logger.info(f"用户登出: {payload.get('sub')}")
            return True
            
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            return False
    
    async def change_password(
        self, 
        user_id: int, 
        old_password: str, 
        new_password: str
    ) -> bool:
        """修改密码"""
        try:
            # 验证旧密码
            user = user_service.get_user_by_id(user_id)
            if not user:
                return False
            
            if not user_service.verify_password(old_password, user.password_hash):
                logger.warning(f"旧密码错误: user_id={user_id}")
                return False
            
            # 更新密码
            success = user_service.update_password(user_id, new_password)
            if success:
                logger.info(f"密码修改成功: user_id={user_id}")
            return success
            
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return False
    
    async def request_password_reset(self, email: str) -> Optional[str]:
        """请求密码重置（生成重置令牌）"""
        try:
            # 查找用户
            user = user_service.get_user_by_email(email)
            if not user:
                logger.warning(f"用户不存在: {email}")
                return None
            
            # 生成重置令牌（有效期1小时）
            reset_token = jwt.encode(
                {
                    "sub": user.username,
                    "user_id": user.id,
                    "email": email,
                    "exp": datetime.utcnow() + timedelta(hours=1)
                },
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
            
            logger.info(f"生成密码重置令牌: {email}")
            # TODO: 发送重置邮件
            return {"reset_token": reset_token}
            
        except Exception as e:
            logger.error(f"请求密码重置失败: {e}")
            return None
    
    async def reset_password(self, reset_token: str, new_password: str) -> bool:
        """使用重置令牌重置密码"""
        try:
            # 验证重置令牌
            payload = self.verify_token(reset_token)
            if not payload:
                return False
            
            user_id = payload.get("user_id")
            if not user_id:
                return False
            
            # 重置密码
            success = user_service.update_password(user_id, new_password)
            if success:
                logger.info(f"密码重置成功: user_id={user_id}")
            return success
            
        except Exception as e:
            logger.error(f"重置密码失败: {e}")
            return False
    
    async def verify_email(self, verification_token: str) -> bool:
        """验证邮箱"""
        try:
            # 验证令牌
            payload = self.verify_token(verification_token)
            if not payload:
                return False
            
            user_id = payload.get("user_id")
            email = payload.get("email", "")
            
            if not user_id:
                return False
            
            # 更新邮箱验证状态
            success = user_service.verify_email(user_id)
            if success:
                logger.info(f"邮箱验证成功: user_id={user_id}, email={email}")
            return success
            
        except Exception as e:
            logger.error(f"邮箱验证失败: {e}")
            return False


# 全局认证服务实例
auth_service = AuthService()
