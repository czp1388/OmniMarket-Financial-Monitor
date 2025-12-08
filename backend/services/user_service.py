import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import hashlib

from models.users import User, UserSession
from database import get_db

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db = next(get_db())
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """创建新用户"""
        try:
            # 检查用户名或邮箱是否已存在
            existing_user = self.db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                logger.warning(f"用户 {username} 或邮箱 {email} 已存在")
                return None
            
            # 创建密码哈希
            password_hash = self._hash_password(password)
            
            # 创建用户
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                is_active=True,
                created_at=datetime.now()
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"创建用户成功: {username}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建用户失败: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        try:
            user = self.db.query(User).filter(
                (User.username == username) & (User.is_active == True)
            ).first()
            
            if not user:
                logger.warning(f"用户不存在或未激活: {username}")
                return None
            
            # 验证密码
            if not self._verify_password(password, user.password_hash):
                logger.warning(f"密码验证失败: {username}")
                return None
            
            logger.info(f"用户认证成功: {username}")
            return user
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    def create_session(self, user_id: int, client_info: Dict[str, Any] = None) -> Optional[str]:
        """创建用户会话"""
        try:
            # 生成会话令牌
            session_token = secrets.token_urlsafe(32)
            
            # 创建会话
            session = UserSession(
                user_id=user_id,
                session_token=session_token,
                expires_at=datetime.now() + timedelta(days=30),  # 30天有效期
                client_info=client_info or {},
                created_at=datetime.now()
            )
            
            self.db.add(session)
            self.db.commit()
            
            logger.info(f"创建会话成功: user_id={user_id}")
            return session_token
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建会话失败: {e}")
            return None
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """验证会话令牌"""
        try:
            session = self.db.query(UserSession).filter(
                (UserSession.session_token == session_token) &
                (UserSession.expires_at > datetime.now()) &
                (UserSession.is_active == True)
            ).first()
            
            if not session:
                logger.warning("会话令牌无效或已过期")
                return None
            
            # 获取用户信息
            user = self.db.query(User).filter(
                (User.id == session.user_id) &
                (User.is_active == True)
            ).first()
            
            if not user:
                logger.warning("用户不存在或未激活")
                return None
            
            # 更新会话最后访问时间
            session.last_accessed_at = datetime.now()
            self.db.commit()
            
            logger.info(f"会话验证成功: user_id={user.id}")
            return user
            
        except Exception as e:
            logger.error(f"会话验证失败: {e}")
            return None
    
    def invalidate_session(self, session_token: str) -> bool:
        """使会话失效"""
        try:
            session = self.db.query(UserSession).filter(
                UserSession.session_token == session_token
            ).first()
            
            if session:
                session.is_active = False
                self.db.commit()
                logger.info(f"会话已失效: {session_token}")
                return True
            
            logger.warning(f"会话不存在: {session_token}")
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"会话失效失败: {e}")
            return False
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        try:
            user = self.db.query(User).filter(
                (User.id == user_id) & (User.is_active == True)
            ).first()
            
            return user
            
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[User]:
        """更新用户资料"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            # 更新允许的字段
            allowed_fields = ['email', 'display_name', 'preferences']
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            user.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"用户资料更新成功: user_id={user_id}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户资料失败: {e}")
            return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # 验证旧密码
            if not self._verify_password(old_password, user.password_hash):
                logger.warning("旧密码验证失败")
                return False
            
            # 更新密码
            user.password_hash = self._hash_password(new_password)
            user.updated_at = datetime.now()
            self.db.commit()
            
            logger.info(f"密码修改成功: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"密码修改失败: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = secrets.token_bytes(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # 迭代次数
        )
        return salt.hex() + password_hash.hex()
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """验证密码"""
        try:
            salt = bytes.fromhex(stored_hash[:64])  # 前64个字符是salt
            stored_password_hash = stored_hash[64:]
            
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            ).hex()
            
            return password_hash == stored_password_hash
            
        except Exception as e:
            logger.error(f"密码验证出错: {e}")
            return False
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """公开的密码验证方法"""
        return self._verify_password(password, stored_hash)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            user = self.db.query(User).filter(User.username == username).first()
            return user
        except Exception as e:
            logger.error(f"根据用户名获取用户失败: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            user = self.db.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            logger.error(f"根据邮箱获取用户失败: {e}")
            return None
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """更新用户信息"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            for key, value in updates.items():
                if hasattr(user, key) and key != 'id' and key != 'password_hash':
                    setattr(user, key, value)
            
            user.updated_at = datetime.now()
            self.db.commit()
            logger.info(f"用户信息更新成功: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户信息失败: {e}")
            return False
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """更新密码（不验证旧密码）"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.password_hash = self._hash_password(new_password)
            user.updated_at = datetime.now()
            self.db.commit()
            logger.info(f"密码更新成功: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"密码更新失败: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """停用用户"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.now()
            self.db.commit()
            logger.info(f"用户已停用: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"停用用户失败: {e}")
            return False
    
    def activate_user(self, user_id: int) -> bool:
        """激活用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_active = True
            user.updated_at = datetime.now()
            self.db.commit()
            logger.info(f"用户已激活: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"激活用户失败: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            logger.info(f"用户已删除: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除用户失败: {e}")
            return False
    
    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """列出所有用户"""
        try:
            users = self.db.query(User).offset(skip).limit(limit).all()
            return users
        except Exception as e:
            logger.error(f"列出用户失败: {e}")
            return []
    
    def count_users(self) -> int:
        """统计用户数量"""
        try:
            count = self.db.query(User).count()
            return count
        except Exception as e:
            logger.error(f"统计用户数量失败: {e}")
            return 0
    
    def update_last_login(self, user_id: int) -> bool:
        """更新最后登录时间"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.last_login_at = datetime.now()
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新最后登录时间失败: {e}")
            return False
    
    def verify_email(self, user_id: int) -> bool:
        """验证邮箱"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.email_verified = True
            user.email_verified_at = datetime.now()
            self.db.commit()
            logger.info(f"邮箱验证成功: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"邮箱验证失败: {e}")
            return False
    
    def change_email(self, user_id: int, new_email: str) -> bool:
        """修改邮箱"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # 检查新邮箱是否已被使用
            existing = self.db.query(User).filter(User.email == new_email).first()
            if existing and existing.id != user_id:
                logger.warning(f"邮箱已被使用: {new_email}")
                return False
            
            user.email = new_email
            user.email_verified = False  # 需要重新验证
            user.updated_at = datetime.now()
            self.db.commit()
            logger.info(f"邮箱修改成功: user_id={user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"修改邮箱失败: {e}")
            return False


# 全局用户服务实例
user_service = UserService()
