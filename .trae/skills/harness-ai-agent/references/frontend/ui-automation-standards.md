# UI自动化测试规范

> **Version**: 2026.1  
> **Framework**: Playwright + TypeScript  
> **Pattern**: Page Object Model + Factory Pattern

---

## 📋 目录

- [1. 核心原则](#1-核心原则)
- [2. data-testid 强制规范](#2-data-testid-强制规范)
- [3. 前端代码生成检查清单](#3-前端代码生成检查清单)
- [4. Playwright 测试最佳实践](#4-playwright-测试最佳实践)
- [5. Page Object Model 规范](#5-page-object-model-规范)
- [6. 数据工厂规范](#6-数据工厂规范)
- [7. API Mock 规范](#7-api-mock-规范)
- [8. 常见UI自动化测试问题及解决方案](#8-常见ui自动化测试问题及解决方案)
- [9. 测试用例编写规范](#9-测试用例编写规范)
- [10. CI/CD 集成](#10-cicd-集成)
- [11. 验收标准](#11-验收标准)
- [📌 快速参考 Cheatsheet](#📌-快速参考-cheatsheet)
- [⚠️ Compliance 强制规则](#⚠️-compliance-强制规则)

---

## ⚠️ Compliance 强制规则

**所有规则均为强制性。违反任何规则都是阻塞性错误 —— 在继续或交付之前必须修复。**

**强制规则摘要：**
1. **所有UI代码必须包含data-testid属性** - 无例外
2. **数组渲染必须同时提供索引和ID标识符** - 确保测试稳定性
3. **选择器优先使用data-testid** - 避免依赖文本内容
4. **Mock服务必须使用Playwright Route Interception** - 不使用MSW
5. **登录状态验证必须使用URL+元素双重确认** - 避免误判
6. **数据工厂必须使用显示文本（label）** - 确保下拉选择成功
7. **Mock数据字段必须使用snake_case** - 与后端API一致

---

## 1. 核心原则

### 1.1 测试原生设计

所有UI代码必须**原生支持自动化测试**，测试不是事后补充，而是开发的一部分。

```
✅ 正确认知：
"我在开发一个登录表单，需要添加data-testid以便测试"

❌ 错误认知：
"先开发功能，测试的事情以后再说"
```

### 1.2 稳定性优先

测试必须稳定可靠，避免 flaky tests（间歇性失败测试）。

| 不稳定因素 | 解决方案 |
|-----------|----------|
| 动态内容 | 使用data-testid而非文本选择器 |
| 异步加载 | 使用waitForSelector而非固定等待 |
| 状态污染 | 每个测试独立登录、独立导航 |
| 时间依赖 | 使用mock时间或相对时间验证 |

---

## 2. data-testid 强制规范

### 2.1 必须添加data-testid的元素

**⚠️ 强制性规则：以下元素类型必须包含data-testid**

| 元素类型 | 示例 | data-testid格式 | 优先级 |
|----------|------|-----------------|--------|
| 页面容器 | 登录页 | `page-{page-name}` | P0 |
| 表单 | 登录表单 | `form-{form-name}` | P0 |
| 输入框 | 用户名输入 | `input-{context}-{field}` | P0 |
| 按钮 | 登录按钮 | `button-{context}-{action}` | P0 |
| 下拉菜单 | 类型选择 | `select-{context}-{field}` | P0 |
| 表格 | 配置项列表 | `table-{entity}-list` | P0 |
| 表格行 | 第i行 | `table-row-{entity}-${index}` | P1 |
| 表格单元格 | 名称列 | `cell-{entity}-{field}-${id}` | P1 |
| 对话框 | 创建配置项 | `dialog-{entity}-{action}` | P0 |
| 导航菜单 | 配置项菜单 | `menu-item-{entity}` | P0 |
| 标签页 | 详情标签 | `tab-{context}-{name}` | P1 |
| 卡片 | 统计卡片 | `card-{context}-{type}` | P1 |
| 列表 | 用户列表 | `list-{entity}` | P1 |
| 列表项 | 用户项 | `list-item-{entity}-${index}` | P1 |
| 链接 | 查看详情 | `link-{context}-{action}` | P1 |
| 图标按钮 | 编辑图标 | `icon-button-{context}-{action}` | P2 |
| 分页器 | 分页组件 | `pagination-{context}` | P1 |
| 搜索框 | 搜索输入 | `search-input-{context}` | P1 |
| 过滤器 | 状态筛选 | `filter-{context}-{field}` | P1 |
| 消息提示 | 成功提示 | `message-{type}` | P1 |

### 2.2 命名规范

```
格式: {组件类型}-{上下文}-{功能/用途}

组件类型（必须）:
- page: 页面容器
- form: 表单
- input: 输入框
- button: 按钮
- select: 下拉选择
- table: 表格
- dialog: 对话框
- menu: 菜单
- tab: 标签页
- card: 卡片
- list: 列表
- item: 列表项
- link: 链接
- icon-button: 图标按钮
- pagination: 分页器
- search-input: 搜索框
- filter: 过滤器
- message: 消息提示

上下文（可选但推荐）:
- login: 登录相关
- ci: 配置项相关
- user: 用户相关
- role: 角色相关
- change: 变更相关
- audit: 审计相关
- dashboard: 仪表盘相关
- header: 头部区域
- sidebar: 侧边栏

功能/用途（必须）:
- submit: 提交
- cancel: 取消
- create: 创建
- edit: 编辑
- delete: 删除
- search: 搜索
- filter: 筛选
- username: 用户名
- password: 密码
- email: 邮箱
- name: 名称
- type: 类型
- status: 状态

示例:
- page-login                  # 登录页面
- form-login                  # 登录表单
- input-login-username        # 登录页用户名输入框
- input-login-password        # 登录页密码输入框
- button-login-submit         # 登录提交按钮
- button-login-cancel         # 登录取消按钮
- table-ci-list               # 配置项列表表格
- table-row-ci-0              # 配置项列表第0行
- cell-ci-name-123            # 配置项ID为123的名称单元格
- button-ci-edit-123          # 编辑配置项ID为123的按钮
- dialog-ci-create            # 创建配置项对话框
- select-ci-type              # 配置项类型选择器
- menu-item-ci                # 配置项菜单项
- search-input-ci             # 配置项搜索框
- filter-ci-status            # 配置项状态筛选器
```

### 2.3 数组/列表渲染规范（关键）

**必须同时提供索引和ID两种标识符**：

```tsx
// ✅ 正确实现 - 同时提供索引和ID标识符
{users.map((user, index) => (
  <tr 
    key={user.id}
    data-testid={`table-row-user-${index}`}        // 索引标识（用于顺序验证）
    data-user-id={user.id}                          // 数据ID（用于业务验证）
  >
    <td data-testid={`cell-user-name-${user.id}`}>{user.name}</td>
    <td data-testid={`cell-user-email-${user.id}`}>{user.email}</td>
    <td>
      <button 
        data-testid={`button-user-edit-${user.id}`}
        onClick={() => editUser(user.id)}
      >
        编辑
      </button>
      <button 
        data-testid={`button-user-delete-${user.id}`}
        onClick={() => deleteUser(user.id)}
      >
        删除
      </button>
    </td>
  </tr>
))}

// ❌ 错误实现 - 缺少data-testid
{users.map((user) => (
  <tr key={user.id}>
    <td>{user.name}</td>
    <td>{user.email}</td>
    <td>
      <button onClick={() => editUser(user.id)}>编辑</button>
      <button onClick={() => deleteUser(user.id)}>删除</button>
    </td>
  </tr>
))}

// ❌ 错误实现 - 只有索引，没有ID
{users.map((user, index) => (
  <tr 
    key={user.id}
    data-testid={`table-row-user-${index}`}
  >
    <td>{user.name}</td>
  </tr>
))}

// ❌ 错误实现 - 只有ID，没有索引
{users.map((user) => (
  <tr 
    key={user.id}
    data-testid={`table-row-user-${user.id}`}
  >
    <td>{user.name}</td>
  </tr>
))}
```

### 2.4 条件渲染处理

条件渲染的元素也需要data-testid：

```tsx
// ✅ 正确实现
{isLoading ? (
  <div data-testid="loading-spinner">加载中...</div>
) : (
  <div data-testid="content-loaded">内容</div>
)}

{error && (
  <div data-testid="error-message">{error}</div>
)}

{items.length === 0 && (
  <div data-testid="empty-state">暂无数据</div>
)}
```

### 2.5 多框架实现示例

#### React 实现

```tsx
import React from 'react'

export const LoginForm: React.FC = () => {
  return (
    <div data-testid="page-login">
      <form data-testid="form-login">
        <input 
          data-testid="input-login-username"
          type="text" 
          placeholder="用户名"
        />
        <input 
          data-testid="input-login-password"
          type="password" 
          placeholder="密码"
        />
        <button 
          data-testid="button-login-submit"
          type="submit"
        >
          登录
        </button>
      </form>
    </div>
  )
}
```

#### Vue 3 实现

```vue
<template>
  <div data-testid="page-login">
    <form data-testid="form-login" @submit.prevent="handleSubmit">
      <input 
        data-testid="input-login-username"
        v-model="username"
        type="text" 
        placeholder="用户名"
      />
      <input 
        data-testid="input-login-password"
        v-model="password"
        type="password" 
        placeholder="密码"
      />
      <button 
        data-testid="button-login-submit"
        type="submit"
      >
        登录
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')

const handleSubmit = () => {
  // 提交逻辑
}
</script>
```

#### Vue 2 实现

```vue
<template>
  <div data-testid="page-login">
    <form data-testid="form-login" @submit.prevent="handleSubmit">
      <input 
        data-testid="input-login-username"
        v-model="username"
        type="text" 
        placeholder="用户名"
      />
      <input 
        data-testid="input-login-password"
        v-model="password"
        type="password" 
        placeholder="密码"
      />
      <button 
        data-testid="button-login-submit"
        type="submit"
      >
        登录
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'LoginForm',
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    handleSubmit() {
      // 提交逻辑
    }
  }
}
</script>
```

---

## 3. 前端代码生成检查清单

**AI生成前端代码时必须执行以下检查**：

### 3.1 基础检查项

- [ ] **所有交互元素**（按钮、输入框、下拉菜单、链接）都有data-testid
- [ ] **所有表单**都有data-testid标识
- [ ] **所有表格**都有data-testid，且每行都有索引标识
- [ ] **所有对话框/模态框**都有data-testid
- [ ] **所有导航菜单项**都有data-testid
- [ ] **数组渲染**同时提供索引和ID两种标识符
- [ ] **页面容器**有page级别的data-testid
- [ ] **命名符合规范**（组件类型-上下文-功能）

### 3.2 高级检查项

- [ ] **条件渲染元素**（loading、error、empty）都有data-testid
- [ ] **分页组件**有data-testid
- [ ] **搜索框**有data-testid
- [ ] **过滤器**有data-testid
- [ ] **消息提示**有data-testid
- [ ] **图标按钮**有data-testid

### 3.3 代码审查检查脚本

```typescript
// 检查data-testid覆盖率
function checkDataTestIdCoverage(component: React.ReactElement): CoverageReport {
  const report: CoverageReport = {
    totalElements: 0,
    elementsWithTestId: 0,
    missingTestIds: [],
    coverage: 0
  }
  
  // 递归遍历组件树
  function traverse(element: React.ReactElement, path: string) {
    if (!element || typeof element !== 'object') return
    
    report.totalElements++
    
    if (element.props?.['data-testid']) {
      report.elementsWithTestId++
    } else if (isInteractiveElement(element)) {
      report.missingTestIds.push({
        path,
        type: element.type,
        suggestion: generateSuggestion(element, path)
      })
    }
    
    // 递归处理子元素
    React.Children.forEach(element.props?.children, (child, index) => {
      traverse(child, `${path}.children[${index}]`)
    })
  }
  
  traverse(component, 'root')
  report.coverage = report.elementsWithTestId / report.totalElements
  
  return report
}
```

---

## 4. Playwright 测试最佳实践

### 4.1 Mock服务选择

```
✅ 推荐：Playwright Route Interception
   - 适用于 E2E 测试
   - 配置灵活，调试方便
   - 与Playwright原生集成
   - 无需额外依赖

❌ 不推荐：MSW (Mock Service Worker)
   - 适用于单元测试/集成测试
   - 与Playwright隔离环境不兼容
   - 需要额外的worker脚本配置
   - 初始化复杂，容易出错
```

### 4.2 登录状态验证规范

```typescript
// ✅ 正确实现
async waitForLoginSuccess(): Promise<void> {
  // 等待URL不再是登录页
  await this.page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 10000 })
  // 等待页面加载完成
  await this.page.waitForLoadState('networkidle', { timeout: 10000 })
  // 验证已登录元素可见
  await this.page.waitForSelector('[data-testid="header-username"]', { timeout: 10000 })
}

// ❌ 错误实现 - 匹配任何URL
async waitForLoginSuccess(): Promise<void> {
  await this.page.waitForURL(/./)  // 匹配任何URL，包括/login
  await this.page.waitForTimeout(2000)  // 不可靠的等待
}

// ❌ 错误实现 - 只等待URL
async waitForLoginSuccess(): Promise<void> {
  await this.page.waitForURL(/\/dashboard/)  // 如果跳转到其他页面会失败
}
```

### 4.3 选择器优先级规范

```
优先级（从高到低）:
1. data-testid 属性（最稳定，强制要求）
   await page.click('[data-testid="button-login-submit"]')

2. role + name 组合（无障碍访问）
   await page.getByRole('button', { name: '登录' }).click()

3. CSS类名（配合语义化命名）
   await page.click('.login-submit-button')

4. XPath（最后手段）
   await page.click('//button[contains(text(), "登录")]')

5. 文本内容（需考虑国际化，不推荐）
   await page.click('text=登录')
```

### 4.4 下拉选项选择规范

```typescript
// ✅ 使用显示文本（label）
await selectElementOption('[data-testid="ci-form-type"]', '服务器')

// ❌ 使用值（value）- 会导致选择失败
await selectElementOption('[data-testid="ci-form-type"]', 'server')

// 实现示例
async selectElementOption(selector: string, value: string): Promise<void> {
  await this.page.click(selector)
  await this.page.waitForTimeout(500)
  
  const dropdown = this.page.locator('.el-select-dropdown:visible').last()
  await dropdown.waitFor({ state: 'visible', timeout: 5000 })
  
  const option = dropdown.locator(`.el-select-dropdown__item:has-text("${value}")`).first()
  await option.click()
}
```

### 4.5 表单验证断言规范

```typescript
// ✅ 处理多个错误元素
await expect(page.locator('.el-form-item__error').first()).toBeVisible()

// 或者验证特定字段的错误
await expect(page.locator('[data-testid="input-login-username"] ~ .el-form-item__error')).toHaveText('请输入用户名')

// ❌ strict mode冲突
await expect(page.locator('.el-form-item__error')).toBeVisible()
// Error: strict mode violation: locator resolved to 2 elements
```

### 4.6 等待策略规范

```typescript
// ✅ 使用waitForSelector等待元素出现
await page.waitForSelector('[data-testid="table-ci-list"]', { timeout: 15000 })

// ✅ 使用waitForLoadState等待页面加载
await page.waitForLoadState('networkidle', { timeout: 10000 })

// ✅ 使用waitForURL等待URL变化
await page.waitForURL(/\/cis/, { timeout: 10000 })

// ❌ 使用固定等待时间
await page.waitForTimeout(2000)  // 不可靠，可能导致测试不稳定
```

### 4.7 测试隔离规范

```typescript
// ✅ 每个测试独立登录
test('CI-001: 创建配置项', async ({ page, loginPage }) => {
  await loginPage.goto()
  await loginPage.login('admin', 'admin123')
  await loginPage.waitForLoginSuccess()
  // ... 测试逻辑
})

// ❌ 依赖fixture的状态（可能导致污染）
test('CI-001: 创建配置项', async ({ authenticatedPage }) => {
  const { page } = authenticatedPage
  // ... 测试逻辑
})
```

---

## 5. Page Object Model 规范

### 5.1 目录结构

```
tests/e2e/
├── pages/
│   ├── index.ts              # 页面导出
│   ├── base.page.ts          # 基础页面对象
│   ├── login.page.ts         # 登录页
│   ├── ci-list.page.ts       # 配置项列表页
│   ├── ci-form.page.ts       # 配置项表单页
│   └── selectors.ts          # 选择器定义
├── fixtures/
│   ├── index.ts              # fixtures定义
│   └── factories.ts          # 数据工厂
├── utils/
│   └── api-mock.ts           # API Mock
└── *.test.ts                 # 测试文件
```

### 5.2 基础页面对象

```typescript
// pages/base.page.ts
import { Page } from '@playwright/test'

export abstract class BasePage {
  constructor(protected page: Page) {}

  async goto(url: string): Promise<void> {
    await this.page.goto(url)
  }

  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle')
  }

  async selectElementOption(selector: string, value: string): Promise<void> {
    await this.page.click(selector)
    await this.page.waitForTimeout(500)
    
    const dropdown = this.page.locator('.el-select-dropdown:visible').last()
    await dropdown.waitFor({ state: 'visible', timeout: 5000 })
    
    const option = dropdown.locator(`.el-select-dropdown__item:has-text("${value}")`).first()
    await option.click()
  }
}
```

### 5.3 具体页面对象

```typescript
// pages/login.page.ts
import { Page } from '@playwright/test'
import { BasePage } from './base.page'

export class LoginPage extends BasePage {
  private readonly selectors = {
    usernameInput: '[data-testid="input-login-username"]',
    passwordInput: '[data-testid="input-login-password"]',
    submitButton: '[data-testid="button-login-submit"]',
    errorMessage: '[data-testid="error-message"]'
  }

  constructor(page: Page) {
    super(page)
  }

  async goto(): Promise<void> {
    await this.page.goto('http://localhost:3000/login')
  }

  async fillUsername(username: string): Promise<void> {
    await this.page.fill(this.selectors.usernameInput, username)
  }

  async fillPassword(password: string): Promise<void> {
    await this.page.fill(this.selectors.passwordInput, password)
  }

  async clickSubmit(): Promise<void> {
    await this.page.click(this.selectors.submitButton)
  }

  async login(username: string, password: string): Promise<void> {
    await this.fillUsername(username)
    await this.fillPassword(password)
    await this.clickSubmit()
  }

  async waitForLoginSuccess(): Promise<void> {
    await this.page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 10000 })
    await this.page.waitForLoadState('networkidle', { timeout: 10000 })
    await this.page.waitForSelector('[data-testid="header-username"]', { timeout: 10000 })
  }

  async getErrorMessage(): Promise<string> {
    const element = this.page.locator(this.selectors.errorMessage)
    await element.waitFor({ state: 'visible' })
    return element.textContent() || ''
  }
}
```

---

## 6. 数据工厂规范

### 6.1 工厂方法定义

```typescript
// fixtures/factories.ts
export interface CIData {
  code: string
  name: string
  ci_type: string
  status: string
  environment: string
  description?: string
}

export class CIFactory {
  static server(overrides?: Partial<CIData>): CIData {
    return {
      code: `SRV-${Date.now()}`,
      name: `测试服务器 ${Date.now()}`,
      ci_type: '服务器',  // 使用显示文本而非值
      status: '在线',
      environment: '生产',
      description: '测试服务器',
      ...overrides,
    }
  }

  static database(overrides?: Partial<CIData>): CIData {
    return {
      code: `DB-${Date.now()}`,
      name: `测试数据库 ${Date.now()}`,
      ci_type: '数据库',
      status: '在线',
      environment: '生产',
      description: '测试数据库',
      ...overrides,
    }
  }
}
```

### 6.2 数据格式规范

```typescript
// ✅ 使用显示文本（label）
{ ci_type: '服务器', status: '在线', environment: '生产' }

// ❌ 使用值（value）- 会导致下拉选择失败
{ ci_type: 'server', status: 'online', environment: 'production' }
```

---

## 7. API Mock 规范

### 7.1 Mock服务配置

```typescript
// utils/api-mock.ts
import { Page } from '@playwright/test'
import { mockUsers, mockCIs } from '../../../mock/data'

export async function setupApiMocks(page: Page) {
  // 登录接口
  await page.route('**/api/auth/login', async (route) => {
    const request = route.request()
    const postData = request.postData()
    
    let username = ''
    let password = ''
    if (postData) {
      const params = new URLSearchParams(postData)
      username = params.get('username') || ''
      password = params.get('password') || ''
    }

    const user = mockUsers.find(u => u.username === username && u.password === password)

    if (user) {
      await route.fulfill({
        status: 200,
        json: { 
          success: true, 
          message: '登录成功', 
          data: { 
            access_token: 'mock-jwt-token-' + user.id, 
            token_type: 'Bearer', 
            expires_in: 3600 
          } 
        },
      })
    } else {
      await route.fulfill({
        status: 401,
        json: { 
          success: false, 
          error: { 
            code: 'INVALID_CREDENTIALS', 
            message: '用户名或密码错误' 
          } 
        },
      })
    }
  })

  // 获取当前用户
  await page.route('**/api/auth/me', async (route) => {
    const request = route.request()
    const authHeader = request.headers().authorization

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      await route.fulfill({ 
        status: 401, 
        json: { 
          success: false, 
          error: { 
            code: 'UNAUTHORIZED', 
            message: '未授权' 
          } 
        } 
      })
      return
    }

    await route.fulfill({
      status: 200,
      json: {
        success: true,
        message: '获取用户信息成功',
        data: mockUsers[0],
      },
    })
  })

  // 配置项列表
  await page.route('**/api/cis**', async (route) => {
    await route.fulfill({
      status: 200,
      json: {
        success: true,
        message: '获取配置项列表成功',
        data: {
          items: mockCIs,
          total: mockCIs.length,
          page: 1,
          page_size: 10,
        },
      },
    })
  })
}
```

### 7.2 数据格式规范

```typescript
// ✅ 使用snake_case字段名，与后端API一致
{
  success: true,
  message: '获取成功',
  data: {
    items: [...],
    total: 100,
    page: 1,
    page_size: 10,
    created_at: '2024-01-01T00:00:00Z',  // snake_case
    updated_at: '2024-01-01T00:00:00Z'
  }
}

// ❌ 使用camelCase字段名 - 会导致前端解析失败
{
  data: {
    createdAt: '...',  // camelCase - 不匹配
    updatedAt: '...'
  }
}
```

---

## 8. 常见UI自动化测试问题及解决方案

| 问题 | 原因 | 解决方案 | 预防措施 |
|------|------|----------|----------|
| **元素找不到** | data-testid缺失或错误 | 强制添加data-testid，使用稳定的选择器 | 代码审查检查data-testid覆盖率 |
| **下拉选项选择失败** | 使用value而非label | 使用显示文本而非值 | 工厂方法使用显示文本 |
| **登录状态判断错误** | URL匹配逻辑错误 | 使用函数式URL匹配+元素可见性验证 | 统一登录验证方法 |
| **测试间歇性失败** | Fixture状态污染 | 独立登录、独立导航，避免状态污染 | 每个测试独立执行前置条件 |
| **表单验证断言失败** | 多个错误元素冲突 | 使用.first()处理多个元素 | 使用特定字段的选择器 |
| **Mock数据格式错误** | 字段名不匹配 | 统一使用snake_case，与后端API一致 | 定义Mock数据接口规范 |
| **页面超时** | 等待策略不当 | 使用waitForSelector替代waitForTimeout | 统一等待策略 |
| **URL解析错误** | request.url vs request.url() | 使用request.url()函数调用 | 代码审查注意API差异 |
| **strict mode冲突** | 多个元素匹配 | 使用.first()或更具体的选择器 | 避免过于宽泛的选择器 |
| **浏览器历史污染** | authenticatedPage fixture | 关键测试独立执行登录 | 避免fixture强制导航 |

---

## 9. 测试用例编写规范

### 9.1 测试结构

```typescript
import { test, expect } from './fixtures/index'
import { UserFactory } from './fixtures/factories'
import { LoginPage, CIListPage, CIFormPage } from './pages'

test.describe('配置项管理测试', () => {
  test.describe('配置项创建功能', () => {
    test('CI-001: 成功创建服务器配置项', async ({ page, loginPage, ciFactory }) => {
      // Arrange - 准备测试数据
      await loginPage.goto()
      await loginPage.login('admin', 'admin123')
      await loginPage.waitForLoginSuccess()
      
      await page.goto('http://localhost:3000/cis')
      await page.waitForSelector('[data-testid="ci-table"]', { timeout: 15000 })
      
      const ciListPage = new CIListPage(page)
      const ciFormPage = new CIFormPage(page)
      const ciData = ciFactory.server()

      // Act - 执行操作
      await ciListPage.clickCreate()
      await ciFormPage.waitForForm()
      await ciFormPage.fill(ciData)
      await ciFormPage.submit()

      // Assert - 验证结果
      await ciListPage.waitForSuccessMessage()
      await expect(page.locator('[data-testid="table-ci-list"]')).toBeVisible()
    })
  })
})
```

### 9.2 测试命名规范

```
格式: {模块}-{编号}: {描述}

示例:
- AUTH-001: 用户成功登录
- CI-001: 成功创建服务器配置项
- CI-010: 按名称搜索配置项
- ROLE-005: 角色创建必填项验证
- CHG-006: 从详情页返回列表
```

### 9.3 测试数据管理

```typescript
// ✅ 使用工厂方法生成数据
const ciData = ciFactory.server()

// ✅ 使用时间戳确保唯一性
const uniqueCode = `TEST-${Date.now()}`

// ❌ 硬编码数据 - 可能导致冲突
const ciData = { code: 'TEST-001', name: '测试' }
```

---

## 10. CI/CD 集成

### 10.1 Pipeline配置

```yaml
# .harness/pipeline.yml
stages:
  - name: e2e-test
    steps:
      - name: install-dependencies
        command: npm ci
      
      - name: start-dev-server
        command: npm run dev &
        background: true
      
      - name: wait-for-server
        command: npx wait-on http://localhost:3000 --timeout 60000
      
      - name: run-e2e-tests
        command: npm run test:e2e
      
      - name: upload-report
        command: npx playwright show-report tests/e2e/playwright-report
```

### 10.2 质量门禁

```yaml
# .harness/quality-gates.yml
gates:
  - name: e2e-test-coverage
    threshold: 80
    
  - name: e2e-test-pass-rate
    threshold: 95
    
  - name: no-flaky-tests
    condition: flaky_tests == 0
```

---

## 11. 验收标准

### 11.1 代码生成验收标准

- [ ] **所有交互元素**都有data-testid
- [ ] **data-testid覆盖率** = 100%
- [ ] **数组渲染**同时提供索引和ID标识符
- [ ] **命名符合规范**（组件类型-上下文-功能）

### 11.2 测试执行验收标准

- [ ] **测试通过率** > 95%
- [ ] **无flaky tests**
- [ ] **测试执行时间** < 3分钟（完整套件）
- [ ] **Mock数据格式**与后端API一致

### 11.3 代码审查验收标准

- [ ] **选择器使用**data-testid
- [ ] **等待策略**使用waitForSelector
- [ ] **测试隔离**独立登录、独立导航
- [ ] **数据工厂**使用显示文本而非值

---

## 📌 快速参考 Cheatsheet

### data-testid 速查表

| 元素类型 | 命名格式 | 示例 |
|---------|---------|------|
| 页面容器 | `page-{name}` | `page-login` |
| 表单 | `form-{name}` | `form-login` |
| 输入框 | `input-{context}-{field}` | `input-login-username` |
| 按钮 | `button-{context}-{action}` | `button-login-submit` |
| 下拉选择 | `select-{context}-{field}` | `select-ci-type` |
| 表格 | `table-{entity}-list` | `table-ci-list` |
| 表格行 | `table-row-{entity}-{index}` | `table-row-ci-0` |
| 表格单元格 | `cell-{entity}-{field}-{id}` | `cell-ci-name-123` |
| 对话框 | `dialog-{entity}-{action}` | `dialog-ci-create` |
| 菜单项 | `menu-item-{entity}` | `menu-item-ci` |

### 选择器优先级速查

```typescript
// 1️⃣ data-testid (首选)
await page.click('[data-testid="button-login-submit"]')

// 2️⃣ role + name
await page.getByRole('button', { name: '登录' }).click()

// 3️⃣ CSS类名
await page.click('.login-submit-button')

// 4️⃣ XPath (最后手段)
await page.click('//button[contains(text(), "登录")]')
```

### 常见操作速查

```typescript
// ✅ 等待URL变化（非登录页）
await page.waitForURL(url => !url.pathname.includes('/login'))

// ✅ 等待元素
await page.waitForSelector('[data-testid="table-ci-list"]', { timeout: 15000 })

// ✅ 处理多个元素
await expect(page.locator('.el-form-item__error').first()).toBeVisible()

// ✅ 下拉选择（使用显示文本）
await selectElementOption('[data-testid="select-ci-type"]', '服务器')

// ✅ 等待网络空闲
await page.waitForLoadState('networkidle')
```

---

**Maintainer**: Platform Engineering Team  
**License**: MIT  
**Version**: 2026.1
