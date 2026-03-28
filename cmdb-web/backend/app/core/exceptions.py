from fastapi import HTTPException, status


class APIException(HTTPException):
    """API 异常基类"""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: list = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": details or []
                }
            }
        )


class BadRequestException(APIException):
    """400 错误"""

    def __init__(self, message: str = "请求参数错误", details: list = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            message=message,
            details=details
        )


class UnauthorizedException(APIException):
    """401 错误"""

    def __init__(self, message: str = "未授权"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            message=message
        )


class ForbiddenException(APIException):
    """403 错误"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            message=message
        )


class NotFoundException(APIException):
    """404 错误"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message
        )


class ConflictException(APIException):
    """409 错误"""

    def __init__(self, message: str = "资源冲突"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message
        )


class InternalServerException(APIException):
    """500 错误"""

    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message=message
        )
