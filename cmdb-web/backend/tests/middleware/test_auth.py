"""认证中间件单元测试"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Request, HTTPException, status
from starlette.responses import JSONResponse

from app.middleware.auth import AuthMiddleware
from app.core.config import settings


class TestAuthMiddleware:
    """认证中间件测试类"""

    @pytest.fixture
    def auth_middleware(self):
        """创建认证中间件实例"""
        app = Mock()
        return AuthMiddleware(app)

    @pytest.fixture
    def valid_token(self, sample_user):
        """生成有效的 JWT Token"""
        from jose import jwt
        from datetime import datetime, timedelta

        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(sample_user.id),
            "username": sample_user.username,
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @pytest.fixture
    def expired_token(self, sample_user):
        """生成过期的 JWT Token"""
        from jose import jwt
        from datetime import datetime, timedelta

        expire = datetime.utcnow() - timedelta(minutes=1)
        payload = {
            "sub": str(sample_user.id),
            "username": sample_user.username,
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @pytest.fixture
    def invalid_signature_token(self, sample_user):
        """生成签名无效的 JWT Token"""
        from jose import jwt
        from datetime import datetime, timedelta

        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(sample_user.id),
            "username": sample_user.username,
            "exp": expire,
        }
        # 使用错误的密钥
        return jwt.encode(payload, "wrong_secret_key", algorithm=settings.ALGORITHM)

    def test_extract_token_valid(self, auth_middleware):
        """测试提取有效 Token"""
        request = Mock(headers={"Authorization": "Bearer valid_token_123"})
        token = auth_middleware._extract_token(request)
        assert token == "valid_token_123"

    def test_extract_token_missing_header(self, auth_middleware):
        """测试缺少 Authorization header"""
        request = Mock(headers={})
        token = auth_middleware._extract_token(request)
        assert token is None

    def test_extract_token_empty_authorization(self, auth_middleware):
        """测试空 Authorization header"""
        request = Mock(headers={"Authorization": ""})
        token = auth_middleware._extract_token(request)
        assert token is None

    def test_extract_token_invalid_format_no_bearer(self, auth_middleware):
        """测试非 Bearer 格式"""
        request = Mock(headers={"Authorization": "Token valid_token_123"})
        token = auth_middleware._extract_token(request)
        assert token is None

    def test_extract_token_only_bearer_keyword(self, auth_middleware):
        """测试只有 'Bearer' 没有 token"""
        request = Mock(headers={"Authorization": "Bearer"})
        token = auth_middleware._extract_token(request)
        assert token is None

    def test_extract_token_multiple_spaces(self, auth_middleware):
        """测试多个空格分隔"""
        request = Mock(headers={"Authorization": "Bearer   valid_token_123"})
        token = auth_middleware._extract_token(request)
        assert token == "valid_token_123"

    def test_extract_token_case_insensitive_bearer(self, auth_middleware):
        """测试 Bearer 大小写不敏感"""
        request = Mock(headers={"Authorization": "BEARER valid_token_123"})
        token = auth_middleware._extract_token(request)
        assert token == "valid_token_123"

    def test_verify_token_valid(self, auth_middleware, valid_token, sample_user):
        """测试验证有效 Token"""
        user_id = auth_middleware._verify_token(valid_token)
        assert user_id == sample_user.id

    def test_verify_token_expired(self, auth_middleware, expired_token):
        """测试验证过期 Token"""
        user_id = auth_middleware._verify_token(expired_token)
        assert user_id is None

    def test_verify_token_invalid_signature(self, auth_middleware, invalid_signature_token):
        """测试验证签名无效的 Token"""
        user_id = auth_middleware._verify_token(invalid_signature_token)
        assert user_id is None

    def test_verify_token_missing_sub(self, auth_middleware):
        """测试 Token payload 中没有 sub 字段"""
        from jose import jwt
        from datetime import datetime, timedelta

        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "username": "test",
            "exp": expire,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        user_id = auth_middleware._verify_token(token)
        assert user_id is None

    def test_verify_token_invalid_sub_type(self, auth_middleware):
        """测试 sub 字段不是整数"""
        from jose import jwt
        from datetime import datetime, timedelta

        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": "not_an_integer",
            "exp": expire,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        user_id = auth_middleware._verify_token(token)
        assert user_id is None

    @pytest.mark.asyncio
    async def test_dispatch_excluded_path(self, auth_middleware):
        """测试排除认证的路径"""
        request = Mock(url=Mock(path="/api/auth/login"))
        call_next = AsyncMock(return_value=Mock())
        
        response = await auth_middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert response == call_next.return_value

    @pytest.mark.asyncio
    async def test_dispatch_missing_token(self, auth_middleware):
        """测试缺少 Token 的请求"""
        request = Mock(url=Mock(path="/api/users"), headers={})
        call_next = AsyncMock()
        
        response = await auth_middleware.dispatch(request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.body == b'{"detail":"\\u672a\\u6388\\u6743"}'
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_invalid_token(self, auth_middleware):
        """测试无效 Token 的请求"""
        request = Mock(
            url=Mock(path="/api/users"),
            headers={"Authorization": "Bearer invalid_token"}
        )
        call_next = AsyncMock()
        
        # Mock _verify_token 返回 None
        with patch.object(auth_middleware, '_verify_token', return_value=None):
            response = await auth_middleware.dispatch(request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.body == b'{"detail":"\\u4ee4\\u724c\\u65e0\\u6548\\u6216\\u5df2\\u8fc7\\u671f"}'
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_valid_token(self, auth_middleware, valid_token, sample_user):
        """测试有效 Token 的请求"""
        request = Mock(
            url=Mock(path="/api/users"),
            headers={"Authorization": f"Bearer {valid_token}"},
            state=Mock()
        )
        call_next = AsyncMock(return_value=Mock())
        
        response = await auth_middleware.dispatch(request, call_next)
        
        assert response == call_next.return_value
        assert request.state.user_id == sample_user.id
        assert request.state.token == valid_token
        call_next.assert_called_once_with(request)

    def test_exclude_paths_default(self):
        """测试默认排除路径"""
        app = Mock()
        middleware = AuthMiddleware(app)
        expected_paths = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/health",
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        assert middleware.exclude_paths == expected_paths

    def test_exclude_paths_custom(self):
        """测试自定义排除路径"""
        app = Mock()
        custom_paths = ["/public", "/no-auth"]
        middleware = AuthMiddleware(app, exclude_paths=custom_paths)
        assert middleware.exclude_paths == custom_paths