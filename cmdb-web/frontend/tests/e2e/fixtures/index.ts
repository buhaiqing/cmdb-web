import { test as base, expect } from '@playwright/test'
import { LoginPage, CIListPage, CIFormPage, LayoutPage } from '../pages'
import { UserFactory, CIFactory } from './factories'

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

  // 提供已登录的页面
  authenticatedPage: async ({ page, loginPage }, use) => {
    try {
      const user = UserFactory.admin()
      await loginPage.goto()
      await loginPage.login(user.username, user.password)
      await loginPage.waitForLoginSuccess()
      
      // 等待页面元素加载完成
      await page.waitForSelector('[data-testid="ci-table"]', { timeout: 15000 })

      await use({
        page,
        username: user.username,
      })
    } finally {
      try {
        await page.goto('http://localhost:3000/logout')
      } catch (e) {
        // ignore
      }
    }
  },
})

export { expect } from '@playwright/test'
