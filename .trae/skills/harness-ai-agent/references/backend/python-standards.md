# Python 后端规范 (2026 Edition)

> **标准**: Python 3.12+ / FastAPI / Pydantic v2  
> **Harness 集成**: STO, CCM, SRM, GitOps

---

## 1. 项目架构

### 1.1 目录结构
```
backend/
├── src/
│   ├── api/                    # API 路由
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── users.py        # 用户模块
│   │   │   └── orders.py       # 订单模块
│   │   └── deps.py             # 依赖注入
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全相关
│   │   └── logging.py          # 日志配置
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── order_service.py
│   ├── repositories/           # 数据访问
│   │   ├── __init__.py
│   │   └── base.py
│   ├── agents/                 # AI Agent 模块
│   │   ├── __init__.py
│   │   ├── code_reviewer.py
│   │   ├── deploy_advisor.py
│   │   └── incident_handler.py
│   └── main.py                 # 应用入口
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── alembic/                    # 数据库迁移
├── .harness/                   # Harness 配置
├── pyproject.toml
└── Dockerfile
```

### 1.2 技术栈
| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | FastAPI | 0.110+ |
| 语言 | Python | 3.12+ |
| 类型 | Pydantic | v2 |
| ORM | SQLAlchemy | 2.0+ |
| 异步 | asyncpg / aioredis | latest |
| 测试 | pytest | 8.x |
| 任务 | Celery + Redis | latest |
| 监控 | OpenTelemetry | v1.0+ |
| MCP | FastMCP | latest |
| 日志 | structlog | latest |
| 指标 | prometheus-client | latest |

---

## 2. 代码规范

### 2.1 类型注解 (强制)
```python
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# 函数签名必须完整注解
async def get_user_by_id(
    session: AsyncSession,
    user_id: UUID,
    *,  # 强制关键字参数
    include_deleted: bool = False,
) -> User | None:
    """通过 ID 获取用户.
    
    Args:
        session: 数据库会话
        user_id: 用户 UUID
        include_deleted: 是否包含已删除用户
        
    Returns:
        用户对象，不存在时返回 None
        
    Raises:
        DatabaseError: 数据库查询失败
    """
    ...
```

### 2.2 Pydantic v2 模型
```python
# schemas/user.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模型."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    """用户创建模型."""
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    """用户响应模型."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """用户更新模型 (可选字段)."""
    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=1, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=128)
```

### 2.3 FastAPI 路由
```python
# api/v1/users.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db_session
from schemas.user import UserCreate, UserResponse, UserUpdate
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户账号，邮箱不能重复",
)
async def create_user(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    data: UserCreate,
) -> UserResponse:
    """创建用户.
    
    - 验证邮箱唯一性
    - 密码自动哈希存储
    - 发送欢迎邮件 (异步任务)
    """
    service = UserService(session)
    
    # 检查邮箱是否已存在
    if await service.get_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    user = await service.create(data)
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="获取用户详情",
)
async def get_user(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: UUID,
) -> UserResponse:
    """获取指定用户详情."""
    service = UserService(session)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="获取用户列表",
)
async def list_users(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[UserResponse]:
    """分页获取用户列表.
    
    - 默认每页 20 条
    - 最大每页 100 条
    """
    service = UserService(session)
    users = await service.list(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]
```

---

## 3. 异步编程

### 3.1 数据库操作
```python
# repositories/base.py
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """基础仓储类."""
    
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: UUID) -> ModelType | None:
        """通过 ID 获取."""
        return await self.session.get(self.model, id)
    
    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """分页查询."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, obj: ModelType) -> ModelType:
        """创建."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
```

### 3.2 避免阻塞操作
```python
# 正确：使用异步 HTTP 客户端
import httpx

async def fetch_external_api(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()


# 错误：使用同步 requests
import requests  # ❌ 不要在异步代码中使用

async def bad_example(url: str) -> dict:
    response = requests.get(url)  # 这会阻塞事件循环！
    return response.json()


# 正确：异步文件操作
import aiofiles

async def read_file_async(path: str) -> str:
    async with aiofiles.open(path, mode='r') as f:
        return await f.read()
```

---

## 4. 安全规范

### 4.1 依赖注入
```python
# api/deps.py
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import verify_token
from db.session import get_async_session
from models.user import User

security = HTTPBearer()


async def get_db_session() -> AsyncSession:
    """获取数据库会话."""
    async for session in get_async_session():
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """获取当前认证用户."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = await session.get(User, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


# 权限检查
async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """获取当前超级用户."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
```

### 4.2 密码安全
```python
# core/security.py
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from core.config import settings

# Argon2 密码哈希
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """哈希密码."""
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """验证密码."""
    try:
        ph.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """创建 JWT Token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
```

---

## 5. 测试规范

### 5.1 单元测试
```python
# tests/unit/test_user_service.py
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCreate
from services.user_service import UserService


@pytest.fixture
def mock_session(mocker: MockerFixture) -> AsyncSession:
    return mocker.AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_service(mock_session: AsyncSession) -> UserService:
    return UserService(mock_session)


class TestUserService:
    async def test_create_user_success(
        self,
        user_service: UserService,
        mock_session: AsyncSession,
    ):
        """测试创建用户成功."""
        data = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="SecurePass123!",
        )
        
        user = await user_service.create(data)
        
        assert user.email == data.email
        assert user.full_name == data.full_name
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
```

### 5.2 集成测试
```python
# tests/integration/test_users_api.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUsersAPI:
    async def test_create_user(self, client: AsyncClient):
        """测试创建用户 API."""
        response = await client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "SecurePass123!",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "password" not in data
```

---

## 6. FastMCP 开发最佳实践

### 6.1 MCP Server 架构

```python
# mcp/server.py
"""FastMCP Server 实现."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import FastMCP, Context
from pydantic import BaseModel

from core.config import settings
from services.user_service import UserService


# 定义 MCP Server
mcp = FastMCP(
    "myapp-mcp-server",
    dependencies=["fastmcp", "httpx", "pydantic"],
)


# 生命周期管理
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """应用生命周期."""
    # 初始化
    await server.log("info", "MCP Server starting...")
    yield {"db": None, "cache": None}
    # 清理
    await server.log("info", "MCP Server stopping...")


mcp = FastMCP("myapp-mcp-server", lifespan=app_lifespan)


# 定义工具 (Tool)
@mcp.tool()
async def get_user_by_email(
    email: str,
    ctx: Context,
) -> dict:
    """通过邮箱获取用户信息.
    
    Args:
        email: 用户邮箱地址
        
    Returns:
        用户信息字典
    """
    ctx.info(f"查询用户: {email}")
    
    # 使用 span 追踪
    with ctx.span("get_user_by_email") as span:
        span.set_attribute("user.email", email)
        
        service = UserService()
        user = await service.get_by_email(email)
        
        if user:
            span.set_attribute("user.found", True)
            return {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name,
            }
        
        span.set_attribute("user.found", False)
        return {"error": "User not found"}


@mcp.tool()
async def create_order(
    user_id: str,
    items: list[dict],
    ctx: Context,
) -> dict:
    """创建订单.
    
    Args:
        user_id: 用户ID
        items: 订单项列表 [{"product_id": "...", "quantity": 1}]
        
    Returns:
        订单信息
    """
    ctx.info(f"创建订单: user={user_id}, items={len(items)}")
    
    # 进度报告
    ctx.report_progress(0, 3)
    
    # 验证用户
    ctx.report_progress(1, 3)
    
    # 创建订单
    ctx.report_progress(2, 3)
    
    # 完成
    ctx.report_progress(3, 3)
    
    return {
        "order_id": "ord_xxx",
        "status": "created",
        "total": 100.00,
    }


# 定义资源 (Resource)
@mcp.resource("user://{user_id}")
async def get_user_resource(user_id: str) -> str:
    """获取用户资源.
    
    URI 格式: user://{user_id}
    """
    service = UserService()
    user = await service.get_by_id(user_id)
    
    if not user:
        return f"User {user_id} not found"
    
    return f"""
# User: {user.full_name}

- Email: {user.email}
- Status: {'Active' if user.is_active else 'Inactive'}
- Created: {user.created_at}
"""


@mcp.resource("config://app")
async def get_app_config() -> str:
    """获取应用配置."""
    return f"""
# Application Configuration

- Name: {settings.APP_NAME}
- Version: {settings.VERSION}
- Debug: {settings.DEBUG}
"""


# 定义提示模板 (Prompt)
@mcp.prompt()
def analyze_user_behavior(user_id: str) -> str:
    """分析用户行为提示模板."""
    return f"""请分析用户 {user_id} 的行为模式:

1. 最近登录时间
2. 活跃功能模块
3. 潜在需求分析

基于以上信息，给出个性化推荐建议。
"""


@mcp.prompt()
def debug_error(error_code: str, context: str) -> str:
    """调试错误提示模板."""
    return f"""请帮助调试以下错误:

错误码: {error_code}
上下文: {context}

请提供:
1. 可能的原因
2. 排查步骤
3. 修复建议
"""


# 启动服务器
if __name__ == "__main__":
    mcp.run(transport="stdio")  # 或 "sse"
```

### 6.2 MCP Client 使用

```python
# mcp/client.py
"""MCP Client 实现."""

from contextlib import asynccontextmanager

from fastmcp import Client


@asynccontextmanager
async def get_mcp_client():
    """获取 MCP Client."""
    async with Client(
        "myapp-mcp-server",
        command="python",
        args=["-m", "mcp.server"],
    ) as client:
        yield client


async def query_user(email: str) -> dict:
    """查询用户信息."""
    async with get_mcp_client() as client:
        result = await client.call_tool("get_user_by_email", {"email": email})
        return result


async def get_user_documentation(user_id: str) -> str:
    """获取用户文档."""
    async with get_mcp_client() as client:
        content = await client.read_resource(f"user://{user_id}")
        return content
```

### 6.3 MCP 与 FastAPI 集成

```python
# api/mcp_router.py
"""MCP API 路由."""

from fastapi import APIRouter, HTTPException
from fastmcp import Client

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.post("/tools/{tool_name}")
async def call_mcp_tool(
    tool_name: str,
    params: dict,
):
    """调用 MCP Tool."""
    async with Client("myapp-mcp-server") as client:
        try:
            result = await client.call_tool(tool_name, params)
            return {"success": True, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/{resource_uri:path}")
async def read_mcp_resource(resource_uri: str):
    """读取 MCP Resource."""
    async with Client("myapp-mcp-server") as client:
        try:
            content = await client.read_resource(resource_uri)
            return {"success": True, "content": content}
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
```

### 6.4 MCP 可观测性

```python
# mcp/telemetry.py
"""MCP 可观测性集成."""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import settings

# 初始化 Tracer
tracer_provider = TracerProvider()
otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer("mcp-server")


class ObservableMCPServer:
    """带可观测性的 MCP Server."""
    
    def __init__(self, name: str):
        self.name = name
        self.mcp = FastMCP(name)
        self._instrument_tools()
    
    def _instrument_tools(self):
        """为所有 tools 添加追踪."""
        original_tool = self.mcp.tool
        
        def instrumented_tool(*args, **kwargs):
            def decorator(func):
                with tracer.start_as_current_span(f"mcp.tool.{func.__name__}") as span:
                    span.set_attribute("mcp.tool.name", func.__name__)
                    span.set_attribute("mcp.server.name", self.name)
                    return func
            return decorator
        
        self.mcp.tool = instrumented_tool
```

---

## 7. 可观测性最佳实践

### 7.1 日志规范 (structlog)

```python
# core/logging.py
"""结构化日志配置."""

import sys

import structlog
from structlog.types import FilteringBoundLogger


def configure_logging() -> None:
    """配置结构化日志."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# 获取 logger
logger: FilteringBoundLogger = structlog.get_logger()


# 使用示例
async def create_user(data: UserCreate) -> User:
    """创建用户."""
    logger.info(
        "creating_user",
        email=data.email,
        request_id=get_request_id(),
    )
    
    try:
        user = await user_repository.create(data)
        logger.info(
            "user_created",
            user_id=str(user.id),
            email=user.email,
        )
        return user
    except Exception as e:
        logger.error(
            "user_creation_failed",
            email=data.email,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
```

### 7.2 指标收集 (Prometheus)

```python
# core/metrics.py
"""Prometheus 指标配置."""

from prometheus_client import Counter, Histogram, Gauge, Info

# 应用信息
APP_INFO = Info("app", "Application information")

# HTTP 请求指标
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# 业务指标
USERS_CREATED = Counter(
    "users_created_total",
    "Total users created",
    ["source"],
)

ORDERS_PROCESSED = Histogram(
    "orders_processed_seconds",
    "Order processing time",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections",
)

# 数据库指标
DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1],
)

DB_CONNECTIONS = Gauge(
    "db_connections",
    "Database connection pool stats",
    ["state"],  # used, free, overflow
)
```

### 7.3 OpenTelemetry 全链路追踪

```python
# core/tracing.py
"""OpenTelemetry 追踪配置."""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import settings


def init_tracing(app=None) -> None:
    """初始化分布式追踪."""
    resource = Resource(
        attributes={
            SERVICE_NAME: settings.OTEL_SERVICE_NAME,
            SERVICE_VERSION: settings.VERSION,
            "deployment.environment": settings.ENVIRONMENT,
        }
    )
    
    provider = TracerProvider(resource=resource)
    
    # OTLP 导出器
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    )
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    trace.set_tracer_provider(provider)
    
    # 自动埋点
    if app:
        FastAPIInstrumentor.instrument_app(app)
    
    AsyncPGInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()


# 自定义追踪装饰器
tracer = trace.get_tracer(__name__)


def traced(name: str | None = None, attributes: dict | None = None):
    """追踪装饰器."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            span_name = name or func.__name__
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                # 记录函数参数 (脱敏)
                span.set_attribute("function.args_count", len(args))
                span.set_attribute("function.kwargs_keys", list(kwargs.keys()))
                
                return await func(*args, **kwargs)
        return wrapper
    return decorator


# 使用示例
class UserService:
    @traced("user_service.create", {"layer": "service"})
    async def create(self, data: UserCreate) -> User:
        """创建用户."""
        with tracer.start_as_current_span("validate_email") as span:
            span.set_attribute("email", data.email)
            await self._validate_email(data.email)
        
        with tracer.start_as_current_span("hash_password"):
            hashed = hash_password(data.password)
        
        with tracer.start_as_current_span("db_insert") as span:
            span.set_attribute("db.table", "users")
            user = await self.repository.create({**data.dict(), "password": hashed})
        
        return user
```

### 7.4 FastAPI 中间件集成

```python
# middleware/observability.py
"""可观测性中间件."""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.logging import logger
from core.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION
from core.tracing import tracer


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """可观测性中间件."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", generate_request_id())
        
        # 绑定请求上下文到日志
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            user_agent=request.headers.get("user-agent"),
            client_ip=request.client.host if request.client else None,
        )
        
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
        )
        
        # 追踪
        with tracer.start_as_current_span("http_request") as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.request_id", request_id)
            
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                
                # 记录指标
                HTTP_REQUESTS_TOTAL.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code,
                ).inc()
                
                HTTP_REQUEST_DURATION.labels(
                    method=request.method,
                    endpoint=request.url.path,
                ).observe(duration)
                
                # 记录日志
                logger.info(
                    "request_completed",
                    status_code=response.status_code,
                    duration_ms=duration * 1000,
                )
                
                # 添加响应头
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Response-Time"] = f"{duration:.3f}s"
                
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.duration_ms", duration * 1000)
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    "request_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_ms=duration * 1000,
                )
                
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                span.set_attribute("error.type", type(e).__name__)
                
                raise


class DatabaseMetricsMiddleware:
    """数据库指标中间件 (SQLAlchemy)."""
    
    async def before_cursor_execute(
        self,
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ):
        context._query_start_time = time.time()
        
    async def after_cursor_execute(
        self,
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ):
        duration = time.time() - context._query_start_time
        
        # 解析 SQL 获取操作类型和表名
        operation = statement.split()[0].upper()
        table = self._extract_table_name(statement)
        
        DB_QUERY_DURATION.labels(
            operation=operation,
            table=table or "unknown",
        ).observe(duration)
    
    def _extract_table_name(self, statement: str) -> str | None:
        """从 SQL 语句中提取表名."""
        import re
        
        # 匹配 FROM, INTO, UPDATE 后的表名
        patterns = [
            r'FROM\s+(\w+)',
            r'INTO\s+(\w+)',
            r'UPDATE\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, statement, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
```

### 7.5 健康检查与探针

```python
# api/health.py
"""健康检查端点."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db_session
from core.config import settings

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """健康状态."""
    status: str
    version: str
    checks: dict


class ReadinessStatus(BaseModel):
    """就绪状态."""
    ready: bool
    checks: dict


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """健康检查 (存活探针)."""
    return HealthStatus(
        status="healthy",
        version=settings.VERSION,
        checks={
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.get("/ready", response_model=ReadinessStatus)
async def readiness_check(
    session: AsyncSession = Depends(get_db_session),
):
    """就绪检查 (就绪探针)."""
    checks = {}
    
    # 检查数据库
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"ready": False, "checks": checks},
        )
    
    # 检查 Redis
    try:
        # await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
    
    # 检查外部依赖
    checks["external_apis"] = await check_external_apis()
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return ReadinessStatus(
        ready=all_ok,
        checks=checks,
    )


@router.get("/metrics")
async def metrics():
    """Prometheus 指标端点."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
```

---

## 8. 配置管理

```python
# core/config.py
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # 应用
    APP_NAME: str = "My Service"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # 数据库
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    DATABASE_POOL_SIZE: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # 安全
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Harness
    HARNESS_API_KEY: str | None = None
    HARNESS_ACCOUNT_ID: str | None = None
    
    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_SERVICE_NAME: str = "python-service"


@lru_cache
def get_settings() -> Settings:
    """获取配置 (单例)."""
    return Settings()


settings = get_settings()
```

---

## 9. AI Agent 集成点

### 7.1 代码审查 Agent
```python
# agents/code_reviewer.py
import ast
from pathlib import Path


class PythonCodeReviewer:
    """Python 代码审查 Agent."""
    
    def review_file(self, file_path: Path) -> list[dict]:
        """审查 Python 文件."""
        content = file_path.read_text()
        issues = []
        
        # 检查类型注解
        issues.extend(self._check_type_annotations(content, file_path))
        
        # 检查异步模式
        issues.extend(self._check_async_patterns(content, file_path))
        
        # 检查 SQL 注入
        issues.extend(self._check_sql_injection(content, file_path))
        
        return issues
    
    def _check_type_annotations(self, content: str, path: Path) -> list[dict]:
        """检查类型注解完整性."""
        tree = ast.parse(content)
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查参数注解
                for arg in node.args.args:
                    if arg.annotation is None and arg.arg not in ('self', 'cls'):
                        issues.append({
                            "file": str(path),
                            "line": node.lineno,
                            "severity": "warning",
                            "message": f"参数 '{arg.arg}' 缺少类型注解",
                        })
                
                # 检查返回值注解
                if node.returns is None:
                    issues.append({
                        "file": str(path),
                        "line": node.lineno,
                        "severity": "warning",
                        "message": f"函数 '{node.name}' 缺少返回值注解",
                    })
        
        return issues
```

### 7.2 部署建议 Agent
```python
# agents/deploy_advisor.py
from typing import Any

import httpx


class DeployAdvisor:
    """部署建议 Agent."""
    
    def __init__(self, harness_api_key: str, account_id: str):
        self.api_key = harness_api_key
        self.account_id = account_id
        self.base_url = f"https://app.harness.io/gateway"
    
    async def analyze_deployment_risk(self, service: str) -> dict[str, Any]:
        """分析部署风险."""
        # 获取 Harness 指标
        metrics = await self._get_service_metrics(service)
        
        risk_factors = []
        
        # 检查错误率
        if metrics.get('error_rate', 0) > 0.01:
            risk_factors.append({
                "level": "high",
                "reason": f"错误率过高: {metrics['error_rate']:.2%}",
            })
        
        # 检查延迟
        if metrics.get('p99_latency', 0) > 500:
            risk_factors.append({
                "level": "medium",
                "reason": f"P99 延迟过高: {metrics['p99_latency']}ms",
            })
        
        return {
            "overall_risk": "high" if any(r['level'] == 'high' for r in risk_factors) else "low",
            "factors": risk_factors,
        }
    
    async def _get_service_metrics(self, service: str) -> dict:
        """从 Harness 获取服务指标."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/cv/api/metrics",
                headers={"x-api-key": self.api_key},
                params={"accountId": self.account_id, "service": service},
            )
            response.raise_for_status()
            return response.json()
```
