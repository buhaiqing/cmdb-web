# CMDB API 接口文档

## 1. 概述

本文档描述 CMDB 系统的 RESTful API 接口规范。

**基础信息**
- Base URL: `/api`
- 认证方式：JWT Bearer Token
- 响应格式：JSON

**统一响应格式**
```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "error": null
}
```

**错误响应格式**
```json
{
  "success": false,
  "message": "错误描述",
  "error": {
    "code": "ERROR_CODE",
    "message": "详细错误信息",
    "details": []
  }
}
```

## 2. 认证接口

### 2.1 用户登录

**POST** `/auth/login`

**请求头**
```
Content-Type: application/x-www-form-urlencoded
```

**请求体**
```
username: string (required)
password: string (required)
```

**响应示例**
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 2.2 用户注册

**POST** `/auth/register`

**请求体**
```json
{
  "username": "string (required, 4-50 chars)",
  "email": "string (required, email format)",
  "password": "string (required, min 8 chars)",
  "full_name": "string (optional)"
}
```

**响应示例**
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2.3 获取当前用户

**GET** `/auth/me`

**请求头**
```
Authorization: Bearer {token}
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "系统管理员",
    "status": "active",
    "is_superuser": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## 3. 配置项接口

### 3.1 获取配置项列表

**GET** `/cis`

**查询参数**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| ci_type | string | 否 | 配置项类型 |
| status | string | 否 | 状态 |
| environment | string | 否 | 环境 |
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 10 |

**响应示例**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "ci_type": "server",
        "name": "Web Server 01",
        "code": "SRV-WEB-001",
        "status": "online",
        "environment": "production",
        "owner": "张三",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

### 3.2 搜索配置项

**POST** `/cis/search`

**请求体**
```json
{
  "ci_type": "server",
  "name": "Web Server",
  "code": "SRV",
  "status": "online",
  "environment": "production",
  "owner": "张三",
  "page": 1,
  "page_size": 10
}
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 50,
    "page": 1,
    "page_size": 10,
    "total_pages": 5
  }
}
```

### 3.3 获取配置项详情

**GET** `/cis/{id}`

**路径参数**
| 参数 | 类型 | 描述 |
|------|------|------|
| id | integer | 配置项 ID |

**响应示例**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "ci_type": "server",
    "name": "Web Server 01",
    "code": "SRV-WEB-001",
    "status": "online",
    "description": "主要 Web 服务器",
    "environment": "production",
    "owner": "张三",
    "tags": {"dept": "技术部", "cost_center": "CC001"},
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 3.4 创建配置项

**POST** `/cis`

**请求体**
```json
{
  "ci_type": "server",
  "name": "Web Server 01",
  "code": "SRV-WEB-001",
  "description": "主要 Web 服务器",
  "status": "online",
  "environment": "production",
  "owner": "张三",
  "tags": {"dept": "技术部"}
}
```

**响应示例**
```json
{
  "success": true,
  "message": "创建成功",
  "data": {
    "id": 1,
    "ci_type": "server",
    "name": "Web Server 01",
    "code": "SRV-WEB-001",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 3.5 更新配置项

**PUT** `/cis/{id}`

**请求体**
```json
{
  "name": "Web Server 01 (Updated)",
  "description": "更新后的描述",
  "status": "maintenance",
  "owner": "李四"
}
```

**响应示例**
```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "ci_type": "server",
    "name": "Web Server 01 (Updated)",
    "updated_at": "2024-01-02T00:00:00Z"
  }
}
```

### 3.6 删除配置项

**DELETE** `/cis/{id}`

**响应示例**
```json
{
  "success": true,
  "message": "删除成功"
}
```

### 3.7 获取配置项关系

**GET** `/cis/{id}/relations`

**响应示例**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "source_ci_id": 1,
      "target_ci_id": 2,
      "relation_type": "depends_on",
      "description": "依赖关系",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 3.8 创建配置项关系

**POST** `/cis/{ci_id}/relations`

**请求体**
```json
{
  "target_ci_id": 2,
  "relation_type": "depends_on",
  "description": "依赖关系"
}
```

### 3.9 删除配置项关系

**DELETE** `/cis/relations/{id}`

## 4. 用户管理接口

### 4.1 获取用户列表

**GET** `/users`

**查询参数**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |

**响应示例**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "status": "active",
        "is_superuser": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 10
  }
}
```

### 4.2 创建用户

**POST** `/users`

**请求体**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "Password123!",
  "full_name": "新用户",
  "role_ids": [2]
}
```

### 4.3 更新用户

**PUT** `/users/{id}`

**请求体**
```json
{
  "email": "updated@example.com",
  "full_name": "更新后的名字",
  "status": "inactive",
  "role_ids": [2, 3]
}
```

### 4.4 删除用户

**DELETE** `/users/{id}`

## 5. 变更管理接口

### 5.1 获取变更列表

**GET** `/changes`

**查询参数**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| ci_id | integer | 否 | 配置项 ID |
| change_type | string | 否 | 变更类型 |
| change_status | string | 否 | 变更状态 |
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |

### 5.2 创建变更申请

**POST** `/changes`

**请求体**
```json
{
  "ci_id": 1,
  "change_type": "update",
  "description": "更新服务器配置",
  "reason": "性能优化需要",
  "priority": "high",
  "planned_start_time": "2024-01-10T10:00:00Z",
  "planned_end_time": "2024-01-10T12:00:00Z"
}
```

### 5.3 审批变更

**POST** `/changes/{id}/approve`

**请求体**
```json
{
  "approved": true,
  "comment": "同意变更"
}
```

## 6. 审计日志接口

### 6.1 获取审计日志列表

**GET** `/audit-logs`

**查询参数**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| user_id | integer | 否 | 用户 ID |
| action | string | 否 | 操作类型 |
| status | string | 否 | 状态 |
| start_time | string | 否 | 开始时间 |
| end_time | string | 否 | 结束时间 |
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |

## 7. 健康检查

### 7.1 健康检查端点

**GET** `/health`

**响应示例**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "cache": "connected",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## 8. 错误码

| 错误码 | HTTP 状态码 | 描述 |
|--------|------------|------|
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| BAD_REQUEST | 400 | 请求参数错误 |
| CONFLICT | 409 | 资源冲突 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
