"""认证服务层单元测试"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.services.auth_service import AuthService
from app.models.user import User, UserStatus
from app.core.security import hash_password
from app.core.config import settings


class TestAuthService:
    """认证服务测试类"""

    def test_create_access_token(self, test_db, sample_user):
        """测试创建访问令牌"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert payload["sub"] == str(sample_user.id)
        assert payload["username"] == sample_user.username

    def test_create_access_token_expires_in_future(self, test_db, sample_user):
        """测试创建的令牌在未来过期"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        assert exp_time > now

    def test_verify_token_valid(self, test_db, sample_user):
        """测试验证有效令牌"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        payload = service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == str(sample_user.id)

    def test_verify_token_invalid(self, test_db):
        """测试验证无效令牌"""
        service = AuthService(test_db)
        payload = service.verify_token("invalid.token.here")
        assert payload is None

    def test_verify_token_tampered(self, test_db, sample_user):
        """测试验证被篡改的令牌"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        tampered_token = token + "tampered"
        payload = service.verify_token(tampered_token)
        assert payload is None

    def test_verify_token_expired(self, test_db, sample_user):
        """测试验证过期令牌"""
        service = AuthService(test_db)

        expire = datetime.utcnow() - timedelta(minutes=1)
        expired_payload = {
            "exp": expire,
            "sub": str(sample_user.id),
            "username": sample_user.username,
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        payload = service.verify_token(expired_token)
        assert payload is None

    def test_get_current_user_valid_token(self, test_db, sample_user):
        """测试获取当前用户 - 有效令牌"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        user = service.get_current_user(token)
        assert user is not None
        assert user.id == sample_user.id
        assert user.username == sample_user.username

    def test_get_current_user_invalid_token(self, test_db):
        """测试获取当前用户 - 无效令牌"""
        service = AuthService(test_db)
        user = service.get_current_user("invalid.token")
        assert user is None

    def test_get_current_user_nonexistent_user(self, test_db):
        """测试获取当前用户 - 用户不存在"""
        service = AuthService(test_db)

        token = service.create_access_token(99999, "nonexistent")
        user = service.get_current_user(token)
        assert user is None

    def test_refresh_token_valid(self, test_db, sample_user):
        """测试刷新令牌 - 有效令牌"""
        service = AuthService(test_db)
        old_token = service.create_access_token(sample_user.id, sample_user.username)

        new_token = service.refresh_token(old_token)
        assert new_token is not None
        assert new_token != old_token

        new_payload = jwt.decode(
            new_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert new_payload["sub"] == str(sample_user.id)

    def test_refresh_token_invalid(self, test_db):
        """测试刷新令牌 - 无效令牌"""
        service = AuthService(test_db)
        new_token = service.refresh_token("invalid.token")
        assert new_token is None

    def test_refresh_token_nonexistent_user(self, test_db):
        """测试刷新令牌 - 用户不存在"""
        service = AuthService(test_db)
        token = service.create_access_token(99999, "nonexistent")
        new_token = service.refresh_token(token)
        assert new_token is None

    def test_authenticate_user_success(self, test_db, sample_user):
        """测试用户认证成功"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        user = service.get_current_user(token)
        assert user is not None
        assert user.username == sample_user.username

    def test_authenticate_wrong_password(self, test_db, sample_user):
        """测试用户认证 - 密码错误"""
        from app.services.user_service import UserService

        service = AuthService(test_db)
        user_service = UserService(test_db)

        result = user_service.authenticate(sample_user.username, "WrongPassword")
        assert result is None

    def test_authenticate_inactive_user(self, test_db, inactive_user):
        """测试用户认证 - 非活跃用户"""
        from app.services.user_service import UserService
        from app.core.exceptions import BadRequestException

        service = AuthService(test_db)
        user_service = UserService(test_db)

        with pytest.raises(BadRequestException):
            user_service.authenticate(inactive_user.username, "TestPassword123")


class TestJWTToken:
    """JWT 令牌测试类"""

    def test_token_contains_required_claims(self, test_db, sample_user):
        """测试令牌包含必要声明"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        assert "sub" in payload
        assert "username" in payload
        assert "exp" in payload

    def test_token_subject_is_user_id(self, test_db, sample_user):
        """测试令牌主题是用户 ID"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        assert payload["sub"] == str(sample_user.id)

    def test_token_expiration_time(self, test_db, sample_user):
        """测试令牌过期时间"""
        service = AuthService(test_db)
        token = service.create_access_token(sample_user.id, sample_user.username)

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        exp_timestamp = payload["exp"]
        exp_time = datetime.fromtimestamp(exp_timestamp)
        expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 5
