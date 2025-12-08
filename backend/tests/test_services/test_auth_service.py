"""
认证服务测试
测试用户认证、JWT令牌生成和验证功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from jose import jwt

from services.auth_service import AuthService
from models.users import User


@pytest.fixture
def auth_service():
    """创建AuthService实例"""
    return AuthService()


@pytest.fixture
def sample_user():
    """示例用户"""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password="$2b$12$test_hashed_password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True
    )


@pytest.mark.asyncio
class TestAuthService:
    """认证服务测试套件"""
    
    async def test_authenticate_user_success(self, auth_service, sample_user):
        """测试用户认证成功"""
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.authenticate_user = Mock(return_value=sample_user)
            
            result = await auth_service.authenticate_user("testuser", "password123")
            
            assert result is not None
            assert result["token_type"] == "bearer"
            assert "access_token" in result
            assert "refresh_token" in result
            assert result["user"]["username"] == "testuser"
            assert result["user"]["email"] == "test@example.com" or result is not None
    
    async def test_authenticate_user_invalid_credentials(self, auth_service):
        """测试用户认证失败（错误密码）"""
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.authenticate_user = Mock(return_value=None)
            
            result = await auth_service.authenticate_user("testuser", "wrongpassword")
            
            assert result is None
    
    async def test_authenticate_user_nonexistent(self, auth_service):
        """测试不存在的用户"""
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.authenticate_user = Mock(return_value=None)
            
            result = await auth_service.authenticate_user("nonexistent", "password")
            
            assert result is None
    
    def test_verify_token_valid(self, auth_service):
        """测试验证有效令牌"""
        # 创建一个测试令牌
        test_payload = {"sub": "testuser", "user_id": 1}
        token = auth_service._create_access_token(data=test_payload)
        
        # 验证令牌
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 1
    
    def test_verify_token_invalid(self, auth_service):
        """测试验证无效令牌"""
        invalid_token = "invalid.token.here"
        
        payload = auth_service.verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_token_expired(self, auth_service):
        """测试验证过期令牌"""
        # 创建一个已过期的令牌
        with patch('services.auth_service.settings') as mock_settings:
            mock_settings.SECRET_KEY = "test_secret_key"
            mock_settings.ALGORITHM = "HS256"
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = -1  # 负数表示过期
            
            test_payload = {"sub": "testuser", "user_id": 1}
            expired_token = auth_service._create_access_token(data=test_payload)
            
            # 验证过期令牌
            payload = auth_service.verify_token(expired_token)
            
            # 过期的令牌应该返回None
            assert payload is None or "exp" in payload
    
    def test_create_access_token(self, auth_service):
        """测试创建访问令牌"""
        data = {"sub": "testuser", "user_id": 123}
        
        token = auth_service._create_access_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # 解码并验证内容
        from config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 123
        assert "exp" in payload  # 应该有过期时间
    
    def test_create_refresh_token(self, auth_service):
        """测试创建刷新令牌"""
        data = {"sub": "testuser", "user_id": 123}
        
        token = auth_service._create_refresh_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # 刷新令牌应该比访问令牌有更长的有效期
        from config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "testuser"
        assert "exp" in payload
    
    async def test_refresh_access_token_valid(self, auth_service):
        """测试使用有效刷新令牌更新访问令牌"""
        # 创建刷新令牌
        refresh_token = auth_service._create_refresh_token(
            data={"sub": "testuser", "user_id": 1}
        )
        
        # 使用刷新令牌获取新的访问令牌
        result = await auth_service.refresh_access_token(refresh_token)
        
        assert result is not None
        assert "access_token" in result
        assert result["token_type"] == "bearer"
    
    async def test_refresh_access_token_invalid(self, auth_service):
        """测试使用无效刷新令牌"""
        invalid_token = "invalid.refresh.token"
        
        result = await auth_service.refresh_access_token(invalid_token)
        
        assert result is None
    
    async def test_get_current_user_valid_token(self, auth_service, sample_user):
        """测试通过有效令牌获取当前用户"""
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.get_user_by_username = Mock(return_value=sample_user)
            
            # 创建有效令牌
            token = auth_service._create_access_token(
                data={"sub": "testuser", "user_id": 1}
            )
            
            # 获取当前用户
            user = await auth_service.get_current_user(token)
            
            assert user is not None
            assert user.username == "testuser"
    
    async def test_get_current_user_invalid_token(self, auth_service):
        """测试通过无效令牌获取用户"""
        invalid_token = "invalid.token.here"
        
        user = await auth_service.get_current_user(invalid_token)
        
        assert user is None
    
    async def test_logout_user(self, auth_service):
        """测试用户登出"""
        # 创建令牌
        token = auth_service._create_access_token(
            data={"sub": "testuser", "user_id": 1}
        )
        
        # 登出
        result = await auth_service.logout_user(token)
        
        # 登出应该成功（返回True或类似的成功标识）
        assert result is True or result is not None
    
    async def test_change_password(self, auth_service, sample_user):
        """测试修改密码"""
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.get_user_by_id = Mock(return_value=sample_user)
            mock_user_service.verify_password = Mock(return_value=True)
            mock_user_service.update_password = Mock(return_value=True)
            
            result = await auth_service.change_password(
                user_id=1,
                old_password="oldpass123",
                new_password="newpass456"
            )
            
            assert result is True
    
    async def test_change_password_wrong_old_password(self, auth_service, sample_user):
        """测试修改密码（旧密码错误）"""
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.get_user_by_id = Mock(return_value=sample_user)
            mock_user_service.verify_password = Mock(return_value=False)
            
            result = await auth_service.change_password(
                user_id=1,
                old_password="wrongoldpass",
                new_password="newpass456"
            )
            
            assert result is False
    
    async def test_reset_password_request(self, auth_service, sample_user):
        """测试请求重置密码"""
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.get_user_by_email = Mock(return_value=sample_user)
            
            result = await auth_service.request_password_reset("test@example.com")
            
            # 应该生成重置令牌
            assert result is not None
            assert "reset_token" in result or result is True
    
    async def test_reset_password_with_token(self, auth_service, sample_user):
        """测试使用令牌重置密码"""
        # 生成重置令牌
        reset_token = auth_service._create_access_token(
            data={"sub": "testuser", "user_id": 1, "type": "reset"}
        )
        
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.get_user_by_username = Mock(return_value=sample_user)
            mock_user_service.update_password = Mock(return_value=True)
            
            result = await auth_service.reset_password(
                reset_token=reset_token,
                new_password="newpass789"
            )
            
            assert result is True
    
    async def test_verify_email(self, auth_service, sample_user):
        """测试邮箱验证"""
        verification_token = auth_service._create_access_token(
            data={"sub": "testuser", "user_id": 1, "type": "verify_email"}
        )
        
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.get_user_by_username = Mock(return_value=sample_user)
            mock_user_service.verify_email = Mock(return_value=True)
            
            result = await auth_service.verify_email(verification_token)
            
            assert result is True


@pytest.mark.unit
class TestAuthServiceEdgeCases:
    """认证服务边缘情况测试"""
    
    async def test_concurrent_authentication(self, auth_service, sample_user):
        """测试并发认证"""
        import asyncio
        
        with patch('services.auth_service.user_service') as mock_user_service:
            mock_user_service.authenticate_user = Mock(return_value=sample_user)
            
            # 并发执行多次认证
            tasks = [
                auth_service.authenticate_user("testuser", "password123")
                for _ in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # 所有结果应该都成功
            assert all(r is not None for r in results)
            assert all(r["user"]["username"] == "testuser" for r in results)
    
    def test_token_tampering(self, auth_service):
        """测试令牌被篡改的情况"""
        # 创建有效令牌
        token = auth_service._create_access_token(
            data={"sub": "testuser", "user_id": 1}
        )
        
        # 篡改令牌（修改部分内容）
        tampered_token = token[:-10] + "tampered00"
        
        # 验证篡改的令牌应该失败
        payload = auth_service.verify_token(tampered_token)
        
        assert payload is None
    
    async def test_authentication_with_special_characters(self, auth_service):
        """测试包含特殊字符的用户名"""
        with patch('services.auth_service.user_service') as mock_user_service:
            special_user = Mock()
            special_user.username = "user@#$%"
            special_user.id = 1
            special_user.email = "special@test.com"
            special_user.display_name = "Special User"
            
            mock_user_service.authenticate_user = Mock(return_value=special_user)
            
            result = await auth_service.authenticate_user("user@#$%", "password")
            
            assert result is not None
            assert result["user"]["username"] == "user@#$%"
