---
name: harness-ai-agent
description: "提供AI驱动的全栈工程最佳实践，深度融合AGENTS.md规范与Harness Engineering平台能力。在需要AI代码审查、部署风险评估、故障自动处理、智能测试时调用本Skill。支持动态生成项目规范文档、多Agent协作编排、人工确认网关等核心能力。"
---

# Harness AI Agent Skill

> **Version**: 2026.1  
> **Frameworks**: Python (FastAPI) | Go (Gin/Echo) | Rust (Axum/Actix) + React 19

---

## 1. 愿景与目标

### 1.1 核心愿景

构建AI驱动的全栈工程体系，实现：

- **AI自主工程能力** - 让AI承担可自动化的代码审查、测试生成、部署决策等工程任务
- **人机协作开发流程** - AI提供建议和执行，人类进行关键决策和确认
- **多Agent协同工作** - 协调多个AI Agent协同处理复杂工程任务
- **可观测可审计** - 所有AI决策可追溯、可审计、可优化
- **UI自动化测试原生支持** - 所有生成的UI代码自动包含完整的测试标识符

### 1.2 Harness平台核心价值

Harness不仅是CI/CD工具，更是**AI Agent的基础设施底座**：

| Harness能力 | 对AI Agent的支撑 |
|-------------|------------------|
| **Pipeline** | Agent执行编排器 |
| **SRM** | Agent决策数据底座 |
| **GitOps** | Agent配置管理 |
| **STO** | 安全扫描结果 |
| **CCM** | 成本分析数据 |
| **Policy** | Agent行为约束 |
| **Approval** | 人工确认网关 |

### 1.3 设计原则

1. **AI优先** - 优先让AI承担重复性、规则明确的工程任务
2. **人机协作** - AI建议，人类决策；关键操作必须人工确认
3. **渐进增强** - 从简单任务逐步扩展到复杂场景
4. **可观测性** - 所有AI决策需记录置信度、推理过程和执行结果
5. **技术中立** - 支持多种编程语言和框架
6. **测试原生** - 所有UI代码必须包含data-testid

---

## 2. 核心能力需求

### 2.1 能力矩阵

| 能力ID | 能力名称 | 目标描述 | 约束条件 |
|--------|----------|----------|----------|
| CAP-001 | 需求分析 | AI解析自然语言需求，生成工程规范、验收标准、API契约 | 需人工审查确认 |
| CAP-002 | 代码生成 | AI根据需求规范生成代码实现 | 生成代码需符合规范；复杂逻辑需人工审查 |
| CAP-003 | 代码审查 | AI自动分析代码质量、安全性、规范性 | 支持Python/Go/Rust；响应时间<30s |
| CAP-004 | 智能测试 | AI生成测试用例，自动维护测试 | 低置信度测试用例需人工审查 |
| CAP-005 | 部署建议 | AI评估部署风险，推荐部署策略 | 高风险部署必须人工确认 |
| CAP-006 | 故障处理 | AI诊断故障根因，推荐修复方案 | 自动修复需人工确认 |
| CAP-007 | 成本优化 | AI分析资源利用率，提供成本优化建议 | 涉及资源删除需人工确认 |
| CAP-008 | Agent编排 | 协调多Agent协作执行复杂工作流 | 支持任务依赖、并行执行 |
| CAP-009 | 规范生成 | 根据项目配置动态生成AGENTS.md | 支持多语言、多框架配置 |
| CAP-010 | UI自动化测试生成 | 基于UI组件自动生成Playwright E2E测试用例 | 必须包含data-testid验证 |

### 2.2 非功能需求

#### NFR-001: 性能要求

- 代码审查响应时间 < 30秒（1000行代码）
- 部署风险评估响应时间 < 10秒
- UI自动化测试生成响应时间 < 30秒（单个页面）

#### NFR-002: 可靠性要求

- AI服务可用性 > 99.9%
- UI测试稳定性 > 95%（避免 flaky tests）

#### NFR-003: 安全要求

**置信度驱动的自动化分级策略**：

| 置信度范围 | 风险等级 | 执行策略 |
|------------|----------|----------|
| ≥ 0.95 | 低 | **自动执行** |
| 0.85 ~ 0.95 | 中 | **通知后执行**（5分钟撤销窗口） |
| < 0.85 | 高 | **强制确认** |
| 任意 | 关键操作 | **强制确认**（生产部署、数据删除等） |

---

## 3. UI自动化测试强制规范

### 3.1 data-testid 强制规则

**⚠️ 强制性规则：所有UI代码必须包含data-testid属性**

#### 必须添加data-testid的元素

| 元素类型 | data-testid格式 |
|----------|-----------------|
| 页面容器 | `page-{page-name}` |
| 表单 | `form-{form-name}` |
| 输入框 | `input-{context}-{field}` |
| 按钮 | `button-{context}-{action}` |
| 下拉菜单 | `select-{context}-{field}` |
| 表格 | `table-{entity}-list` |
| 表格行 | `table-row-{entity}-${index}` |
| 对话框 | `dialog-{entity}-{action}` |
| 导航菜单 | `menu-item-{entity}` |

#### 命名规范

```
格式: {组件类型}-{上下文}-{功能}

组件类型: page | form | input | button | select | table | dialog | menu

示例:
- input-login-username
- button-ci-create
- table-ci-list
- dialog-user-edit
```

#### 数组/列表渲染规范（关键）

**必须同时提供索引和ID两种标识符**：

```tsx
// ✅ 正确实现
{users.map((user, index) => (
  <tr 
    key={user.id}
    data-testid={`table-row-user-${index}`}        // 索引标识
    data-user-id={user.id}                          // 数据ID
  >
    <td data-testid={`cell-user-name-${user.id}`}>{user.name}</td>
    <td>
      <button data-testid={`button-user-edit-${user.id}`}>编辑</button>
    </td>
  </tr>
))}
```

### 3.2 前端代码生成强制检查清单

- [ ] **所有交互元素**都有data-testid
- [ ] **所有表单**都有data-testid标识
- [ ] **所有表格**都有data-testid，且每行都有索引标识
- [ ] **数组渲染**同时提供索引和ID两种标识符
- [ ] **命名符合规范**（组件类型-上下文-功能）

### 3.3 UI自动化测试最佳实践

#### Mock服务选择

```
✅ 推荐：Playwright Route Interception
❌ 不推荐：MSW (与Playwright隔离环境不兼容)
```

#### 登录状态验证规范

```typescript
// ✅ 正确实现
async waitForLoginSuccess(): Promise<void> {
  await this.page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 10000 })
  await this.page.waitForLoadState('networkidle', { timeout: 10000 })
  await this.page.waitForSelector('[data-testid="header-username"]', { timeout: 10000 })
}
```

#### 选择器优先级

```
1. data-testid 属性（最稳定，强制要求）
2. role + name 组合
3. CSS类名
4. XPath（最后手段）
5. 文本内容（不推荐）
```

#### 下拉选项选择规范

```typescript
// ✅ 使用显示文本（label）
await selectElementOption('[data-testid="ci-form-type"]', '服务器')

// ❌ 使用值（value）- 会导致选择失败
await selectElementOption('[data-testid="ci-form-type"]', 'server')
```

---

## 4. 人机协作规范

### 4.1 必须人工确认的场景

1. **AI决策置信度 < 0.85**
2. **生产环境部署操作**
3. **自动回滚操作**
4. **数据库Schema变更**
5. **安全策略修改**
6. **成本优化建议涉及资源删除**
7. **跨服务依赖变更**
8. **UI自动化测试覆盖率 < 80%**

### 4.2 可AI自主执行的场景

1. **开发/测试环境代码审查**
2. **测试用例生成（置信度 > 0.9）**
3. **低风险配置变更**
4. **监控告警通知发送**
5. **文档自动生成**
6. **data-testid自动添加（置信度 > 0.95）**

---

## 5. 输入/输出规范

### 5.1 统一输入格式

```json
{
  "request_id": "uuid",
  "timestamp": "ISO8601",
  "context": {
    "project": "project-name",
    "environment": "dev|staging|prod",
    "trigger": "manual|webhook|scheduled"
  },
  "payload": { }
}
```

### 5.2 统一输出格式

```json
{
  "request_id": "uuid",
  "status": "success|partial|failure",
  "confidence": 0.0-1.0,
  "result": { },
  "reasoning": "AI决策推理过程摘要",
  "requires_approval": true|false,
  "suggested_action": "描述建议的下一步操作"
}
```

### 5.3 错误码体系

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| AGENT-001 | AI服务不可用 | 重试或降级到人工处理 |
| AGENT-002 | 置信度不足 | 触发人工确认流程 |
| AGENT-006 | data-testid缺失 | 返回缺失列表，要求补充 |
| AGENT-007 | UI测试失败 | 返回失败截图和日志 |

---

## 6. 技术栈支持

### 6.1 后端技术栈（三选一）

| 语言 | 框架 | 版本要求 |
|------|------|----------|
| Python | FastAPI | 3.12+ |
| Go | Gin/Echo | 1.22+ |
| Rust | Axum/Actix | 1.75+ |

### 6.2 前端技术栈

- **框架**: React 19
- **语言**: TypeScript 5.x
- **构建**: Vite 5.x
- **样式**: Tailwind CSS
- **UI组件**: Element Plus / Ant Design / shadcn/ui

### 6.3 自动化测试技术栈

- **E2E框架**: Playwright
- **Mock方案**: Playwright Route Interception
- **测试模式**: Page Object Model
- **数据工厂**: Factory Pattern

---

## 7. 验收标准

### 7.1 功能验收标准

- **CAP-010 UI自动化测试生成**: E2E测试生成有效率 > 80%，data-testid覆盖率 100%

### 7.2 质量验收标准

- **所有交互元素均具备唯一的data-testid属性**
- **数组类组件实现索引+ID双标识符系统**
- **UI自动化测试通过率 > 95%**
- **无flaky tests**

### 7.3 DORA效能指标目标

| DORA指标 | 基线值 | 目标值 |
|----------|--------|--------|
| **部署频率** | 1-2次/周 | 5-10次/天 |
| **变更前置时间** | 1-2周 | 2-4小时 |
| **变更失败率** | 15-20% | 5-8% |
| **UI自动化测试覆盖率** | 30% | 80% |

---

## 8. 渐进式落地路径

### Phase 1: AI需求分析 + 代码生成 + 代码审查（3-4周）

- 配置需求分析Agent（CAP-001）
- 配置代码生成Agent（CAP-002）
- **建立data-testid强制检查机制**
- **验收标准**: data-testid覆盖率 100%

### Phase 2: 智能测试 + UI自动化测试（3-4周）

- 配置UI自动化测试生成Agent（CAP-010）
- 集成Playwright测试框架
- 建立Page Object Model模式
- **验收标准**: E2E测试通过率 > 95%，无flaky tests

### Phase 3: 部署风险评估 + 故障自动处理（4-6周）

- 配置部署建议Agent（CAP-005）
- 配置故障处理Agent（CAP-006）

### Phase 4: Agent编排 + 规范生成（3-4周）

- 配置Agent编排器（CAP-008）
- 配置规范生成器（CAP-009）

### Phase 5: 全链路优化（持续）

- 基于DORA指标持续优化
- **长期目标**: UI自动化测试覆盖率维持80%以上

---

## 9. 参考文档

### 9.1 实现指南

- [实现指南](./IMPLEMENTATION_GUIDE.md) - 详细实现步骤和代码示例
- [Python后端规范](./references/backend/python-standards.md)
- [Go后端规范](./references/backend/golang-standards.md)
- [Rust后端规范](./references/backend/rust-standards.md)
- [前端规范](./references/frontend/engineering-standards.md)
- [UI自动化测试规范](./references/frontend/ui-automation-standards.md) - **详细实现规范**

### 9.2 模板与配置

- [AGENTS.md模板](./templates/AGENTS.md.j2)
- [Pipeline模板](./references/harness/pipeline-templates.md)
- [UI测试Page Object模板](./templates/page-object.ts.j2)

---

## Compliance

**All rules in this skill are mandatory. Violating any rule is a blocking error.**

**UI自动化测试特别强制规则：**
1. **所有UI代码必须包含data-testid属性**
2. **数组渲染必须同时提供索引和ID标识符**
3. **选择器优先使用data-testid**
4. **Mock服务必须使用Playwright Route Interception**
5. **登录状态验证必须使用URL+元素双重确认**

