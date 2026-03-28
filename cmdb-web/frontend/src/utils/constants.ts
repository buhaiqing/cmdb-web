/**
 * 配置项类型选项
 */
export const CI_TYPE_OPTIONS = [
  { label: '服务器', value: 'server' },
  { label: '网络设备', value: 'network_device' },
  { label: '数据库', value: 'database' },
  { label: '中间件', value: 'middleware' },
  { label: '应用', value: 'application' },
  { label: '容器', value: 'container' },
  { label: 'K8s 资源', value: 'k8s_resource' },
  { label: '云资源', value: 'cloud_resource' }
]

/**
 * 配置项状态选项
 */
export const CI_STATUS_OPTIONS = [
  { label: '在线', value: 'online', type: 'success' },
  { label: '离线', value: 'offline', type: 'info' },
  { label: '维护中', value: 'maintenance', type: 'warning' },
  { label: '故障', value: 'error', type: 'danger' },
  { label: '已退役', value: 'retired', type: 'info' }
]

/**
 * 用户状态选项
 */
export const USER_STATUS_OPTIONS = [
  { label: '活跃', value: 'active', type: 'success' },
  { label: '未激活', value: 'inactive', type: 'info' },
  { label: '已禁用', value: 'disabled', type: 'danger' }
]

/**
 * 分页选项
 */
export const PAGE_SIZE_OPTIONS = [
  { label: '10 条/页', value: 10 },
  { label: '20 条/页', value: 20 },
  { label: '50 条/页', value: 50 },
  { label: '100 条/页', value: 100 }
]

/**
 * 角色选项
 */
export const ROLE_OPTIONS = [
  { label: '系统管理员', value: 'admin' },
  { label: '运维工程师', value: 'operator' },
  { label: '只读用户', value: 'viewer' },
  { label: '审计员', value: 'auditor' }
]

/**
 * 变更类型选项
 */
export const CHANGE_TYPE_OPTIONS = [
  { label: '创建', value: 'create' },
  { label: '更新', value: 'update' },
  { label: '删除', value: 'delete' },
  { label: '回滚', value: 'rollback' }
]

/**
 * 变更状态选项
 */
export const CHANGE_STATUS_OPTIONS = [
  { label: '待处理', value: 'pending', type: 'warning' },
  { label: '审批中', value: 'reviewing', type: 'info' },
  { label: '已批准', value: 'approved', type: 'success' },
  { label: '已拒绝', value: 'rejected', type: 'danger' },
  { label: '已完成', value: 'completed', type: 'success' },
  { label: '已取消', value: 'cancelled', type: 'info' }
]

/**
 * 变更优先级选项
 */
export const CHANGE_PRIORITY_OPTIONS = [
  { label: '低', value: 'low', type: 'info' },
  { label: '中', value: 'medium', type: '' },
  { label: '高', value: 'high', type: 'warning' },
  { label: '紧急', value: 'critical', type: 'danger' }
]

/**
 * 审计动作选项
 */
export const AUDIT_ACTION_OPTIONS = [
  { label: '登录', value: 'login' },
  { label: '登出', value: 'logout' },
  { label: '创建资源', value: 'create_resource' },
  { label: '更新资源', value: 'update_resource' },
  { label: '删除资源', value: 'delete_resource' },
  { label: '查看资源', value: 'view_resource' },
  { label: '导出资源', value: 'export_resource' },
  { label: '导入资源', value: 'import_resource' },
  { label: '变更审批', value: 'approve_change' },
  { label: '变更拒绝', value: 'reject_change' }
]

/**
 * 审计状态选项
 */
export const AUDIT_STATUS_OPTIONS = [
  { label: '成功', value: 'success', type: 'success' },
  { label: '失败', value: 'failed', type: 'danger' }
]

/**
 * K8s 资源类型选项
 */
export const K8S_RESOURCE_TYPE_OPTIONS = [
  { label: 'Pod', value: 'pod' },
  { label: 'Deployment', value: 'deployment' },
  { label: 'Service', value: 'service' },
  { label: 'ConfigMap', value: 'configmap' },
  { label: 'Secret', value: 'secret' },
  { label: 'Namespace', value: 'namespace' },
  { label: 'Ingress', value: 'ingress' },
  { label: 'PersistentVolume', value: 'persistentvolume' },
  { label: 'PersistentVolumeClaim', value: 'persistentvolumeclaim' }
]

/**
 * 云平台类型选项
 */
export const CLOUD_PROVIDER_OPTIONS = [
  { label: '阿里云', value: 'aliyun' },
  { label: 'AWS', value: 'aws' },
  { label: '腾讯云', value: 'tencent' },
  { label: '华为云', value: 'huawei' }
]

/**
 * 关系类型选项
 */
export const RELATION_TYPE_OPTIONS = [
  { label: '依赖', value: 'depends_on' },
  { label: '连接', value: 'connects_to' },
  { label: '运行于', value: 'runs_on' },
  { label: '包含', value: 'contains' },
  { label: '部署于', value: 'deployed_on' }
]

/**
 * 获取配置项类型标签
 */
export function getCITypeLabel(type: string): string {
  const option = CI_TYPE_OPTIONS.find(opt => opt.value === type)
  return option?.label || type
}

/**
 * 获取配置项状态标签和类型
 */
export function getCIStatusInfo(status: string): { label: string; type: string } {
  const option = CI_STATUS_OPTIONS.find(opt => opt.value === status)
  return {
    label: option?.label || status,
    type: option?.type || ''
  }
}

/**
 * 获取用户状态标签和类型
 */
export function getUserStatusInfo(status: string): { label: string; type: string } {
  const option = USER_STATUS_OPTIONS.find(opt => opt.value === status)
  return {
    label: option?.label || status,
    type: option?.type || ''
  }
}
