"""API 路由模块"""

from app.api.routes.auth import router as auth_router
from app.api.routes.ci import router as ci_router
from app.api.routes.user import router as user_router
from app.api.routes.health import router as health_router

__all__ = ["auth_router", "ci_router", "user_router", "health_router"]
