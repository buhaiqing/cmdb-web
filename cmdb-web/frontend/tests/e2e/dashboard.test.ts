import { test, expect } from './fixtures/index'
import { LayoutSelectors, DashboardSelectors } from './pages/selectors'

/**
 * 仪表盘模块 E2E 测试
 * 
 * 测试覆盖：
 * - 仪表盘数据展示
 * - 统计卡片展示
 * - 图表展示
 * - 最近变更列表
 */
test.describe('仪表盘测试', () => {
  test.describe('仪表盘数据展示', () => {
    test('DASH-001: 查看仪表盘', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuDashboard)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(DashboardSelectors.statTotal)).toBeVisible()
    })

    test('DASH-002: 统计卡片展示', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuDashboard)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(DashboardSelectors.statTotal)).toBeVisible()
      await expect(page.locator(DashboardSelectors.statOnline)).toBeVisible()
      await expect(page.locator(DashboardSelectors.statChanges)).toBeVisible()
      await expect(page.locator(DashboardSelectors.statUsers)).toBeVisible()
    })

    test('DASH-003: 配置项类型分布图', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuDashboard)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(DashboardSelectors.chartType)).toBeVisible()
    })

    test('DASH-004: 环境分布图', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuDashboard)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(DashboardSelectors.chartEnv)).toBeVisible()
    })

    test('DASH-005: 最近变更列表', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuDashboard)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(DashboardSelectors.recentChanges)).toBeVisible()
    })

    test('DASH-006: 查看全部变更链接', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuDashboard)
      await page.waitForLoadState('networkidle')

      const viewAllLink = page.locator(DashboardSelectors.viewAllChanges)
      if (await viewAllLink.isVisible()) {
        await viewAllLink.click()
        await page.waitForLoadState('networkidle')
        await expect(page).toHaveURL(/\/changes/)
      }
    })
  })
})
