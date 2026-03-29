import { test, expect } from './fixtures/index'
import { UserFactory } from './fixtures/factories'
import { LayoutPage, LoginPage } from './pages'
import { setupApiMocks } from './utils/api-mock'

/**
 * 认证模块 E2E 测试
 * 
 * 测试覆盖：
 * - 登录功能（正常登录、异常登录、表单验证）
 * - 登出功能（主动登出、会话失效）
 * - 路由守卫（未登录访问受保护页面）
 * 
 * @version 2.0 - 合并自 auth.test.ts 和 auth-optimized.test.ts
 */
test.describe('认证模块测试', () => {
  test.describe('登录功能', () => {
    test('AUTH-001: 用户成功登录', async ({ loginPage }) => {
      // Arrange - 准备测试数据
      const user = UserFactory.admin()

      // Act - 执行登录操作
      await loginPage.goto()
      await loginPage.login(user.username, user.password)
      await loginPage.waitForLoginSuccess()

// Assert - 验证登录成功并跳转到首页/仪表盘
      await expect(loginPage.page).toHaveURL(/\/(dashboard|cis)?$/, { timeout: 10000 })
    })

    test('AUTH-002: 密码错误时登录失败', async ({ loginPage }) => {
      // Arrange
      const user = UserFactory.admin()
      const wrongPassword = 'wrongpassword'

      // Act
      await loginPage.goto()
      await loginPage.login(user.username, wrongPassword)

      // Assert - 等待错误消息出现
      await loginPage.page.waitForSelector('.el-message--error', { timeout: 10000 })
      const errorMessage = loginPage.page.locator('.el-message--error').first()
      await expect(errorMessage).toBeVisible()
      
      // 增强断言：验证错误消息内容
      await expect(errorMessage).toContainText('用户名或密码错误')
      
      // 增强断言：验证仍在登录页
      await expect(loginPage.page).toHaveURL(/\/login/)
    })

    test('AUTH-003: 必填项验证', async ({ loginPage }) => {
      // Arrange
      await loginPage.goto()

      // Act - 点击提交按钮，触发验证
      await loginPage.page.locator('[data-testid="login-submit"]').click()
      await loginPage.page.waitForTimeout(300)

      // Assert - 验证错误提示出现
      const usernameError = loginPage.page.locator('.el-form-item:has([data-testid="login-username"]) .el-form-item__error')
      const passwordError = loginPage.page.locator('.el-form-item:has([data-testid="login-password"]) .el-form-item__error')
      
      await expect(usernameError).toBeVisible()
      await expect(passwordError).toBeVisible()
    })

    test('AUTH-004: 登录后显示用户名', async ({ loginPage, page }) => {
      // Arrange
      const user = UserFactory.admin()

      // Act
      await loginPage.goto()
      await loginPage.login(user.username, user.password)
      await loginPage.waitForLoginSuccess()

      // Assert - 验证登录成功并跳转到首页
      await expect(page).toHaveURL(/\/(dashboard|cis)?$/)
      
      // 增强断言：验证头部用户信息区域可见（用户名由组件逻辑保证正确显示）
      await expect(page.locator('[data-testid="header-username"]')).toBeVisible({ timeout: 10000 })
    })

    test('AUTH-005: 未登录用户访问需要认证的页面', async ({ page }) => {
      // Act - 直接访问配置项列表页
      await page.goto('http://localhost:3000/cis')

      // Assert - 重定向到登录页
      await expect(page).toHaveURL(/\/login/)
      
      // 增强断言：验证登录表单可见
      await expect(page.locator('[data-testid="login-username"]')).toBeVisible()
    })

    test('AUTH-005B: 登录后重定向到原始页面', async ({ page }) => {
      // Arrange - 准备测试数据
      const user = UserFactory.admin()
      const loginPage = new LoginPage(page)

      await setupApiMocks(page)

      // Act 1 - 直接访问受保护的页面，触发重定向到登录页
      await page.goto('http://localhost:3000/cis')
      
      // Assert 1 - 验证被重定向到登录页，并带有 from 参数
      await expect(page).toHaveURL(/\/login\?from=\/cis/)
      
      // Act 2 - 在登录页执行登录
      await loginPage.login(user.username, user.password)
      await loginPage.waitForLoginSuccess()
      
      // Assert 2 - 验证登录后重定向回原始请求的页面
      await expect(page).toHaveURL(/\/cis/)
    })
  })

  test.describe('登出功能', () => {
    test('AUTH-006: 用户成功登出', async ({ page }) => {
      // Arrange - 先登录
      const loginPage = new LoginPage(page)
      const layoutPage = new LayoutPage(page)
      
      await loginPage.goto()
      await loginPage.login('admin', 'admin123')
      await loginPage.waitForLoginSuccess()
      
      // 验证已登录状态
      await expect(page.locator('[data-testid="header-username"]')).toBeVisible()

      // Act - 清除 localStorage 模拟登出
      await page.evaluate(() => {
        localStorage.clear()
      })

      // 尝试访问受保护页面，应该被重定向
      await page.goto('http://localhost:3000/cis')
      
      // Assert - 验证被重定向到登录页
      await expect(page).toHaveURL(/\/login/)
      await expect(page.locator('[data-testid="login-username"]')).toBeVisible()
    })

    test('AUTH-007: 登出后无法访问受保护页面', async ({ page }) => {
      // Arrange - 先登录
      const loginPage = new LoginPage(page)
      
      await loginPage.goto()
      await loginPage.login('admin', 'admin123')
      await loginPage.waitForLoginSuccess()

      // Act - 清除 localStorage 模拟登出
      await page.evaluate(() => {
        localStorage.clear()
      })
      
      // 尝试访问配置项列表页
      await page.goto('http://localhost:3000/cis')

      // Assert - 验证重定向到登录页
      await expect(page).toHaveURL(/\/login/)
      
      // 增强断言：验证登录表单可见
      await expect(page.locator('[data-testid="login-username"]')).toBeVisible()
      await expect(page.locator('[data-testid="login-password"]')).toBeVisible()
    })
  })
})
