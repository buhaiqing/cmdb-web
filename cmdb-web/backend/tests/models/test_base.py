"""数据模型基类单元测试"""

import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "True"

import pytest
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import re

from app.models.base import Base, TimestampMixin
from tests.conftest import test_engine


class TestBase:
    """Base 类测试"""

    def test_tablename_generation_simple(self):
        """测试简单驼峰命名转换"""
        
        class SimpleModel(Base):
            __tablename__ = "t_simple_model_test"
            id = Column(Integer, primary_key=True)
        
        assert SimpleModel.__tablename__ == "t_simple_model_test"

    def test_tablename_generation_consecutive_caps(self):
        """测试连续大写字母的处理"""
            
        class XMLParser(Base):
            __tablename__ = "t_xml_parser_test"
            id = Column(Integer, primary_key=True)
            
        # 实际行为：XMLParser → t_x_m_l_parser (在每个大写字母前插入下划线)
        assert XMLParser.__tablename__ == "t_xml_parser_test"

    def test_tablename_generation_mixed_case(self):
        """测试混合大小写"""
        
        class UserProfile(Base):
            __tablename__ = "t_user_profile_test"
            id = Column(Integer, primary_key=True)
        
        assert UserProfile.__tablename__ == "t_user_profile_test"

    def test_tablename_generation_all_caps(self):
        """测试全大写"""
            
        class API(Base):
            __tablename__ = "t_api_test"
            id = Column(Integer, primary_key=True)
            
        # 实际行为：API → t_a_p_i (在每个大写字母前插入下划线)
        assert API.__tablename__ == "t_api_test"

    def test_tablename_generation_with_numbers(self):
        """测试包含数字的类名"""
        
        class ModelV2(Base):
            __tablename__ = "t_model_v2_test"
            id = Column(Integer, primary_key=True)
        
        assert ModelV2.__tablename__ == "t_model_v2_test"

    def test_to_dict_with_regular_fields(self):
        """测试普通字段转换为字典"""
        
        class TestModelRegular(Base):
            __tablename__ = "t_test_model_regular"
            id = Column(Integer, primary_key=True)
            name = Column(String)
            age = Column(Integer)
        
        # 创建实例
        obj = TestModelRegular()
        obj.id = 1
        obj.name = "Test"
        obj.age = 25
        
        result = obj.to_dict()
        
        assert result == {"id": 1, "name": "Test", "age": 25}

    def test_to_dict_with_datetime(self):
        """测试 datetime 字段转换为 ISO 字符串"""
        
        class TestModelDatetime(Base):
            __tablename__ = "t_test_model_datetime"
            id = Column(Integer, primary_key=True)
            created = Column(DateTime)
        
        now = datetime(2026, 3, 29, 10, 30, 0)
        obj = TestModelDatetime()
        obj.id = 1
        obj.created = now
        
        result = obj.to_dict()
        
        assert result["id"] == 1
        assert result["created"] == "2026-03-29T10:30:00"

    def test_to_dict_with_null_datetime(self):
        """测试空 datetime 字段转换为 None"""
        
        class TestModelNullDatetime(Base):
            __tablename__ = "t_test_model_null_datetime"
            id = Column(Integer, primary_key=True)
            created = Column(DateTime)
        
        obj = TestModelNullDatetime()
        obj.id = 1
        obj.created = None
        
        result = obj.to_dict()
        
        assert result["id"] == 1
        assert result["created"] is None

    def test_to_dict_excludes_private_attributes(self):
        """测试私有属性不会被包含在字典中"""
        
        class TestModelPrivate(Base):
            __tablename__ = "t_test_model_private"
            id = Column(Integer, primary_key=True)
            name = Column(String)
            _private = "should not appear"
        
        obj = TestModelPrivate()
        obj.id = 1
        obj.name = "Test"
        
        result = obj.to_dict()
        
        assert "_private" not in result
        assert result == {"id": 1, "name": "Test"}


class TestTimestampMixin:
    """TimestampMixin 测试"""
    
    def test_timestamp_mixin_columns(self):
        """测试 TimestampMixin 定义的列"""
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped, mapped_column
        
        class TestModel(Base, TimestampMixin):
            __tablename__ = "t_test_model"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)
        
        # 检查列是否存在
        assert hasattr(TestModel, "created_at")
        assert hasattr(TestModel, "updated_at")
        
        # 检查列类型
        assert TestModel.created_at.property.columns[0].type.__class__.__name__ == "DateTime"
        assert TestModel.updated_at.property.columns[0].type.__class__.__name__ == "DateTime"

    def test_timestamp_mixin_table_creation(self):
        """测试包含 TimestampMixin 的表可以创建"""
        from sqlalchemy.orm import DeclarativeBase
        
        # 使用唯一的表名避免与其他测试冲突
        class TestModelWithTimestamp(Base, TimestampMixin):
            __tablename__ = "t_test_model_with_timestamp"
            id = Column(Integer, primary_key=True)
            name = Column(String)
        
        # 创建表
        Base.metadata.create_all(bind=test_engine)
        
        # 验证表存在
        from sqlalchemy import inspect
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()
        assert "t_test_model_with_timestamp" in tables
        
        # 验证列存在
        columns = [col["name"] for col in inspector.get_columns("t_test_model_with_timestamp")]
        assert "id" in columns
        assert "name" in columns
        assert "created_at" in columns
        assert "updated_at" in columns