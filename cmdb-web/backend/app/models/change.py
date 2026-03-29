"""变更管理模型"""

from sqlalchemy import (
    String,
    Text,
    Integer,
    ForeignKey,
    Column,
    Enum as SQLEnum,
    DateTime,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
from datetime import datetime
from app.models.base import Base, TimestampMixin


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


class ChangeRecord(Base, TimestampMixin):
    """变更记录模型"""

    __tablename__ = "t_change_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ci_id: Mapped[int] = mapped_column(
        ForeignKey("t_configuration_item.id", ondelete="CASCADE"), nullable=False
    )
    change_type: Mapped[ChangeType] = mapped_column(
        SQLEnum(ChangeType), nullable=False
    )
    status: Mapped[ChangeStatus] = mapped_column(
        SQLEnum(ChangeStatus), default=ChangeStatus.PENDING, nullable=False
    )
    priority: Mapped[ChangePriority] = mapped_column(
        SQLEnum(ChangePriority), default=ChangePriority.MEDIUM, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 字符串
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 字符串
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("t_user.id", ondelete="SET NULL"), nullable=True
    )
    approver_id: Mapped[int | None] = mapped_column(
        ForeignKey("t_user.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 关系
    configuration_item = relationship("ConfigurationItem", back_populates="change_records")
    operator = relationship("User", foreign_keys=[operator_id], back_populates="change_records")
    approver = relationship("User", foreign_keys=[approver_id])

    def __repr__(self) -> str:
        return f"<ChangeRecord(id={self.id}, ci_id={self.ci_id}, type={self.change_type})>"
