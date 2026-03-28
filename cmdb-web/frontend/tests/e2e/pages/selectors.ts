import { type Locator } from '@playwright/test'

/**
 * 登录页面选择器
 */
export const LoginSelectors = {
  // 表单
  form: '[data-testid="login-form"]',
  
  // 输入框
  usernameInput: '[data-testid="login-username"]',
  passwordInput: '[data-testid="login-password"]',
  submitButton: '[data-testid="login-submit"]',
  
  // 错误消息
  errorMessage: '.el-message--error',
  formError: '.el-form-item.is-error',
  
  // 注册相关
  registerLink: '[data-testid="login-toggle-register"]',
  registerDialog: '[data-testid="register-dialog"]',
  registerForm: '[data-testid="register-form"]',
  registerUsername: '[data-testid="register-username"]',
  registerEmail: '[data-testid="register-email"]',
  registerPassword: '[data-testid="register-password"]',
  registerFullname: '[data-testid="register-fullname"]',
  registerSubmit: '[data-testid="register-submit"]',
  registerCancel: '[data-testid="register-cancel"]',
} as const

/**
 * 配置项列表页面选择器
 */
export const CIListSelectors = {
  // 表格
  table: '[data-testid="ci-table"]',
  tableRow: '[data-testid="ci-table"] tbody tr',

  // 搜索区域
  searchForm: '[data-testid="ci-search-form"]',
  searchName: '[data-testid="ci-search-name"]',
  searchType: '[data-testid="ci-search-type"]',
  searchStatus: '[data-testid="ci-search-status"]',
  searchEnvironment: '[data-testid="ci-search-environment"]',
  searchButton: '[data-testid="ci-search-btn"]',
  resetButton: '[data-testid="ci-reset"]',

  // 操作按钮
  createButton: '[data-testid="ci-create-btn"]',
  viewButton: (id: string) => `[data-testid="ci-view-${id}"]`,
  editButton: (id: string) => `[data-testid="ci-edit-${id}"]`,
  deleteButton: (id: string) => `[data-testid="ci-delete-${id}"]`,

  // 分页器
  pagination: '[data-testid="ci-pagination"]',
  paginationNext: '[data-testid="ci-pagination"] .btn-next',
  paginationPrev: '[data-testid="ci-pagination"] .btn-prev',
  pageSize: '[data-testid="ci-pagination"] .el-pagination__sizes .el-select',

  // 消息提示
  successMessage: '.el-message--success',
  errorMessage: '.el-message--error',

  // 菜单
  menuCIList: '[data-testid="menu-ci-list"]',
} as const

/**
 * 配置项表单选择器（创建/编辑）
 */
export const CIFormSelectors = {
  form: '[data-testid="ci-form"]',
  code: '[data-testid="ci-form-code"]',
  name: '[data-testid="ci-form-name"]',
  description: '[data-testid="ci-form-description"]',
  typeSelect: '[data-testid="ci-form-type"]',
  statusSelect: '[data-testid="ci-form-status"]',
  environmentSelect: '[data-testid="ci-form-environment"]',
  submitButton: '[data-testid="ci-form-submit"]',
  cancelButton: '[data-testid="ci-form-cancel"]',
} as const

/**
 * 布局页面选择器（头部/侧边栏）
 */
export const LayoutSelectors = {
  // 头部
  headerUsername: '[data-testid="header-username"]',
  userDropdown: '[data-testid="layout-user-dropdown"]',
  logoutButton: '[data-testid="user-logout"]',
  breadcrumb: '[data-testid="layout-breadcrumb"]',
  
  // 菜单
  menuCIList: '[data-testid="menu-ci-list"]',
  menuUserList: '[data-testid="menu-user-list"]',
} as const

/**
 * 用户列表页面选择器
 */
export const UserListSelectors = {
  table: '[data-testid="user-table"]',
  createButton: '[data-testid="user-create-btn"]',
  editButton: (id: string) => `[data-testid="user-edit-${id}"]`,
  deleteButton: (id: string) => `[data-testid="user-delete-${id}"]`,
  
  // 表单
  form: '[data-testid="user-form"]',
  username: '[data-testid="user-form-username"]',
  email: '[data-testid="user-form-email"]',
  password: '[data-testid="user-form-password"]',
  fullname: '[data-testid="user-form-fullname"]',
  submitButton: '[data-testid="user-form-submit"]',
} as const

/**
 * 配置项详情页面选择器
 */
export const CIDetailSelectors = {
  backButton: '[data-testid="ci-detail-back-btn"]',
  editButton: '[data-testid="ci-detail-edit-btn"]',
  infoDescriptions: '[data-testid="ci-detail-info"]',
  relationsTable: '[data-testid="ci-relations-table"]',
} as const
