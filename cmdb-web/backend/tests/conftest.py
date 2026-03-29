"""pytest 配置"""

# 必须在导入 app 之前设置环境变量
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "True"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.db.session import get_db
from app.models.base import Base
from app.models.user import User, Role, Permission, UserStatus
from app.models.ci import ConfigurationItem, CIType, CIStatus
from app.core.security import hash_password


import tempfile
import os

# 使用临时文件数据库代替内存数据库，避免连接问题
_test_db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
TEST_DATABASE_URL = f"sqlite:///{_test_db_file.name}"

# 创建测试引擎
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Import all models to ensure they are registered with Base.metadata before create_all
from app.models.user import User, Role, Permission, UserStatus  # noqa: F401
from app.models.ci import ConfigurationItem, CIType, CIStatus  # noqa: F401
from app.models.change import ChangeRecord  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401

Base.metadata.create_all(bind=test_engine)


def pytest_sessionfinish(session, exitstatus):
    """测试结束后清理临时数据库文件"""
    import os
    try:
        os.unlink(_test_db_file.name)
    except Exception:
        pass


def create_test_app():
    """创建测试用 FastAPI 应用（不带 lifespan，避免初始化真实数据库）"""
    from app.api import api_router
    from app.middleware.auth import AuthMiddleware
    from app.middleware.logging import LoggingMiddleware
    from fastapi.middleware.cors import CORSMiddleware

    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        """测试用生命周期（不初始化数据库）"""
        yield

    test_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="运维部 CMDB 配置管理数据库 API (Test)",
        lifespan=test_lifespan,
    )

    # 添加 CORS 中间件
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加认证中间件
    test_app.add_middleware(
        AuthMiddleware,
        exclude_paths=[
            "/api/auth/login",
            "/api/auth/register",
            "/api/health",
            "/api/info",
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ],
    )

    # 添加日志中间件
    test_app.add_middleware(LoggingMiddleware)

    # 注册路由
    test_app.include_router(api_router, prefix="/api")

    @test_app.get("/")
    async def root():
        """根路径"""
        from app.core.config import settings
        return {
            "message": "Welcome to CMDB API",
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }

    @test_app.get("/health")
    async def health_check():
        """健康检查"""
        from app.core.config import settings
        return {"status": "healthy", "version": settings.APP_VERSION}

    return test_app


@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库会话"""
    session = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)()

    # 每个测试前清理所有表数据
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""
    test_app = create_test_app()

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as test_client:
        yield test_client
    test_app.dependency_overrides.clear()


@pytest.fixture
def sample_permission(test_db):
    """创建示例权限"""
    permission = Permission(
        name="测试权限",
        code="test:read",
        resource="test",
        action="read",
        description="测试用权限",
    )
    test_db.add(permission)
    test_db.commit()
    test_db.refresh(permission)
    return permission


@pytest.fixture
def sample_role(test_db, sample_permission):
    """创建示例角色"""
    role = Role(
        name="测试角色",
        code="test_role",
        description="测试用角色",
        is_system=False,
    )
    role.permissions.append(sample_permission)
    test_db.add(role)
    test_db.commit()
    test_db.refresh(role)
    return role


@pytest.fixture
def sample_user(test_db):
    """创建示例用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("TestPassword123"),
        full_name="测试用户",
        status=UserStatus.ACTIVE,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_user_with_role(test_db, sample_role):
    """创建带角色的示例用户"""
    user = User(
        username="testuser_with_role",
        email="test_role@example.com",
        password_hash=hash_password("TestPassword123"),
        full_name="测试用户（带角色）",
        status=UserStatus.ACTIVE,
    )
    user.roles.append(sample_role)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def inactive_user(test_db):
    """创建非活跃用户"""
    user = User(
        username="inactive_user",
        email="inactive@example.com",
        password_hash=hash_password("TestPassword123"),
        full_name="非活跃用户",
        status=UserStatus.INACTIVE,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_ci(test_db):
    """创建示例配置项"""
    ci = ConfigurationItem(
        ci_type=CIType.SERVER,
        name="测试服务器",
        code="TEST-SERVER-001",
        description="测试用服务器",
        status=CIStatus.ONLINE,
        environment="production",
        owner="test_owner",
    )
    test_db.add(ci)
    test_db.commit()
    test_db.refresh(ci)
    return ci


@pytest.fixture
def multiple_users(test_db):
    """创建多个测试用户"""
    users = []
    for i in range(5):
        user = User(
            username=f"user_{i}",
            email=f"user_{i}@example.com",
            password_hash=hash_password(f"Password{i}"),
            full_name=f"用户 {i}",
            status=UserStatus.ACTIVE,
        )
        test_db.add(user)
        users.append(user)
    test_db.commit()
    for user in users:
        test_db.refresh(user)
    return users


@pytest.fixture
def multiple_cis(test_db):
    """创建多个测试配置项"""
    cis = []
    for i in range(5):
        ci = ConfigurationItem(
            ci_type=CIType.SERVER,
            name=f"服务器 {i}",
            code=f"SERVER-{i:03d}",
            description=f"测试服务器 {i}",
            status=CIStatus.ONLINE,
            environment="production" if i % 2 == 0 else "development",
            owner=f"owner_{i}",
        )
        test_db.add(ci)
        cis.append(ci)
    test_db.commit()
    for ci in cis:
        test_db.refresh(ci)
    return cis
