"""数据模型基类"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Integer, DateTime, func
from typing import Any


class Base(DeclarativeBase):
    """所有模型的基类"""

    # 表名自动生成
    @declared_attr
    def __tablename__(cls) -> str:
        # 将驼峰命名转换为下划线命名
        import re
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        return f"t_{name}"

    def to_dict(self) -> dict[str, Any]:
        """将模型转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TimestampMixin:
    """时间戳混合类，包含创建时间和更新时间"""

    created_at = DateTime(timezone=True, server_default=func.now(), nullable=False)
    updated_at = DateTime(
        timezone=True, server_default=func.now(), onupdate=func.now(), nullable=False
    )
