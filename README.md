# Agent Harness 全栈开发实践案例

本项目是一个运用 Agent Harness 技术进行全栈开发的实践案例，基于 CMDB（配置管理数据库）系统进行演示。

## 项目概述

CMDB-Web 是一个配置管理数据库系统的前后端分离应用，用于管理 IT 基础设施中的配置项（CI），如服务器、数据库、应用等。

### 技术栈

- **前端**: Vue 3 + TypeScript + Element Plus + Vite
- **后端**: Python FastAPI + SQLAlchemy + Alembic
- **测试**: Playwright E2E 测试
- **容器化**: Docker + Docker Compose

## 项目结构

```
agent_harness_example1/
├── cmdb-web/                      # 主项目目录
│   ├── backend/                   # Python FastAPI 后端
│   │   ├── app/
│   │   │   ├── api/              # API 路由
│   │   │   │   ├── routes/       # 认证、配置项、用户等路由
│   │   │   │   └── __init__.py
│   │   │   ├── core/             # 核心配置和安全
│   │   │   ├── db/               # 数据库会话和基础 CRUD
│   │   │   ├── middleware/       # 中间件（日志、认证）
│   │   │   ├── models/           # SQLAlchemy 模型
│   │   │   ├── schemas/          # Pydantic 数据模型
│   │   │   └── services/         # 业务逻辑服务层
│   │   ├── tests/                # 后端测试
│   │   │   ├── integration/      # 集成测试
│   │   │   └── unit/             # 单元测试
│   │   ├── alembic/              # 数据库迁移
│   │   └── requirements.txt      # Python 依赖
│   │
│   ├── frontend/                 # Vue 3 前端
│   │   ├── src/
│   │   │   ├── api/              # API 调用封装
│   │   │   ├── components/      # Vue 组件
│   │   │   ├── mocks/            # MSW Mock 配置
│   │   │   ├── router/           # Vue Router 路由
│   │   │   ├── stores/           # Pinia 状态管理
│   │   │   ├── types/            # TypeScript 类型定义
│   │   │   ├── utils/            # 工具函数
│   │   │   └── views/            # 页面视图
│   │   │       ├── ci/          # 配置项相关页面
│   │   │       ├── user/         # 用户管理页面
│   │   │       ├── Login.vue     # 登录页
│   │   │       └── Layout.vue    # 布局组件
│   │   ├── tests/e2e/            # Playwright E2E 测试
│   │   │   ├── fixtures/        # 测试夹具（页面对象、数据工厂）
│   │   │   ├── pages/            # 页面对象模型
│   │   │   ├── mock-handlers.ts  # MSW 请求拦截
│   │   │   ├── ci-manage.test.ts # 配置项管理测试
│   │   │   └── playwright.config.ts
│   │   └── package.json
│   │
│   ├── docs/                     # 项目文档
│   │   ├── api-spec.md          # API 规范文档
│   │   ├── architecture.md      # 系统架构设计
│   │   ├── data-model.md        # 数据模型说明
│   │   ├── frontend-design.md   # 前端设计文档
│   │   ├── rbac-matrix.md       # RBAC 权限矩阵
│   │   ├── requirements.md      # 需求规格说明
│   │   └── test-plan.md         # 测试计划
│   │
│   ├── docker-compose.yml        # Docker 编排配置
│   └── README.md                 # 项目说明
│
└── .claude/skills/              # Agent Harness 技能配置
    ├── harness-ai-agent-skill/  # AI Agent 编排技能
    ├── frontend-design/          # 前端设计技能
    └── modern-web-app/           # 现代 Web 应用技能
```

## 核心功能

### 配置项管理（CI）

- 创建、查看、编辑、删除配置项
- 支持多种配置项类型：服务器、数据库、应用、中间件等
- 配置项属性管理：名称、代码、状态、环境、负责人等
- 配置项关系管理：服务器 ↔ 数据库、服务器 ↔ 应用等

### 用户认证

- 用户注册与登录
- JWT Token 认证
- 角色权限控制（RBAC）

### 搜索与筛选

- 按名称模糊搜索
- 按类型、状态、环境筛选
- 分页显示

## 测试策略

### E2E 测试（Playwright）

本项目采用 Page Object 模式进行 E2E 测试，测试文件位于 `frontend/tests/e2e/`。

#### 测试文件说明

| 文件 | 说明 |
|------|------|
| `ci-manage.test.ts` | 配置项管理全流程测试（16 个测试用例） |
| `auth.test.ts` | 用户认证测试 |
| `ui-basic.test.ts` | UI 基础功能测试 |

#### 页面对象模型

| 文件 | 说明 |
|------|------|
| `pages/index.ts` | 页面对象类（LoginPage, CIListPage, CIFormPage 等） |
| `pages/selectors.ts` | 页面元素选择器定义 |
| `pages/base.page.ts` | 基础页面对象类，封装通用操作 |

#### 测试数据工厂

| 文件 | 说明 |
|------|------|
| `fixtures/factories.ts` | 测试数据工厂（CIFactory, UserFactory） |
| `fixtures/index.ts` | Fixtures 定义和扩展 |

#### Mock 服务

| 文件 | 说明 |
|------|------|
| `mock-handlers.ts` | MSW 请求拦截和模拟响应 |

#### 运行测试

```bash
cd cmdb-web/frontend
npm run test:e2e              # 运行所有 E2E 测试
npm run test:e2e -- ci-manage  # 只运行配置项管理测试
```

### 后端测试

```bash
cd cmdb-web/backend
pytest                        # 运行所有测试
pytest tests/unit/           # 运行单元测试
pytest tests/integration/     # 运行集成测试
```

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- Docker & Docker Compose

### 本地开发

1. **启动后端**
```bash
cd cmdb-web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **启动前端**
```bash
cd cmdb-web/frontend
npm install
npm run dev
```

3. **访问应用**
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### Docker 部署

```bash
cd cmdb-web
docker-compose up --build
```

## Agent Harness 技术

本项目展示了如何使用 Agent Harness 技术进行高效的全栈开发：

### 核心技术要点

1. **Page Object 模式**: 将页面元素和操作封装为页面对象类，提高测试代码可维护性
2. **数据工厂模式**: 使用工厂方法生成测试数据，统一数据格式
3. **MSW Mock 服务**: 拦截网络请求，提供可控的测试数据
4. **CI/CD 集成**: 配置文件已准备好 GitHub Actions 工作流

### 相关文档

- [AGENTS.md](./.claude/skills/harness-ai-agent-skill/references/agents/implementation-guide.md) - Agent 实现指南
- [前端工程标准](./.claude/skills/harness-ai-agent-skill/references/frontend/engineering-standards.md) - 前端开发规范
- [测试指南](./cmdb-web/frontend/tests/e2e/TESTING_GUIDE.md) - E2E 测试指南

## 项目文档

本项目包含完整的开发文档，涵盖从需求分析到测试验证的完整流程。

| 文档 | 说明 | 关键内容 |
|------|------|----------|
| [API 规范](./cmdb-web/docs/api-spec.md) | 后端 API 接口规范 | 认证接口(/auth)、配置项接口(/cis)、用户接口(/users)、变更管理、审计日志等 20+ API 端点，包含完整的请求/响应示例和错误码定义 |
| [架构设计](./cmdb-web/docs/architecture.md) | 系统架构和设计决策 | 分层架构设计（前端/API/服务/数据访问层）、目录结构、核心模块设计（JWT认证、配置项多态、RBAC权限）、部署架构和安全设计 |
| [数据模型](./cmdb-web/docs/data-model.md) | 数据库表结构和关系 | 配置项模型、用户模型、关系模型、变更模型、审计日志模型，包含 ER 图和字段说明 |
| [前端设计](./cmdb-web/docs/frontend-design.md) | 前端界面设计说明 | 页面布局、组件设计、状态管理、路由设计、API 调用封装 |
| [权限矩阵](./cmdb-web/docs/rbac-matrix.md) | 角色权限对照表 | 用户角色定义、功能权限矩阵、页面访问权限、API 操作权限 |
| [需求规格](./cmdb-web/docs/requirements.md) | 功能需求详细说明 | 需求背景、功能需求清单、非功能性需求、用户故事和验收标准 |
| [测试计划](./cmdb-web/docs/test-plan.md) | 测试策略和用例 | 测试范围、测试策略、功能测试用例、集成测试策略、E2E 测试规划 |

### 文档亮点

- **API 规范**: 提供 8 大模块 20+ API 端点，包含完整的请求/响应示例和错误码定义
- **架构设计**: 采用分层架构，支持多态配置项模型，展示完整的系统设计决策过程
- **数据模型**: 详细的数据库表结构设计，包含配置项主表+子表的多态设计
- **测试计划**: 包含 30+ 测试用例，涵盖功能测试、集成测试和 E2E 测试

## 许可证

MIT License
