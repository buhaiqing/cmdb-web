"""CRUD 基础操作测试"""

import pytest
from sqlalchemy import select

from app.db.crud_base import CRUDBase
from app.models.user import User
from app.models.ci import ConfigurationItem, CIType, CIStatus
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.ci import CICreate, CIUpdate


class TestCRUDBaseUser:
    """用户 CRUD 测试"""

    @pytest.fixture
    def user_crud(self):
        """创建用户 CRUD 实例"""
        return CRUDBase[User, UserCreate, UserUpdate](User)

    def test_get_by_id(self, test_db, sample_user, user_crud):
        """测试根据 ID 获取"""
        user = user_crud.get(test_db, sample_user.id)
        assert user is not None
        assert user.id == sample_user.id

    def test_get_by_id_not_found(self, test_db, user_crud):
        """测试根据 ID 获取 - 不存在"""
        user = user_crud.get(test_db, 99999)
        assert user is None

    def test_get_multi(self, test_db, multiple_users, user_crud):
        """测试获取多个"""
        users = user_crud.get_multi(test_db, skip=0, limit=10)
        assert len(users) >= 5

    def test_get_multi_with_pagination(self, test_db, multiple_users, user_crud):
        """测试分页获取"""
        users = user_crud.get_multi(test_db, skip=0, limit=2)
        assert len(users) == 2

    def test_get_count(self, test_db, multiple_users, user_crud):
        """测试获取总数"""
        count = user_crud.get_count(test_db)
        assert count >= 5

    def test_create(self, test_db, user_crud):
        """测试创建"""
        user_in = UserCreate(
            username="newuser",
            email="new@example.com",
            password="Password123",
        )
        user = user_crud.create(test_db, obj_in=user_in)
        assert user.id is not None
        assert user.username == "newuser"

    def test_update(self, test_db, sample_user, user_crud):
        """测试更新"""
        user_in = UserUpdate(full_name="新名称")
        user = user_crud.update(test_db, db_obj=sample_user, obj_in=user_in)
        assert user.full_name == "新名称"

    def test_remove(self, test_db, sample_user, user_crud):
        """测试删除"""
        user_id = sample_user.id
        deleted = user_crud.remove(test_db, id=user_id)
        assert deleted.id == user_id

        result = user_crud.get(test_db, user_id)
        assert result is None


class TestCRUDBaseCI:
    """配置项 CRUD 测试"""

    @pytest.fixture
    def ci_crud(self):
        """创建配置项 CRUD 实例"""
        return CRUDBase[ConfigurationItem, CICreate, CIUpdate](ConfigurationItem)

    def test_get_by_id(self, test_db, sample_ci, ci_crud):
        """测试根据 ID 获取"""
        ci = ci_crud.get(test_db, sample_ci.id)
        assert ci is not None
        assert ci.id == sample_ci.id

    def test_get_by_id_not_found(self, test_db, ci_crud):
        """测试根据 ID 获取 - 不存在"""
        ci = ci_crud.get(test_db, 99999)
        assert ci is None

    def test_get_multi(self, test_db, multiple_cis, ci_crud):
        """测试获取多个"""
        cis = ci_crud.get_multi(test_db, skip=0, limit=10)
        assert len(cis) >= 5

    def test_get_count(self, test_db, multiple_cis, ci_crud):
        """测试获取总数"""
        count = ci_crud.get_count(test_db)
        assert count >= 5

    def test_create(self, test_db, ci_crud):
        """测试创建"""
        ci_in = CICreate(
            ci_type=CIType.SERVER,
            name="新服务器",
            code="NEW-SERVER-001",
            environment="production",
        )
        ci = ci_crud.create(test_db, obj_in=ci_in)
        assert ci.id is not None
        assert ci.name == "新服务器"

    def test_update(self, test_db, sample_ci, ci_crud):
        """测试更新"""
        ci_in = CIUpdate(name="新名称", status=CIStatus.OFFLINE)
        ci = ci_crud.update(test_db, db_obj=sample_ci, obj_in=ci_in)
        assert ci.name == "新名称"
        assert ci.status == CIStatus.OFFLINE

    def test_remove(self, test_db, sample_ci, ci_crud):
        """测试删除"""
        ci_id = sample_ci.id
        deleted = ci_crud.remove(test_db, id=ci_id)
        assert deleted.id == ci_id

        result = ci_crud.get(test_db, ci_id)
        assert result is None
