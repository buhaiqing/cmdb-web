"""CMDB Web 应用主入口"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import api_router
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.db.session import init_db


# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行的操作
    logger.info("Starting CMDB API...")
    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")

    # 初始化数据库
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

    yield

    # 关闭时执行的操作
    logger.info("Shutting down CMDB API...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="运维部 CMDB 配置管理数据库 API",
    lifespan=lifespan,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加认证中间件
app.add_middleware(
    AuthMiddleware,
    exclude_paths=[
        "/api/auth/login",
        "/api/auth/register",
        "/api/health",
        "/api",
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
    ],
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to CMDB API",
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
