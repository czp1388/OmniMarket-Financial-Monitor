import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException

from .user_service import user_service
from backend.config import settings

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
                    "display_name": user.display_name
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
        except jwt.InvalidTokenError:
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


# 全局认证服务实例
auth_service = AuthService()
