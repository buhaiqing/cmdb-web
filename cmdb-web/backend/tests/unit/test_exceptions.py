"""异常模块测试"""

import pytest
from fastapi import status

from app.core.exceptions import (
    APIException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    InternalServerException,
)


class TestExceptions:
    """异常类测试"""

    def test_api_exception_basic(self):
        """测试基础异常"""
        exc = APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="TEST_ERROR",
            message="测试错误",
            details=["详情 1", "详情 2"],
        )
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail["error"]["code"] == "TEST_ERROR"
        assert exc.detail["error"]["message"] == "测试错误"
        assert exc.detail["error"]["details"] == ["详情 1", "详情 2"]

    def test_bad_request_exception(self):
        """测试 400 错误"""
        exc = BadRequestException(message="请求参数错误", details=["字段验证失败"])
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail["error"]["code"] == "BAD_REQUEST"
        assert exc.detail["error"]["message"] == "请求参数错误"

    def test_unauthorized_exception(self):
        """测试 401 错误"""
        exc = UnauthorizedException(message="未授权")
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail["error"]["code"] == "UNAUTHORIZED"

    def test_forbidden_exception(self):
        """测试 403 错误"""
        exc = ForbiddenException(message="权限不足")
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail["error"]["code"] == "FORBIDDEN"

    def test_not_found_exception(self):
        """测试 404 错误"""
        exc = NotFoundException(message="资源不存在")
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail["error"]["code"] == "NOT_FOUND"

    def test_conflict_exception(self):
        """测试 409 错误"""
        exc = ConflictException(message="资源冲突")
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail["error"]["code"] == "CONFLICT"

    def test_internal_server_exception(self):
        """测试 500 错误"""
        exc = InternalServerException(message="服务器内部错误")
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail["error"]["code"] == "INTERNAL_ERROR"

    def test_exception_default_values(self):
        """测试异常默认值"""
        exc = BadRequestException()
        assert exc.detail["error"]["message"] == "请求参数错误"
        assert exc.detail["error"]["details"] == []

        exc2 = UnauthorizedException()
        assert exc2.detail["error"]["message"] == "未授权"

        exc3 = ForbiddenException()
        assert exc3.detail["error"]["message"] == "权限不足"

        exc4 = NotFoundException()
        assert exc4.detail["error"]["message"] == "资源不存在"

        exc5 = ConflictException()
        assert exc5.detail["error"]["message"] == "资源冲突"

        exc6 = InternalServerException()
        assert exc6.detail["error"]["message"] == "服务器内部错误"
