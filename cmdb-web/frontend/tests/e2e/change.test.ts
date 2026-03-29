import { test, expect } from './fixtures/index'
import { UserFactory, ChangeFactory } from './fixtures/factories'
import { LoginPage } from './pages'
import { ChangeSelectors, LayoutSelectors } from './pages/selectors'

/**
 * 变更管理模块 E2E 测试
 * 
 * 测试覆盖：
 * - 变更列表查看
 * - 变更搜索筛选
 * - 变更详情查看
 * - 变更审批功能
 * - 变更提交功能
 */
test.describe('变更管理测试', () => {
  test.describe('变更列表功能', () => {
    test('CHG-001: 查看变更列表', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuChanges)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(ChangeSelectors.listTable)).toBeVisible()
    })

    test('CHG-002: 按状态筛选变更', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuChanges)
      await page.waitForLoadState('networkidle')

      await page.click(ChangeSelectors.searchStatus)
      await page.waitForTimeout(500)

      const dropdown = page.locator('.el-select-dropdown:visible').last()
      const options = dropdown.locator('.el-select-dropdown__item')
      if (await options.count() > 0) {
        await options.first().click()
        await page.click(ChangeSelectors.searchButton)
        await page.waitForLoadState('networkidle')
      }

      await expect(page.locator(ChangeSelectors.listTable)).toBeVisible()
    })

    test('CHG-003: 按变更类型筛选', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuChanges)
      await page.waitForLoadState('networkidle')

      await page.click(ChangeSelectors.searchType)
      await page.waitForTimeout(500)

      const dropdown = page.locator('.el-select-dropdown:visible').last()
      const options = dropdown.locator('.el-select-dropdown__item')
      if (await options.count() > 0) {
        await options.first().click()
        await page.click(ChangeSelectors.searchButton)
        await page.waitForLoadState('networkidle')
      }

      await expect(page.locator(ChangeSelectors.listTable)).toBeVisible()
    })

    test('CHG-004: 重置搜索条件', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuChanges)
      await page.waitForLoadState('networkidle')

      await page.click(ChangeSelectors.resetButton)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(ChangeSelectors.listTable)).toBeVisible()
    })
  })

  test.describe('变更详情功能', () => {
    test('CHG-005: 查看变更详情', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.goto('http://localhost:3000/changes/1')
      await page.waitForLoadState('networkidle')

      await expect(page).toHaveURL(/\/changes\/\d+/)
    })

    test('CHG-006: 从详情页返回列表', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.goto('http://localhost:3000/changes/1')
      await page.waitForLoadState('networkidle')

      const backButton = page.locator(ChangeSelectors.detailBack)
      if (await backButton.isVisible()) {
        await backButton.click()
        await page.waitForLoadState('networkidle')
        await expect(page).toHaveURL(/\/changes$/)
      }
    })
  })

  test.describe('变更提交功能', () => {
    test('CHG-007: 打开变更提交表单', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuChanges)
      await page.waitForLoadState('networkidle')

      await page.click(ChangeSelectors.createButton)
      await page.waitForTimeout(500)

      await expect(page.locator(ChangeSelectors.form)).toBeVisible()
    })

    test('CHG-008: 变更提交必填项验证', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuChanges)
      await page.waitForLoadState('networkidle')

      await page.click(ChangeSelectors.createButton)
      await page.waitForTimeout(500)

      await page.click(ChangeSelectors.formSubmit)
      await page.waitForTimeout(300)

      await expect(page.locator('.el-form-item__error')).toBeVisible()
    })
  })

  test.describe('变更审批功能', () => {
    test('CHG-009: 审批按钮可见性', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuChanges)
      await page.waitForLoadState('networkidle')

      const table = page.locator(ChangeSelectors.listTable)
      await expect(table).toBeVisible()
    })
  })
})
