"""用户模型单元测试"""

import pytest
from app.models.user import User, Role, Permission, UserStatus


class TestUserModel:
    """User 模型测试"""

    def test_user_repr(self, sample_user):
        """测试 User.__repr__ 方法"""
        repr_str = repr(sample_user)

        assert f"<User(id={sample_user.id}," in repr_str
        assert f"username={sample_user.username}," in repr_str
        assert f"email={sample_user.email})>" in repr_str

    def test_has_role_returns_true_when_user_has_role(self, sample_user_with_role):
        """测试 has_role 方法 - 用户拥有指定角色时返回 True"""
        result = sample_user_with_role.has_role("test_role")

        assert result is True

    def test_has_role_returns_false_when_user_does_not_have_role(self, sample_user):
        """测试 has_role 方法 - 用户没有指定角色时返回 False"""
        result = sample_user.has_role("non_existent_role")

        assert result is False

    def test_has_permission_returns_true_when_user_has_permission(self, sample_user_with_role):
        """测试 has_permission 方法 - 用户拥有指定权限时返回 True"""
        result = sample_user_with_role.has_permission("test:read")

        assert result is True

    def test_has_permission_returns_false_when_user_does_not_have_permission(self, sample_user):
        """测试 has_permission 方法 - 用户没有指定权限时返回 False"""
        result = sample_user.has_permission("non_existent:permission")

        assert result is False

    def test_has_permission_returns_false_when_role_has_no_permissions(self, test_db):
        """测试 has_permission 方法 - 用户角色没有权限时返回 False"""
        # 创建没有权限的角色
        role = Role(
            name="无权限角色",
            code="no_perm_role",
            description="没有权限的角色",
        )
        test_db.add(role)

        # 创建用户并关联角色
        user = User(
            username="user_no_perm",
            email="user_no_perm@example.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
        )
        user.roles.append(role)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        result = user.has_permission("test:read")

        assert result is False

    def test_has_permission_with_multiple_roles(self, test_db, sample_permission):
        """测试 has_permission 方法 - 用户有多个角色时，只要其中一个角色有权限就返回 True"""
        # 创建第二个权限
        perm2 = Permission(
            name="写入权限",
            code="test:write",
            resource="test",
            action="write",
        )
        test_db.add(perm2)

        # 创建两个角色，分别拥有不同权限
        role1 = Role(
            name="角色1",
            code="role1",
        )
        role1.permissions.append(sample_permission)

        role2 = Role(
            name="角色2",
            code="role2",
        )
        role2.permissions.append(perm2)

        test_db.add(role1)
        test_db.add(role2)

        # 创建用户并关联两个角色
        user = User(
            username="multi_role_user",
            email="multi_role@example.com",
            password_hash="hashed_password",
            status=UserStatus.ACTIVE,
        )
        user.roles.append(role1)
        user.roles.append(role2)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # 验证可以访问两个角色的权限
        assert user.has_permission("test:read") is True
        assert user.has_permission("test:write") is True


class TestRoleModel:
    """Role 模型测试"""

    def test_role_repr(self, sample_role):
        """测试 Role.__repr__ 方法"""
        repr_str = repr(sample_role)

        assert f"<Role(id={sample_role.id}," in repr_str
        assert f"code={sample_role.code}," in repr_str
        assert f"name={sample_role.name})>" in repr_str


class TestPermissionModel:
    """Permission 模型测试"""

    def test_permission_repr(self, sample_permission):
        """测试 Permission.__repr__ 方法"""
        repr_str = repr(sample_permission)

        assert f"<Permission(id={sample_permission.id}," in repr_str
        assert f"code={sample_permission.code}," in repr_str
        assert f"resource={sample_permission.resource})>" in repr_str
