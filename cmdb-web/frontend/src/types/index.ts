/**
 * API 响应数据类型
 */
export interface ApiResponse<T = unknown> {
  success: boolean
  message: string
  data?: T
  error?: {
    code: string
    message: string
    details?: string[]
  }
}

/**
 * 分页响应数据类型
 */
export interface PaginatedResponse<T = unknown> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/**
 * 用户信息
 */
export interface UserInfo {
  id: number
  username: string
  email: string
  phone?: string
  role_ids: number[]
  is_superuser: boolean
  status: 'active' | 'inactive' | 'disabled'
  created_at: string
  updated_at: string
}

/**
 * 角色信息
 */
export interface RoleInfo {
  id: number
  name: string
  code: string
  description?: string
  permission_ids: number[]
  created_at: string
  updated_at: string
}

/**
 * 权限信息
 */
export interface PermissionInfo {
  id: number
  name: string
  code: string
  resource_type: string
  actions: string[]
  description?: string
}

/**
 * 配置项基础信息
 */
export interface CI {
  id: number
  name: string
  type: CIType
  status: CIStatus
  description?: string
  owner?: string
  tags?: string[]
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number
}

/**
 * 配置项类型
 */
export type CIType =
  | 'server'
  | 'network_device'
  | 'database'
  | 'middleware'
  | 'application'
  | 'container'
  | 'k8s_resource'
  | 'cloud_resource'

/**
 * 配置项状态
 */
export type CIStatus = 'online' | 'offline' | 'maintenance' | 'error' | 'retired'

/**
 * 服务器类型配置项
 */
export interface ServerCI extends CI {
  type: 'server'
  hostname: string
  ip_address: string
  os_type: string
  os_version: string
  cpu_cores: number
  memory_gb: number
  disk_gb: number
}

/**
 * 网络设备类型配置项
 */
export interface NetworkDeviceCI extends CI {
  type: 'network_device'
  device_type: string
  vendor: string
  model: string
  ip_address: string
  mac_address: string
  port_count: number
}

/**
 * 数据库类型配置项
 */
export interface DatabaseCI extends CI {
  type: 'database'
  db_type: string
  version: string
  host: string
  port: number
  instance_name: string
  max_connections: number
}

/**
 * 中间件类型配置项
 */
export interface MiddlewareCI extends CI {
  type: 'middleware'
  middleware_type: string
  version: string
  host: string
  port: number
  cluster_nodes?: string[]
}

/**
 * 应用类型配置项
 */
export interface ApplicationCI extends CI {
  type: 'application'
  app_type: string
  version: string
  deploy_url: string
  health_check_url?: string
  dependencies?: number[]
}

/**
 * 容器类型配置项
 */
export interface ContainerCI extends Omit<CI, 'status'> {
  type: 'container'
  container_id: string
  image: string
  host: string
  status: 'running' | 'stopped' | 'paused' | 'error'
  ports: string[]
  created_at_time: string
}

/**
 * K8s 资源类型配置项
 */
export interface K8sResourceCI extends CI {
  type: 'k8s_resource'
  resource_type: string
  namespace: string
  cluster_name: string
  yaml_config?: string
  replicas?: number
}

/**
 * 云资源类型配置项
 */
export interface CloudResourceCI extends CI {
  type: 'cloud_resource'
  cloud_provider: string
  region: string
  instance_type: string
  instance_id: string
  public_ip?: string
  private_ip?: string
}

/**
 * 配置项关系
 */
export interface CIRelation {
  id: number
  source_ci_id: number
  target_ci_id: number
  relation_type: string
  description?: string
  created_at: string
}

/**
 * 变更记录
 */
export interface ChangeRecord {
  id: number
  ci_id: number
  ci_name: string
  change_type: ChangeType
  change_status: ChangeStatus
  priority: ChangePriority
  description: string
  reason?: string
  planned_start_time?: string
  planned_end_time?: string
  actual_start_time?: string
  actual_end_time?: string
  requested_by: number
  approved_by?: number
  created_at: string
  updated_at: string
}

/**
 * 变更类型
 */
export type ChangeType = 'create' | 'update' | 'delete' | 'rollback'

/**
 * 变更状态
 */
export type ChangeStatus = 'pending' | 'reviewing' | 'approved' | 'rejected' | 'completed' | 'cancelled'

/**
 * 变更优先级
 */
export type ChangePriority = 'low' | 'medium' | 'high' | 'critical'

/**
 * 审计日志
 */
export interface AuditLog {
  id: number
  user_id: number
  username: string
  action: AuditAction
  status: AuditStatus
  resource_type?: string
  resource_id?: number
  request_method?: string
  request_path?: string
  ip_address?: string
  user_agent?: string
  details?: string
  created_at: string
}

/**
 * 审计动作
 */
export type AuditAction =
  | 'login'
  | 'logout'
  | 'create_resource'
  | 'update_resource'
  | 'delete_resource'
  | 'view_resource'
  | 'export_resource'
  | 'import_resource'
  | 'approve_change'
  | 'reject_change'

/**
 * 审计状态
 */
export type AuditStatus = 'success' | 'failed'

/**
 * 登录请求参数
 */
export interface LoginRequest {
  username: string
  password: string
}

/**
 * 登录响应数据
 */
export interface LoginResponse {
  token: string
  user: UserInfo
}

/**
 * 注册请求参数
 */
export interface RegisterRequest {
  username: string
  email: string
  password: string
  confirm_password: string
}

/**
 * 分页参数
 */
export interface PaginationParams {
  page?: number
  page_size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

/**
 * 搜索参数
 */
export interface CISearchParams extends PaginationParams {
  search?: string
  type?: CIType
  status?: CIStatus
  owner?: string
  created_after?: string
  created_before?: string
}
