import { type Page, type Locator } from '@playwright/test'

/**
 * 基础页面对象 - 所有页面的基类
 */
export class BasePage {
  readonly page: Page
  readonly baseURL: string

  constructor(page: Page, baseURL: string = 'http://localhost:3000') {
    this.page = page
    this.baseURL = baseURL
  }

  /**
   * 导航到指定路径
   */
  async navigateTo(path: string): Promise<void> {
    await this.page.goto(`${this.baseURL}${path}`)
  }

  /**
   * 等待页面加载完成
   */
  async waitForPageLoad(selector: string): Promise<void> {
    await this.page.waitForSelector(selector)
  }

  /**
   * 获取当前 URL
   */
  getCurrentURL(): string {
    return this.page.url()
  }

  /**
   * 等待 URL 匹配
   */
  async waitForURL(pattern: RegExp): Promise<void> {
    await this.page.waitForURL(pattern, { timeout: 15000 })
  }

  /**
   * Element Plus Select 组件选择操作
   * @param selector Select 组件的选择器 (通常是 data-testid)
   * @param value 选项的值或文本
   */
  async selectElementOption(selector: string, value: string): Promise<void> {
    await this.page.click(selector)
    // 等待下拉框展开动画完成
    await this.page.waitForTimeout(800)
    
    // 查找所有包含目标文本的选项，并选择第一个可见的
    const options = await this.page.locator(`.el-select-dropdown__item:has-text("${value}")`).all()
    
    // 遍历找到第一个可见的选项并点击
    for (const option of options) {
      if (await option.isVisible()) {
        await option.click()
        return
      }
    }
    
    // 如果没有找到可见的选项，尝试使用其他选择器
    await this.page.click(`.el-select-dropdown__item:has-text("${value}")`)
  }

  /**
   * Element Plus Select 组件通过文本选择操作
   * @param selector Select 组件的选择器
   * @param text 选项的显示文本
   */
  async selectElementOptionByText(selector: string, text: string): Promise<void> {
    await this.page.click(selector)
    // 等待下拉框展开动画完成
    await this.page.waitForTimeout(300)
    const dropdown = this.page.locator('.el-select-dropdown').filter({ hasText: text })
    await dropdown.waitFor({ state: 'visible', timeout: 5000 })
    await dropdown.locator(`.el-select-dropdown__item`).filter({ hasText: text }).first().click()
  }

  /**
   * 等待成功消息提示
   */
  async waitForSuccessMessage(): Promise<void> {
    await this.page.waitForSelector('.el-message--success', { state: 'visible' })
  }

  /**
   * 等待错误消息提示
   */
  async waitForErrorMessage(): Promise<void> {
    await this.page.waitForSelector('.el-message--error', { state: 'visible' })
  }
}
