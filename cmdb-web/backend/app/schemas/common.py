"""通用 Schemas"""

from pydantic import BaseModel, Field
from typing import Any, Generic, TypeVar, Optional, List

T = TypeVar("T")


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = Field(..., description="状态")
    version: str = Field(..., description="版本号")


class BaseResponse(BaseModel):
    """基础响应"""

    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    error: Optional[dict[str, Any]] = Field(default=None, description="错误信息")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""

    items: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
