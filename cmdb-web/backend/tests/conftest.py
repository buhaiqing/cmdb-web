"""pytest 配置"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.session import get_db
from app.models.base import Base
from app.models.user import User, Role, Permission, UserStatus
from app.models.ci import ConfigurationItem, CIType, CIStatus
from app.core.security import hash_password


TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine):
    """创建测试数据库会话"""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    db = Session()

    yield db

    transaction.rollback()
    db.close()
    connection.close()


@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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
