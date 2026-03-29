export const mockUsers = [
  { id: '1', username: 'admin', password: 'admin123', name: '管理员', email: 'admin@example.com', role: 'admin', full_name: '系统管理员', status: 'active', is_superuser: true },
  { id: '2', username: 'user', password: 'user123', name: '普通用户', email: 'user@example.com', role: 'user', full_name: '张三', status: 'active', is_superuser: false },
  { id: '3', username: 'ops', password: 'ops123', name: '运维工程师', email: 'ops@example.com', role: 'operator', full_name: '李四', status: 'active', is_superuser: false },
  { id: '4', username: 'developer', password: 'dev123', name: '开发工程师', email: 'developer@example.com', role: 'developer', full_name: '王五', status: 'active', is_superuser: false },
  { id: '5', username: 'viewer', password: 'viewer123', name: '只读用户', email: 'viewer@example.com', role: 'viewer', full_name: '赵六', status: 'active', is_superuser: false },
]

export let mockCIs = [
  { id: '1', name: '生产 Web 服务器 01', code: 'PROD-WEB-001', ci_type: 'server', status: 'online', environment: 'production', ip_address: '192.168.1.101', cpu_cores: 16, memory_gb: 64, disk_gb: 500, owner: '张三', description: '主生产环境 Web 服务器', created_at: '2024-01-01T10:00:00Z', updated_at: '2024-01-15T08:30:00Z' },
  { id: '2', name: '生产 Web 服务器 02', code: 'PROD-WEB-002', ci_type: 'server', status: 'online', environment: 'production', ip_address: '192.168.1.102', cpu_cores: 16, memory_gb: 64, disk_gb: 500, owner: '张三', description: '主生产环境 Web 服务器备用', created_at: '2024-01-02T10:00:00Z', updated_at: '2024-01-20T09:00:00Z' },
  { id: '3', name: '生产应用服务器 01', code: 'PROD-APP-001', ci_type: 'server', status: 'online', environment: 'production', ip_address: '192.168.1.111', cpu_cores: 32, memory_gb: 128, disk_gb: 1000, owner: '李四', description: '核心业务应用服务器', created_at: '2024-01-03T10:00:00Z', updated_at: '2024-02-01T14:00:00Z' },
  { id: '4', name: '生产应用服务器 02', code: 'PROD-APP-002', ci_type: 'server', status: 'maintenance', environment: 'production', ip_address: '192.168.1.112', cpu_cores: 32, memory_gb: 128, disk_gb: 1000, owner: '李四', description: '核心业务应用服务器备用', created_at: '2024-01-04T10:00:00Z', updated_at: '2024-02-10T16:00:00Z' },
  { id: '5', name: '测试 Web 服务器', code: 'TEST-WEB-001', ci_type: 'server', status: 'online', environment: 'testing', ip_address: '192.168.2.101', cpu_cores: 8, memory_gb: 32, disk_gb: 200, owner: '王五', description: '测试环境 Web 服务器', created_at: '2024-01-05T10:00:00Z', updated_at: '2024-01-25T11:00:00Z' },
  { id: '6', name: '测试应用服务器', code: 'TEST-APP-001', ci_type: 'server', status: 'offline', environment: 'testing', ip_address: '192.168.2.111', cpu_cores: 16, memory_gb: 64, disk_gb: 500, owner: '王五', description: '测试环境应用服务器', created_at: '2024-01-06T10:00:00Z', updated_at: '2024-02-05T10:00:00Z' },
  { id: '7', name: '开发 Web 服务器', code: 'DEV-WEB-001', ci_type: 'server', status: 'online', environment: 'development', ip_address: '192.168.3.101', cpu_cores: 4, memory_gb: 16, disk_gb: 100, owner: '赵六', description: '开发环境 Web 服务器', created_at: '2024-01-07T10:00:00Z', updated_at: '2024-01-30T09:00:00Z' },
  { id: '8', name: '开发应用服务器', code: 'DEV-APP-001', ci_type: 'server', status: 'online', environment: 'development', ip_address: '192.168.3.111', cpu_cores: 8, memory_gb: 32, disk_gb: 200, owner: '赵六', description: '开发环境应用服务器', created_at: '2024-01-08T10:00:00Z', updated_at: '2024-02-08T15:00:00Z' },
  { id: '9', name: '生产主数据库', code: 'PROD-DB-001', ci_type: 'database', status: 'online', environment: 'production', db_type: 'MySQL', db_version: '8.0.32', ip_address: '192.168.1.201', port: 3306, owner: '张三', description: '生产环境主数据库', created_at: '2024-01-09T10:00:00Z', updated_at: '2024-02-15T08:00:00Z' },
  { id: '10', name: '生产从数据库', code: 'PROD-DB-002', ci_type: 'database', status: 'online', environment: 'production', db_type: 'MySQL', db_version: '8.0.32', ip_address: '192.168.1.202', port: 3306, owner: '张三', description: '生产环境从数据库', created_at: '2024-01-10T10:00:00Z', updated_at: '2024-02-16T10:00:00Z' },
  { id: '11', name: '生产 Redis 集群', code: 'PROD-REDIS-001', ci_type: 'database', status: 'online', environment: 'production', db_type: 'Redis', db_version: '7.0.5', ip_address: '192.168.1.211', port: 6379, owner: '李四', description: '生产环境 Redis 缓存集群', created_at: '2024-01-11T10:00:00Z', updated_at: '2024-02-12T11:00:00Z' },
  { id: '12', name: '生产 MongoDB', code: 'PROD-MONGO-001', ci_type: 'database', status: 'online', environment: 'production', db_type: 'MongoDB', db_version: '6.0.4', ip_address: '192.168.1.221', port: 27017, owner: '李四', description: '生产环境 MongoDB 文档数据库', created_at: '2024-01-12T10:00:00Z', updated_at: '2024-02-18T14:00:00Z' },
  { id: '13', name: '测试 MySQL', code: 'TEST-DB-001', ci_type: 'database', status: 'online', environment: 'testing', db_type: 'MySQL', db_version: '8.0.32', ip_address: '192.168.2.201', port: 3306, owner: '王五', description: '测试环境 MySQL 数据库', created_at: '2024-01-13T10:00:00Z', updated_at: '2024-01-28T09:00:00Z' },
  { id: '14', name: '测试 Redis', code: 'TEST-REDIS-001', ci_type: 'database', status: 'online', environment: 'testing', db_type: 'Redis', db_version: '7.0.5', ip_address: '192.168.2.211', port: 6379, owner: '王五', description: '测试环境 Redis', created_at: '2024-01-14T10:00:00Z', updated_at: '2024-02-01T10:00:00Z' },
  { id: '15', name: '电商后台管理系统', code: 'PROD-APP-ADMIN', ci_type: 'application', status: 'online', environment: 'production', app_version: 'v2.3.1', language: 'Java', framework: 'Spring Boot', owner: '李四', description: '电商后台管理应用', created_at: '2024-01-15T10:00:00Z', updated_at: '2024-02-20T16:00:00Z' },
  { id: '16', name: '用户中心服务', code: 'PROD-APP-USER', ci_type: 'application', status: 'online', environment: 'production', app_version: 'v1.8.5', language: 'Java', framework: 'Spring Cloud', owner: '张三', description: '用户认证与授权服务', created_at: '2024-01-16T10:00:00Z', updated_at: '2024-02-22T11:00:00Z' },
  { id: '17', name: '订单服务', code: 'PROD-APP-ORDER', ci_type: 'application', status: 'online', environment: 'production', app_version: 'v3.1.2', language: 'Go', framework: 'Gin', owner: '李四', description: '订单处理核心服务', created_at: '2024-01-17T10:00:00Z', updated_at: '2024-02-24T14:00:00Z' },
  { id: '18', name: '支付网关', code: 'PROD-APP-PAY', ci_type: 'application', status: 'online', environment: 'production', app_version: 'v2.0.8', language: 'Java', framework: 'Spring Boot', owner: '张三', description: '第三方支付集成网关', created_at: '2024-01-18T10:00:00Z', updated_at: '2024-02-25T09:00:00Z' },
  { id: '19', name: '商品服务', code: 'PROD-APP-PRODUCT', ci_type: 'application', status: 'offline', environment: 'production', app_version: 'v1.5.3', language: 'Python', framework: 'FastAPI', owner: '王五', description: '商品信息管理服务（维护中）', created_at: '2024-01-19T10:00:00Z', updated_at: '2024-02-26T17:00:00Z' },
  { id: '20', name: '测试后台管理', code: 'TEST-APP-ADMIN', ci_type: 'application', status: 'online', environment: 'testing', app_version: 'v2.4.0-beta', language: 'Java', framework: 'Spring Boot', owner: '王五', description: '测试环境后台管理', created_at: '2024-01-20T10:00:00Z', updated_at: '2024-02-27T10:00:00Z' },
  { id: '21', name: '测试订单服务', code: 'TEST-APP-ORDER', ci_type: 'application', status: 'online', environment: 'testing', app_version: 'v3.2.0-alpha', language: 'Go', framework: 'Gin', owner: '王五', description: '测试环境订单服务', created_at: '2024-01-21T10:00:00Z', updated_at: '2024-02-28T11:00:00Z' },
  { id: '22', name: '生产 Nginx 集群', code: 'PROD-NGINX-001', ci_type: 'middleware', status: 'online', environment: 'production', mw_type: 'Nginx', mw_version: '1.24.0', owner: '张三', description: '生产环境负载均衡与反向代理', created_at: '2024-01-22T10:00:00Z', updated_at: '2024-03-01T08:00:00Z' },
  { id: '23', name: '生产 Kafka 集群', code: 'PROD-KAFKA-001', ci_type: 'middleware', status: 'online', environment: 'production', mw_type: 'Kafka', mw_version: '3.4.0', owner: '李四', description: '生产环境消息队列', created_at: '2024-01-23T10:00:00Z', updated_at: '2024-03-02T09:00:00Z' },
  { id: '24', name: '生产 RabbitMQ', code: 'PROD-MQ-001', ci_type: 'middleware', status: 'online', environment: 'production', mw_type: 'RabbitMQ', mw_version: '3.11.10', owner: '李四', description: '生产环境消息代理', created_at: '2024-01-24T10:00:00Z', updated_at: '2024-03-03T10:00:00Z' },
  { id: '25', name: '生产 Elasticsearch', code: 'PROD-ES-001', ci_type: 'middleware', status: 'online', environment: 'production', mw_type: 'Elasticsearch', mw_version: '8.6.2', owner: '张三', description: '生产环境日志搜索与分析', created_at: '2024-01-25T10:00:00Z', updated_at: '2024-03-04T11:00:00Z' },
  { id: '26', name: '核心交换机', code: 'CORE-SW-001', ci_type: 'network_device', status: 'online', environment: 'production', device_type: 'Switch', vendor: 'Cisco', model: 'Catalyst 9300', ip_address: '192.168.0.1', owner: '张三', description: '数据中心核心交换机', created_at: '2024-01-26T10:00:00Z', updated_at: '2024-03-05T08:00:00Z' },
  { id: '27', name: '边界防火墙', code: 'EDGE-FW-001', ci_type: 'network_device', status: 'online', environment: 'production', device_type: 'Firewall', vendor: 'Fortinet', model: 'FortiGate 600F', ip_address: '10.0.0.1', owner: '张三', description: '互联网边界防火墙', created_at: '2024-01-27T10:00:00Z', updated_at: '2024-03-06T09:00:00Z' },
  { id: '28', name: '负载均衡器', code: 'LB-001', ci_type: 'network_device', status: 'online', environment: 'production', device_type: 'Load Balancer', vendor: 'F5', model: 'BIG-IP i4800', ip_address: '192.168.0.100', owner: '张三', description: '应用负载均衡器', created_at: '2024-01-28T10:00:00Z', updated_at: '2024-03-07T10:00:00Z' },
  { id: '29', name: '生产 K8s 集群', code: 'PROD-K8S-001', ci_type: 'container', status: 'online', environment: 'production', k8s_version: '1.26.3', node_count: 12, owner: '李四', description: '生产环境 Kubernetes 集群', created_at: '2024-01-29T10:00:00Z', updated_at: '2024-03-08T11:00:00Z' },
  { id: '30', name: '测试 K8s 集群', code: 'TEST-K8S-001', ci_type: 'container', status: 'online', environment: 'testing', k8s_version: '1.26.3', node_count: 3, owner: '王五', description: '测试环境 Kubernetes 集群', created_at: '2024-01-30T10:00:00Z', updated_at: '2024-03-09T12:00:00Z' },
]

export let mockChanges = [
  { id: '1', title: 'Web 服务器扩容', description: '增加生产 Web 服务器内存到 128GB', status: 'pending', change_type: 'normal', priority: 'medium', ci_id: '1', ci_name: '生产 Web 服务器 01', ci_code: 'PROD-WEB-001', requester: '张三', approver: null, created_at: '2024-03-01T10:00:00Z', updated_at: '2024-03-01T10:00:00Z', planned_start: '2024-03-10T22:00:00Z', planned_end: '2024-03-11T02:00:00Z' },
  { id: '2', title: '数据库版本升级', description: '将 MySQL 从 8.0.28 升级到 8.0.32', status: 'approved', change_type: 'major', priority: 'high', ci_id: '9', ci_name: '生产主数据库', ci_code: 'PROD-DB-001', requester: '李四', approver: '系统管理员', created_at: '2024-02-28T14:00:00Z', updated_at: '2024-03-02T09:00:00Z', planned_start: '2024-03-15T00:00:00Z', planned_end: '2024-03-15T06:00:00Z' },
  { id: '3', title: 'Kafka 集群扩容', description: '新增 3 个 Kafka broker 节点', status: 'in_progress', change_type: 'normal', priority: 'medium', ci_id: '23', ci_name: '生产 Kafka 集群', ci_code: 'PROD-KAFKA-001', requester: '李四', approver: '系统管理员', created_at: '2024-02-25T09:00:00Z', updated_at: '2024-03-05T15:00:00Z', planned_start: '2024-03-05T14:00:00Z', planned_end: '2024-03-05T18:00:00Z' },
  { id: '4', title: 'Redis 内存优化', description: '调整 Redis 内存策略，优化缓存命中率', status: 'completed', change_type: 'normal', priority: 'low', ci_id: '11', ci_name: '生产 Redis 集群', ci_code: 'PROD-REDIS-001', requester: '张三', approver: '系统管理员', created_at: '2024-02-20T11:00:00Z', updated_at: '2024-02-22T16:00:00Z', planned_start: '2024-02-22T14:00:00Z', planned_end: '2024-02-22T16:00:00Z', actual_start: '2024-02-22T14:00:00Z', actual_end: '2024-02-22T15:30:00Z' },
  { id: '5', title: '紧急安全补丁', description: '修复 Log4j 漏洞 CVE-2024-XXX', status: 'completed', change_type: 'emergency', priority: 'critical', ci_id: '15', ci_name: '电商后台管理系统', ci_code: 'PROD-APP-ADMIN', requester: '张三', approver: '系统管理员', created_at: '2024-02-18T08:00:00Z', updated_at: '2024-02-18T12:00:00Z', planned_start: '2024-02-18T09:00:00Z', planned_end: '2024-02-18T12:00:00Z', actual_start: '2024-02-18T09:00:00Z', actual_end: '2024-02-18T11:30:00Z' },
  { id: '6', title: '支付网关证书更新', description: '更新 SSL 证书，证书即将过期', status: 'rejected', change_type: 'normal', priority: 'high', ci_id: '18', ci_name: '支付网关', ci_code: 'PROD-APP-PAY', requester: '王五', approver: '系统管理员', created_at: '2024-02-15T10:00:00Z', updated_at: '2024-02-16T14:00:00Z', planned_start: '2024-02-20T22:00:00Z', planned_end: '2024-02-20T23:00:00Z', reject_reason: '证书已通过其他方式自动更新，无需手动变更' },
  { id: '7', title: '测试环境部署', description: '部署最新版本到测试环境', status: 'completed', change_type: 'normal', priority: 'low', ci_id: '20', ci_name: '测试后台管理', ci_code: 'TEST-APP-ADMIN', requester: '王五', approver: '李四', created_at: '2024-02-10T09:00:00Z', updated_at: '2024-02-10T11:00:00Z', planned_start: '2024-02-10T10:00:00Z', planned_end: '2024-02-10T11:00:00Z', actual_start: '2024-02-10T10:00:00Z', actual_end: '2024-02-10T10:45:00Z' },
  { id: '8', title: 'Nginx 配置优化', description: '优化负载均衡策略，添加健康检查', status: 'completed', change_type: 'normal', priority: 'medium', ci_id: '22', ci_name: '生产 Nginx 集群', ci_code: 'PROD-NGINX-001', requester: '张三', approver: '系统管理员', created_at: '2024-02-05T14:00:00Z', updated_at: '2024-02-06T10:00:00Z', planned_start: '2024-02-06T08:00:00Z', planned_end: '2024-02-06T10:00:00Z', actual_start: '2024-02-06T08:00:00Z', actual_end: '2024-02-06T09:30:00Z' },
]

export let mockAuditLogs = [
  { id: '1', user: 'admin', action: 'login', resource_type: 'user', resource_id: '1', resource_name: 'admin', operation: 'read', details: '用户登录成功', ip_address: '192.168.1.100', user_agent: 'Chrome/122.0', timestamp: '2024-03-09T15:30:00Z' },
  { id: '2', user: 'admin', action: 'create', resource_type: 'ci', resource_id: '30', resource_name: '测试 K8s 集群', operation: 'create', details: '创建配置项: 测试 K8s 集群', ip_address: '192.168.1.100', user_agent: 'Chrome/122.0', timestamp: '2024-03-09T14:00:00Z' },
  { id: '3', user: '张三', action: 'update', resource_type: 'ci', resource_id: '1', resource_name: '生产 Web 服务器 01', operation: 'update', details: '更新配置项: 内存从 32GB 升级到 64GB', ip_address: '192.168.1.101', user_agent: 'Chrome/122.0', timestamp: '2024-03-09T11:30:00Z' },
  { id: '4', user: '李四', action: 'update', resource_type: 'ci', resource_id: '23', resource_name: '生产 Kafka 集群', operation: 'update', details: '新增 broker 节点: kafka-broker-04, kafka-broker-05, kafka-broker-06', ip_address: '192.168.1.102', user_agent: 'Chrome/122.0', timestamp: '2024-03-09T10:00:00Z' },
  { id: '5', user: 'admin', action: 'approve', resource_type: 'change', resource_id: '2', resource_name: '数据库版本升级', operation: 'approve', details: '批准变更申请', ip_address: '192.168.1.100', user_agent: 'Chrome/122.0', timestamp: '2024-03-09T09:00:00Z' },
  { id: '6', user: '王五', action: 'create', resource_type: 'change', resource_id: '1', resource_name: 'Web 服务器扩容', operation: 'create', details: '创建变更申请', ip_address: '192.168.1.103', user_agent: 'Chrome/122.0', timestamp: '2024-03-08T16:00:00Z' },
  { id: '7', user: '张三', action: 'delete', resource_type: 'ci', resource_id: '31', resource_name: '废弃服务器', operation: 'delete', details: '删除配置项: 废弃服务器', ip_address: '192.168.1.101', user_agent: 'Chrome/122.0', timestamp: '2024-03-08T14:00:00Z' },
  { id: '8', user: 'admin', action: 'create', resource_type: 'user', resource_id: '5', resource_name: 'viewer', operation: 'create', details: '创建用户: viewer', ip_address: '192.168.1.100', user_agent: 'Chrome/122.0', timestamp: '2024-03-08T11:00:00Z' },
  { id: '9', user: '李四', action: 'view', resource_type: 'dashboard', resource_id: null, resource_name: '仪表盘', operation: 'read', details: '访问仪表盘', ip_address: '192.168.1.102', user_agent: 'Chrome/122.0', timestamp: '2024-03-08T10:00:00Z' },
  { id: '10', user: '张三', action: 'export', resource_type: 'report', resource_id: null, resource_name: '配置项报表', operation: 'read', details: '导出配置项报表 (Excel)', ip_address: '192.168.1.101', user_agent: 'Chrome/122.0', timestamp: '2024-03-07T17:00:00Z' },
  { id: '11', user: '王五', action: 'login', resource_type: 'user', resource_id: '3', resource_name: 'ops', operation: 'read', details: '用户登录成功', ip_address: '192.168.1.103', user_agent: 'Firefox/123.0', timestamp: '2024-03-07T09:00:00Z' },
  { id: '12', user: 'admin', action: 'update', resource_type: 'user', resource_id: '3', resource_name: 'ops', operation: 'update', details: '更新用户角色: operator -> admin', ip_address: '192.168.1.100', user_agent: 'Chrome/122.0', timestamp: '2024-03-06T15:00:00Z' },
]

export const getDashboardStats = () => {
  const cis = mockCIs
  const changes = mockChanges
  
  const cisByType = cis.reduce((acc, ci) => {
    acc[ci.ci_type] = (acc[ci.ci_type] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const cisByStatus = cis.reduce((acc, ci) => {
    acc[ci.status] = (acc[ci.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const cisByEnvironment = cis.reduce((acc, ci) => {
    acc[ci.environment] = (acc[ci.environment] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const changesByStatus = changes.reduce((acc, change) => {
    acc[change.status] = (acc[change.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const changesByType = changes.reduce((acc, change) => {
    acc[change.change_type] = (acc[change.change_type] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  return {
    total_cis: cis.length,
    online_cis: cis.filter(c => c.status === 'online').length,
    offline_cis: cis.filter(c => c.status === 'offline').length,
    maintenance_cis: cis.filter(c => c.status === 'maintenance').length,
    total_changes: changes.length,
    pending_changes: changes.filter(c => c.status === 'pending').length,
    in_progress_changes: changes.filter(c => c.status === 'in_progress').length,
    completed_changes: changes.filter(c => c.status === 'completed').length,
    cis_by_type: cisByType,
    cis_by_status: cisByStatus,
    cis_by_environment: cisByEnvironment,
    changes_by_status: changesByStatus,
    changes_by_type: changesByType,
  }
}

export const getDashboardData = () => {
  const cis = mockCIs
  const changes = mockChanges
  const users = mockUsers
  const totalCis = cis.length
  
  const cisByType = cis.reduce((acc, ci) => {
    acc[ci.ci_type] = (acc[ci.ci_type] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const cisByEnvironment = cis.reduce((acc, ci) => {
    acc[ci.environment] = (acc[ci.environment] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const ciTypeDistribution = Object.entries(cisByType).map(([ci_type, count]) => ({
    ci_type,
    count,
    percentage: Math.round((count / totalCis) * 100),
  }))
  
  const environmentDistribution = Object.entries(cisByEnvironment).map(([environment, count]) => ({
    environment,
    count,
    percentage: Math.round((count / totalCis) * 100),
  }))
  
  const recentChanges = changes.slice(0, 5).map(change => ({
    id: parseInt(change.id),
    ci_name: change.ci_name,
    change_type: change.change_type === 'major' ? 'update' : change.change_type === 'normal' ? 'update' : change.change_type === 'emergency' ? 'update' : 'create',
    status: change.status,
    created_at: change.created_at,
    created_by: change.requester,
  }))
  
  return {
    stats: {
      total_cis: cis.length,
      online_cis: cis.filter(c => c.status === 'online').length,
      offline_cis: cis.filter(c => c.status === 'offline').length,
      maintenance_cis: cis.filter(c => c.status === 'maintenance').length,
      total_changes: changes.length,
      pending_changes: changes.filter(c => c.status === 'pending').length,
      total_users: users.length,
      active_users: users.filter(u => u.status === 'active').length,
    },
    ci_type_distribution: ciTypeDistribution,
    environment_distribution: environmentDistribution,
    change_trend: [],
    recent_changes: recentChanges,
  }
}