"""用户相关 Schemas"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """用户状态"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


# ==================== 用户 Schemas ====================


class UserBase(BaseModel):
    """用户基础 Schema"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    """创建用户请求"""

    password: str = Field(..., min_length=8, max_length=128, description="密码")


class UserUpdate(BaseModel):
    """更新用户请求"""

    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="新密码")
    status: Optional[UserStatus] = Field(None, description="用户状态")


class UserResponse(UserBase):
    """用户响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户 ID")
    status: UserStatus = Field(..., description="用户状态")
    is_superuser: bool = Field(default=False, description="是否超级管理员")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UserInDB(UserResponse):
    """数据库中的用户 Schema（包含密码哈希）"""

    password_hash: str = Field(..., description="密码哈希")


# ==================== 角色 Schemas ====================


class RoleBase(BaseModel):
    """角色基础 Schema"""

    name: str = Field(..., min_length=2, max_length=50, description="角色名称")
    code: str = Field(..., min_length=2, max_length=50, description="角色代码")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")


class RoleCreate(RoleBase):
    """创建角色请求"""

    permission_ids: Optional[List[int]] = Field(None, description="权限 ID 列表")


class RoleUpdate(BaseModel):
    """更新角色请求"""

    name: Optional[str] = Field(None, min_length=2, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")
    permission_ids: Optional[List[int]] = Field(None, description="权限 ID 列表")


class RoleResponse(RoleBase):
    """角色响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色 ID")
    is_system: bool = Field(default=False, description="是否系统角色")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ==================== 权限 Schemas ====================


class PermissionBase(BaseModel):
    """权限基础 Schema"""

    name: str = Field(..., min_length=2, max_length=50, description="权限名称")
    code: str = Field(..., min_length=2, max_length=100, description="权限代码")
    resource: str = Field(..., min_length=2, max_length=50, description="资源类型")
    action: str = Field(..., min_length=2, max_length=20, description="操作类型")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")


class PermissionCreate(PermissionBase):
    """创建权限请求"""


class PermissionResponse(PermissionBase):
    """权限响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="权限 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ==================== 认证 Schemas ====================


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""

    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
