# Harness AI Agent Skill

> **2026 Edition** - AI 驱动的全栈工程最佳实践  
> **Governance**: [Harness Governance](https://developer.harness.io/docs/category/governance)

---

## 概述

本 Skill 提供了一套完整的 **AGENTS.md + Harness Engineering** 融合方案，涵盖：

- 🤖 **AI Agent 智能体**: 代码审查、部署建议、故障处理
- 🚀 **Harness 平台集成**: CI/CD、GitOps、Feature Flags、SRM
- 📋 **前后端规范**: React 19 + Python 3.12 最佳实践
- 🔒 **治理与合规**: Policy as Code、安全扫描、审计追踪

---

## 目录结构

```
harness-ai-agent-skill/
├── AGENTS.md                          # 核心规范 (精简版)
├── README.md                          # 本文件
├── references/                        # 详细参考文档
│   ├── frontend/
│   │   └── engineering-standards.md   # 前端工程化规范
│   ├── backend/
│   │   └── python-standards.md        # Python 后端规范
│   ├── harness/
│   │   └── pipeline-templates.md      # Harness Pipeline 模板
│   └── agents/
│       └── implementation-guide.md    # Agent 实现指南
├── templates/                         # 可复用模板
│   ├── pipelines/
│   │   ├── ci-pipeline.yml            # CI Pipeline
│   │   └── cd-pipeline.yml            # CD Pipeline (含 AI)
│   └── configs/
│       └── gitops-config.yml          # GitOps 配置
└── examples/                          # 示例项目
    └── fullstack-app/
        └── README.md
```

---

## 快速开始

### 1. 复制 AGENTS.md 到你的项目

```bash
cp AGENTS.md /your-project/AGENTS.md
```

### 2. 配置 Harness Pipeline

```bash
# 复制 CI/CD Pipeline 模板
cp templates/pipelines/*.yml /your-project/.harness/pipelines/

# 根据项目调整配置
# - 修改 connectorRef
# - 调整镜像名称
# - 配置环境变量
```

### 3. 部署 AI Agent 服务

```bash
# 参考 agents/implementation-guide.md
cd agents/
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 核心特性

### AI Agent 矩阵

| Agent | 功能 | Harness 集成 |
|-------|------|--------------|
| **CodeReviewer** | 代码审查、规范检查 | STO (Security Testing) |
| **DeployAdvisor** | 风险评估、金丝雀配置 | CD Pipeline + Feature Flags |
| **IncidentHandler** | 故障诊断、自动回滚 | CCM + SRM (Service Reliability) |
| **CostOptimizer** | 资源优化建议 | CCM (Cloud Cost Management) |

### 2026 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | React + TypeScript | 19 + 5.5 |
| 后端 | Python FastAPI | 3.12+ |
| 构建 | Vite | 6.x |
| 部署 | Harness CD + GitOps | Latest |
| 观测 | OpenTelemetry | v1.0+ |

---

## 使用指南

### 场景 1: 代码提交触发 AI 审查

```yaml
# .harness/pipelines/ci.yml
steps:
  - step:
      name: AI Code Review
      type: Run
      spec:
        command: |
          curl -X POST http://ai-agent:8000/review/code \
            -H "Content-Type: application/json" \
            -d @<(echo '{"file_path": "src/main.py", "content": "..."}')
```

### 场景 2: 部署前风险评估

```yaml
# 在 CD Pipeline 中添加
steps:
  - step:
      name: AI Risk Assessment
      type: Run
      spec:
        command: |
          python -m agents.deploy_advisor analyze \
            --service myapp \
            --environment production
```

### 场景 3: 故障自动处理

```python
# 在告警 Webhook 中调用
@app.post("/webhook/alert")
async def handle_alert(alert: Alert):
    agent = IncidentHandlerAgent(harness_client, llm_client)
    result = await agent.execute(IncidentContext(
        service=alert.service,
        alert_name=alert.name,
        severity=alert.severity,
        description=alert.description,
    ))
    
    if result.data.get("should_rollback"):
        await trigger_rollback(alert.service)
```

---

## 治理与合规

### Policy as Code (OPA)

```rego
# 示例: 禁止无 AI 审查的部署
deny[msg] {
    input.pipeline.stages[_].type == "Deployment"
    not input.pipeline.stages[_].spec.execution.steps[_].identifier == "ai_code_review"
    msg := "Pipeline must include AI code review step"
}
```

### 安全红线

- ✅ 密钥管理: 使用 Harness Secrets
- ✅ 镜像扫描: Trivy 集成
- ✅ 依赖审计: Snyk + pip-audit
- ✅ 访问控制: RBAC + 审批流

---

## 参考链接

- [Harness Governance](https://developer.harness.io/docs/category/governance)
- [前端规范详情](./references/frontend/engineering-standards.md)
- [后端规范详情](./references/backend/python-standards.md)
- [Pipeline 模板详情](./references/harness/pipeline-templates.md)
- [Agent 实现详情](./references/agents/implementation-guide.md)

---

## 贡献

欢迎提交 Issue 和 PR 来完善本 Skill。

---

**Version**: 2026.1  
**Maintainer**: Platform Engineering Team
