# CMDB 系统前端设计文档

## 1. 页面布局设计

### 1.1 整体布局

```
┌────────────────────────────────────────────────────────────┐
│                      Header (64px)                          │
│  [Logo] [导航菜单]                           [用户] [通知]   │
├─────────────┬──────────────────────────────────────────────┤
│             │                                               │
│  Sidebar    │              Main Content                     │
│  (240px)    │                                               │
│  [菜单]     │  ┌─────────────────────────────────────────┐ │
│             │  │                                         │ │
│             │  │           Page Content                  │ │
│             │  │                                         │ │
│             │  └─────────────────────────────────────────┘ │
│             │                                               │
└─────────────┴──────────────────────────────────────────────┘
│                      Footer (32px)                          │
│                   © 2024 CMDB System                        │
└────────────────────────────────────────────────────────────┘
```

### 1.2 布局组件结构

```vue
<!-- App.vue -->
<template>
  <el-config-provider :locale="zhCn">
    <div class="app-layout">
      <AppHeader />
      <div class="app-body">
        <AppSidebar />
        <main class="app-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
      <AppFooter />
    </div>
  </el-config-provider>
</template>
```

## 2. 路由设计

### 2.1 路由配置

```typescript
// router/routes.ts
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表盘', requiresAuth: true, icon: 'Dashboard' }
  },
  {
    path: '/ci',
    name: 'CI',
    redirect: '/ci/list',
    meta: { title: '配置项管理', icon: 'Files' },
    children: [
      {
        path: 'list',
        name: 'CiList',
        component: () => import('@/views/ci/CiListPage.vue'),
        meta: { title: '配置项列表', permission: 'ci:read' }
      },
      {
        path: ':id',
        name: 'CiDetail',
        component: () => import('@/views/ci/CiDetailPage.vue'),
        meta: { title: '配置项详情', permission: 'ci:read' }
      },
      {
        path: 'create',
        name: 'CiCreate',
        component: () => import('@/views/ci/CiFormPage.vue'),
        meta: { title: '创建配置项', permission: 'ci:create' }
      },
      {
        path: ':id/edit',
        name: 'CiEdit',
        component: () => import('@/views/ci/CiFormPage.vue'),
        meta: { title: '编辑配置项', permission: 'ci:update' }
      }
    ]
  },
  {
    path: '/relation',
    name: 'Relation',
    children: [
      {
        path: 'graph',
        name: 'RelationGraph',
        component: () => import('@/views/relation/RelationGraphPage.vue'),
        meta: { title: '关系图', permission: 'relation:read' }
      }
    ]
  },
  {
    path: '/change',
    name: 'Change',
    children: [
      {
        path: 'list',
        name: 'ChangeList',
        component: () => import('@/views/change/ChangeListPage.vue'),
        meta: { title: '变更记录', permission: 'change:read' }
      },
      {
        path: ':id',
        name: 'ChangeDetail',
        component: () => import('@/views/change/ChangeDetailPage.vue'),
        meta: { title: '变更详情', permission: 'change:read' }
      }
    ]
  },
  {
    path: '/report',
    name: 'Report',
    children: [
      {
        path: 'summary',
        name: 'ReportSummary',
        component: () => import('@/views/report/ReportSummaryPage.vue'),
        meta: { title: '资源统计', permission: 'report:view' }
      }
    ]
  },
  {
    path: '/system',
    name: 'System',
    children: [
      {
        path: 'user',
        name: 'SystemUser',
        component: () => import('@/views/system/UserManagePage.vue'),
        meta: { title: '用户管理', permission: 'user:manage' }
      },
      {
        path: 'role',
        name: 'SystemRole',
        component: () => import('@/views/system/RoleManagePage.vue'),
        meta: { title: '角色管理', permission: 'role:manage' }
      },
      {
        path: 'audit',
        name: 'SystemAudit',
        component: () => import('@/views/system/AuditLogPage.vue'),
        meta: { title: '审计日志', permission: 'audit:read' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]
```

### 2.2 路由守卫

```typescript
// router/guards.ts
import type { Router } from 'vue-router'
import { useUserStore } from '@/stores/user'

export function setupRouterGuards(router: Router) {
  router.beforeEach(async (to, from, next) => {
    // 设置页面标题
    document.title = to.meta.title ? `${to.meta.title} - CMDB` : 'CMDB'

    // 检查是否需要认证
    if (to.meta.requiresAuth !== false) {
      const userStore = useUserStore()

      if (!userStore.isLoggedIn) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }

      // 检查权限
      const permission = to.meta.permission as string
      if (permission && !userStore.hasPermission(permission)) {
        next({ name: 'Forbidden' })
        return
      }
    }

    next()
  })
}
```

## 3. 页面设计

### 3.1 登录页面

```vue
<!-- views/Login.vue -->
<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <h1>CMDB 配置管理系统</h1>
        <p>运维部统一资源配置平台</p>
      </div>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
            data-testid="login-username"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            size="large"
            data-testid="login-password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            data-testid="login-submit"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.login(loginForm)
      const redirect = route.query.redirect as string
      router.push(redirect || '/')
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  h1 {
    color: #303133;
    font-size: 24px;
    margin-bottom: 8px;
  }

  p {
    color: #909399;
    font-size: 14px;
  }
}

.login-button {
  width: 100%;
}
</style>
```

### 3.2 配置项列表页

```vue
<!-- views/ci/CiListPage.vue -->
<template>
  <div class="ci-list-page">
    <PageHeader title="配置项列表">
      <template #actions>
        <el-button
          v-if="hasPermission('ci:create')"
          type="primary"
          data-testid="ci-create-btn"
          @click="handleCreate"
        >
          <i class="el-icon-plus" /> 新建
        </el-button>
        <el-button
          v-if="hasPermission('ci:import')"
          data-testid="ci-import-btn"
          @click="handleImport"
        >
          <i class="el-icon-upload" /> 导入
        </el-button>
        <el-button
          v-if="hasPermission('ci:export')"
          data-testid="ci-export-btn"
          @click="handleExport"
        >
          <i class="el-icon-download" /> 导出
        </el-button>
      </template>
    </PageHeader>

    <SearchForm
      :fields="searchFields"
      v-model="searchForm"
      data-testid="ci-search-form"
      @search="handleSearch"
      @reset="handleReset"
    >
      <template #ci_type="{ model }">
        <el-select v-model="model.ci_type" placeholder="选择类型">
          <el-option label="服务器" value="server" />
          <el-option label="网络设备" value="network_device" />
          <el-option label="数据库" value="database" />
          <el-option label="中间件" value="middleware" />
          <el-option label="应用程序" value="application" />
        </el-select>
      </template>
    </SearchForm>

    <DataTable
      v-loading="loading"
      :data="ciList"
      :columns="columns"
      :pagination="pagination"
      data-testid="ci-data-table"
      @page-change="handlePageChange"
      @row-click="handleRowClick"
    >
      <template #status="{ row }">
        <el-tag :type="getStatusType(row.status)">
          {{ getStatusText(row.status) }}
        </el-tag>
      </template>

      <template #actions="{ row }">
        <el-button
          v-if="hasPermission('ci:read')"
          link
          type="primary"
          data-testid="ci-view-btn"
          @click.stop="handleView(row)"
        >
          查看
        </el-button>
        <el-button
          v-if="hasPermission('ci:update')"
          link
          type="primary"
          data-testid="ci-edit-btn"
          @click.stop="handleEdit(row)"
        >
          编辑
        </el-button>
        <el-button
          v-if="hasPermission('ci:delete')"
          link
          type="danger"
          data-testid="ci-delete-btn"
          @click.stop="handleDelete(row)"
        >
          删除
        </el-button>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCiStore } from '@/stores/ci'
import { usePermission } from '@/composables/permission'

const router = useRouter()
const ciStore = useCiStore()
const { hasPermission } = usePermission()

const loading = ref(false)
const ciList = ref([])

const searchForm = reactive({
  keyword: '',
  ci_type: '',
  status: '',
  environment: ''
})

const searchFields = [
  { key: 'keyword', label: '关键字', type: 'input' },
  { key: 'ci_type', label: '类型', type: 'slot' },
  { key: 'status', label: '状态', type: 'select', options: [
    { label: '活跃', value: 'active' },
    { label: '非活跃', value: 'inactive' }
  ]},
  { key: 'environment', label: '环境', type: 'select', options: [
    { label: '生产', value: 'production' },
    { label: '测试', value: 'test' },
    { label: '开发', value: 'development' }
  ]}
]

const columns = [
  { key: 'name', label: '名称', width: 200 },
  { key: 'ci_type', label: '类型', width: 120 },
  { key: 'code', label: '编码', width: 120 },
  { key: 'status', label: '状态', width: 100, slot: true },
  { key: 'environment', label: '环境', width: 100 },
  { key: 'owner', label: '负责人', width: 100 },
  { key: 'updated_at', label: '更新时间', width: 180 },
  { key: 'actions', label: '操作', width: 200, slot: true }
]

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const fetchCiList = async () => {
  loading.value = true
  try {
    const { data } = await ciStore.getList({
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    })
    ciList.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchCiList()
}

const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    ci_type: '',
    status: '',
    environment: ''
  })
  handleSearch()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  fetchCiList()
}

const handleCreate = () => {
  router.push('/ci/create')
}

const handleView = (row: any) => {
  router.push(`/ci/${row.id}`)
}

const handleEdit = (row: any) => {
  router.push(`/ci/${row.id}/edit`)
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该配置项吗？', '提示', {
      type: 'warning'
    })
    await ciStore.delete(row.id)
    ElMessage.success('删除成功')
    fetchCiList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
    }
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    active: 'success',
    inactive: 'info',
    deleted: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: '活跃',
    inactive: '非活跃',
    deleted: '已删除'
  }
  return map[status] || status
}

onMounted(() => {
  fetchCiList()
})
</script>
```

### 3.3 配置项详情页

```vue
<!-- views/ci/CiDetailPage.vue -->
<template>
  <div class="ci-detail-page" v-loading="loading">
    <PageHeader :title="ci.name" :back="true">
      <template #actions>
        <el-button
          v-if="hasPermission('ci:update')"
          type="primary"
          data-testid="ci-edit-btn"
          @click="handleEdit"
        >
          编辑
        </el-button>
      </template>
    </PageHeader>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="detail-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="2" data-testid="ci-basic-info">
            <el-descriptions-item label="名称">{{ ci.name }}</el-descriptions-item>
            <el-descriptions-item label="编码">{{ ci.code }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ ciTypeLabel }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(ci.status)">{{ ci.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="环境">{{ ci.environment }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ ci.owner }}</el-descriptions-item>
            <el-descriptions-item label="部门">{{ ci.department }}</el-descriptions-item>
            <el-descriptions-item label="区域">{{ ci.region }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="detail-card" v-if="ci.attributes">
          <template #header>
            <span>详细属性</span>
          </template>
          <el-descriptions :column="2" data-testid="ci-attributes">
            <el-descriptions-item
              v-for="(value, key) in ci.attributes"
              :key="key"
              :label="key"
            >
              {{ value }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="detail-card">
          <template #header>
            <span>变更历史</span>
          </template>
          <el-timeline data-testid="ci-changes">
            <el-timeline-item
              v-for="change in changes"
              :key="change.id"
              :timestamp="change.created_at"
              placement="top"
            >
              <el-card>
                <p>{{ change.change_type }} - {{ change.change_reason }}</p>
                <p class="change-user">操作人：{{ change.created_by?.username }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="relation-card">
          <template #header>
            <div class="card-header">
              <span>关联关系</span>
              <el-button
                v-if="hasPermission('relation:create')"
                link
                type="primary"
                data-testid="relation-add-btn"
                @click="handleAddRelation"
              >
                添加
              </el-button>
            </div>
          </template>
          <div class="relation-list">
            <div
              v-for="relation in relations"
              :key="relation.id"
              class="relation-item"
              data-testid="relation-item"
            >
              <div class="relation-type">{{ relation.relation_type }}</div>
              <div class="relation-target" @click="goToCi(relation.target_ci.id)">
                {{ relation.target_ci.name }}
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="metric-card" v-if="metrics">
          <template #header>
            <span>监控指标</span>
          </template>
          <div class="metric-list">
            <div class="metric-item">
              <span class="metric-label">CPU 使用率</span>
              <el-progress :percentage="metrics.cpu_usage" />
            </div>
            <div class="metric-item">
              <span class="metric-label">内存使用率</span>
              <el-progress :percentage="metrics.memory_usage" />
            </div>
            <div class="metric-item">
              <span class="metric-label">磁盘使用率</span>
              <el-progress :percentage="metrics.disk_usage" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCiStore } from '@/stores/ci'
import { usePermission } from '@/composables/permission'

const router = useRouter()
const route = useRoute()
const ciStore = useCiStore()
const { hasPermission } = usePermission()

const loading = ref(false)
const ci = ref<any>({})
const changes = ref([])
const relations = ref([])
const metrics = ref(null)

const ciTypeLabel = computed(() => {
  const map: Record<string, string> = {
    server: '服务器',
    network_device: '网络设备',
    database: '数据库',
    middleware: '中间件',
    application: '应用程序'
  }
  return map[ci.value.ci_type] || ci.value.ci_type
})

const fetchCiDetail = async () => {
  loading.value = true
  try {
    const { data } = await ciStore.getDetail(route.params.id as string)
    ci.value = data
    changes.value = data.changes || []
    relations.value = data.relations || []
    metrics.value = data.metrics || null
  } finally {
    loading.value = false
  }
}

const handleEdit = () => {
  router.push(`/ci/${route.params.id}/edit`)
}

const handleAddRelation = () => {
  // TODO: 打开添加关系对话框
}

const goToCi = (id: string) => {
  router.push(`/ci/${id}`)
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    active: 'success',
    inactive: 'info'
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchCiDetail()
})
</script>

<style scoped lang="scss">
.ci-detail-page {
  padding: 20px;
}

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.relation-item {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;

  &:last-child {
    border-bottom: none;
  }

  .relation-type {
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
  }

  .relation-target {
    cursor: pointer;
    color: #409eff;

    &:hover {
      text-decoration: underline;
    }
  }
}

.metric-item {
  margin-bottom: 16px;

  .metric-label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: #606266;
  }
}

.change-user {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
```

## 4. 状态管理设计

### 4.1 用户 Store

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, logout as apiLogout, getMe } from '@/api/auth'
import type { User, Role, Permission } from '@/types'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('')
  const user = ref<User | null>(null)
  const permissions = ref<Permission[]>([])

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role)

  const hasPermission = (code: string) => {
    if (!user.value) return false
    if (user.value.role?.code === 'super_admin') return true
    return permissions.value.some(p => p.code === code)
  }

  const login = async (credentials: { username: string; password: string }) => {
    const { data } = await apiLogin(credentials)
    token.value = data.token
    user.value = data.user
    localStorage.setItem('token', data.token)
  }

  const logout = async () => {
    await apiLogout()
    token.value = ''
    user.value = null
    permissions.value = []
    localStorage.removeItem('token')
  }

  const initUser = async () => {
    const storedToken = localStorage.getItem('token')
    if (!storedToken) return

    try {
      const { data } = await getMe()
      token.value = storedToken
      user.value = data
      permissions.value = data.permissions || []
    } catch (error) {
      logout()
    }
  }

  return {
    token,
    user,
    permissions,
    isLoggedIn,
    role,
    hasPermission,
    login,
    logout,
    initUser
  }
})
```

### 4.2 CI Store

```typescript
// stores/ci.ts
import { defineStore } from 'pinia'
import {
  getCiList,
  getCiDetail,
  createCi,
  updateCi,
  deleteCi
} from '@/api/ci'
import type { Ci, CiListParams, CiCreateParams, CiUpdateParams } from '@/types'

export const useCiStore = defineStore('ci', () => {
  const getList = async (params: CiListParams) => {
    return await getCiList(params)
  }

  const getDetail = async (id: string) => {
    return await getCiDetail(id)
  }

  const create = async (data: CiCreateParams) => {
    return await createCi(data)
  }

  const update = async (id: string, data: CiUpdateParams) => {
    return await updateCi(id, data)
  }

  const delete = async (id: string) => {
    return await deleteCi(id)
  }

  return {
    getList,
    getDetail,
    create,
    update,
    delete
  }
})
```

## 5. UI 组件设计

### 5.1 数据表格组件

```vue
<!-- components/common/DataTable.vue -->
<template>
  <el-table
    :data="data"
    v-bind="$attrs"
    class="data-table"
    data-testid="data-table"
  >
    <el-table-column
      v-for="column in columns"
      :key="column.key"
      :prop="column.key"
      :label="column.label"
      :width="column.width"
    >
      <template #default="{ row }" v-if="column.slot">
        <slot :name="column.key" :row="row" />
      </template>
    </el-table-column>
  </el-table>

  <div class="pagination-container" v-if="pagination">
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      data-testid="data-table-pagination"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
interface Column {
  key: string
  label: string
  width?: number
  slot?: boolean
}

interface Pagination {
  page: number
  page_size: number
  total: number
}

defineProps<{
  data: any[]
  columns: Column[]
  pagination?: Pagination
}>()

const emit = defineEmits<{
  pageChange: [page: number]
  rowClick: [row: any]
}>()

const handlePageChange = (page: number) => {
  emit('pageChange', page)
}
</script>

<style scoped lang="scss">
.data-table {
  width: 100%;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
```

### 5.2 搜索表单组件

```vue
<!-- components/common/SearchForm.vue -->
<template>
  <el-card class="search-form-card">
    <el-form
      :model="modelValue"
      inline
      class="search-form"
      data-testid="search-form"
    >
      <el-form-item
        v-for="field in fields"
        :key="field.key"
        :label="field.label"
      >
        <template v-if="field.type === 'slot'">
          <slot :name="field.key" :model="modelValue" />
        </template>
        <template v-else-if="field.type === 'select'">
          <el-select
            v-model="modelValue[field.key]"
            :placeholder="`请选择${field.label}`"
            clearable
          >
            <el-option
              v-for="opt in field.options"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </template>
        <template v-else>
          <el-input
            v-model="modelValue[field.key]"
            :placeholder="`请输入${field.label}`"
            clearable
          />
        </template>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          data-testid="search-submit"
          @click="handleSearch"
        >
          搜索
        </el-button>
        <el-button data-testid="search-reset" @click="handleReset">
          重置
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
interface SearchField {
  key: string
  label: string
  type: 'input' | 'select' | 'slot'
  options?: { label: string; value: any }[]
}

const props = defineProps<{
  fields: SearchField[]
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  search: []
  reset: []
}>()

const handleSearch = () => {
  emit('search')
}

const handleReset = () => {
  emit('reset')
}
</script>

<style scoped lang="scss">
.search-form-card {
  margin-bottom: 20px;
}

.search-form {
  .el-form-item {
    margin-bottom: 16px;
  }
}
</style>
```

## 6. API 客户端设计

```typescript
// api/index.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'

let requestInstance: AxiosInstance | null = null

export function createRequestInstance() {
  if (requestInstance) return requestInstance

  const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api/v1',
    timeout: 30000
  })

  instance.interceptors.request.use((config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  })

  instance.interceptors.response.use(
    (response) => {
      return response.data
    },
    (error) => {
      if (error.response?.status === 401) {
        const userStore = useUserStore()
        userStore.logout()
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )

  requestInstance = instance
  return instance
}

export const request = createRequestInstance()
```

```typescript
// api/ci.ts
import { request } from './index'
import type { Ci, CiListParams, CiCreateParams, CiUpdateParams } from '@/types'

export function getCiList(params: CiListParams) {
  return request.get('/ci', { params })
}

export function getCiDetail(id: string) {
  return request.get(`/ci/${id}`)
}

export function createCi(data: CiCreateParams) {
  return request.post('/ci', data)
}

export function updateCi(id: string, data: CiUpdateParams) {
  return request.put(`/ci/${id}`, data)
}

export function deleteCi(id: string) {
  return request.delete(`/ci/${id}`)
}
```

## 7. UI 自动化测试支持

### 7.1 Test ID 规范

所有可交互的 UI 元素必须添加 `data-testid` 属性：

| 元素类型 | Test ID 命名规范 | 示例 |
|----------|------------------|------|
| 登录输入框 | login-username | `data-testid="login-username"` |
| 登录密码框 | login-password | `data-testid="login-password"` |
| 登录按钮 | login-submit | `data-testid="login-submit"` |
| 列表页搜索表单 | ci-search-form | `data-testid="ci-search-form"` |
| 列表页数据表格 | ci-data-table | `data-testid="ci-data-table"` |
| 创建按钮 | ci-create-btn | `data-testid="ci-create-btn"` |
| 查看按钮 | ci-view-btn | `data-testid="ci-view-btn"` |
| 编辑按钮 | ci-edit-btn | `data-testid="ci-edit-btn"` |
| 删除按钮 | ci-delete-btn | `data-testid="ci-delete-btn"` |
| 分页组件 | data-table-pagination | `data-testid="data-table-pagination"` |
| 详情基本信息 | ci-basic-info | `data-testid="ci-basic-info"` |
| 详情属性信息 | ci-attributes | `data-testid="ci-attributes"` |
| 详情变更历史 | ci-changes | `data-testid="ci-changes"` |

### 7.2 加载状态指示

```vue
<template>
  <div v-loading="loading" element-loading-text="加载中...">
    <!-- 页面内容 -->
  </div>
</template>
```

### 7.3 操作反馈

```typescript
// 成功反馈
ElMessage.success('操作成功')

// 错误反馈
ElMessage.error('操作失败')

// 确认对话框
await ElMessageBox.confirm('确定要删除吗？', '提示', {
  type: 'warning'
})
```
