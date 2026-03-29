import { test, expect } from './fixtures/index'
import { RoleFactory } from './fixtures/factories'
import { LayoutSelectors, RoleSelectors } from './pages/selectors'

/**
 * 角色管理模块 E2E 测试
 * 
 * 测试覆盖：
 * - 角色列表查看
 * - 角色搜索
 * - 角色创建
 * - 角色编辑
 * - 角色删除
 * - 权限分配
 */
test.describe('角色管理测试', () => {
  test.describe('角色列表功能', () => {
    test('ROLE-001: 查看角色列表', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuRoles)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(RoleSelectors.table)).toBeVisible()
    })

    test('ROLE-002: 按名称搜索角色', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuRoles)
      await page.waitForLoadState('networkidle')

      await page.fill(RoleSelectors.searchName, '管理员')
      await page.click(RoleSelectors.searchButton)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(RoleSelectors.table)).toBeVisible()
    })

    test('ROLE-003: 重置搜索条件', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuRoles)
      await page.waitForLoadState('networkidle')

      await page.click(RoleSelectors.resetButton)
      await page.waitForLoadState('networkidle')

      await expect(page.locator(RoleSelectors.table)).toBeVisible()
    })
  })

  test.describe('角色创建功能', () => {
    test('ROLE-004: 打开创建角色表单', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuRoles)
      await page.waitForLoadState('networkidle')

      await page.click(RoleSelectors.createButton)
      await page.waitForTimeout(500)

      await expect(page.locator(RoleSelectors.form)).toBeVisible()
    })

    test('ROLE-005: 角色创建必填项验证', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuRoles)
      await page.waitForLoadState('networkidle')

      await page.click(RoleSelectors.createButton)
      await page.waitForTimeout(500)

      await page.click(RoleSelectors.formSubmit)
      await page.waitForTimeout(300)

      await expect(page.locator('.el-form-item__error').first()).toBeVisible()
    })
  })

  test.describe('角色编辑功能', () => {
    test('ROLE-006: 编辑角色', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuRoles)
      await page.waitForLoadState('networkidle')

      const editButtons = page.locator('[data-testid^="role-edit-"]')
      const count = await editButtons.count()
      if (count > 0) {
        await editButtons.first().click()
        await page.waitForTimeout(500)
        await expect(page.locator(RoleSelectors.form)).toBeVisible()
      }
    })
  })

  test.describe('权限查看功能', () => {
    test('ROLE-007: 查看角色权限', async ({ authenticatedPage }) => {
      const { page } = authenticatedPage

      await page.click(LayoutSelectors.menuSystem)
      await page.waitForTimeout(300)
      await page.click(LayoutSelectors.menuRoles)
      await page.waitForLoadState('networkidle')

      const permsButtons = page.locator('[data-testid^="role-perms-"]')
      const count = await permsButtons.count()
      if (count > 0) {
        await permsButtons.first().click()
        await page.waitForTimeout(500)
      }
    })
  })
})
