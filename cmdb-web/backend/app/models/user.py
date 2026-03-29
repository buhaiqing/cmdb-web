"""用户和权限模型"""

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Table,
    Column,
    Integer,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
from app.models.base import Base, TimestampMixin


class UserStatus(str, Enum):
    """用户状态枚举"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


# 用户 - 角色关联表（多对多）
user_roles = Table(
    "t_user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("t_user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("t_role.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base, TimestampMixin):
    """用户模型"""

    __tablename__ = "t_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    change_records = relationship(
        "ChangeRecord",
        foreign_keys="[ChangeRecord.operator_id]",
        back_populates="operator"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    def has_role(self, role_code: str) -> bool:
        """检查用户是否拥有指定角色"""
        return any(role.code == role_code for role in self.roles)

    def has_permission(self, permission_code: str) -> bool:
        """检查用户是否拥有指定权限"""
        for role in self.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        return False


class Role(Base, TimestampMixin):
    """角色模型"""

    __tablename__ = "t_role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 关系
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship(
        "Permission",
        secondary="t_role_permissions",
        back_populates="roles",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, code={self.code}, name={self.name})>"


# 角色 - 权限关联表（多对多）
role_permissions = Table(
    "t_role_permissions",
    Base.metadata,
    Column(
        "role_id", ForeignKey("t_role.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        ForeignKey("t_permission.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(Base, TimestampMixin):
    """权限模型"""

    __tablename__ = "t_permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)

    # 关系
    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code={self.code}, resource={self.resource})>"
