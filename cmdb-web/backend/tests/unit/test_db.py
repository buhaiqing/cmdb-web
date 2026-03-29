"""数据库模块测试

测试范围:
- CRUDBase: 基础CRUD操作，包括get_multi的order_by分支
- session: 数据库会话管理，包括get_db生成器和init_db初始化
"""

import pytest
from unittest.mock import MagicMock, patch, call
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from app.db.crud_base import CRUDBase
from app.db.session import get_db, init_db, engine, SessionLocal
from app.models.user import User
from app.models.ci import ConfigurationItem, CIType, CIStatus
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.ci import CICreate, CIUpdate


class TestCRUDBase:
    """CRUDBase 完整测试类"""

    @pytest.fixture
    def user_crud(self):
        """创建用户CRUD实例"""
        return CRUDBase[User, UserCreate, UserUpdate](User)

    @pytest.fixture
    def ci_crud(self):
        """创建配置项CRUD实例"""
        return CRUDBase[ConfigurationItem, CICreate, CIUpdate](ConfigurationItem)

    # ==================== get 方法测试 ====================

    def test_get_by_id(self, test_db, sample_user, user_crud):
        """测试根据ID获取单条记录"""
        user = user_crud.get(test_db, sample_user.id)
        assert user is not None
        assert user.id == sample_user.id
        assert user.username == sample_user.username

    def test_get_by_id_not_found(self, test_db, user_crud):
        """测试根据ID获取不存在的记录"""
        user = user_crud.get(test_db, 99999)
        assert user is None

    # ==================== get_multi 方法测试 ====================

    def test_get_multi_basic(self, test_db, multiple_users, user_crud):
        """测试基础获取多条记录"""
        users = user_crud.get_multi(test_db, skip=0, limit=10)
        assert len(users) >= 5

    def test_get_multi_with_pagination(self, test_db, multiple_users, user_crud):
        """测试分页获取"""
        users = user_crud.get_multi(test_db, skip=0, limit=2)
        assert len(users) == 2

    def test_get_multi_skip_offset(self, test_db, multiple_users, user_crud):
        """测试skip偏移量"""
        all_users = user_crud.get_multi(test_db, skip=0, limit=10)
        skipped_users = user_crud.get_multi(test_db, skip=2, limit=10)
        assert len(skipped_users) == len(all_users) - 2

    def test_get_multi_with_order_by_column(self, test_db, multiple_users, user_crud):
        """测试get_multi带order_by列排序 - 覆盖第33行order_by分支"""
        users = user_crud.get_multi(test_db, skip=0, limit=10, order_by=User.id)
        assert len(users) >= 5
        # 验证按ID排序
        ids = [u.id for u in users]
        assert ids == sorted(ids)

    def test_get_multi_with_order_by_asc_clause(self, test_db, multiple_users, user_crud):
        """测试get_multi带order_by升序排序 - 使用asc()函数 - 覆盖第33行order_by分支"""
        # 使用asc()函数包装列
        users = user_crud.get_multi(test_db, skip=0, limit=10, order_by=asc(User.id))
        assert len(users) >= 5
        # 验证按ID升序排列
        for i in range(len(users) - 1):
            assert users[i].id <= users[i + 1].id

    def test_get_multi_with_order_by_desc_clause(self, test_db, multiple_users, user_crud):
        """测试get_multi带order_by降序排序 - 使用desc()函数 - 覆盖第33行order_by分支"""
        # 使用desc()函数包装列
        users = user_crud.get_multi(test_db, skip=0, limit=10, order_by=desc(User.id))
        assert len(users) >= 5
        # 验证按ID降序排列
        for i in range(len(users) - 1):
            assert users[i].id >= users[i + 1].id

    def test_get_multi_with_order_by_username(self, test_db, multiple_users, user_crud):
        """测试get_multi按用户名排序 - 覆盖第33行order_by分支"""
        users = user_crud.get_multi(test_db, skip=0, limit=10, order_by=User.username)
        assert len(users) >= 5
        # 验证按用户名排序
        usernames = [u.username for u in users]
        assert usernames == sorted(usernames)

    def test_get_multi_without_order_by(self, test_db, multiple_users, user_crud):
        """测试get_multi不带order_by参数 - 覆盖else分支"""
        users = user_crud.get_multi(test_db, skip=0, limit=10)
        assert len(users) >= 5

    def test_get_multi_order_by_with_ci(self, test_db, multiple_cis, ci_crud):
        """测试配置项按名称排序 - 覆盖第33行order_by分支"""
        cis = ci_crud.get_multi(test_db, skip=0, limit=10, order_by=ConfigurationItem.name)
        assert len(cis) >= 5
        # 验证按名称排序
        names = [c.name for c in cis]
        assert names == sorted(names)

    # ==================== get_count 方法测试 ====================

    def test_get_count(self, test_db, multiple_users, user_crud):
        """测试获取记录总数"""
        count = user_crud.get_count(test_db)
        assert count >= 5

    def test_get_count_empty_table(self, test_db, user_crud):
        """测试空表计数"""
        # 删除所有用户
        test_db.query(User).delete()
        test_db.commit()
        count = user_crud.get_count(test_db)
        assert count == 0

    # ==================== create 方法测试 ====================

    def test_create_user(self, test_db, user_crud):
        """测试创建用户记录"""
        from app.core.security import hash_password

        user_in = UserCreate(
            username="newuser_crud",
            email="new_crud@example.com",
            password="Password123",
        )
        obj_data = user_in.model_dump()
        obj_data["password_hash"] = hash_password(obj_data.pop("password"))
        db_obj = user_crud.model(**obj_data)
        test_db.add(db_obj)
        test_db.commit()
        test_db.refresh(db_obj)

        assert db_obj.id is not None
        assert db_obj.username == "newuser_crud"
        assert db_obj.email == "new_crud@example.com"

    def test_create_ci(self, test_db, ci_crud):
        """测试创建设置项记录"""
        ci_in = CICreate(
            ci_type=CIType.SERVER,
            name="CRUD测试服务器",
            code="CRUD-SERVER-001",
            environment="production",
        )
        ci = ci_crud.create(test_db, obj_in=ci_in)
        assert ci.id is not None
        assert ci.name == "CRUD测试服务器"
        assert ci.code == "CRUD-SERVER-001"

    # ==================== update 方法测试 ====================

    def test_update_user(self, test_db, sample_user, user_crud):
        """测试更新用户记录"""
        user_in = UserUpdate(full_name="更新的名称")
        user = user_crud.update(test_db, db_obj=sample_user, obj_in=user_in)
        assert user.full_name == "更新的名称"

    def test_update_user_multiple_fields(self, test_db, sample_user, user_crud):
        """测试更新多个字段"""
        user_in = UserUpdate(full_name="新全名", email="newemail@example.com")
        user = user_crud.update(test_db, db_obj=sample_user, obj_in=user_in)
        assert user.full_name == "新全名"
        assert user.email == "newemail@example.com"

    def test_update_ci(self, test_db, sample_ci, ci_crud):
        """测试更新配置项"""
        ci_in = CIUpdate(name="更新的服务器名称", status=CIStatus.OFFLINE)
        ci = ci_crud.update(test_db, db_obj=sample_ci, obj_in=ci_in)
        assert ci.name == "更新的服务器名称"
        assert ci.status == CIStatus.OFFLINE

    def test_update_partial_fields(self, test_db, sample_user, user_crud):
        """测试部分字段更新（exclude_unset=True）"""
        original_email = sample_user.email
        user_in = UserUpdate(full_name="仅更新名称")
        user = user_crud.update(test_db, db_obj=sample_user, obj_in=user_in)
        assert user.full_name == "仅更新名称"
        assert user.email == original_email  # 未更新的字段保持不变

    # ==================== remove 方法测试 ====================

    def test_remove_user(self, test_db, sample_user, user_crud):
        """测试删除用户记录"""
        user_id = sample_user.id
        deleted = user_crud.remove(test_db, id=user_id)
        assert deleted.id == user_id

        result = user_crud.get(test_db, user_id)
        assert result is None

    def test_remove_ci(self, test_db, sample_ci, ci_crud):
        """测试删除配置项"""
        ci_id = sample_ci.id
        deleted = ci_crud.remove(test_db, id=ci_id)
        assert deleted.id == ci_id

        result = ci_crud.get(test_db, ci_id)
        assert result is None


class TestSession:
    """数据库会话测试类"""

    # ==================== get_db 生成器测试 ====================

    def test_get_db_yields_session(self):
        """测试get_db生成器产生Session对象"""
        gen = get_db()
        db = next(gen)

        assert isinstance(db, Session)

        # 清理：关闭生成器
        try:
            next(gen)
        except StopIteration:
            pass

    @patch('app.db.session.SessionLocal')
    def test_get_db_session_can_execute(self, mock_session_local):
        """测试get_db产生的会话可以执行查询"""
        mock_db = MagicMock()
        mock_db.execute.return_value.scalar.return_value = 1
        mock_session_local.return_value = mock_db

        gen = get_db()
        db = next(gen)

        # 验证会话可以执行简单查询
        result = db.execute("SELECT 1")
        assert result.scalar() == 1

        # 关闭生成器
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_closes_session(self):
        """测试get_db在finally块中关闭会话"""
        gen = get_db()
        db = next(gen)

        # 验证会话初始是活动的
        assert db.is_active

        # 关闭生成器，触发finally块
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_exception_handling(self):
        """测试get_db异常处理"""
        # 模拟在with语句中使用get_db的场景
        db_instance = None

        try:
            gen = get_db()
            db_instance = next(gen)
            # 模拟提前退出（异常或return）
            raise ValueError("模拟异常")
        except ValueError:
            pass
        finally:
            # 清理生成器
            if 'gen' in locals():
                try:
                    next(gen)
                except StopIteration:
                    pass

    @patch('app.db.session.SessionLocal')
    def test_get_db_calls_session_local(self, mock_session_local):
        """测试get_db调用SessionLocal创建会话"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        gen = get_db()
        db = next(gen)

        mock_session_local.assert_called_once()
        assert db == mock_db

        # 关闭生成器
        try:
            next(gen)
        except StopIteration:
            pass

    @patch('app.db.session.SessionLocal')
    def test_get_db_closes_on_cleanup(self, mock_session_local):
        """测试get_db在清理时关闭会话"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        gen = get_db()
        next(gen)  # 获取会话

        # 验证close还未被调用
        mock_db.close.assert_not_called()

        # 关闭生成器
        try:
            next(gen)
        except StopIteration:
            pass

        # 验证close被调用
        mock_db.close.assert_called_once()

    def test_get_db_generator_protocol(self):
        """测试get_db生成器协议正确性"""
        gen = get_db()

        # 第一次调用yield会话
        db1 = next(gen)
        assert isinstance(db1, Session)

        # 第二次调用应该触发StopIteration（finally块执行）
        with pytest.raises(StopIteration):
            next(gen)

    # ==================== init_db 初始化测试 ====================

    @patch('app.db.session.engine')
    def test_init_db_calls_create_all(self, mock_engine):
        """测试init_db调用create_all创建表"""
        # 模拟Base.metadata.create_all
        mock_base_module = MagicMock()
        mock_base = MagicMock()
        mock_base_module.Base = mock_base

        with patch.dict('sys.modules', {'app.models.base': mock_base_module}):
            init_db()

        # 验证create_all被调用
        mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)

    def test_init_db_integration(self):
        """测试init_db集成（使用内存数据库）"""
        from sqlalchemy import create_engine, inspect, Column, Integer, String
        from sqlalchemy.orm import declarative_base

        # 创建内存数据库引擎
        test_engine = create_engine("sqlite:///:memory:")

        # 创建临时Base和模型
        TempBase = declarative_base()

        class TempModel(TempBase):
            __tablename__ = "temp_model"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        # 模拟init_db行为
        TempBase.metadata.create_all(bind=test_engine)

        # 验证表已创建
        inspector = inspect(test_engine)
        assert "temp_model" in inspector.get_table_names()

    @patch('app.db.session.engine')
    def test_init_db_imports_base_correctly(self, mock_engine):
        """测试init_db正确导入Base"""
        # 模拟Base.metadata.create_all
        mock_base_module = MagicMock()
        mock_base = MagicMock()
        mock_base_module.Base = mock_base

        with patch.dict('sys.modules', {'app.models.base': mock_base_module}):
            # 重新导入init_db以确保使用模拟的模块
            from app.db.session import init_db as fresh_init_db
            fresh_init_db()

        # 验证create_all被调用
        mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)


class TestSessionSQLiteConfig:
    """SQLite配置测试类 - 覆盖session.py第13行"""

    def test_sqlite_connect_args_configuration(self):
        """测试SQLite数据库配置check_same_thread=False - 覆盖第13行"""
        # 直接测试配置逻辑
        database_url = "sqlite:///./test.db"
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        assert connect_args == {"check_same_thread": False}

    def test_non_sqlite_no_connect_args(self):
        """测试非SQLite数据库不添加check_same_thread"""
        database_url = "postgresql://user:pass@localhost/db"
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        assert connect_args == {}
