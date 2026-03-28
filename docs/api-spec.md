# CMDB 系统 API 接口规范

## 1. API 概述

### 1.1 基础信息

- **基础路径**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 认证机制

所有 API 请求（除登录外）需要在 Header 中携带 JWT Token：

```
Authorization: Bearer <token>
```

### 1.3 通用响应格式

**成功响应:**
```json
{
    "success": true,
    "data": {},
    "message": "操作成功",
    "timestamp": 1711612800
}
```

**错误响应:**
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": []
    },
    "timestamp": 1711612800
}
```

---

## 2. 认证 API

### 2.1 用户登录

**端点:** `POST /api/v1/auth/login`

**请求:**
```json
{
    "username": "admin",
    "password": "password123"
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "expires_in": 86400,
        "user": {
            "id": "uuid",
            "username": "admin",
            "email": "admin@example.com",
            "role": {
                "code": "super_admin",
                "name": "系统管理员"
            }
        }
    }
}
```

### 2.2 Token 刷新

**端点:** `POST /api/v1/auth/refresh`

**请求:**
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "expires_in": 86400
    }
}
```

### 2.3 用户登出

**端点:** `POST /api/v1/auth/logout`

**响应:**
```json
{
    "success": true,
    "message": "登出成功"
}
```

### 2.4 获取当前用户

**端点:** `GET /api/v1/auth/me`

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "管理员",
        "role": {
            "code": "super_admin",
            "name": "系统管理员"
        },
        "permissions": ["ci:create", "ci:read", "..."]
    }
}
```

---

## 3. 配置项 API

### 3.1 获取配置项列表

**端点:** `GET /api/v1/ci`

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| page | integer | 页码，默认 1 |
| page_size | integer | 每页数量，默认 20 |
| ci_type | string | CI 类型筛选 |
| status | string | 状态筛选 |
| environment | string | 环境筛选 |
| keyword | string | 关键字搜索 |
| sort_by | string | 排序字段 |
| sort_order | string | asc/desc |

**响应:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "uuid",
                "name": "web-server-01",
                "ci_type": "server",
                "code": "SRV-001",
                "status": "active",
                "environment": "production",
                "owner": "张三",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}
```

### 3.2 获取配置项详情

**端点:** `GET /api/v1/ci/{id}`

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "web-server-01",
        "ci_type": "server",
        "code": "SRV-001",
        "status": "active",
        "environment": "production",
        "region": "cn-hangzhou",
        "owner": "张三",
        "department": "运维部",
        "description": "Web 应用服务器",
        "attributes": {
            "hostname": "web-01",
            "ip_addresses": ["192.168.1.10"],
            "cpu_cores": 4,
            "memory_gb": 16
        },
        "version": 3,
        "created_by": {
            "id": "uuid",
            "username": "admin"
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "relations": [
            {
                "id": "uuid",
                "target_ci": {
                    "id": "uuid",
                    "name": "app-01"
                },
                "relation_type": "runs_on"
            }
        ]
    }
}
```

### 3.3 创建配置项

**端点:** `POST /api/v1/ci`

**请求:**
```json
{
    "name": "web-server-02",
    "ci_type": "server",
    "code": "SRV-002",
    "environment": "production",
    "owner": "李四",
    "attributes": {
        "hostname": "web-02",
        "ip_addresses": ["192.168.1.11"],
        "cpu_cores": 4,
        "memory_gb": 16
    }
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "web-server-02",
        "ci_type": "server"
    },
    "message": "配置项创建成功"
}
```

### 3.4 更新配置项

**端点:** `PUT /api/v1/ci/{id}`

**请求:**
```json
{
    "name": "web-server-02-updated",
    "owner": "王五",
    "attributes": {
        "memory_gb": 32
    }
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "web-server-02-updated",
        "version": 4
    },
    "message": "配置项更新成功"
}
```

### 3.5 删除配置项

**端点:** `DELETE /api/v1/ci/{id}`

**响应:**
```json
{
    "success": true,
    "message": "配置项已删除"
}
```

### 3.6 批量导入

**端点:** `POST /api/v1/ci/batch/import`

**Content-Type:** `multipart/form-data`

**请求:**
```
file: [Excel/CSV 文件]
```

**响应:**
```json
{
    "success": true,
    "data": {
        "total": 100,
        "success_count": 98,
        "failed_count": 2,
        "failed_items": [
            {
                "row": 5,
                "error": "CI 编码已存在"
            }
        ]
    }
}
```

### 3.7 批量导出

**端点:** `GET /api/v1/ci/batch/export`

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| ci_type | string | CI 类型 |
| ids | array | CI ID 列表 |
| format | string | xls/csv |

**响应:** 文件下载

---

## 4. 关系 API

### 4.1 获取 CI 关系

**端点:** `GET /api/v1/ci/{id}/relations`

**响应:**
```json
{
    "success": true,
    "data": {
        "ci": {
            "id": "uuid",
            "name": "web-server-01"
        },
        "relations": [
            {
                "id": "uuid",
                "source_ci": {
                    "id": "uuid",
                    "name": "app-01"
                },
                "target_ci": {
                    "id": "uuid",
                    "name": "web-server-01"
                },
                "relation_type": "runs_on",
                "description": "应用运行于服务器"
            }
        ]
    }
}
```

### 4.2 创建关系

**端点:** `POST /api/v1/ci/{id}/relations`

**请求:**
```json
{
    "target_ci_id": "uuid",
    "relation_type": "depends_on",
    "description": "依赖于数据库"
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid"
    },
    "message": "关系创建成功"
}
```

### 4.3 删除关系

**端点:** `DELETE /api/v1/relations/{id}`

**响应:**
```json
{
    "success": true,
    "message": "关系已删除"
}
```

---

## 5. 变更 API

### 5.1 获取变更列表

**端点:** `GET /api/v1/changes`

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| page | integer | 页码 |
| page_size | integer | 每页数量 |
| ci_id | string | CI ID |
| change_type | string | 变更类型 |
| status | string | 状态 |
| created_by | string | 创建人 |

**响应:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "uuid",
                "ci": {
                    "id": "uuid",
                    "name": "web-server-01"
                },
                "change_type": "update",
                "status": "approved",
                "change_reason": "内存升级",
                "created_by": {
                    "id": "uuid",
                    "username": "admin"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "approved_at": "2024-01-01T00:01:00Z"
            }
        ],
        "total": 50
    }
}
```

### 5.2 获取变更详情

**端点:** `GET /api/v1/changes/{id}`

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "ci": {
            "id": "uuid",
            "name": "web-server-01"
        },
        "change_type": "update",
        "status": "approved",
        "change_reason": "内存升级",
        "old_values": {
            "attributes": {
                "memory_gb": 16
            }
        },
        "new_values": {
            "attributes": {
                "memory_gb": 32
            }
        },
        "created_by": {
            "id": "uuid",
            "username": "admin"
        },
        "approver": {
            "id": "uuid",
            "username": "super_admin"
        },
        "created_at": "2024-01-01T00:00:00Z",
        "approved_at": "2024-01-01T00:01:00Z"
    }
}
```

### 5.3 创建变更申请

**端点:** `POST /api/v1/changes`

**请求:**
```json
{
    "ci_id": "uuid",
    "change_type": "update",
    "change_reason": "内存升级",
    "new_values": {
        "attributes": {
            "memory_gb": 32
        }
    }
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "status": "pending"
    },
    "message": "变更申请已提交"
}
```

### 5.4 审批变更

**端点:** `POST /api/v1/changes/{id}/approve`

**请求:**
```json
{
    "approved": true,
    "comment": "同意变更"
}
```

**响应:**
```json
{
    "success": true,
    "message": "变更已批准"
}
```

---

## 6. 用户 API

### 6.1 获取用户列表

**端点:** `GET /api/v1/users`

**响应:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "uuid",
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "管理员",
                "role": {
                    "code": "super_admin",
                    "name": "系统管理员"
                },
                "is_active": true,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 10
    }
}
```

### 6.2 创建用户

**端点:** `POST /api/v1/users`

**请求:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "full_name": "新用户",
    "role_id": "uuid"
}
```

### 6.3 更新用户

**端点:** `PUT /api/v1/users/{id}`

**请求:**
```json
{
    "full_name": "更新后的名字",
    "role_id": "uuid",
    "is_active": true
}
```

### 6.4 删除用户

**端点:** `DELETE /api/v1/users/{id}`

---

## 7. 角色 API

### 7.1 获取角色列表

**端点:** `GET /api/v1/roles`

**响应:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "code": "super_admin",
            "name": "系统管理员",
            "description": "完整系统权限",
            "is_system": true,
            "permission_count": 30
        }
    ]
}
```

### 7.2 创建角色

**端点:** `POST /api/v1/roles`

**请求:**
```json
{
    "code": "custom_role",
    "name": "自定义角色",
    "description": "自定义描述",
    "permissions": ["ci:read", "ci:create"]
}
```

### 7.3 更新角色权限

**端点:** `PUT /api/v1/roles/{id}/permissions`

**请求:**
```json
{
    "permissions": ["ci:read", "ci:create", "ci:update"]
}
```

---

## 8. 审计 API

### 8.1 获取审计日志

**端点:** `GET /api/v1/audit-logs`

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| page | integer | 页码 |
| page_size | integer | 每页数量 |
| user_id | string | 用户 ID |
| action | string | 操作类型 |
| resource_type | string | 资源类型 |
| start_time | string | 开始时间 |
| end_time | string | 结束时间 |

**响应:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "uuid",
                "user": {
                    "id": "uuid",
                    "username": "admin"
                },
                "action": "ci_create",
                "resource_type": "ci",
                "resource_id": "uuid",
                "ip_address": "192.168.1.100",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1000
    }
}
```

---

## 9. 报表 API

### 9.1 获取资源统计

**端点:** `GET /api/v1/reports/resource-summary`

**响应:**
```json
{
    "success": true,
    "data": {
        "total_ci": 1000,
        "by_type": [
            {"type": "server", "count": 300},
            {"type": "database", "count": 100},
            {"type": "application", "count": 200}
        ],
        "by_environment": [
            {"environment": "production", "count": 500},
            {"environment": "test", "count": 300},
            {"environment": "development", "count": 200}
        ],
        "by_status": [
            {"status": "active", "count": 950},
            {"status": "inactive", "count": 50}
        ]
    }
}
```

---

## 10. 同步 API

### 10.1 执行同步

**端点:** `POST /api/v1/sync/execute`

**请求:**
```json
{
    "sync_type": "k8s",
    "cluster_id": "uuid"
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "task_id": "uuid",
        "status": "running"
    },
    "message": "同步任务已启动"
}
```

### 10.2 获取同步状态

**端点:** `GET /api/v1/sync/tasks/{id}`

**响应:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "sync_type": "k8s",
        "status": "completed",
        "progress": 100,
        "result": {
            "total": 100,
            "success": 98,
            "failed": 2
        },
        "started_at": "2024-01-01T00:00:00Z",
        "completed_at": "2024-01-01T00:05:00Z"
    }
}
```

---

## 11. 错误码定义

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| SUCCESS | 200 | 操作成功 |
| BAD_REQUEST | 400 | 请求参数错误 |
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| VALIDATION_ERROR | 422 | 验证失败 |

---

## 12. API 版本管理

| 版本 | 状态 | 说明 |
|------|------|------|
| v1 | 当前版本 | 生产环境使用 |

API 版本通过 URL 路径标识：`/api/v1/...`
