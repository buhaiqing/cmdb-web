import { test as base, expect } from '@playwright/test'
import { LoginPage, CIListPage, CIFormPage, LayoutPage } from '../pages'
import { UserFactory, CIFactory } from './factories'
import { setupApiMocks } from '../utils/api-mock'

/**
 * 扩展 Playwright fixtures，提供页面对象和测试数据工厂
 */
export const test = base.extend<{
  // 页面对象
  loginPage: LoginPage
  ciListPage: CIListPage
  ciFormPage: CIFormPage
  layoutPage: LayoutPage
  
  // 数据工厂
  userFactory: typeof UserFactory
  ciFactory: typeof CIFactory
  
  // 登录的用户
  authenticatedPage: {
    page: any
    username: string
  }
}>({
  // 初始化页面对象
  loginPage: async ({ page }, use) => {
    await setupApiMocks(page)
    await use(new LoginPage(page))
  },

  ciListPage: async ({ page }, use) => {
    await use(new CIListPage(page))
  },

  ciFormPage: async ({ page }, use) => {
    await use(new CIFormPage(page))
  },

  layoutPage: async ({ page }, use) => {
    await use(new LayoutPage(page))
  },

  // 提供数据工厂
  userFactory: async ({}, use) => {
    await use(UserFactory)
  },

  ciFactory: async ({}, use) => {
    await use(CIFactory)
  },

  // 设置 API Mock 并获取已登录的页面
  authenticatedPage: async ({ page, loginPage }, use) => {
    try {
      // 设置 API Mock
      await setupApiMocks(page)

      const user = UserFactory.admin()
      await loginPage.goto()
      await loginPage.login(user.username, user.password)

      // 等待登录成功并跳转到首页
      await loginPage.waitForLoginSuccess()

      // 登录成功后，前端会跳转到首页(/dashboard)
      // 手动导航到配置项列表页，以便测试可以访问 ci-table
      await page.goto('http://localhost:3000/cis')
      await page.waitForSelector('[data-testid="ci-table"]', { timeout: 15000 })

      await use({
        page,
        username: user.username,
      })
    } finally {
      try {
        await page.evaluate(() => localStorage.clear())
        await page.goto('http://localhost:3000/logout')
      } catch (e) {
        // ignore
      }
    }
  },
})

export { expect } from '@playwright/test'
