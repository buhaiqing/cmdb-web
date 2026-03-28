import { test as base, expect, type Page } from '@playwright/test'

/**
 * 测试工具函数
 */

// 测试数据接口
export interface TestUserData {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface TestCIData {
  ci_type: string
  code: string
  name: string
  description?: string
  status?: string
  environment: string
  owner?: string
}

/**
 * 登录工具函数
 */
export async function login(page: Page, username: string, password: string): Promise<void> {
  await page.goto('http://localhost:3000/login', { waitUntil: 'domcontentloaded' })

  // 等待页面加载完成
  await page.waitForSelector('[data-testid="login-username"]', { state: 'visible' })

  // 填写用户名
  await page.fill('[data-testid="login-username"]', username)

  // 填写密码
  await page.fill('[data-testid="login-password"]', password)

  // 点击登录按钮
  await page.click('[data-testid="login-submit"]')

  // 等待登录成功，跳转到首页，给足够的超时时间
  await page.waitForURL(/\/cis|\/$|\/login/, { timeout: 15000 })
}

/**
 * 登出工具函数
 */
export async function logout(page: Page): Promise<void> {
  // 点击用户头像下拉菜单
  await page.click('[data-testid="layout-user-dropdown"]')

  // 点击退出登录
  await page.click('[data-testid="user-logout"]')

  // 等待跳转到登录页
  await page.waitForURL(/\/login/, { timeout: 15000 })
}

/**
 * 创建配置项工具函数
 */
export async function createCI(page: Page, ciData: TestCIData): Promise<void> {
  // 等待对话框打开
  await page.waitForSelector('[data-testid="ci-form"]', { state: 'visible' })

  const typeMap: Record<string, string> = {
    server: '服务器', network_device: '网络设备', database: '数据库',
    middleware: '中间件', application: '应用', container: '容器',
    k8s_resource: 'K8s 资源', cloud_resource: '云资源'
  }
  const statusMap: Record<string, string> = {
    online: '在线', offline: '离线', maintenance: '维护中', decommissioned: '已退役'
  }
  const envMap: Record<string, string> = {
    production: '生产', int: '测试', dev: '开发'
  }

  // 选择类型
  await page.click('[data-testid="ci-form-type"]')
  await page.waitForTimeout(300)
  const typeText = typeMap[ciData.ci_type] || ciData.ci_type
  const typeDropdown = page.locator('.el-select-dropdown').filter({ hasText: typeText })
  await typeDropdown.waitFor({ state: 'visible', timeout: 5000 })
  await typeDropdown.locator('.el-select-dropdown__item').filter({ hasText: typeText }).first().click()

  // 填写代码
  await page.fill('[data-testid="ci-form-code"]', ciData.code)

  // 填写名称
  await page.fill('[data-testid="ci-form-name"]', ciData.name)

  // 填写描述（如果有）
  if (ciData.description) {
    await page.fill('[data-testid="ci-form-description"]', ciData.description)
  }

  // 选择状态
  if (ciData.status) {
    await page.click('[data-testid="ci-form-status"]')
    await page.waitForTimeout(300)
    const statusText = statusMap[ciData.status] || ciData.status
    const statusDropdown = page.locator('.el-select-dropdown').filter({ hasText: statusText })
    await statusDropdown.waitFor({ state: 'visible', timeout: 5000 })
    await statusDropdown.locator('.el-select-dropdown__item').filter({ hasText: statusText }).first().click()
  }

  // 选择环境
  await page.click('[data-testid="ci-form-environment"]')
  await page.waitForTimeout(300)
  const envText = envMap[ciData.environment] || ciData.environment
  const envDropdown = page.locator('.el-select-dropdown').filter({ hasText: envText })
  await envDropdown.waitFor({ state: 'visible', timeout: 5000 })
  await envDropdown.locator('.el-select-dropdown__item').filter({ hasText: envText }).first().click()

  // 点击提交
  await page.click('[data-testid="ci-form-submit"]')

  // 等待创建成功提示
  await page.waitForSelector('.el-message--success', { state: 'visible' })
}

/**
 * 搜索配置项工具函数
 */
export async function searchCI(page: Page, name: string): Promise<void> {
  // 填写搜索名称
  await page.fill('[data-testid="ci-search-name"]', name)

  // 点击搜索按钮
  await page.click('[data-testid="ci-search-btn"]')

  // 等待搜索结果
  await page.waitForSelector('[data-testid="ci-table"]')
}

/**
 * 断言工具函数
 */
export function expectElementVisible(page: Page, selector: string): Promise<void> {
  return expect(page.locator(selector)).toBeVisible()
}

export function expectElementHidden(page: Page, selector: string): Promise<void> {
  return expect(page.locator(selector)).toBeHidden()
}

export function expectTextToContain(page: Page, selector: string, text: string): Promise<void> {
  return expect(page.locator(selector)).toContainText(text)
}

/**
 * 扩展 test 对象，添加自定义 fixtures
 */
export const test = base.extend<{
  loginAndNavigate: (username: string, password: string) => Promise<void>
}>({
  loginAndNavigate: async ({ page }, use) => {
    await use(async (username: string, password: string) => {
      await login(page, username, password)
    })
  },
})

export { expect } from '@playwright/test'
