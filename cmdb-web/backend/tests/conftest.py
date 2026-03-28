"""pytest 配置"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.session import get_db


# 测试数据库 URL
TEST_DATABASE_URL = "postgresql://cmdb:cmdb@localhost:5432/cmdb_test"


@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """创建测试数据库会话"""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    db = Session()

    yield db

    # 回滚事务
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
