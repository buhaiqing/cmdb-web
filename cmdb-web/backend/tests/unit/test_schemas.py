"""Schemas 验证测试"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RoleCreate,
    RoleUpdate,
    PermissionCreate,
)
from app.schemas.ci import (
    CICreate,
    CIUpdate,
    CIResponse,
    CISearchRequest,
    CIRelationCreate,
    CIType,
    CIStatus,
)
from app.schemas.common import (
    HealthResponse,
    BaseResponse,
    PaginatedResponse,
)
from app.schemas.change import (
    ChangeRecordCreate,
    ChangeRecordUpdate,
    ChangeType,
    ChangeStatus,
    ChangePriority,
)


class TestUserSchemas:
    """用户 Schemas 测试"""

    def test_user_create_valid(self):
        """测试创建用户 schema - 有效数据"""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123",
            full_name="测试用户",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "Password123"

    def test_user_create_minimal(self):
        """测试创建用户 schema - 最少数据"""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123",
        )
        assert user.full_name is None

    def test_user_create_invalid_email(self):
        """测试创建用户 schema - 无效邮箱"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="Password123",
            )

    def test_user_create_short_username(self):
        """测试创建用户 schema - 用户名过短"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="ab",
                email="test@example.com",
                password="Password123",
            )

    def test_user_create_short_password(self):
        """测试创建用户 schema - 密码过短"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="short",
            )

    def test_user_update_valid(self):
        """测试更新用户 schema - 有效数据"""
        update = UserUpdate(
            email="new@example.com",
            full_name="新名称",
        )
        assert update.email == "new@example.com"
        assert update.full_name == "新名称"

    def test_user_update_partial(self):
        """测试更新用户 schema - 部分更新"""
        update = UserUpdate(full_name="仅更新名称")
        assert update.full_name == "仅更新名称"
        assert update.email is None
        assert update.password is None

    def test_user_update_with_password(self):
        """测试更新用户 schema - 更新密码"""
        update = UserUpdate(password="NewPassword123")
        assert update.password == "NewPassword123"

    def test_user_update_with_status(self):
        """测试更新用户 schema - 更新状态"""
        update = UserUpdate(status="inactive")
        assert update.status == "inactive"

    def test_login_request_valid(self):
        """测试登录请求 schema - 有效数据"""
        login = LoginRequest(
            username="testuser",
            password="Password123",
        )
        assert login.username == "testuser"
        assert login.password == "Password123"

    def test_login_request_missing_password(self):
        """测试登录请求 schema - 缺少密码"""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser")

    def test_token_response(self):
        """测试令牌响应 schema"""
        response = TokenResponse(
            access_token="test_token",
            expires_in=86400,
        )
        assert response.access_token == "test_token"
        assert response.token_type == "bearer"
        assert response.expires_in == 86400


class TestRoleAndPermissionSchemas:
    """角色和权限 Schemas 测试"""

    def test_role_create_valid(self):
        """测试创建角色 schema - 有效数据"""
        role = RoleCreate(
            name="管理员",
            code="admin",
            description="系统管理员",
        )
        assert role.name == "管理员"
        assert role.code == "admin"

    def test_role_create_with_permissions(self):
        """测试创建角色 schema - 带权限"""
        role = RoleCreate(
            name="管理员",
            code="admin",
            permission_ids=[1, 2, 3],
        )
        assert role.permission_ids == [1, 2, 3]

    def test_role_update_valid(self):
        """测试更新角色 schema - 有效数据"""
        update = RoleUpdate(
            name="新名称",
            description="新描述",
        )
        assert update.name == "新名称"
        assert update.description == "新描述"

    def test_permission_create_valid(self):
        """测试创建权限 schema - 有效数据"""
        perm = PermissionCreate(
            name="查看配置项",
            code="ci:read",
            resource="ci",
            action="read",
        )
        assert perm.name == "查看配置项"
        assert perm.code == "ci:read"


class TestCISchemas:
    """配置项 Schemas 测试"""

    def test_ci_create_valid(self):
        """测试创建配置项 schema - 有效数据"""
        ci = CICreate(
            ci_type=CIType.SERVER,
            name="测试服务器",
            code="TEST-SERVER-001",
            environment="production",
        )
        assert ci.name == "测试服务器"
        assert ci.code == "TEST-SERVER-001"
        assert ci.ci_type == CIType.SERVER

    def test_ci_create_with_optional_fields(self):
        """测试创建配置项 schema - 带可选字段"""
        ci = CICreate(
            ci_type=CIType.SERVER,
            name="测试服务器",
            code="TEST-SERVER-001",
            environment="production",
            description="描述",
            owner="admin",
            tags={"env": "test"},
        )
        assert ci.description == "描述"
        assert ci.owner == "admin"
        assert ci.tags == {"env": "test"}

    def test_ci_create_invalid_empty_name(self):
        """测试创建配置项 schema - 空名称"""
        with pytest.raises(ValidationError):
            CICreate(
                ci_type=CIType.SERVER,
                name="",
                code="TEST-SERVER-001",
                environment="production",
            )

    def test_ci_update_valid(self):
        """测试更新配置项 schema - 有效数据"""
        update = CIUpdate(
            name="新名称",
            status=CIStatus.OFFLINE,
        )
        assert update.name == "新名称"
        assert update.status == CIStatus.OFFLINE

    def test_ci_search_request_defaults(self):
        """测试搜索配置项 schema - 默认值"""
        search = CISearchRequest()
        assert search.page == 1
        assert search.page_size == 20
        assert search.ci_type is None

    def test_ci_search_request_with_filters(self):
        """测试搜索配置项 schema - 带筛选条件"""
        search = CISearchRequest(
            ci_type=CIType.SERVER,
            name="server",
            status=CIStatus.ONLINE,
            environment="production",
            page=2,
            page_size=50,
        )
        assert search.ci_type == CIType.SERVER
        assert search.name == "server"
        assert search.page == 2
        assert search.page_size == 50

    def test_ci_search_request_page_size_limit(self):
        """测试搜索配置项 schema - 分页大小限制"""
        with pytest.raises(ValidationError):
            CISearchRequest(page_size=200)

    def test_ci_relation_create_valid(self):
        """测试创建配置项关系 schema - 有效数据"""
        relation = CIRelationCreate(
            source_ci_id=1,
            target_ci_id=2,
            relation_type="connects_to",
        )
        assert relation.source_ci_id == 1
        assert relation.target_ci_id == 2
        assert relation.relation_type == "connects_to"

    def test_ci_relation_create_without_description(self):
        """测试创建配置项关系 schema - 无描述"""
        relation = CIRelationCreate(
            source_ci_id=1,
            target_ci_id=2,
            relation_type="depends_on",
        )
        assert relation.description is None


class TestCommonSchemas:
    """通用 Schemas 测试"""

    def test_health_response(self):
        """测试健康检查响应 schema"""
        health = HealthResponse(
            status="healthy",
            version="1.0.0",
        )
        assert health.status == "healthy"
        assert health.version == "1.0.0"

    def test_base_response_success(self):
        """测试基础响应 schema - 成功"""
        response = BaseResponse(
            success=True,
            message="操作成功",
            data={"id": 1},
        )
        assert response.success is True
        assert response.data["id"] == 1

    def test_base_response_with_error(self):
        """测试基础响应 schema - 带错误"""
        response = BaseResponse(
            success=False,
            message="操作失败",
            error={"code": "ERROR", "details": []},
        )
        assert response.success is False
        assert response.error["code"] == "ERROR"

    def test_paginated_response(self):
        """测试分页响应 schema"""
        response = PaginatedResponse.create(
            items=[{"id": 1}, {"id": 2}],
            total=100,
            page=1,
            page_size=20,
        )
        assert len(response.items) == 2
        assert response.total == 100
        assert response.page == 1
        assert response.page_size == 20
        assert response.total_pages == 5

    def test_paginated_response_single_page(self):
        """测试分页响应 schema - 单页"""
        response = PaginatedResponse.create(
            items=[{"id": 1}],
            total=1,
            page=1,
            page_size=20,
        )
        assert response.total_pages == 1


class TestChangeSchemas:
    """变更管理 Schemas 测试"""

    def test_change_record_create_valid(self):
        """测试创建变更记录 schema - 有效数据"""
        change = ChangeRecordCreate(
            ci_id=1,
            change_type=ChangeType.CREATE,
            title="创建配置项",
            description="创建测试服务器",
            priority=ChangePriority.HIGH,
        )
        assert change.ci_id == 1
        assert change.change_type == ChangeType.CREATE
        assert change.title == "创建配置项"

    def test_change_record_create_with_values(self):
        """测试创建变更记录 schema - 带新旧值"""
        change = ChangeRecordCreate(
            ci_id=1,
            change_type=ChangeType.UPDATE,
            title="更新配置项",
            old_value={"status": "online"},
            new_value={"status": "offline"},
        )
        assert change.old_value == {"status": "online"}
        assert change.new_value == {"status": "offline"}

    def test_change_record_update_valid(self):
        """测试更新变更记录 schema - 有效数据"""
        update = ChangeRecordUpdate(
            title="新标题",
            priority=ChangePriority.CRITICAL,
        )
        assert update.title == "新标题"
        assert update.priority == ChangePriority.CRITICAL

    def test_change_record_update_partial(self):
        """测试更新变更记录 schema - 部分更新"""
        update = ChangeRecordUpdate(reason="紧急变更")
        assert update.reason == "紧急变更"
        assert update.title is None

    def test_change_types_enum(self):
        """测试变更类型枚举"""
        assert ChangeType.CREATE.value == "create"
        assert ChangeType.UPDATE.value == "update"
        assert ChangeType.DELETE.value == "delete"

    def test_change_status_enum(self):
        """测试变更状态枚举"""
        assert ChangeStatus.PENDING.value == "pending"
        assert ChangeStatus.APPROVED.value == "approved"
        assert ChangeStatus.COMPLETED.value == "completed"

    def test_change_priority_enum(self):
        """测试变更优先级枚举"""
        assert ChangePriority.LOW.value == "low"
        assert ChangePriority.HIGH.value == "high"
        assert ChangePriority.CRITICAL.value == "critical"
