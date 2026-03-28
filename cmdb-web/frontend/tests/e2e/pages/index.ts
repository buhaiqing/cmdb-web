import { type Page } from '@playwright/test'
import { BasePage } from './base.page'
import { LoginSelectors, LayoutSelectors, CIListSelectors, CIFormSelectors, UserListSelectors, CIDetailSelectors } from './selectors'

/**
 * 登录页面对象
 */
export class LoginPage extends BasePage {
  constructor(page: Page) {
    super(page)
  }

  /**
   * 导航到登录页
   */
  async goto(): Promise<void> {
    await this.page.goto(`${this.baseURL}/login`, { waitUntil: 'domcontentloaded' })
    await this.page.waitForLoadState('networkidle')
  }

  /**
   * 执行登录操作
   * @param username 用户名
   * @param password 密码
   */
  async login(username: string, password: string): Promise<void> {
    await this.fillUsername(username)
    await this.fillPassword(password)
    await this.clickSubmit()
  }

  /**
   * 切换到注册模式
   */
  async toggleRegister(): Promise<void> {
    await this.page.click(LoginSelectors.registerLink)
  }

  /**
   * 填写注册信息
   */
  async register(data: { username: string; email: string; password: string; fullname?: string }): Promise<void> {
    await this.page.fill(LoginSelectors.registerUsername, data.username)
    await this.page.fill(LoginSelectors.registerEmail, data.email)
    await this.page.fill(LoginSelectors.registerPassword, data.password)
    if (data.fullname) {
      await this.page.fill(LoginSelectors.registerFullname, data.fullname)
    }
    await this.page.click(LoginSelectors.registerSubmit)
  }

  /**
   * 填写用户名
   */
  async fillUsername(username: string): Promise<void> {
    await this.page.fill(LoginSelectors.usernameInput, username)
  }

  /**
   * 填写密码
   */
  async fillPassword(password: string): Promise<void> {
    await this.page.fill(LoginSelectors.passwordInput, password)
  }

  /**
   * 点击登录按钮
   */
  async clickSubmit(): Promise<void> {
    await this.page.click(LoginSelectors.submitButton)
  }

  /**
   * 等待登录成功并跳转到首页
   */
  async waitForLoginSuccess(): Promise<void> {
    await this.page.waitForURL(/\/cis|\/$/, { timeout: 15000 })
  }

  /**
   * 验证错误消息
   */
  async getErrorMessage(): Promise<string> {
    const element = this.page.locator(LoginSelectors.errorMessage)
    await element.waitFor({ state: 'visible' })
    return (await element.textContent()) || ''
  }

  /**
   * 验证表单错误
   */
  async hasFormError(): Promise<boolean> {
    const element = this.page.locator(LoginSelectors.formError)
    return (await element.count()) > 0
  }

  /**
   * 点击注册链接
   */
  async clickRegisterLink(): Promise<void> {
    await this.page.click(LoginSelectors.registerLink)
  }

  /**
   * 等待注册对话框打开
   */
  async waitForRegisterDialog(): Promise<void> {
    await this.page.waitForSelector(LoginSelectors.registerDialog)
  }
}

/**
 * 用户列表页面对象
 */
export class UserListPage extends BasePage {
  constructor(page: Page) {
    super(page)
  }

  async goto(): Promise<void> {
    await this.navigateTo('/users')
    await this.page.waitForLoadState('networkidle')
  }

  async clickCreate(): Promise<void> {
    await this.page.click(UserListSelectors.createButton)
  }

  async fillForm(data: { username: string; email: string; password?: string; fullname?: string }): Promise<void> {
    await this.page.fill(UserListSelectors.username, data.username)
    await this.page.fill(UserListSelectors.email, data.email)
    if (data.password) {
      await this.page.fill(UserListSelectors.password, data.password)
    }
    if (data.fullname) {
      await this.page.fill(UserListSelectors.fullname, data.fullname)
    }
  }

  async submit(): Promise<void> {
    await this.page.click(UserListSelectors.submitButton)
  }
}

/**
 * 配置项列表页面对象
 */
export class CIListPage extends BasePage {
  constructor(page: Page) {
    super(page)
  }

  /**
   * 导航到配置项列表页
   */
  async goto(): Promise<void> {
    await this.navigateTo('/cis')
    await this.page.waitForLoadState('networkidle')
    // 等待表格加载完成，确保页面元素可见
    await this.waitForTable()
  }

  /**
   * 等待表格加载完成
   */
  async waitForTable(): Promise<void> {
    await this.page.waitForSelector(CIListSelectors.table)
  }

  /**
   * 点击创建按钮
   */
  async clickCreate(): Promise<void> {
    await this.page.click(CIListSelectors.createButton)
  }

  /**
   * 搜索配置项
   * @param name 名称
   */
  async searchByName(name: string): Promise<void> {
    await this.page.fill(CIListSelectors.searchName, name)
    await this.page.click(CIListSelectors.searchButton)
  }

  /**
   * 筛选配置项
   * @param type 类型
   * @param status 状态
   */
  async filter(type?: string, status?: string): Promise<void> {
    if (type) {
      await this.selectElementOption(CIListSelectors.searchType, type)
    }
    if (status) {
      await this.selectElementOption(CIListSelectors.searchStatus, status)
    }
    await this.page.click(CIListSelectors.searchButton)
  }

  /**
   * 重置搜索条件
   */
  async reset(): Promise<void> {
    await this.page.click(CIListSelectors.resetButton)
  }

  /**
   * 获取表格行数
   */
  async getRowCount(): Promise<number> {
    const count = await this.page.locator(CIListSelectors.tableRow).count()
    return count
  }

  /**
   * 点击查看按钮
   * @param id 配置项 ID
   */
  async clickView(id?: string): Promise<void> {
    if (id) {
      await this.page.click(CIListSelectors.viewButton(id))
    } else {
      await this.page.locator('[data-testid^="ci-view-"]').first().click()
    }
  }

  /**
   * 点击编辑按钮
   * @param id 配置项 ID
   */
  async clickEdit(id?: string): Promise<void> {
    if (id) {
      await this.page.click(CIListSelectors.editButton(id))
    } else {
      await this.page.locator('[data-testid^="ci-edit-"]').first().click()
    }
  }

  /**
   * 点击删除按钮
   * @param id 配置项 ID
   */
  async clickDelete(id?: string, position: 'first' | 'last' = 'first'): Promise<void> {
    if (id) {
      await this.page.click(CIListSelectors.deleteButton(id))
    } else {
      const locator = this.page.locator('[data-testid^="ci-delete-"]')
      if (position === 'last') {
        await locator.last().click()
      } else {
        await locator.first().click()
      }
    }
  }

  /**
   * 点击下一页
   */
  async nextPage(): Promise<void> {
    await this.page.click(CIListSelectors.paginationNext)
  }

  /**
   * 切换每页显示数量
   * @param size 每页数量
   */
  async changePageSize(size: number): Promise<void> {
    await this.selectElementOptionByText(CIListSelectors.pageSize, String(size))
  }

  /**
   * 等待成功消息提示
   */
  async waitForSuccessMessage(): Promise<void> {
    await this.page.waitForSelector('.el-message--success', { state: 'visible' })
  }

  /**
   * 验证分页信息可见
   */
  async expectPaginationVisible(): Promise<void> {
    await this.page.waitForSelector(CIListSelectors.pagination, { state: 'visible' })
  }

  /**
   * 检查是否可以点击下一页
   */
  async canGoNextPage(): Promise<boolean> {
    const nextBtn = this.page.locator(CIListSelectors.paginationNext)
    return await nextBtn.isEnabled()
  }

  /**
   * 等待请求完成
   */
  async waitForRequestDelay(ms: number = 500): Promise<void> {
    await this.page.waitForTimeout(ms)
  }

  /**
   * 验证当前页码
   */
  async expectCurrentPage(page: string): Promise<void> {
    const currentPage = this.page.locator(`${CIListSelectors.pagination} .el-pager .is-active`)
    await this.page.waitForSelector(`${CIListSelectors.pagination} .el-pager .is-active`, { state: 'visible' })
    const text = await currentPage.textContent()
    if (!text?.includes(page)) {
      throw new Error(`Expected current page to be ${page}, but got ${text}`)
    }
  }
  /**
   * 等待错误消息提示
   */
  async waitForErrorMessage(): Promise<void> {
    await this.page.waitForSelector('.el-message--error', { state: 'visible' })
  }
}

/**
 * 配置项表单页面对象（用于创建/编辑对话框）
 */
export class CIFormPage extends BasePage {
  constructor(page: Page) {
    super(page)
  }

  /**
   * 等待表单加载
   */
  async waitForForm(): Promise<void> {
    await this.page.waitForSelector(CIFormSelectors.form, { state: 'visible' })
  }

  /**
   * 填写配置项信息
   */
  async fill(data: {
    code: string
    name: string
    type?: string
    ci_type?: string
    status?: string
    environment?: string
    description?: string
    owner?: string
  }): Promise<void> {
    const ciType = data.ci_type || data.type
    if (ciType) {
      await this.selectType(ciType)
    }
    await this.fillCode(data.code)
    await this.fillName(data.name)
    if (data.description) {
      await this.fillDescription(data.description)
    }
    if (data.status) {
      await this.selectStatus(data.status)
    }
    if (data.environment) {
      await this.selectEnvironment(data.environment)
    }
  }

  /**
   * 选择类型
   */
  async selectType(type: string): Promise<void> {
    await this.selectElementOption(CIFormSelectors.typeSelect, type)
  }

  /**
   * 选择状态
   */
  async selectStatus(status: string): Promise<void> {
    await this.selectElementOption(CIFormSelectors.statusSelect, status)
  }

  /**
   * 填写代码
   */
  async fillCode(code: string): Promise<void> {
    await this.page.fill(CIFormSelectors.code, code)
  }

  /**
   * 填写名称
   */
  async fillName(name: string): Promise<void> {
    await this.page.fill(CIFormSelectors.name, name)
  }

  /**
   * 填写描述
   */
  async fillDescription(description: string): Promise<void> {
    await this.page.fill(CIFormSelectors.description, description)
  }

  /**
   * 选择环境
   */
  async selectEnvironment(environment: string): Promise<void> {
    await this.selectElementOption(CIFormSelectors.environmentSelect, environment)
  }

  /**
   * 提交表单
   */
  async submit(): Promise<void> {
    await this.page.click(CIFormSelectors.submitButton)
  }

  /**
   * 取消操作
   */
  async cancel(): Promise<void> {
    await this.page.click(CIFormSelectors.cancelButton)
  }
}

/**
 * 配置项详情页面对象
 */
export class CIDetailPage extends BasePage {
  constructor(page: Page) {
    super(page)
  }

  async goto(id: string): Promise<void> {
    await this.navigateTo(`/cis/${id}`)
    await this.page.waitForLoadState('networkidle')
  }

  async back(): Promise<void> {
    await this.page.click(CIDetailSelectors.backButton)
  }

  async clickEdit(): Promise<void> {
    await this.page.click(CIDetailSelectors.editButton)
  }

  async getInfo(): Promise<string> {
    const element = this.page.locator(CIDetailSelectors.infoDescriptions)
    return (await element.textContent()) || ''
  }
}

/**
 * 布局页面对象（头部导航）
 */
export class LayoutPage {
  readonly page: Page

  constructor(page: Page) {
    this.page = page
  }

  /**
   * 获取当前登录的用户名
   */
  async getUsername(): Promise<string> {
    const element = this.page.locator(LayoutSelectors.headerUsername)
    await element.waitFor({ state: 'visible' })
    return (await element.textContent()) || ''
  }

  /**
   * 验证用户名可见
   */
  async isUsernameVisible(): Promise<boolean> {
    const element = this.page.locator(LayoutSelectors.headerUsername)
    return element.isVisible()
  }

  /**
   * 点击用户菜单
   */
  async clickUserMenu(): Promise<void> {
    await this.page.click(LayoutSelectors.userDropdown)
  }

  /**
   * 执行登出操作
   */
  async logout(): Promise<void> {
    await this.clickUserMenu()
    await this.page.click(LayoutSelectors.logoutButton)
  }
}
