# E2E 测试最佳实践

本文档描述了 CMDB Web 应用前端 E2E 测试的最佳实践和代码规范。

## 目录结构

```
tests/e2e/
├── pages/                    # Page Object 模式实现
│   ├── base.page.ts         # 基础页面对象
│   ├── index.ts             # 页面对象导出
│   └── selectors.ts         # 选择器集中管理
├── fixtures/                 # 测试夹具
│   ├── factories.ts         # 测试数据工厂
│   └── index.ts             # 扩展 fixtures
├── utils/                    # 工具函数
│   └── test-helpers.ts      # 遗留工具函数（逐步迁移）
├── auth-optimized.test.ts    # 认证模块测试（优化版）
├── ci-manage-optimized.test.ts # 配置项管理测试（优化版）
└── playwright.config.ts      # Playwright 配置
```

## 核心原则

### 1. Page Object 模式

**优点：**
- 封装页面细节，测试更关注业务逻辑
- 减少代码重复，提高可维护性
- 页面变更时只需修改一处

**示例：**
```typescript
// ❌ 不好的做法 - 硬编码选择器
await page.click('[data-testid="login-username"]')
await page.fill('[data-testid="login-password"]', 'admin')

// ✅ 好的做法 - 使用 Page Object
const loginPage = new LoginPage(page)
await loginPage.login('admin', 'admin123')
```

### 2. 选择器集中管理

**优点：**
- 选择器变更时只需修改一处
- 便于审查和维护
- 避免拼写错误

**示例：**
```typescript
// selectors.ts
export const LoginSelectors = {
  usernameInput: '[data-testid="login-username"]',
  passwordInput: '[data-testid="login-password"]',
} as const

// 测试文件
await page.click(LoginSelectors.usernameInput)
```

### 3. 测试数据工厂

**优点：**
- 测试数据生成逻辑集中
- 易于创建各种场景的测试数据
- 避免硬编码测试数据

**示例：**
```typescript
// ❌ 不好的做法
const user = {
  username: 'admin',
  password: 'admin123',
  email: 'admin@example.com',
}

// ✅ 好的做法
const user = UserFactory.admin()
const customUser = UserFactory.random('test')
const server = CIFactory.server({ status: 'offline' })
```

### 4. 测试结构规范

使用 `Arrange-Act-Assert` 模式：

```typescript
test('用户成功登录', async ({ loginPage, ciListPage }) => {
  // Arrange - 准备测试数据
  const user = UserFactory.admin()

  // Act - 执行操作
  await loginPage.goto()
  await loginPage.login(user.username, user.password)
  await loginPage.waitForLoginSuccess()

  // Assert - 验证结果
  await expect(ciListPage.page).toHaveURL(/\/cis/)
  await ciListPage.waitForTable()
})
```

### 5. 使用 Fixtures 提供共享依赖

**优点：**
- 自动 setup/teardown
- 减少重复代码
- 提高测试可复用性

**示例：**
```typescript
// 使用已登录的页面
test('创建配置项', async ({ authenticatedPage }) => {
  const { page } = authenticatedPage
  // 页面已自动登录，测试结束自动登出
})
```

## 命名规范

### 测试文件
- 格式：`<module>.test.ts` 或 `<module>-optimized.test.ts`
- 示例：`auth.test.ts`, `ci-manage.test.ts`

### 测试用例
- 格式：`<MODULE-CODE>: <描述>`
- 示例：`AUTH-001: 用户成功登录`, `CI-001: 成功创建服务器配置项`

### Page Object 方法
- 动词开头：`goto()`, `login()`, `clickCreate()`
- 等待方法：`waitForXxx()`, `waitForTable()`
- 断言方法：`getXxx()`, `hasXxx()`, `isXxxVisible()`

## 数据测试策略

### 1. 边界值测试
```typescript
test('创建配置项 - 代码长度为 1', async () => {
  const ciData = CIFactory.server({ code: 'A' })
  // ...
})

test('创建配置项 - 代码长度超限', async () => {
  const ciData = CIFactory.server({ code: 'A'.repeat(100) })
  // ...
})
```

### 2. 错误场景测试
```typescript
test('登录失败 - 密码错误', async () => {
  const user = UserFactory.admin()
  await loginPage.login(user.username, 'wrongpassword')
  // ...
})
```

### 3. 数据清理
使用 `afterEach` 或 fixtures 自动清理：
```typescript
test.afterEach(async ({ page }) => {
  // 清理测试数据
})
```

## 常见模式

### 1. 登录模式
```typescript
test('需要登录的测试', async ({ authenticatedPage }) => {
  const { page } = authenticatedPage
  // 直接使用已登录的页面
})
```

### 2. 创建 - 验证模式
```typescript
test('创建并验证', async ({ authenticatedPage, ciFactory }) => {
  const { page } = authenticatedPage
  const ciListPage = new CIListPage(page)
  const ciFormPage = new CIFormPage(page)
  const ciData = ciFactory.server()

  await ciListPage.createCI(ciData)
  await ciListPage.searchByName(ciData.name)
  // 验证创建成功
})
```

### 3. 批量操作模式
```typescript
test('批量删除', async ({ authenticatedPage }) => {
  const { page } = authenticatedPage
  const ciListPage = new CIListPage(page)

  // 创建多个配置项
  for (let i = 0; i < 5; i++) {
    await ciListPage.createCI(CIFactory.random())
  }

  // 批量选择并删除
  await ciListPage.selectAll()
  await ciListPage.batchDelete()
})
```

## 性能优化

### 1. 减少不必要的等待
```typescript
// ❌ 不好的做法
await page.waitForTimeout(1000)

// ✅ 好的做法
await page.waitForSelector('.el-message--success')
```

### 2. 复用登录状态
使用 `authenticatedPage` fixture 自动处理登录/登出

### 3. 并行执行测试
```typescript
// playwright.config.ts
fullyParallel: true
```

## 调试技巧

### 1. 使用 Playwright Inspector
```bash
npm run test:e2e:debug
```

### 2. 截图调试
```typescript
await page.screenshot({ path: 'debug.png' })
```

### 3. 慢动作回放
```typescript
test.slow()
```

## 迁移指南

### 从旧测试迁移到新测试

1. 将硬编码选择器替换为 `LoginSelectors`/`CIListSelectors`
2. 将登录逻辑替换为 `LoginPage.login()`
3. 将测试数据提取为 `UserFactory`/`CIFactory`
4. 使用 `authenticatedPage` fixture 处理登录

**迁移前：**
```typescript
test('旧测试', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[data-testid="login-username"]', 'admin')
  await page.fill('[data-testid="login-password"]', 'admin123')
  await page.click('[data-testid="login-submit"]')
  // ...
})
```

**迁移后：**
```typescript
test('新测试', async ({ loginPage, ciListPage }) => {
  const user = UserFactory.admin()
  await loginPage.login(user.username, user.password)
  await loginPage.waitForLoginSuccess()
  // ...
})
```

## 参考资料

- [Playwright 官方文档](https://playwright.dev)
- [Page Object 模式](https://playwright.dev/docs/pom)
- [测试最佳实践](https://playwright.dev/docs/best-practices)
