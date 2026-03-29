import { type Locator } from '@playwright/test'

/**
 * 登录页面选择器
 */
export const LoginSelectors = {
  form: '[data-testid="login-form"]',
  usernameInput: '[data-testid="login-username"]',
  passwordInput: '[data-testid="login-password"]',
  submitButton: '[data-testid="login-submit"]',
  errorMessage: '.el-message--error',
  formError: '.el-form-item.is-error',
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
  table: '[data-testid="ci-table"]',
  tableRow: '[data-testid="ci-table"] tbody tr',
  searchForm: '[data-testid="ci-search-form"]',
  searchName: '[data-testid="ci-search-name"]',
  searchType: '[data-testid="ci-search-type"]',
  searchStatus: '[data-testid="ci-search-status"]',
  searchEnvironment: '[data-testid="ci-search-environment"]',
  searchButton: '[data-testid="ci-search-btn"]',
  resetButton: '[data-testid="ci-reset"]',
  createButton: '[data-testid="ci-create-btn"]',
  viewButton: (id: string) => `[data-testid="ci-view-${id}"]`,
  editButton: (id: string) => `[data-testid="ci-edit-${id}"]`,
  deleteButton: (id: string) => `[data-testid="ci-delete-${id}"]`,
  pagination: '[data-testid="ci-pagination"]',
  paginationNext: '[data-testid="ci-pagination"] .btn-next',
  paginationPrev: '[data-testid="ci-pagination"] .btn-prev',
  pageSize: '[data-testid="ci-pagination"] .el-pagination__sizes .el-select',
  successMessage: '.el-message--success',
  errorMessage: '.el-message--error',
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
  owner: '[data-testid="ci-form-owner"]',
  submitButton: '[data-testid="ci-form-submit"]',
  cancelButton: '[data-testid="ci-form-cancel"]',
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

/**
 * 布局页面选择器（头部/侧边栏）
 */
export const LayoutSelectors = {
  headerUsername: '[data-testid="header-username"]',
  userDropdown: '[data-testid="layout-user-dropdown"]',
  logoutButton: '[data-testid="user-logout"]',
  breadcrumb: '[data-testid="layout-breadcrumb"]',
  menuDashboard: '[data-testid="menu-dashboard"]',
  menuCI: '[data-testid="menu-ci"]',
  menuCIList: '[data-testid="menu-ci-list"]',
  menuRelation: '[data-testid="menu-relation"]',
  menuChanges: '[data-testid="menu-changes"]',
  menuReports: '[data-testid="menu-reports"]',
  menuSystem: '[data-testid="menu-system"]',
  menuUsers: '[data-testid="menu-users"]',
  menuRoles: '[data-testid="menu-roles"]',
  menuAudit: '[data-testid="menu-audit"]',
} as const

/**
 * 用户列表页面选择器
 */
export const UserListSelectors = {
  table: '[data-testid="user-table"]',
  createButton: '[data-testid="user-create-btn"]',
  editButton: (id: string) => `[data-testid="user-edit-${id}"]`,
  deleteButton: (id: string) => `[data-testid="user-delete-${id}"]`,
  form: '[data-testid="user-form"]',
  username: '[data-testid="user-form-username"]',
  email: '[data-testid="user-form-email"]',
  password: '[data-testid="user-form-password"]',
  fullname: '[data-testid="user-form-fullname"]',
  submitButton: '[data-testid="user-form-submit"]',
  pagination: '[data-testid="user-pagination"]',
} as const

/**
 * 仪表盘页面选择器
 */
export const DashboardSelectors = {
  statTotal: '[data-testid="dashboard-stat-total"]',
  statOnline: '[data-testid="dashboard-stat-online"]',
  statChanges: '[data-testid="dashboard-stat-changes"]',
  statUsers: '[data-testid="dashboard-stat-users"]',
  chartType: '[data-testid="dashboard-chart-type"]',
  chartEnv: '[data-testid="dashboard-chart-env"]',
  recentChanges: '[data-testid="dashboard-recent-changes"]',
  viewAllChanges: '[data-testid="dashboard-view-all-changes"]',
} as const

/**
 * 变更管理页面选择器
 */
export const ChangeSelectors = {
  listTable: '[data-testid="change-table"]',
  searchForm: '[data-testid="change-search-form"]',
  searchCI: '[data-testid="change-search-ci"]',
  searchType: '[data-testid="change-search-type"]',
  searchStatus: '[data-testid="change-search-status"]',
  searchButton: '[data-testid="change-search-btn"]',
  resetButton: '[data-testid="change-reset-btn"]',
  createButton: '[data-testid="change-create-btn"]',
  viewButton: (id: string) => `[data-testid="change-view-${id}"]`,
  approveButton: (id: string) => `[data-testid="change-approve-${id}"]`,
  pagination: '[data-testid="change-pagination"]',
  form: '[data-testid="change-form"]',
  formCI: '[data-testid="change-form-ci"]',
  formType: '[data-testid="change-form-type"]',
  formReason: '[data-testid="change-form-reason"]',
  formSubmit: '[data-testid="change-form-submit"]',
  formCancel: '[data-testid="change-form-cancel"]',
  detailInfo: '[data-testid="change-detail-info"]',
  detailBack: '[data-testid="change-detail-back-btn"]',
  detailApprove: '[data-testid="change-detail-approve"]',
  detailReject: '[data-testid="change-detail-reject"]',
  detailOldValue: '[data-testid="change-old-value"]',
  detailNewValue: '[data-testid="change-new-value"]',
} as const

/**
 * 角色管理页面选择器
 */
export const RoleSelectors = {
  table: '[data-testid="role-table"]',
  searchForm: '[data-testid="role-search-form"]',
  searchName: '[data-testid="role-search-name"]',
  searchButton: '[data-testid="role-search-btn"]',
  resetButton: '[data-testid="role-reset-btn"]',
  createButton: '[data-testid="role-create-btn"]',
  editButton: (id: string) => `[data-testid="role-edit-${id}"]`,
  permsButton: (id: string) => `[data-testid="role-perms-${id}"]`,
  deleteButton: (id: string) => `[data-testid="role-delete-${id}"]`,
  pagination: '[data-testid="role-pagination"]',
  form: '[data-testid="role-form"]',
  formName: '[data-testid="role-form-name"]',
  formCode: '[data-testid="role-form-code"]',
  formDesc: '[data-testid="role-form-desc"]',
  formPermissions: '[data-testid="role-form-permissions"]',
  formSubmit: '[data-testid="role-form-submit"]',
  formCancel: '[data-testid="role-form-cancel"]',
} as const

/**
 * 审计日志页面选择器
 */
export const AuditSelectors = {
  table: '[data-testid="audit-table"]',
  searchForm: '[data-testid="audit-search-form"]',
  searchUser: '[data-testid="audit-search-user"]',
  searchAction: '[data-testid="audit-search-action"]',
  searchResource: '[data-testid="audit-search-resource"]',
  searchDate: '[data-testid="audit-search-date"]',
  searchButton: '[data-testid="audit-search-btn"]',
  resetButton: '[data-testid="audit-reset-btn"]',
  exportButton: '[data-testid="audit-export-btn"]',
  pagination: '[data-testid="audit-pagination"]',
  detailButton: (id: string) => `[data-testid="audit-detail-${id}"]`,
} as const

/**
 * 关系图页面选择器
 */
export const RelationSelectors = {
  selectCI: '[data-testid="relation-select-ci"]',
  depth: '[data-testid="relation-depth"]',
  refresh: '[data-testid="relation-refresh"]',
  graph: '[data-testid="relation-graph"]',
  nodeDetail: '[data-testid="relation-node-detail"]',
} as const

/**
 * 报表页面选择器
 */
export const ReportSelectors = {
  dateRange: '[data-testid="report-date-range"]',
  refresh: '[data-testid="report-refresh"]',
  export: '[data-testid="report-export"]',
  ciSummary: '[data-testid="report-ci-summary"]',
  changeSummary: '[data-testid="report-change-summary"]',
  userSummary: '[data-testid="report-user-summary"]',
  statusChart: '[data-testid="report-status-chart"]',
  envChart: '[data-testid="report-env-chart"]',
  changeTypeTable: '[data-testid="report-change-type-table"]',
  userRoleTable: '[data-testid="report-user-role-table"]',
} as const
