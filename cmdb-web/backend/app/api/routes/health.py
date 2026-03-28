"""健康检查路由"""

from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import HealthResponse, BaseResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
    )


@router.get("", response_model=BaseResponse)
def root():
    """根路径"""
    return BaseResponse(
        message=f"Welcome to {settings.APP_NAME}",
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
        },
    )
