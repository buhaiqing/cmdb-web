# CMDB 系统测试计划

## 1. 测试概述

### 1.1 测试目标
- 验证 CMDB 系统所有核心功能正常工作
- 确保 UI 自动化测试覆盖所有关键用户流程
- 建立持续集成测试机制
- 提供可靠的测试报告和问题追踪

### 1.2 测试范围
| 模块 | 测试类型 | 优先级 |
|------|----------|--------|
| 认证模块 | E2E、单元测试 | P0 |
| 配置项管理 | E2E、集成测试 | P0 |
| 关系管理 | E2E、集成测试 | P1 |
| 变更管理 | E2E、集成测试 | P1 |
| 用户管理 | E2E、单元测试 | P1 |
| 权限管理 | E2E、单元测试 | P1 |
| 报表统计 | E2E | P2 |
| 自动发现 | 集成测试 | P2 |

### 1.3 测试环境
| 环境 | 用途 | 访问地址 |
|------|------|----------|
| 本地开发 | 开发测试 | http://localhost:3000 |
| 测试环境 | 集成测试 | http://test-cmdb.example.com |
| 预发布环境 | 回归测试 | http://staging-cmdb.example.com |

---

## 2. 测试用例设计

### 2.1 认证模块测试用例

| 用例 ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| AUTH-001 | 正常登录 | 1. 打开登录页 2. 输入用户名密码 3. 点击登录 | 登录成功，跳转到首页 | P0 |
| AUTH-002 | 密码错误登录 | 1. 打开登录页 2. 输入用户名和错误密码 3. 点击登录 | 显示错误提示，停留在登录页 | P0 |
| AUTH-003 | 空用户名登录 | 1. 打开登录页 2. 不输入用户名 3. 点击登录 | 显示用户名必填验证 | P0 |
| AUTH-004 | 空密码登录 | 1. 打开登录页 2. 不输入密码 3. 点击登录 | 显示密码必填验证 | P0 |
| AUTH-005 | Token 过期处理 | 1. 登录后等待 Token 过期 2. 访问需要认证的页面 | 自动跳转到登录页 | P1 |
| AUTH-006 | 登出功能 | 1. 登录后点击登出 | 成功登出，跳转到登录页 | P1 |
| AUTH-007 | 未登录访问 | 1. 直接访问需要认证的页面 | 重定向到登录页 | P0 |

### 2.2 配置项管理测试用例

| 用例 ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| CI-001 | 创建服务器 CI | 1. 进入创建页面 2. 填写服务器信息 3. 提交 | 创建成功，显示详情页 | P0 |
| CI-002 | 必填字段验证 | 1. 进入创建页面 2. 不填必填字段 3. 提交 | 显示必填字段验证错误 | P0 |
| CI-003 | 查看 CI 列表 | 1. 进入列表页 | 正确显示 CI 列表和分页 | P0 |
| CI-004 | CI 搜索 | 1. 在列表页输入搜索条件 2. 点击搜索 | 显示筛选后的结果 | P0 |
| CI-005 | 查看 CI 详情 | 1. 在列表页点击某 CI | 显示完整的 CI 详情 | P0 |
| CI-006 | 编辑 CI | 1. 进入编辑页 2. 修改字段 3. 保存 | 修改成功，显示更新后的数据 | P0 |
| CI-007 | 删除 CI | 1. 点击删除按钮 2. 确认删除 | 删除成功，列表中不再显示 | P0 |
| CI-008 | 批量导入 | 1. 上传导入文件 2. 确认导入 | 导入成功，显示导入结果 | P1 |
| CI-009 | 批量导出 | 1. 选择导出条件 2. 点击导出 | 下载 Excel/CSV 文件 | P1 |
| CI-010 | 列表分页 | 1. 切换到其他页码 | 正确显示对应页的数据 | P1 |

### 2.3 关系管理测试用例

| 用例 ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| REL-001 | 创建关系 | 1. 进入 CI 详情 2. 点击添加关系 3. 选择目标 CI 和关系类型 | 关系创建成功 | P0 |
| REL-002 | 查看关系图 | 1. 进入关系图页面 | 正确显示 CI 关系图 | P0 |
| REL-003 | 删除关系 | 1. 选择关系 2. 点击删除 | 关系删除成功 | P1 |
| REL-004 | 关系类型选择 | 1. 创建关系时选择不同类型 | 所有关系类型可选 | P1 |

### 2.4 变更管理测试用例

| 用例 ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| CHG-001 | 提交变更申请 | 1. 进入变更页面 2. 填写变更信息 3. 提交 | 变更申请提交成功 | P0 |
| CHG-002 | 查看变更列表 | 1. 进入变更列表页 | 正确显示变更列表 | P0 |
| CHG-003 | 查看变更详情 | 1. 点击某个变更 | 显示完整的变更详情和对比 | P0 |
| CHG-004 | 审批变更 | 1. 审批人登录 2. 进入变更详情 3. 点击批准 | 变更状态变为已批准 | P1 |
| CHG-005 | 拒绝变更 | 1. 审批人登录 2. 进入变更详情 3. 点击拒绝 | 变更状态变为已拒绝 | P1 |
| CHG-006 | 变更历史查看 | 1. 进入 CI 详情页 | 显示该 CI 的所有变更记录 | P1 |

### 2.5 权限管理测试用例

| 用例 ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| RBAC-001 | 管理员访问所有功能 | 1. 使用管理员账号登录 2. 访问各功能页面 | 所有页面和功能可访问 | P0 |
| RBAC-002 | 运维工程师权限 | 1. 使用运维工程师账号登录 | 可创建/编辑 CI，不能删除 | P0 |
| RBAC-003 | 只读用户权限 | 1. 使用只读用户账号登录 | 只能查看，不能修改 | P0 |
| RBAC-004 | 审计员权限 | 1. 使用审计员账号登录 | 可查看 CI 和审计日志 | P0 |
| RBAC-005 | 越权访问阻止 | 1. 使用低权限账号 2. 尝试访问高权限功能 | 显示权限不足提示 | P0 |

---

## 3. Playwright 测试配置

### 3.1 Playwright 配置文件

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  outputDir: 'test-results/',
})
```

### 3.2 测试工具函数

```typescript
// tests/utils/test-helpers.ts
import { Page, expect } from '@playwright/test'

export async function login(page: Page, username: string, password: string) {
  await page.goto('/login')
  await page.fill('[data-testid="login-username"]', username)
  await page.fill('[data-testid="login-password"]', password)
  await page.click('[data-testid="login-submit"]')
  await page.waitForURL('/dashboard')
}

export async function logout(page: Page) {
  await page.click('[data-testid="user-menu"]')
  await page.click('[data-testid="logout-btn"]')
  await page.waitForURL('/login')
}

export async function createCi(page: Page, ciData: any) {
  await page.click('[data-testid="ci-create-btn"]')

  if (ciData.name) {
    await page.fill('[data-testid="ci-name-input"]', ciData.name)
  }
  if (ciData.ci_type) {
    await page.selectOption('[data-testid="ci-type-select"]', ciData.ci_type)
  }
  if (ciData.code) {
    await page.fill('[data-testid="ci-code-input"]', ciData.code)
  }

  await page.click('[data-testid="ci-submit-btn"]')
  await expect(page.locator('[data-testid="ci-detail"]')).toBeVisible()
}

export async function searchCi(page: Page, keyword: string) {
  await page.fill('[data-testid="ci-search-keyword"]', keyword)
  await page.click('[data-testid="search-submit"]')
  await page.waitForSelector('[data-testid="ci-data-table"]')
}
```

### 3.3 认证模块测试

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('认证模块', () => {
  test('AUTH-001: 正常登录', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="login-username"]', 'admin')
    await page.fill('[data-testid="login-password"]', 'password123')
    await page.click('[data-testid="login-submit"]')

    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })

  test('AUTH-002: 密码错误登录', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="login-username"]', 'admin')
    await page.fill('[data-testid="login-password"]', 'wrongpassword')
    await page.click('[data-testid="login-submit"]')

    await expect(page.locator('.el-message--error')).toBeVisible()
    await expect(page).toHaveURL('/login')
  })

  test('AUTH-003: 空用户名登录', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="login-password"]', 'password123')
    await page.click('[data-testid="login-submit"]')

    await expect(page.locator('.el-form-item__error')).toContainText('用户名')
  })

  test('AUTH-004: 空密码登录', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="login-username"]', 'admin')
    await page.click('[data-testid="login-submit"]')

    await expect(page.locator('.el-form-item__error')).toContainText('密码')
  })

  test('AUTH-005: Token 过期处理', async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('[data-testid="login-username"]', 'admin')
    await page.fill('[data-testid="login-password"]', 'password123')
    await page.click('[data-testid="login-submit"]')

    // 模拟 Token 过期
    await page.evaluate(() => {
      localStorage.setItem('token', 'expired_token')
    })
    await page.reload()

    await expect(page).toHaveURL('/login')
  })

  test('AUTH-006: 登出功能', async ({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('[data-testid="login-username"]', 'admin')
    await page.fill('[data-testid="login-password"]', 'password123')
    await page.click('[data-testid="login-submit"]')

    // 登出
    await page.click('[data-testid="user-menu"]')
    await page.click('[data-testid="logout-btn"]')

    await expect(page).toHaveURL('/login')
  })

  test('AUTH-007: 未登录访问', async ({ page }) => {
    await page.goto('/ci/list')
    await expect(page).toHaveURL('/login')
  })
})
```

### 3.4 配置项管理测试

```typescript
// tests/e2e/ci.spec.ts
import { test, expect } from '@playwright/test'
import { login, logout, createCi } from '../utils/test-helpers'

test.describe('配置项管理', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin', 'password123')
  })

  test('CI-001: 创建服务器 CI', async ({ page }) => {
    await page.goto('/ci/list')

    await page.click('[data-testid="ci-create-btn"]')
    await page.fill('[data-testid="ci-name-input"]', 'test-server-001')
    await page.selectOption('[data-testid="ci-type-select"]', 'server')
    await page.fill('[data-testid="ci-code-input"]', 'SRV-TEST-001')
    await page.selectOption('[data-testid="ci-environment-select"]', 'test')
    await page.fill('[data-testid="ci-owner-input"]', '测试用户')

    await page.click('[data-testid="ci-submit-btn"]')

    await expect(page.locator('[data-testid="ci-detail"]')).toBeVisible()
    await expect(page.locator('[data-testid="ci-basic-info"]')).toContainText('test-server-001')
  })

  test('CI-002: 必填字段验证', async ({ page }) => {
    await page.goto('/ci/create')

    await page.click('[data-testid="ci-submit-btn"]')

    await expect(page.locator('.el-form-item__error')).toBeVisible()
  })

  test('CI-003: 查看 CI 列表', async ({ page }) => {
    await page.goto('/ci/list')

    await expect(page.locator('[data-testid="ci-data-table"]')).toBeVisible()
    await expect(page.locator('[data-testid="data-table-pagination"]')).toBeVisible()
  })

  test('CI-004: CI 搜索', async ({ page }) => {
    await page.goto('/ci/list')

    await page.fill('[data-testid="ci-search-keyword"]', 'server')
    await page.click('[data-testid="search-submit"]')

    await expect(page.locator('[data-testid="ci-data-table"] tbody tr')).toHaveCount({ min: 1 })
  })

  test('CI-005: 查看 CI 详情', async ({ page }) => {
    await page.goto('/ci/list')

    await page.click('[data-testid="ci-view-btn"]:first')

    await expect(page.locator('[data-testid="ci-basic-info"]')).toBeVisible()
    await expect(page.locator('[data-testid="ci-attributes"]')).toBeVisible()
  })

  test('CI-006: 编辑 CI', async ({ page }) => {
    await page.goto('/ci/list')

    const firstCiName = await page.locator('[data-testid="ci-name-cell"]:first').textContent()
    await page.click('[data-testid="ci-edit-btn"]:first')

    const newName = `edited-${firstCiName}`
    await page.fill('[data-testid="ci-name-input"]', newName)
    await page.click('[data-testid="ci-submit-btn"]')

    await expect(page.locator('[data-testid="ci-detail"]')).toContainText(newName)
  })

  test('CI-007: 删除 CI', async ({ page }) => {
    await page.goto('/ci/list')

    // 先创建一个测试 CI
    await page.click('[data-testid="ci-create-btn"]')
    await page.fill('[data-testid="ci-name-input"]', 'to-delete-ci')
    await page.selectOption('[data-testid="ci-type-select"]', 'server')
    await page.fill('[data-testid="ci-code-input"]', 'DELETE-001')
    await page.click('[data-testid="ci-submit-btn"]')

    // 返回列表并删除
    await page.goto('/ci/list')
    await page.click('[data-testid="ci-delete-btn"]:has-text("to-delete-ci")')

    // 确认删除
    await page.click('.el-button--danger:has-text("确定")')

    await expect(page.locator('.el-message--success')).toContainText('删除成功')
  })
})
```

### 3.5 权限管理测试

```typescript
// tests/e2e/rbac.spec.ts
import { test, expect } from '@playwright/test'
import { login, logout } from '../utils/test-helpers'

test.describe('权限管理', () => {
  test('RBAC-001: 管理员访问所有功能', async ({ page }) => {
    await login(page, 'admin', 'password123')

    // 测试各菜单可访问
    await page.goto('/ci/list')
    await expect(page.locator('[data-testid="ci-create-btn"]')).toBeVisible()

    await page.goto('/system/user')
    await expect(page).toHaveURL('/system/user')

    await page.goto('/system/role')
    await expect(page).toHaveURL('/system/role')

    await page.goto('/system/audit')
    await expect(page).toHaveURL('/system/audit')
  })

  test('RBAC-002: 运维工程师权限', async ({ page }) => {
    await login(page, 'ops_user', 'password123')

    await page.goto('/ci/list')
    await expect(page.locator('[data-testid="ci-create-btn"]')).toBeVisible()

    // 运维工程师应该有编辑权限，但没有删除权限（或需要审批）
    await expect(page.locator('[data-testid="ci-edit-btn"]:first')).toBeVisible()
  })

  test('RBAC-003: 只读用户权限', async ({ page }) => {
    await login(page, 'readonly_user', 'password123')

    await page.goto('/ci/list')

    // 只读用户不应该看到创建、编辑、删除按钮
    await expect(page.locator('[data-testid="ci-create-btn"]')).not.toBeVisible()
    await expect(page.locator('[data-testid="ci-edit-btn"]')).not.toBeVisible()
    await expect(page.locator('[data-testid="ci-delete-btn"]')).not.toBeVisible()

    // 但可以查看详情
    await expect(page.locator('[data-testid="ci-view-btn"]:first')).toBeVisible()
  })

  test('RBAC-004: 审计员权限', async ({ page }) => {
    await login(page, 'auditor', 'password123')

    await page.goto('/system/audit')
    await expect(page).toHaveURL('/system/audit')

    // 审计员可以查看审计日志
    await expect(page.locator('[data-testid="audit-table"]')).toBeVisible()
  })

  test('RBAC-005: 越权访问阻止', async ({ page }) => {
    await login(page, 'readonly_user', 'password123')

    // 尝试直接访问需要权限的页面
    await page.goto('/system/user')

    // 应该显示权限不足或被重定向
    await expect(page.locator('.el-message--error')).toContainText('权限')
  })
})
```

---

## 4. 测试执行策略

### 4.1 测试分组

| 分组名称 | 测试标签 | 执行时机 |
|----------|----------|----------|
| 冒烟测试 | @smoke | 每次提交后 |
| 回归测试 | @regression | 每日构建 |
| 认证测试 | @auth | 认证模块变更后 |
| CI 测试 | @ci | CI 模块变更后 |
| 权限测试 | @rbac | 权限模块变更后 |
| 全量测试 | @all | 发布前 |

### 4.2 执行命令

```bash
# 运行所有测试
npx playwright test

# 运行冒烟测试
npx playwright test --grep @smoke

# 运行特定项目的测试
npx playwright test auth
npx playwright test ci
npx playwright test rbac

# 运行特定浏览器
npx playwright test --project=chromium

# 调试模式
npx playwright test --debug

# 生成报告
npx playwright show-report
```

### 4.3 CI/CD 集成

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Install Playwright
        run: |
          cd frontend
          npx playwright install --with-deps

      - name: Build application
        run: |
          cd frontend
          npm run build

      - name: Run Playwright tests
        run: |
          cd frontend
          npx playwright test

      - name: Upload test report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
          retention-days: 30
```

---

## 5. 测试报告

### 5.1 HTML 报告

Playwright 自动生成 HTML 报告，包含：
- 测试用例执行结果
- 失败用例截图和视频
- 执行时间统计
- 浏览器分布

```bash
# 查看报告
npx playwright show-report
```

### 5.2 报告结构

```
test-results/
├── results.json              # JSON 格式结果
├── junit.xml                 # JUnit 格式结果
└── playwright-report/        # HTML 报告
    ├── index.html
    ├── data/
    └── images/
```

---

## 6. 问题追踪机制

### 6.1 失败用例分析

当测试失败时，Playwright 自动：
1. 截取失败时的屏幕截图
2. 录制失败前的操作视频
3. 生成详细的错误日志

### 6.2 问题分类

| 问题类型 | 说明 | 处理方式 |
|----------|------|----------|
| 功能缺陷 | 功能未按预期工作 | 提交 Bug 到问题追踪系统 |
| 测试脚本问题 | 测试脚本错误或脆弱 | 修复测试脚本 |
| 环境问题 | 测试环境配置问题 | 修复环境配置 |
| 数据问题 | 测试数据缺失或错误 | 修复测试数据 |

### 6.3 问题追踪流程

```
测试失败
    ↓
分析失败原因（查看截图/视频/日志）
    ↓
分类问题类型
    ↓
功能缺陷 → 提交 Jira/Bugzilla
测试问题 → 修复测试脚本
环境问题 → 通知运维团队
    ↓
跟踪问题状态
    ↓
验证修复
```

---

## 7. 测试覆盖度目标

| 测试类型 | 覆盖度目标 |
|----------|------------|
| 核心功能 E2E | 100% |
| API 集成测试 | 90% |
| 单元测试 | 80% |

---

## 8. 测试维护

### 8.1 测试脚本维护
- 定期审查测试脚本
- 更新过期的选择器
- 优化测试执行时间

### 8.2 测试数据维护
- 定期清理测试数据
- 使用测试数据工厂
- 确保测试数据隔离
