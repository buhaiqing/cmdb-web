# Full-Stack App 示例

> 基于 Harness AI Agent Skill 构建的全栈应用示例

## 项目结构

```
fullstack-app/
├── backend/                    # Python FastAPI 后端
│   ├── src/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── agents/            # AI Agent 集成
│   ├── tests/
│   ├── alembic/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                   # React 19 前端
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── lib/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── .harness/                   # Harness 配置
│   ├── pipelines/
│   └── triggers/
├── docker-compose.yml
└── README.md
```

## 快速开始

### 1. 本地开发

```bash
# 启动依赖服务
docker-compose up -d postgres redis

# 后端
cd backend
poetry install
poetry run uvicorn src.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### 2. 使用 Harness Pipeline

```bash
# 提交代码触发 CI
gh pr create --title "Feature: Add AI review integration"

# Pipeline 将自动执行:
# 1. AI 代码审查
# 2. 安全扫描
# 3. 单元测试
# 4. 构建镜像
# 5. 部署到 Staging
```

## AI Agent 集成点

### 代码审查
- 自动 PR Review
- 类型检查
- 安全扫描

### 部署决策
- 风险评估
- 金丝雀配置建议
- 自动回滚

### 故障处理
- 告警分析
- 根因定位
- 自动修复

## 参考文档

- [前端规范](../../references/frontend/engineering-standards.md)
- [后端规范](../../references/backend/python-standards.md)
- [Pipeline 模板](../../references/harness/pipeline-templates.md)
