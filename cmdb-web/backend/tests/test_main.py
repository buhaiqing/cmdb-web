"""应用主入口单元测试"""

import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "True"

import pytest
from fastapi.testclient import TestClient
import logging

from app.main import app, lifespan


class TestMain:
    """主应用测试类"""

    def test_root_endpoint(self, client: TestClient):
        """测试根路径端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Welcome to CMDB API"
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/docs"

    def test_health_check_endpoint(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data

    def test_openapi_docs_endpoint(self, client: TestClient):
        """测试 OpenAPI 文档端点"""
        response = client.get("/docs")
        assert response.status_code == 200
        # 应该返回 HTML 文档
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json_endpoint(self, client: TestClient):
        """测试 OpenAPI JSON 端点"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_lifespan_startup_logs(self, caplog):
        """测试应用启动时的日志记录"""
        from app.core.config import settings
        
        caplog.set_level(logging.INFO)
        
        # 创建异步上下文管理器
        import asyncio
        from fastapi import FastAPI
        
        test_app = FastAPI(lifespan=lifespan)
        
        # 手动调用生命周期
        async def test_lifespan():
            async with lifespan(test_app) as _:
                pass
        
        asyncio.run(test_lifespan())
        
        # 检查启动日志
        log_messages = [record.message for record in caplog.records]
        assert any("Starting CMDB API..." in message for message in log_messages)
        assert any(f"App Name: {settings.APP_NAME}" in message for message in log_messages)
        assert any(f"Version: {settings.APP_VERSION}" in message for message in log_messages)
        assert any(f"Debug Mode: {settings.DEBUG}" in message for message in log_messages)
        assert any("Initializing database..." in message for message in log_messages)
        assert any("Database initialized successfully" in message for message in log_messages)

    def test_lifespan_shutdown_logs(self, caplog):
        """测试应用关闭时的日志记录"""
        caplog.set_level(logging.INFO)
        
        # 创建异步上下文管理器
        import asyncio
        from fastapi import FastAPI
        
        test_app = FastAPI(lifespan=lifespan)
        
        # 手动调用生命周期
        async def test_lifespan():
            async with lifespan(test_app) as _:
                pass
        
        asyncio.run(test_lifespan())
        
        # 检查关闭日志
        log_messages = [record.message for record in caplog.records]
        assert any("Shutting down CMDB API..." in message for message in log_messages)

    def test_cors_middleware_configuration(self):
        """测试 CORS 中间件配置"""
        from app.core.config import settings
        
        # 检查应用中是否添加了 CORS 中间件
        middleware_exists = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                middleware_exists = True
                break
        
        assert middleware_exists, "CORS 中间件未正确配置"

    def test_auth_middleware_configuration(self):
        """测试认证中间件配置"""
        # 检查应用中是否添加了认证中间件
        middleware_exists = False
        for middleware in app.user_middleware:
            if "AuthMiddleware" in str(middleware.cls):
                middleware_exists = True
                break
        
        assert middleware_exists, "认证中间件未正确配置"

    def test_logging_middleware_configuration(self):
        """测试日志中间件配置"""
        # 检查应用中是否添加了日志中间件
        middleware_exists = False
        for middleware in app.user_middleware:
            if "LoggingMiddleware" in str(middleware.cls):
                middleware_exists = True
                break
        
        assert middleware_exists, "日志中间件未正确配置"

    def test_api_router_registration(self):
        """测试 API 路由注册"""
        # 检查路由是否已注册
        routes = [route.path for route in app.routes]
        # 应该包含 API 前缀的路由
        api_routes = [route for route in routes if route and route.startswith("/api")]
        assert len(api_routes) > 0, "API 路由未正确注册"

    def test_application_metadata(self):
        """测试应用元数据"""
        assert app.title == "CMDB API"
        assert app.version == "1.0.0"
        assert "description" in app.__dict__

    def test_application_lifespan_present(self):
        """测试应用生命周期管理器存在"""
        assert hasattr(app, "router")
        # lifespan 是作为参数传递的，但我们可以检查应用是否正常启动
        assert app.lifespan is not None