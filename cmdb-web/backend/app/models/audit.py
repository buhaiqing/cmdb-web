"""审计日志模型"""

from sqlalchemy import (
    String,
    Text,
    Integer,
    ForeignKey,
    Column,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
from app.models.base import Base, TimestampMixin


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


class AuditLog(Base, TimestampMixin):
    """审计日志模型"""

    __tablename__ = "t_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("t_user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction), nullable=False, index=True
    )
    status: Mapped[AuditStatus] = mapped_column(
        SQLEnum(AuditStatus), nullable=False, index=True
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[int | None] = mapped_column(nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    request_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 字符串

    # 关系
    user = relationship("User", back_populates="audit_logs")

    # 索引
    __table_args__ = (
        Index("ix_audit_log_created_at", "created_at"),
        Index("ix_audit_log_user_action", "user_id", "action"),
        Index("ix_audit_log_resource", "resource_type", "resource_id"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
