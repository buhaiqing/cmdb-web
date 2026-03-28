"""Pydantic schemas 模块"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionCreate,
    PermissionResponse,
    LoginRequest,
    TokenResponse,
)
from app.schemas.ci import (
    CIBase,
    CICreate,
    CIUpdate,
    CIResponse,
    CIListResponse,
    CIRelationCreate,
    CIRelationResponse,
    CISearchRequest,
    ServerCI,
    NetworkDeviceCI,
    DatabaseCI,
    MiddlewareCI,
    ApplicationCI,
    ContainerCI,
    K8sResourceCI,
    CloudResourceCI,
)
from app.schemas.change import (
    ChangeRecordCreate,
    ChangeRecordUpdate,
    ChangeRecordResponse,
    ChangeRecordListResponse,
    ChangeApprovalRequest,
)
from app.schemas.audit import (
    AuditLogResponse,
    AuditLogListResponse,
)
from app.schemas.common import (
    BaseResponse,
    PaginatedResponse,
    HealthResponse,
)

__all__ = [
    # 用户
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "PermissionCreate",
    "PermissionResponse",
    "LoginRequest",
    "TokenResponse",
    # 配置项
    "CIBase",
    "CICreate",
    "CIUpdate",
    "CIResponse",
    "CIListResponse",
    "CIRelationCreate",
    "CIRelationResponse",
    "CISearchRequest",
    "ServerCI",
    "NetworkDeviceCI",
    "DatabaseCI",
    "MiddlewareCI",
    "ApplicationCI",
    "ContainerCI",
    "K8sResourceCI",
    "CloudResourceCI",
    # 变更
    "ChangeRecordCreate",
    "ChangeRecordUpdate",
    "ChangeRecordResponse",
    "ChangeRecordListResponse",
    "ChangeApprovalRequest",
    # 审计
    "AuditLogResponse",
    "AuditLogListResponse",
    # 通用
    "BaseResponse",
    "PaginatedResponse",
    "HealthResponse",
]
