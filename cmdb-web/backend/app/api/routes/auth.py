"""认证路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.schemas.user import TokenResponse, UserResponse, UserCreate
from app.schemas.common import BaseResponse
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, BadRequestException, ConflictException

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """用户登录"""
    user_service = UserService(db)
    auth_service = AuthService(db)

    # 认证用户
    user = user_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException(message="用户名或密码错误")

    # 创建访问令牌
    access_token = auth_service.create_access_token(user.id, user.username)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """用户注册"""
    user_service = UserService(db)
    return user_service.create(user_in=user_in)


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> UserResponse:
    """获取当前用户依赖项"""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if not user:
        raise UnauthorizedException(message="令牌无效或已过期")
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
):
    """获取当前用户信息"""
    return current_user
