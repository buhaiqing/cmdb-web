# CMDB 前端设计文档

## 1. 概述

本文档描述 CMDB 系统前端的设计规范，包括技术选型、组件设计、页面布局和交互规范。

### 1.1 技术栈

| 技术 | 选型 | 说明 |
|------|------|------|
| 框架 | Vue 3.4 | Composition API |
| 语言 | TypeScript 5.3 | 严格模式 |
| 构建工具 | Vite 5.0 | 快速开发和构建 |
| 状态管理 | Pinia 2.1 | 轻量级状态管理 |
| UI 组件库 | Element Plus 2.5 | 企业级组件库 |
| 路由 | Vue Router 4.2 | 单页应用路由 |
| HTTP 客户端 | Axios 1.6 | HTTP 请求封装 |
| E2E 测试 | Playwright 1.41 | 端到端测试 |

### 1.2 目录结构

```
frontend/src/
├── api/              # API 客户端
│   ├── request.ts    # HTTP 请求封装
│   ├── auth.ts       # 认证 API
│   └── ci.ts         # 配置项 API
├── components/       # 通用组件
│   ├── DataTable.vue
│   ├── SearchForm.vue
│   └── LoadingSpinner.vue
├── views/            # 页面视图
│   ├── Login.vue
│   ├── Layout.vue
│   ├── ci/
│   │   ├── CIList.vue
│   │   └── CIDetail.vue
│   └── user/
│       └── UserList.vue
├── stores/           # Pinia 状态管理
│   ├── user.ts
│   └── ci.ts
├── router/           # 路由配置
│   └── index.ts
├── types/            # TypeScript 类型定义
│   └── index.ts
├── utils/            # 工具函数
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
├── App.vue           # 根组件
└── main.ts           # 应用入口
```

## 2. 通用组件设计

### 2.1 DataTable 组件

封装 Element Plus 的 el-table 组件，提供统一的数据表格展示。

**Props**
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| data | array | [] | 表格数据 |
| columns | array | [] | 列配置 |
| loading | boolean | false | 加载状态 |
| pagination | boolean | true | 是否显示分页 |
| total | number | 0 | 总记录数 |

**Events**
- `page-change`: 分页变化
- `sort-change`: 排序变化
- `view`: 点击查看
- `edit`: 点击编辑
- `delete`: 点击删除

**测试标识**: `data-testid="data-table"`

### 2.2 SearchForm 组件

动态搜索表单组件，支持多种输入类型。

**Props**
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| fields | array | [] | 字段配置 |
| inline | boolean | true | 是否行内布局 |
| loading | boolean | false | 搜索加载状态 |

**Events**
- `search`: 点击搜索
- `reset`: 点击重置

**测试标识**: `data-testid="search-form"`

### 2.3 LoadingSpinner 组件

加载状态指示器。

**Props**
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| size | string | 'default' | 尺寸 |
| text | string | '' | 提示文本 |
| fullscreen | boolean | false | 是否全屏 |

## 3. 页面设计

### 3.1 登录页 (Login.vue)

**功能**
- 用户名/密码登录表单
- 忘记密码链接
- 用户注册入口
- 登录状态反馈

**UI 布局**
```
┌─────────────────────────────────┐
│                                 │
│     ┌───────────────────┐       │
│     │    CMDB 系统       │       │
│     │                   │       │
│     │  用户名：[____]   │       │
│     │  密码：  [____]   │       │
│     │                   │       │
│     │  [登录] [注册]    │       │
│     │                   │       │
│     └───────────────────┘       │
│                                 │
└─────────────────────────────────┘
```

**测试标识**
- 用户名输入框：`data-testid="input-username"`
- 密码输入框：`data-testid="input-password"`
- 登录按钮：`data-testid="btn-login"`
- 注册链接：`data-testid="link-register"`

### 3.2 布局页 (Layout.vue)

**功能**
- 顶部导航栏
- 侧边栏菜单
- 主内容区域
- 用户信息展示

**UI 布局**
```
┌─────────────────────────────────────────────┐
│  CMDB Logo    导航菜单           用户信息 ▾ │
├──────────────┬──────────────────────────────┤
│              │                              │
│  侧边菜单     │        主内容区域             │
│  - 配置项     │                              │
│  - 用户管理   │                              │
│  - 变更记录   │                              │
│  - 审计日志   │                              │
│              │                              │
└──────────────┴──────────────────────────────┘
```

### 3.3 配置项列表页 (CIList.vue)

**功能**
- 搜索/过滤表单
- 数据表格展示
- 分页功能
- 新建/编辑/删除操作
- 状态标签显示

**UI 布局**
```
┌─────────────────────────────────────────────┐
│  [搜索表单]                    [+ 新建]     │
├─────────────────────────────────────────────┤
│  │ 名称 │ 类型 │ 状态 │ 负责人 │ 操作 │    │
│  │------│------│------│--------│------│    │
│  │      │      │      │        │      │    │
│  │      │      │      │        │      │    │
├─────────────────────────────────────────────┤
│              [分页组件]                      │
└─────────────────────────────────────────────┘
```

**测试标识**
- 搜索按钮：`data-testid="btn-search"`
- 新建按钮：`data-testid="btn-create"`
- 表格行：`data-testid="table-row-{id}"`
- 编辑按钮：`data-testid="action-edit"`
- 删除按钮：`data-testid="action-delete"`

### 3.4 配置项详情页 (CIDetail.vue)

**功能**
- 配置项基本信息展示
- 配置项关系图
- 变更历史记录
- 编辑/删除操作

### 3.5 用户列表页 (UserList.vue)

**功能**
- 用户列表展示
- 用户搜索/过滤
- 创建/编辑用户
- 分配角色权限

## 4. 状态管理

### 4.1 User Store

```typescript
interface UserState {
  userInfo: UserInfo | null
  token: string | null
  isLoggedIn: boolean
  username: string
  isSuperUser: boolean
}

// Actions
- setToken(token: string)
- setUserInfo(info: UserInfo)
- logout()
```

### 4.2 CI Store

```typescript
interface CIState {
  ciList: CI[]
  total: number
  loading: boolean
  currentCI: CI | null
}

// Actions
- setCIList(items: CI[], total: number)
- setCurrentCI(ci: CI | null)
- setLoading(loading: boolean)
```

## 5. 路由设计

```typescript
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/cis',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'cis',
        name: 'CIList',
        component: () => import('@/views/ci/CIList.vue')
      },
      {
        path: 'cis/:id',
        name: 'CIDetail',
        component: () => import('@/views/ci/CIDetail.vue')
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/user/UserList.vue')
      }
    ]
  }
]
```

## 6. API 调用规范

### 6.1 请求封装

```typescript
// api/request.ts
export const http = {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>>
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>>
  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>>
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>>
}
```

### 6.2 错误处理

```typescript
// 统一错误处理
try {
  const response = await http.get('/cis')
  // 处理成功响应
} catch (error) {
  // 错误已在拦截器处理，显示 ElMessage
}
```

## 7. UI/UX 规范

### 7.1 颜色规范

| 用途 | 颜色值 | 说明 |
|------|--------|------|
| 主色 | #409EFF | Element Plus 主色 |
| 成功 | #67C23A | 成功状态 |
| 警告 | #E6A23C | 警告状态 |
| 危险 | #F56C6C | 危险/删除 |
| 信息 | #909399 | 信息提示 |

### 7.2 状态标签

| 状态 | 标签类型 |
|------|----------|
| online | success |
| offline | info |
| maintenance | warning |
| error | danger |
| retired | info |

### 7.3 交互反馈

- 操作成功：ElMessage.success()
- 操作失败：ElMessage.error()
- 确认操作：ElMessageBox.confirm()
- 加载状态：loading 属性控制

### 7.4 表单验证

```typescript
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 50, message: '长度在 4 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少 8 位', trigger: 'blur' }
  ]
}
```

## 8. 自动化测试支持

### 8.1 Data Test ID 规范

所有可交互元素必须添加 `data-testid` 属性：
- 按钮：`data-testid="btn-{action}"`
- 输入框：`data-testid="input-{field}"`
- 表格：`data-testid="table-{entity}"`
- 对话框：`data-testid="dialog-{name}"`

### 8.2 加载状态

所有异步操作必须有明确的加载状态指示：
- 按钮 loading 状态
- 表格 loading 状态
- 全屏 loading（必要时）

### 8.3 路由可预测性

- 使用命名路由
- 明确的路由守卫
- 统一的认证检查
