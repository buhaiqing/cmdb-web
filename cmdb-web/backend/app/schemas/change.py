"""变更管理 Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class ChangeType(str, Enum):
    """变更类型"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RELATION_ADD = "relation_add"
    RELATION_REMOVE = "relation_remove"


class ChangeStatus(str, Enum):
    """变更状态"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


class ChangePriority(str, Enum):
    """变更优先级"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeRecordBase(BaseModel):
    """变更记录基础 Schema"""

    title: str = Field(..., min_length=1, max_length=200, description="变更标题")
    description: Optional[str] = Field(None, description="变更描述")
    reason: Optional[str] = Field(None, max_length=500, description="变更原因")


class ChangeRecordCreate(ChangeRecordBase):
    """创建变更记录请求"""

    ci_id: int = Field(..., description="配置项 ID")
    change_type: ChangeType = Field(..., description="变更类型")
    priority: ChangePriority = Field(default=ChangePriority.MEDIUM, description="优先级")
    old_value: Optional[dict[str, Any]] = Field(None, description="旧值")
    new_value: Optional[dict[str, Any]] = Field(None, description="新值")
    scheduled_at: Optional[datetime] = Field(None, description="计划执行时间")


class ChangeRecordUpdate(BaseModel):
    """更新变更记录请求"""

    title: Optional[str] = Field(None, max_length=200, description="变更标题")
    description: Optional[str] = Field(None, description="变更描述")
    priority: Optional[ChangePriority] = Field(None, description="优先级")
    reason: Optional[str] = Field(None, max_length=500, description="变更原因")
    scheduled_at: Optional[datetime] = Field(None, description="计划执行时间")


class ChangeRecordResponse(ChangeRecordBase):
    """变更记录响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="变更记录 ID")
    ci_id: int = Field(..., description="配置项 ID")
    change_type: ChangeType = Field(..., description="变更类型")
    status: ChangeStatus = Field(..., description="变更状态")
    priority: ChangePriority = Field(..., description="优先级")
    old_value: Optional[dict[str, Any]] = Field(None, description="旧值")
    new_value: Optional[dict[str, Any]] = Field(None, description="新值")
    operator_id: Optional[int] = Field(None, description="操作人 ID")
    approver_id: Optional[int] = Field(None, description="审批人 ID")
    approved_at: Optional[datetime] = Field(None, description="审批时间")
    scheduled_at: Optional[datetime] = Field(None, description="计划执行时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ChangeRecordListResponse(BaseModel):
    """变更记录列表响应"""

    items: List[ChangeRecordResponse] = Field(..., description="变更记录列表")
    total: int = Field(..., description="总数")


class ChangeApprovalRequest(BaseModel):
    """变更审批请求"""

    approved: bool = Field(..., description="是否批准")
    reason: Optional[str] = Field(None, max_length=500, description="审批意见")
