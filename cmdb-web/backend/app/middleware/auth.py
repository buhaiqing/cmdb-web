"""认证中间件"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from jose import jwt, JWTError

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.db.session import SessionLocal
from app.models.user import User, UserStatus


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""

    def __init__(
        self,
        app,
        exclude_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/api/auth/login",
            "/api/auth/register",
            "/api/health",
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        # 检查是否需要跳过认证
        path = request.url.path
        # 精确匹配或前缀匹配
        if path in self.exclude_paths or any(
            path.startswith(exclude_path + "/") for exclude_path in self.exclude_paths
        ):
            return await call_next(request)

        # 获取 Token
        token = self._extract_token(request)
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "未授权"},
            )

        # 验证 Token
        user_id = self._verify_token(token)
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "令牌无效或已过期"},
            )

        # 将用户 ID 注入到请求状态中
        request.state.user_id = user_id
        request.state.token = token

        return await call_next(request)

    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求中提取 Token"""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    def _verify_token(self, token: str) -> Optional[int]:
        """验证 Token 并返回用户 ID"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            user_id = payload.get("sub")
            if not user_id:
                return None
            return int(user_id)
        except (JWTError, ValueError):
            return None
