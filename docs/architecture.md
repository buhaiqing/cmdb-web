# CMDB 系统架构设计文档

## 1. 系统架构概览

### 1.1 整体架构图

```mermaid
graph TB
    subgraph "客户端层"
        Browser[浏览器]
        Mobile[移动端]
    end

    subgraph "接入层"
        Nginx[Nginx 负载均衡器]
        SLB[SLB 负载均衡]
    end

    subgraph "应用层"
        Frontend[Vue 3 前端应用]
        Backend[FastAPI 后端服务]
        Auth[认证授权服务]
    end

    subgraph "集成层"
        K8sIntegration[K8s 集成服务]
        CloudIntegration[云平台集成服务]
        MonitorIntegration[监控集成服务]
    end

    subgraph "数据层"
        PostgreSQL[(PostgreSQL 主库)]
        Redis[(Redis 缓存)]
    end

    subgraph "外部系统"
        K8s[Kubernetes 集群]
        Aliyun[阿里云 API]
        Prometheus[Prometheus]
    end

    Browser --> SLB
    Mobile --> SLB
    SLB --> Nginx
    Nginx --> Frontend
    Nginx --> Backend
    Frontend --> Backend
    Backend --> Auth
    Backend --> K8sIntegration
    Backend --> CloudIntegration
    Backend --> MonitorIntegration
    Backend --> PostgreSQL
    Backend --> Redis
    K8sIntegration --> K8s
    CloudIntegration --> Aliyun
    MonitorIntegration --> Prometheus
```

### 1.2 架构分层说明

| 层级 | 组件 | 技术选型 | 职责 |
|------|------|----------|------|
| 客户端层 | 浏览器、移动端 | Chrome、Safari、Edge | 用户交互界面 |
| 接入层 | Nginx、SLB | Nginx、阿里云 SLB | 负载均衡、SSL 终止、静态资源 |
| 应用层 | 前端、后端 | Vue 3、FastAPI | 业务逻辑处理、API 服务 |
| 集成层 | 集成服务 | Python 服务 | 外部系统对接、数据同步 |
| 数据层 | PostgreSQL、Redis | PostgreSQL 15、Redis 7 | 数据存储、缓存 |

## 2. 技术栈说明

### 2.1 前端技术栈

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| Vue | 3.x | 前端框架 | 组件化开发、响应式数据绑定、生态丰富 |
| TypeScript | 5.x | 类型系统 | 类型安全、代码提示、减少运行时错误 |
| Vite | 5.x | 构建工具 | 快速启动、热更新、按需编译 |
| Pinia | 2.x | 状态管理 | Vue 3 官方推荐、TypeScript 友好、轻量 |
| Element Plus | 2.x | UI 组件库 | 企业级组件、主题定制、文档完善 |
| Vue Router | 4.x | 路由管理 | 官方路由、支持懒加载、路由守卫 |
| Axios | 1.x | HTTP 客户端 | 拦截器、请求取消、类型安全 |
| Playwright | 1.x | E2E 测试 | 跨浏览器、自动化、报告生成 |

### 2.2 后端技术栈

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| Python | 3.11+ | 编程语言 | 开发效率高、生态丰富、AI/运维友好 |
| FastAPI | 0.100+ | Web 框架 | 高性能、异步支持、自动生成文档 |
| SQLAlchemy | 2.0+ | ORM 框架 | 功能强大、异步支持、类型安全 |
| Pydantic | 2.x | 数据验证 | 数据校验、序列化、类型安全 |
| Alembic | 1.x | 数据库迁移 | SQLAlchemy 官方迁移工具 |
| Pytest | 7.x | 测试框架 | 插件丰富、断言简洁、并发测试 |
| JWT | - | Token 认证 | 无状态、跨域、成熟稳定 |

### 2.3 基础设施

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| PostgreSQL | 15+ | 关系数据库 | JSONB 支持、扩展性强、开源 |
| Redis | 7+ | 缓存 | 高性能、数据结构丰富、持久化 |
| Docker | 24+ | 容器化 | 标准化部署、环境隔离 |
| Docker Compose | - | 容器编排 | 本地开发、多容器管理 |

## 3. 组件划分

### 3.1 前端组件架构

```
frontend/
├── src/
│   ├── main.ts                 # 应用入口
│   ├── App.vue                 # 根组件
│   ├── api/                    # API 客户端
│   │   ├── index.ts            # API 配置
│   │   ├── ci.ts               # 配置项 API
│   │   ├── relation.ts         # 关系 API
│   │   ├── change.ts           # 变更 API
│   │   ├── user.ts             # 用户 API
│   │   └── auth.ts             # 认证 API
│   ├── components/             # 公共组件
│   │   ├── common/             # 通用组件
│   │   │   ├── PageHeader.vue
│   │   │   ├── DataTable.vue
│   │   │   ├── SearchForm.vue
│   │   │   └── Loading.vue
│   │   ├── ci/                 # CI 组件
│   │   │   ├── CiList.vue
│   │   │   ├── CiDetail.vue
│   │   │   ├── CiForm.vue
│   │   │   └── RelationGraph.vue
│   │   └── ui/                 # UI 基础组件
│   │       ├── Button.vue
│   │       ├── Input.vue
│   │       └── Modal.vue
│   ├── views/                  # 页面视图
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   ├── ci/
│   │   │   ├── CiListPage.vue
│   │   │   └── CiDetailPage.vue
│   │   ├── relation/
│   │   ├── change/
│   │   ├── user/
│   │   └── system/
│   ├── stores/                 # Pinia 状态管理
│   │   ├── user.ts
│   │   ├── ci.ts
│   │   ├── app.ts
│   │   └── permission.ts
│   ├── router/                 # 路由配置
│   │   ├── index.ts
│   │   ├── routes.ts
│   │   └── guards.ts
│   ├── types/                  # TypeScript 类型
│   │   ├── ci.ts
│   │   ├── user.ts
│   │   └── api.ts
│   ├── utils/                  # 工具函数
│   │   ├── request.ts
│   │   ├── auth.ts
│   │   └── storage.ts
│   ├── styles/                 # 样式文件
│   │   ├── variables.scss
│   │   └── global.scss
│   └── assets/                 # 静态资源
├── tests/                      # 测试文件
│   ├── e2e/                    # E2E 测试
│   └── unit/                   # 单元测试
├── package.json
├── vite.config.ts
├── tsconfig.json
└── playwright.config.ts
```

### 3.2 后端服务架构

```
backend/
├── app/
│   ├── main.py                 # 应用入口
│   ├── api/                    # API 路由层
│   │   ├── deps.py             # 依赖注入
│   │   ├── auth.py             # 认证路由
│   │   ├── ci.py               # 配置项路由
│   │   ├── relation.py         # 关系路由
│   │   ├── change.py           # 变更路由
│   │   ├── user.py             # 用户路由
│   │   └── system.py           # 系统路由
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全相关
│   │   └── exceptions.py       # 异常处理
│   ├── models/                 # 数据模型
│   │   ├── base.py             # 基类模型
│   │   ├── user.py             # 用户模型
│   │   ├── ci.py               # CI 模型
│   │   ├── relation.py         # 关系模型
│   │   └── audit.py            # 审计模型
│   ├── schemas/                # Pydantic 模式
│   │   ├── user.py             # 用户模式
│   │   ├── ci.py               # CI 模式
│   │   ├── relation.py         # 关系模式
│   │   └── common.py           # 通用模式
│   ├── services/               # 业务逻辑层
│   │   ├── ci_service.py       # CI 服务
│   │   ├── relation_service.py # 关系服务
│   │   ├── change_service.py   # 变更服务
│   │   ├── user_service.py     # 用户服务
│   │   ├── auth_service.py     # 认证服务
│   │   └── sync/               # 同步服务
│   │       ├── k8s_sync.py     # K8s 同步
│   │       ├── cloud_sync.py   # 云同步
│   │       └── monitor_sync.py # 监控同步
│   ├── db/                     # 数据库层
│   │   ├── session.py          # 会话管理
│   │   ├── base.py             # 基类
│   │   └── crud.py             # CRUD 操作
│   └── middleware/             # 中间件
│       ├── auth.py             # 认证中间件
│       ├── permission.py       # 权限中间件
│       └── audit.py            # 审计中间件
├── tests/                      # 测试文件
│   ├── conftest.py             # 测试配置
│   ├── test_api/               # API 测试
│   └── test_services/          # 服务测试
├── alembic/                    # 数据库迁移
├── requirements.txt
└── Dockerfile
```

### 3.3 服务间调用关系

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端
    participant BE as 后端 API
    participant Auth as 认证服务
    participant DB as 数据库
    participant Redis as 缓存
    participant Sync as 同步服务

    User->>FE: 登录请求
    FE->>BE: POST /api/auth/login
    BE->>Auth: 验证用户凭证
    Auth->>DB: 查询用户信息
    DB-->>Auth: 返回用户数据
    Auth->>Auth: 生成 JWT Token
    Auth-->>BE: 返回 Token
    BE-->>FE: 返回登录结果
    FE->>Redis: 缓存 Token
    FE-->>User: 登录成功

    User->>FE: 查询 CI 列表
    FE->>BE: GET /api/ci
    BE->>Auth: 验证 Token
    Auth-->>BE: 验证通过
    BE->>DB: 查询 CI 数据
    DB-->>BE: 返回 CI 列表
    BE->>Redis: 缓存查询结果
    BE-->>FE: 返回 CI 数据
    FE-->>User: 展示 CI 列表
```

## 4. 部署架构

### 4.1 开发环境部署

```mermaid
graph LR
    subgraph "开发环境"
        DevPC[开发者电脑]
        DockerDocker[Docker Desktop]

        subgraph "Docker Compose"
            FrontendDev[前端开发服务器]
            BackendDev[后端开发服务器]
            PostgresDev[(PostgreSQL)]
            RedisDev[(Redis)]
        end
    end

    DevPC --> DockerDocker
    DockerDocker --> FrontendDev
    DockerDocker --> BackendDev
    DockerDocker --> PostgresDev
    DockerDocker --> RedisDev
    FrontendDev --> BackendDev
    BackendDev --> PostgresDev
    BackendDev --> RedisDev
```

### 4.2 生产环境部署

```mermaid
graph TB
    subgraph "阿里云 VPC"
        SLB[SLB 负载均衡]

        subgraph "Kubernetes 集群"
            subgraph "Namespace: cmdb"
                Ingress[Ingress Controller]

                subgraph "Deployment: frontend"
                    FrontendPod1[Frontend Pod 1]
                    FrontendPod2[Frontend Pod 2]
                end

                subgraph "Deployment: backend"
                    BackendPod1[Backend Pod 1]
                    BackendPod2[Backend Pod 2]
                    BackendPod3[Backend Pod 3]
                end
            end
        end

        subgraph "RDS"
            PostgreSQL[RDS PostgreSQL]
        end

        subgraph "Redis"
            RedisCluster[Redis 集群]
        end
    end

    User((用户)) --> SLB
    SLB --> Ingress
    Ingress --> FrontendPod1
    Ingress --> FrontendPod2
    FrontendPod1 --> BackendPod1
    FrontendPod2 --> BackendPod2
    BackendPod1 --> PostgreSQL
    BackendPod2 --> PostgreSQL
    BackendPod1 --> RedisCluster
    BackendPod2 --> RedisCluster
```

### 4.3 Docker Compose 配置

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://backend:8000

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://cmdb:cmdb@postgres:5432/cmdb
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=your-secret-key

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=cmdb
      - POSTGRES_USER=cmdb
      - POSTGRES_PASSWORD=cmdb
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  redis_data:
```

## 5. 数据流设计

### 5.1 配置项数据流

```mermaid
flowchart LR
    subgraph "数据源"
        K8sSource[K8s API]
        CloudSource[云 API]
        ManualSource[手动录入]
    end

    subgraph "数据处理"
        Sync[同步服务]
        Validate[数据验证]
        Transform[数据转换]
    end

    subgraph "数据存储"
        CI[配置项表]
        Relation[关系表]
        History[历史表]
    end

    K8sSource --> Sync
    CloudSource --> Sync
    ManualSource --> Validate
    Sync --> Validate
    Validate --> Transform
    Transform --> CI
    Transform --> Relation
    CI --> History
    Relation --> History
```

### 5.2 变更管理数据流

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端
    participant BE as 后端
    participant Change as 变更服务
    participant DB as 数据库
    participant Notify as 通知服务

    User->>FE: 提交变更申请
    FE->>BE: POST /api/changes
    BE->>Change: 创建变更记录
    Change->>DB: 保存变更数据 (pending)
    DB-->>Change: 保存成功

    alt 需要审批
        Change->>Notify: 发送审批通知
        Notify-->>User: 通知审批人
        User->>FE: 审批变更
        FE->>BE: POST /api/changes/:id/approve
        BE->>Change: 更新变更状态
        Change->>DB: 更新状态 (approved)
        Change->>Change: 执行变更
    else 自动批准
        Change->>Change: 执行变更
    end

    Change->>DB: 保存 CI 新版本
    Change->>DB: 记录审计日志
    Change->>Notify: 发送变更通知
    Notify-->>User: 通知申请人
```

## 6. 安全设计

### 6.1 认证流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端
    participant BE as 后端
    participant Auth as 认证服务
    participant DB as 数据库

    User->>FE: 输入用户名密码
    FE->>BE: POST /api/auth/login
    BE->>Auth: 验证凭证
    Auth->>DB: 查询用户
    DB-->>Auth: 用户数据
    Auth->>Auth: 验证密码 (bcrypt)
    Auth->>Auth: 生成 JWT Token

    alt 验证成功
        Auth-->>BE: 返回 Token
        BE-->>FE: 返回登录结果
        FE->>FE: 存储 Token (localStorage)
        FE-->>User: 登录成功
    else 验证失败
        Auth-->>BE: 返回错误
        BE-->>FE: 返回错误信息
        FE-->>User: 显示错误
    end
```

### 6.2 授权机制

```python
# JWT Token 结构
{
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "sub": "user-uuid",
        "username": "admin",
        "role": "super_admin",
        "permissions": ["ci:create", "ci:read", "..."],
        "exp": 1234567890,
        "iat": 1234567800
    },
    "signature": "HMACSHA256(...)"
}
```

### 6.3 安全中间件

```python
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户"""
    token = credentials.credentials

    try:
        # 验证 Token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")

        # 查询用户
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(401, "用户不存在")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token 无效")
```

## 7. API 设计规范

### 7.1 RESTful 风格

| 操作 | HTTP 方法 | 端点 | 描述 |
|------|----------|------|------|
| 列表查询 | GET | /api/ci | 获取 CI 列表 |
| 创建 | POST | /api/ci | 创建新 CI |
| 详情 | GET | /api/ci/{id} | 获取 CI 详情 |
| 更新 | PUT | /api/ci/{id} | 更新 CI |
| 删除 | DELETE | /api/ci/{id} | 删除 CI |
| 批量导入 | POST | /api/ci/batch/import | 批量导入 |
| 批量导出 | GET | /api/ci/batch/export | 批量导出 |

### 7.2 响应格式

```json
{
    "success": true,
    "data": {},
    "message": "操作成功",
    "timestamp": 1234567890
}
```

### 7.3 错误响应

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "参数验证失败",
        "details": [
            {
                "field": "name",
                "message": "名称不能为空"
            }
        ]
    },
    "timestamp": 1234567890
}
```

### 7.4 分页参数

```json
// 请求参数
{
    "page": 1,
    "page_size": 20,
    "sort_by": "name",
    "sort_order": "asc"
}

// 响应格式
{
    "success": true,
    "data": {
        "items": [],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}
```

## 8. 监控与日志

### 8.1 监控指标

| 指标类型 | 指标名称 | 说明 |
|----------|----------|------|
| 应用指标 | request_count | 请求总数 |
| 应用指标 | request_duration | 请求耗时 |
| 应用指标 | error_count | 错误数量 |
| 数据库指标 | connection_count | 连接数 |
| 数据库指标 | query_duration | 查询耗时 |
| 缓存指标 | hit_rate | 缓存命中率 |
| 系统指标 | cpu_usage | CPU 使用率 |
| 系统指标 | memory_usage | 内存使用率 |

### 8.2 日志格式

```json
{
    "timestamp": "2024-01-01T00:00:00Z",
    "level": "INFO",
    "logger": "app.api.ci",
    "message": "CI created successfully",
    "context": {
        "user_id": "uuid",
        "ci_id": "uuid",
        "ip": "127.0.0.1"
    }
}
```
