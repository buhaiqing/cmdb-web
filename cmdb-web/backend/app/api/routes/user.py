"""用户路由"""

from fastapi import APIRouter, Depends, Query, Body, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    RoleResponse,
    RoleCreate,
    PermissionResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.user_service import UserService
from app.core.exceptions import NotFoundException
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取用户列表"""
    user_service = UserService(db)
    skip = (page - 1) * page_size

    items = user_service.get_multi(skip=skip, limit=page_size)
    total = user_service.get_count()

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """创建用户"""
    user_service = UserService(db)
    return user_service.create(user_in=user_in)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取用户详情"""
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException(message="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """更新用户"""
    user_service = UserService(db)
    return user_service.update(user_id=user_id, user_in=user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """删除用户"""
    user_service = UserService(db)
    user_service.delete(user_id=user_id)
