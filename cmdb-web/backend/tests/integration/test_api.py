"""API 集成测试"""

import pytest
from fastapi import status

from app.core.security import hash_password
from app.models.user import User, UserStatus


class TestHealthEndpoint:
    """健康检查端点测试"""

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/api/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/api")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "CMDB" in data["message"]


class TestAuthEndpoint:
    """认证端点测试"""

    def test_login_success(self, client, test_db):
        """测试登录成功"""
        # 创建测试用户
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("TestPassword123"),
            status=UserStatus.ACTIVE,
        )
        test_db.add(user)
        test_db.commit()

        # 登录
        response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPassword123"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_db):
        """测试登录密码错误"""
        # 创建测试用户
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("TestPassword123"),
            status=UserStatus.ACTIVE,
        )
        test_db.add(user)
        test_db.commit()

        # 登录 - 错误密码
        response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "WrongPassword"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """测试登录不存在的用户"""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistent", "password": "TestPassword123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCIEndpoint:
    """配置项端点测试"""

    @pytest.fixture
    def authenticated_client(self, client, test_db):
        """创建已认证的客户端"""
        # 创建测试用户
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("TestPassword123"),
            status=UserStatus.ACTIVE,
        )
        test_db.add(user)
        test_db.commit()

        # 登录获取 token
        login_response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]

        # 设置认证头
        client.headers["Authorization"] = f"Bearer {token}"

        yield client

    def test_list_cis_empty(self, authenticated_client):
        """测试获取空配置项列表"""
        response = authenticated_client.get("/api/cis")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_create_ci_success(self, authenticated_client):
        """测试创建配置项"""
        ci_data = {
            "ci_type": "server",
            "name": "测试服务器",
            "code": "TEST-SERVER-001",
            "environment": "production",
        }

        response = authenticated_client.post("/api/cis", json=ci_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "测试服务器"
        assert data["code"] == "TEST-SERVER-001"

    def test_create_ci_duplicate_code(self, authenticated_client, test_db):
        """测试创建重复代码的配置项"""
        from app.models.ci import ConfigurationItem, CIType, CIStatus

        # 创建已有配置项
        ci = ConfigurationItem(
            ci_type=CIType.SERVER,
            name="已有服务器",
            code="EXISTING-CODE",
            environment="production",
            status=CIStatus.ONLINE,
        )
        test_db.add(ci)
        test_db.commit()

        # 尝试创建重复代码
        ci_data = {
            "ci_type": "server",
            "name": "新服务器",
            "code": "EXISTING-CODE",
            "environment": "production",
        }

        response = authenticated_client.post("/api/cis", json=ci_data)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_get_ci_not_found(self, authenticated_client):
        """测试获取不存在的配置项"""
        response = authenticated_client.get("/api/cis/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/cis")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
