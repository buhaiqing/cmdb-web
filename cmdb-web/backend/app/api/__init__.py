"""API 路由模块"""

from fastapi import APIRouter

from app.api.routes import auth, ci, user, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(ci.router, prefix="/cis", tags=["配置项"])
api_router.include_router(user.router, prefix="/users", tags=["用户"])
api_router.include_router(health.router, prefix="", tags=["健康检查"])

__all__ = ["api_router"]
