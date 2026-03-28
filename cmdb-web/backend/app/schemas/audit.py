"""审计日志 Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AuditAction(str, Enum):
    """审计操作类型"""

    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
    PERMISSION_CHANGE = "permission_change"
    ROLE_CHANGE = "role_change"


class AuditStatus(str, Enum):
    """审计状态"""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class AuditLogBase(BaseModel):
    """审计日志基础 Schema"""

    action: AuditAction = Field(..., description="操作类型")
    resource_type: str = Field(..., min_length=1, max_length=50, description="资源类型")
    request_method: Optional[str] = Field(None, max_length=10, description="请求方法")
    request_path: Optional[str] = Field(None, max_length=255, description="请求路径")


class AuditLogResponse(AuditLogBase):
    """审计日志响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="审计日志 ID")
    user_id: Optional[int] = Field(None, description="用户 ID")
    status: AuditStatus = Field(..., description="操作状态")
    resource_id: Optional[int] = Field(None, description="资源 ID")
    ip_address: Optional[str] = Field(None, description="IP 地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    request_body: Optional[str] = Field(None, description="请求体")
    response_code: Optional[int] = Field(None, description="响应码")
    error_message: Optional[str] = Field(None, description="错误消息")
    created_at: datetime = Field(..., description="创建时间")


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""

    items: List[AuditLogResponse] = Field(..., description="审计日志列表")
    total: int = Field(..., description="总数")
