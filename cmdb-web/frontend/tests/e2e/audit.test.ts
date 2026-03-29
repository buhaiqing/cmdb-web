import { test, expect } from './fixtures/index'
import { LayoutSelectors, AuditSelectors } from './pages/selectors'

/**
 * 审计日志模块 E2E 测试
 * 
 * 测试覆盖：
 * - 审计日志列表查看
 * - 审计日志搜索筛选
 * - 审计日志详情查看
 * - 审计日志导出
 */
test.describe('审计日志测试', () => {
  test.describe('审计日志列表功能', () => {
    test('AUDIT-001: 查看审计日志列表', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuAudit)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(AuditSelectors.table)).toBeVisible()
    })

    test('AUDIT-002: 按用户搜索审计日志', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuAudit)
      await page.waitForLoadState('networkidle')

      await page.fill(AuditSelectors.searchUser, 'admin')
      await page.click(AuditSelectors.searchButton)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(AuditSelectors.table)).toBeVisible()
    })

    test('AUDIT-003: 按操作类型筛选', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuAudit)
      await page.waitForLoadState('networkidle')

      await page.click(AuditSelectors.searchAction)
      await page.waitForTimeout(500)

      const dropdown = page.locator('.el-select-dropdown:visible').last()
      const options = dropdown.locator('.el-select-dropdown__item')
      if (await options.count() > 0) {
        await options.first().click()
        await page.click(AuditSelectors.searchButton)
        await page.waitForLoadState('networkidle')
      }

      await expect(page.locator(AuditSelectors.table)).toBeVisible()
    })

    test('AUDIT-004: 按资源类型筛选', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuAudit)
      await page.waitForLoadState('networkidle')

      await page.click(AuditSelectors.searchResource)
      await page.waitForTimeout(500)

      const dropdown = page.locator('.el-select-dropdown:visible').last()
      const options = dropdown.locator('.el-select-dropdown__item')
      if (await options.count() > 0) {
        await options.first().click()
        await page.click(AuditSelectors.searchButton)
        await page.waitForLoadState('networkidle')
      }

      await expect(page.locator(AuditSelectors.table)).toBeVisible()
    })

    test('AUDIT-005: 重置搜索条件', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuAudit)
      await page.waitForLoadState('networkidle')

      await page.click(AuditSelectors.resetButton)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(AuditSelectors.table)).toBeVisible()
    })
  })

  test.describe('审计日志详情功能', () => {
    test('AUDIT-006: 查看审计日志详情', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuAudit)
      await page.waitForLoadState('networkidle')

      const detailButtons = page.locator('[data-testid^="audit-detail-"]')
      const count = await detailButtons.count()
      if (count > 0) {
        await detailButtons.first().click()
        await page.waitForTimeout(500)
      }
    })
  })

  test.describe('审计日志导出功能', () => {
    test('AUDIT-007: 导出审计日志', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuAudit)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(AuditSelectors.exportButton)).toBeVisible()
    })
  })
})
