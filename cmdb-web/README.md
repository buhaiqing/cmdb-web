# CMDB Web Application

运维部 CMDB（配置管理数据库）Web 应用程序 - 统一的 IT 资源配置管理平台。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite (构建工具)
- Pinia (状态管理)
- Element Plus (UI 组件库)
- Vue Router (路由)
- Axios (HTTP 客户端)
- Playwright (E2E 测试)

### 后端
- Python 3.11+
- FastAPI (Web 框架)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 15 (数据库)
- Redis 7 (缓存)
- Alembic (数据库迁移)
- Pytest (测试)

## 项目结构

```
cmdb-web/
├── backend/
│   ├── app/
│   │   ├── api/           # API 路由
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── auth.py      # 认证 API
│   │   │       ├── ci.py        # 配置项 API
│   │   │       ├── user.py      # 用户 API
│   │   │       └── health.py    # 健康检查
│   │   ├── core/          # 核心配置
│   │   │   ├── config.py        # 应用配置
│   │   │   ├── security.py      # 安全工具
│   │   │   └── exceptions.py    # 自定义异常
│   │   ├── models/        # 数据模型
│   │   │   ├── base.py          # 模型基类
│   │   │   ├── user.py          # 用户模型
│   │   │   ├── ci.py            # 配置项模型
│   │   │   ├── relation.py      # 关系模型
│   │   │   ├── change.py        # 变更模型
│   │   │   └── audit.py         # 审计模型
│   │   ├── schemas/       # Pydantic schemas
│   │   │   ├── user.py          # 用户 schemas
│   │   │   ├── ci.py            # 配置项 schemas
│   │   │   ├── change.py        # 变更 schemas
│   │   │   └── audit.py         # 审计 schemas
│   │   ├── services/      # 业务逻辑
│   │   │   ├── user_service.py  # 用户服务
│   │   │   ├── ci_service.py    # 配置项服务
│   │   │   └── auth_service.py  # 认证服务
│   │   ├── db/            # 数据库配置
│   │   │   ├── session.py       # 数据库会话
│   │   │   └── crud_base.py     # CRUD 基类
│   │   ├── middleware/    # 中间件
│   │   │   ├── auth.py          # 认证中间件
│   │   │   └── logging.py       # 日志中间件
│   │   └── main.py        # 应用入口
│   ├── tests/
│   │   ├── unit/                # 单元测试
│   │   └── integration/         # 集成测试
│   ├── alembic/         # 数据库迁移
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   │   ├── request.ts       # HTTP 请求封装
│   │   │   ├── auth.ts          # 认证 API
│   │   │   ├── ci.ts            # 配置项 API
│   │   │   ├── audit.ts         # 审计 API
│   │   │   ├── change.ts        # 变更 API
│   │   │   ├── dashboard.ts     # 仪表盘 API
│   │   │   └── role.ts          # 角色 API
│   │   ├── components/    # UI 组件
│   │   │   ├── DataTable.vue      # 数据表格组件
│   │   │   ├── LoadingSpinner.vue # 加载动画组件
│   │   │   └── SearchForm.vue     # 搜索表单组件
│   │   ├── views/         # 页面视图
│   │   │   ├── Login.vue        # 登录页
│   │   │   ├── Layout.vue       # 布局页
│   │   │   ├── NotFound.vue     # 404 页面
│   │   │   ├── ci/
│   │   │   │   ├── CIList.vue   # 配置项列表
│   │   │   │   └── CIDetail.vue # 配置项详情
│   │   │   ├── user/
│   │   │   │   └── UserList.vue # 用户列表
│   │   │   ├── change/
│   │   │   │   ├── ChangeList.vue   # 变更列表
│   │   │   │   └── ChangeDetail.vue  # 变更详情
│   │   │   ├── dashboard/
│   │   │   │   └── Dashboard.vue    # 仪表盘
│   │   │   ├── relation/
│   │   │   │   └── RelationGraph.vue # 关系图
│   │   │   ├── report/
│   │   │   │   └── ReportSummary.vue # 报表汇总
│   │   │   └── system/
│   │   │       ├── AuditLog.vue     # 审计日志
│   │   │       └── RoleManage.vue   # 角色管理
│   │   ├── stores/        # Pinia 状态
│   │   │   ├── user.ts          # 用户 store
│   │   │   └── ci.ts            # 配置项 store
│   │   ├── router/        # 路由配置
│   │   │   └── index.ts
│   │   ├── types/         # TypeScript 类型
│   │   ├── utils/         # 工具函数
│   │   ├── mocks/         # MSW 浏览器 mocks
│   │   ├── styles/        # 样式
│   │   ├── App.vue        # 根组件
│   │   └── main.ts        # 入口文件
│   ├── mock/            # MSW Mock 服务
│   │   ├── server.ts       # Mock 服务器
│   │   ├── handlers.ts     # 请求处理
│   │   └── data.ts         # Mock 数据
│   ├── tests/e2e/       # E2E 测试
│   │   ├── pages/           # 页面对象
│   │   ├── fixtures/       # 测试 fixtures
│   │   ├── utils/          # 测试工具
│   │   ├── auth.test.ts         # 认证测试
│   │   ├── ci-manage.test.ts    # 配置项管理测试
│   │   ├── change.test.ts       # 变更管理测试
│   │   ├── dashboard.test.ts    # 仪表盘测试
│   │   ├── audit.test.ts        # 审计日志测试
│   │   ├── role.test.ts         # 角色管理测试
│   │   └── ui-basic.test.ts     # UI 基础测试
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                  # 文档
│   ├── requirements.md    # 需求规格说明书
│   ├── data-model.md      # 数据模型文档
│   ├── rbac-matrix.md     # RBAC 权限矩阵
│   ├── architecture.md    # 架构设计文档
│   ├── api-spec.md        # API 接口文档
│   ├── frontend-design.md # 前端设计文档
│   └── test-plan.md       # 测试计划
├── .github/
│   └── workflows/
│       └── ci.yml         # CI/CD 工作流
├── docker-compose.yml     # Docker 编排
├── README.md
└── .gitignore
```

## 快速开始

### 环境要求
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 使用 Docker Compose 启动

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务启动后访问：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

## 核心功能

### 配置项管理
- 支持服务器、网络设备、数据库、中间件、应用程序等配置项
- 配置项 CRUD 操作
- 批量导入/导出
- 搜索和过滤

### 关系管理
- 配置项之间的依赖、连接、运行等关系
- 图形化关系图展示
- 影响分析

### 变更管理
- 变更申请和审批流程
- 变更历史记录
- 版本对比

### 权限管理
- RBAC 角色权限控制
- 用户和角色管理
- 审计日志

### 自动发现
- K8s 集群资源同步
- 云平台资源同步（阿里云/AWS）
- 定时同步任务

## 测试

### 后端测试

```bash
cd backend
pytest                           # 运行所有测试
pytest --cov=app                 # 带覆盖率报告
pytest tests/unit                # 仅单元测试
pytest tests/integration         # 仅集成测试
```

### 前端测试

```bash
cd frontend

# E2E 测试
npx playwright test              # 运行所有测试
npx playwright test --ui         # UI 模式
npx playwright test --reporter=html  # 生成 HTML 报告

# 查看测试报告
npx playwright show-report
```

## API 文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认账号

- 用户名：admin
- 密码：Admin@123

**请首次登录后立即修改密码！**

## 配置项类型

| 类型 | 代码 | 描述 |
|------|------|------|
| 服务器 | server | 物理服务器、虚拟机 |
| 网络设备 | network_device | 路由器、交换机、防火墙 |
| 数据库 | database | MySQL、PostgreSQL、MongoDB |
| 中间件 | middleware | Redis、Kafka、Nginx |
| 应用 | application | Web 应用、API 服务 |
| 容器 | container | Docker 容器 |
| K8s 资源 | k8s_resource | Pod、Deployment、Service |
| 云资源 | cloud_resource | ECS、RDS、SLB |

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 相关文档

- [需求规格说明书](docs/requirements.md)
- [数据模型文档](docs/data-model.md)
- [RBAC 权限矩阵](docs/rbac-matrix.md)
- [架构设计文档](docs/architecture.md)
- [API 接口文档](docs/api-spec.md)

## 许可证

MIT License

## 联系方式

- 项目团队：运维部
