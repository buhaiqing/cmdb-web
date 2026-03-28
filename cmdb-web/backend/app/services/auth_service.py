"""认证服务层"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

from app.core.config import settings
from app.services.user_service import UserService
from app.models.user import User


class AuthService:
    """认证服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def create_access_token(self, user_id: int, username: str) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "exp": expire,
            "sub": str(user_id),
            "username": username,
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return payload
        except JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """获取当前用户"""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = int(payload.get("sub"))
        if not user_id:
            return None

        return self.user_service.get_by_id(user_id)

    def refresh_token(self, token: str) -> Optional[str]:
        """刷新令牌"""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = int(payload.get("sub"))
        username = payload.get("username")

        if not user_id or not username:
            return None

        user = self.user_service.get_by_id(user_id)
        if not user:
            return None

        return self.create_access_token(user.id, user.username)
