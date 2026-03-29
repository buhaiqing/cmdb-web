"""配置模块测试"""

import pytest
from app.core.config import settings


class TestSettings:
    """配置测试"""

    def test_app_name(self):
        """测试应用名称"""
        assert settings.APP_NAME == "CMDB API"

    def test_app_version(self):
        """测试应用版本"""
        assert settings.APP_VERSION == "1.0.0"

    def test_debug_mode(self):
        """测试调试模式"""
        assert settings.DEBUG is True

    def test_host_and_port(self):
        """测试服务器配置"""
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000

    def test_database_url(self):
        """测试数据库 URL"""
        assert "sqlite:///" in settings.DATABASE_URL
        assert "cmdb" in settings.DATABASE_URL

    def test_redis_url(self):
        """测试 Redis URL"""
        assert "redis://" in settings.REDIS_URL

    def test_jwt_config(self):
        """测试 JWT 配置"""
        assert settings.SECRET_KEY is not None
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24

    def test_cors_origins(self):
        """测试 CORS 配置"""
        assert isinstance(settings.CORS_ORIGINS, list)
        assert "http://localhost:3000" in settings.CORS_ORIGINS
        assert "http://localhost:5173" in settings.CORS_ORIGINS

    def test_pagination_config(self):
        """测试分页配置"""
        assert settings.DEFAULT_PAGE_SIZE == 20
        assert settings.MAX_PAGE_SIZE == 100
