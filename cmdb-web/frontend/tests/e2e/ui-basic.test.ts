import { test, expect } from './fixtures/index'
import { UserFactory } from './fixtures/factories'
import { LoginPage } from './pages'

test.describe('前端UI自动化测试 - 基础功能', () => {
  test.describe('登录功能', () => {
    test('AUTH-001: 用户成功登录', async ({ loginPage }) => {
      const user = UserFactory.admin()
      await loginPage.goto()
      await loginPage.login(user.username, user.password)
      await loginPage.waitForLoginSuccess()
      await expect(loginPage.page).toHaveURL(/\/(dashboard|cis)?$/)
    })

    test('AUTH-002: 密码错误时登录失败', async ({ loginPage }) => {
      const user = UserFactory.admin()
      await loginPage.goto()
      await loginPage.login(user.username, 'wrongpassword')
      await loginPage.page.waitForSelector('.el-message--error', { timeout: 10000 })
      const errorMessage = loginPage.page.locator('.el-message--error').first()
      await expect(errorMessage).toBeVisible()
    })

    test('AUTH-003: 必填项验证', async ({ loginPage }) => {
      await loginPage.goto()
      await loginPage.page.locator('[data-testid="login-submit"]').click()
      await loginPage.page.waitForTimeout(300)
      const usernameError = loginPage.page.locator('.el-form-item:has([data-testid="login-username"]) .el-form-item__error')
      const passwordError = loginPage.page.locator('.el-form-item:has([data-testid="login-password"]) .el-form-item__error')
      await expect(usernameError).toBeVisible()
      await expect(passwordError).toBeVisible()
    })
  })

  test.describe('页面导航', () => {
    test('NAV-001: 未登录访问配置项页面重定向到登录页', async ({ page }) => {
      await page.goto('http://localhost:3000/cis')
      await expect(page).toHaveURL(/\/login/)
    })

    test('NAV-002: 登录后访问配置项页面', async ({ page }) => {
      const loginPage = new LoginPage(page)
      await loginPage.goto()
      await loginPage.login('admin', 'admin123')
      await loginPage.waitForLoginSuccess()
      await page.goto('http://localhost:3000/cis')
      await expect(page).toHaveURL(/\/cis/)
    })
  })

  test.describe('登出功能', () => {
    test('LOGOUT-001: 清除登录状态', async ({ page }) => {
      const loginPage = new LoginPage(page)
      await loginPage.goto()
      await loginPage.login('admin', 'admin123')
      await loginPage.waitForLoginSuccess()

      await page.evaluate(() => localStorage.clear())

      await page.goto('http://localhost:3000/cis')
      await expect(page).toHaveURL(/\/login/)
    })
  })
})