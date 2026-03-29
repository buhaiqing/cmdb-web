"""用户服务层单元测试"""

import pytest
from app.services.user_service import UserService
from app.models.user import User, UserStatus, Role, Permission
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import ConflictException, NotFoundException, BadRequestException
from app.core.security import hash_password


class TestUserService:
    """用户服务测试类"""

    def test_get_by_id_found(self, test_db, sample_user):
        """测试根据 ID 获取用户 - 找到"""
        service = UserService(test_db)
        user = service.get_by_id(sample_user.id)
        assert user is not None
        assert user.id == sample_user.id
        assert user.username == sample_user.username

    def test_get_by_id_not_found(self, test_db):
        """测试根据 ID 获取用户 - 未找到"""
        service = UserService(test_db)
        user = service.get_by_id(99999)
        assert user is None

    def test_get_by_username_found(self, test_db, sample_user):
        """测试根据用户名获取用户 - 找到"""
        service = UserService(test_db)
        user = service.get_by_username(sample_user.username)
        assert user is not None
        assert user.username == sample_user.username

    def test_get_by_username_not_found(self, test_db):
        """测试根据用户名获取用户 - 未找到"""
        service = UserService(test_db)
        user = service.get_by_username("nonexistent")
        assert user is None

    def test_get_by_email_found(self, test_db, sample_user):
        """测试根据邮箱获取用户 - 找到"""
        service = UserService(test_db)
        user = service.get_by_email(sample_user.email)
        assert user is not None
        assert user.email == sample_user.email

    def test_get_by_email_not_found(self, test_db):
        """测试根据邮箱获取用户 - 未找到"""
        service = UserService(test_db)
        user = service.get_by_email("nonexistent@example.com")
        assert user is None

    def test_get_multi_returns_users(self, test_db, multiple_users):
        """测试获取多个用户"""
        service = UserService(test_db)
        users = service.get_multi(skip=0, limit=10)
        assert len(users) == 5

    def test_get_multi_with_pagination(self, test_db, multiple_users):
        """测试分页获取用户"""
        service = UserService(test_db)
        users = service.get_multi(skip=0, limit=2)
        assert len(users) == 2

        users_page2 = service.get_multi(skip=2, limit=2)
        assert len(users_page2) == 2

    def test_get_multi_with_status_filter(self, test_db, sample_user, inactive_user):
        """测试按状态筛选用户"""
        service = UserService(test_db)
        active_users = service.get_multi(status=UserStatus.ACTIVE)
        assert len(active_users) >= 1
        for user in active_users:
            assert user.status == UserStatus.ACTIVE

    def test_get_count(self, test_db, multiple_users):
        """测试获取用户总数"""
        service = UserService(test_db)
        count = service.get_count()
        assert count >= 5

    def test_create_user_success(self, test_db):
        """测试创建用户成功"""
        service = UserService(test_db)
        user_in = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="NewPassword123",
            full_name="新用户",
        )
        user = service.create(user_in)
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.full_name == "新用户"
        assert user.status == UserStatus.ACTIVE
        assert user.password_hash is not None

    def test_create_user_duplicate_username(self, test_db, sample_user):
        """测试创建用户 - 用户名重复"""
        service = UserService(test_db)
        user_in = UserCreate(
            username=sample_user.username,
            email="different@example.com",
            password="Password123",
        )
        with pytest.raises(ConflictException) as exc_info:
            service.create(user_in)
        assert "用户名已存在" in str(exc_info.value.detail)

    def test_create_user_duplicate_email(self, test_db, sample_user):
        """测试创建用户 - 邮箱重复"""
        service = UserService(test_db)
        user_in = UserCreate(
            username="differentuser",
            email=sample_user.email,
            password="Password123",
        )
        with pytest.raises(ConflictException) as exc_info:
            service.create(user_in)
        assert "邮箱已被使用" in str(exc_info.value.detail)

    def test_update_user_success(self, test_db, sample_user):
        """测试更新用户成功"""
        service = UserService(test_db)
        user_in = UserUpdate(full_name="更新后的名称", email="updated@example.com")
        user = service.update(sample_user.id, user_in)
        assert user.full_name == "更新后的名称"
        assert user.email == "updated@example.com"

    def test_update_user_not_found(self, test_db):
        """测试更新用户 - 用户不存在"""
        service = UserService(test_db)
        user_in = UserUpdate(full_name="新名称")
        with pytest.raises(NotFoundException):
            service.update(99999, user_in)

    def test_update_user_password(self, test_db, sample_user):
        """测试更新用户密码"""
        service = UserService(test_db)
        user_in = UserUpdate(password="NewPassword456")
        user = service.update(sample_user.id, user_in)
        assert service.verify_password("NewPassword456", user.password_hash) is True

    def test_update_user_email_conflict(self, test_db, sample_user, multiple_users):
        """测试更新用户 - 邮箱冲突"""
        service = UserService(test_db)
        other_user = multiple_users[0]
        user_in = UserUpdate(email=other_user.email)
        with pytest.raises(ConflictException) as exc_info:
            service.update(sample_user.id, user_in)
        assert "邮箱已被其他用户使用" in str(exc_info.value.detail)

    def test_delete_user_success(self, test_db, sample_user):
        """测试删除用户成功"""
        service = UserService(test_db)
        user_id = sample_user.id
        deleted_user = service.delete(user_id)
        assert deleted_user.id == user_id

        result = service.get_by_id(user_id)
        assert result is None

    def test_delete_user_not_found(self, test_db):
        """测试删除用户 - 用户不存在"""
        service = UserService(test_db)
        with pytest.raises(NotFoundException):
            service.delete(99999)

    def test_update_status_success(self, test_db, sample_user):
        """测试更新用户状态成功"""
        service = UserService(test_db)
        user = service.update_status(sample_user.id, UserStatus.INACTIVE)
        assert user.status == UserStatus.INACTIVE

    def test_update_status_not_found(self, test_db):
        """测试更新用户状态 - 用户不存在"""
        service = UserService(test_db)
        with pytest.raises(NotFoundException):
            service.update_status(99999, UserStatus.INACTIVE)

    def test_verify_password_correct(self, test_db):
        """测试验证正确密码"""
        service = UserService(test_db)
        hashed = hash_password("CorrectPassword")
        result = service.verify_password("CorrectPassword", hashed)
        assert result is True

    def test_verify_password_incorrect(self, test_db):
        """测试验证错误密码"""
        service = UserService(test_db)
        hashed = hash_password("CorrectPassword")
        result = service.verify_password("WrongPassword", hashed)
        assert result is False

    def test_authenticate_success(self, test_db, sample_user):
        """测试认证成功"""
        service = UserService(test_db)
        user = service.authenticate(sample_user.username, "TestPassword123")
        assert user is not None
        assert user.id == sample_user.id

    def test_authenticate_wrong_password(self, test_db, sample_user):
        """测试认证 - 密码错误"""
        service = UserService(test_db)
        user = service.authenticate(sample_user.username, "WrongPassword")
        assert user is None

    def test_authenticate_nonexistent_user(self, test_db):
        """测试认证 - 用户不存在"""
        service = UserService(test_db)
        user = service.authenticate("nonexistent", "Password")
        assert user is None

    def test_authenticate_inactive_user(self, test_db, inactive_user):
        """测试认证 - 非活跃用户"""
        service = UserService(test_db)
        with pytest.raises(BadRequestException) as exc_info:
            service.authenticate(inactive_user.username, "TestPassword123")
        assert "已被禁用" in str(exc_info.value.detail)

    def test_assign_role_success(self, test_db, sample_user, sample_role):
        """测试分配角色成功"""
        service = UserService(test_db)
        user = service.assign_role(sample_user.id, sample_role.id)
        assert sample_role in user.roles

    def test_assign_role_user_not_found(self, test_db, sample_role):
        """测试分配角色 - 用户不存在"""
        service = UserService(test_db)
        with pytest.raises(NotFoundException):
            service.assign_role(99999, sample_role.id)

    def test_assign_role_role_not_found(self, test_db, sample_user):
        """测试分配角色 - 角色不存在"""
        service = UserService(test_db)
        with pytest.raises(NotFoundException):
            service.assign_role(sample_user.id, 99999)

    def test_remove_role_success(self, test_db, sample_user_with_role, sample_role):
        """测试移除角色成功"""
        service = UserService(test_db)
        user = service.remove_role(sample_user_with_role.id, sample_role.id)
        assert sample_role not in user.roles

    def test_remove_role_user_not_found(self, test_db, sample_role):
        """测试移除角色 - 用户不存在"""
        service = UserService(test_db)
        with pytest.raises(NotFoundException):
            service.remove_role(99999, sample_role.id)

    def test_remove_role_role_not_found(self, test_db, sample_user):
        """测试移除角色 - 角色不存在"""
        service = UserService(test_db)
        with pytest.raises(NotFoundException):
            service.remove_role(sample_user.id, 99999)
