# CMDB RBAC 权限矩阵

## 1. 角色定义

| 角色代码 | 角色名称 | 描述 |
|----------|----------|------|
| admin | 系统管理员 | 拥有系统全部权限，可管理用户、角色和所有配置项 |
| operator | 运维工程师 | 可操作配置项的增删改查，发起变更申请 |
| viewer | 只读用户 | 仅可查看配置项和审计日志，无修改权限 |
| auditor | 审计员 | 可查看配置项、变更记录和审计日志，可审批变更 |

## 2. 资源类型

| 资源代码 | 资源名称 | 描述 |
|----------|----------|------|
| ci | 配置项 | 所有类型的配置项 |
| ci_server | 服务器配置项 | 服务器类型的配置项 |
| ci_network_device | 网络设备配置项 | 网络设备类型的配置项 |
| ci_database | 数据库配置项 | 数据库类型的配置项 |
| ci_middleware | 中间件配置项 | 中间件类型的配置项 |
| ci_application | 应用配置项 | 应用类型的配置项 |
| ci_container | 容器配置项 | 容器类型的配置项 |
| ci_k8s_resource | K8s 资源配置项 | K8s 资源类型的配置项 |
| ci_cloud_resource | 云资源配置项 | 云资源类型的配置项 |
| user | 用户 | 系统用户 |
| role | 角色 | 系统角色 |
| change | 变更 | 变更记录 |
| audit_log | 审计日志 | 审计日志记录 |

## 3. 权限矩阵

### 3.1 配置项权限

| 角色 | 创建 | 查看 | 编辑 | 删除 | 导出 | 导入 |
|------|------|------|------|------|------|------|
| admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| operator | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| viewer | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| auditor | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |

### 3.2 用户与角色权限

| 角色 | 创建用户 | 管理用户 | 创建角色 | 管理角色 |
|------|----------|----------|----------|----------|
| admin | ✅ | ✅ | ✅ | ✅ |
| operator | ❌ | ❌ | ❌ | ❌ |
| viewer | ❌ | ❌ | ❌ | ❌ |
| auditor | ❌ | ❌ | ❌ | ❌ |

### 3.3 变更管理权限

| 角色 | 发起变更 | 审批变更 | 查看变更 | 取消变更 |
|------|----------|----------|----------|----------|
| admin | ✅ | ✅ | ✅ | ✅ |
| operator | ✅ | ❌ | ✅ | ✅ |
| viewer | ❌ | ❌ | ✅ | ❌ |
| auditor | ❌ | ✅ | ✅ | ❌ |

### 3.4 审计日志权限

| 角色 | 查看 | 导出 | 删除 |
|------|------|------|------|
| admin | ✅ | ✅ | ✅ |
| operator | ✅ | ✅ | ❌ |
| viewer | ✅ | ❌ | ❌ |
| auditor | ✅ | ✅ | ❌ |

## 4. 详细权限列表

### 4.1 系统管理员 (admin)

```
权限代码                              | 资源类型  | 动作
-------------------------------------|----------|----------------------------------
ci:create                            | ci       | 创建配置项
ci:read                              | ci       | 查看配置项
ci:update                            | ci       | 编辑配置项
ci:delete                            | ci       | 删除配置项
ci:export                            | ci       | 导出配置项
ci:import                            | ci       | 导入配置项
user:create                          | user     | 创建用户
user:read                            | user     | 查看用户
user:update                          | user     | 编辑用户
user:delete                          | user     | 删除用户
role:create                          | role     | 创建角色
role:read                            | role     | 查看角色
role:update                          | role     | 编辑角色
role:delete                          | role     | 删除角色
change:create                        | change   | 发起变更
change:read                          | change   | 查看变更
change:approve                       | change   | 审批变更
change:cancel                        | change   | 取消变更
audit_log:read                       | audit_log| 查看审计日志
audit_log:export                     | audit_log| 导出审计日志
```

### 4.2 运维工程师 (operator)

```
权限代码                              | 资源类型  | 动作
-------------------------------------|----------|----------------------------------
ci:create                            | ci       | 创建配置项
ci:read                              | ci       | 查看配置项
ci:update                            | ci       | 编辑配置项
ci:export                            | ci       | 导出配置项
ci:import                            | ci       | 导入配置项
change:create                        | change   | 发起变更
change:read                          | change   | 查看变更
change:cancel                        | change   | 取消变更
audit_log:read                       | audit_log| 查看审计日志
audit_log:export                     | audit_log| 导出审计日志
```

### 4.3 只读用户 (viewer)

```
权限代码                              | 资源类型  | 动作
-------------------------------------|----------|----------------------------------
ci:read                              | ci       | 查看配置项
change:read                          | change   | 查看变更
audit_log:read                       | audit_log| 查看审计日志
```

### 4.4 审计员 (auditor)

```
权限代码                              | 资源类型  | 动作
-------------------------------------|----------|----------------------------------
ci:read                              | ci       | 查看配置项
ci:export                            | ci       | 导出配置项
change:read                          | change   | 查看变更
change:approve                       | change   | 审批变更
audit_log:read                       | audit_log| 查看审计日志
audit_log:export                     | audit_log| 导出审计日志
```

## 5. 权限校验流程

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│   User   │────>│  JWT Token   │────>│  Permission │
│  Request │     │   Extract    │     │    Check    │
└──────────┘     └──────────────┘     └──────┬──────┘
                                              │
                                              ▼
                                      ┌─────────────┐
                                      │  Allow/     │
                                      │   Deny      │
                                      └─────────────┘
```

## 6. 权限代码规范

权限代码采用三段式命名：
```
{resource}:{action}

示例:
- ci:create     - 创建配置项
- user:read     - 查看用户
- change:approve - 审批变更
```

## 7. 超级管理员特权

`is_superuser = true` 的用户拥有以下特权：
- 绕过所有权限检查
- 访问所有受保护的资源
- 执行所有操作

> ⚠️ **注意**: 超级管理员权限应谨慎授予，建议仅用于紧急情况和系统维护。
