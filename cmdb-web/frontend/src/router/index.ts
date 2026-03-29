import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'DataLine' },
      },
      {
        path: 'cis',
        name: 'CIList',
        component: () => import('@/views/ci/CIList.vue'),
        meta: { title: '配置项列表', permission: 'ci:read' },
      },
      {
        path: 'cis/:id',
        name: 'CIDetail',
        component: () => import('@/views/ci/CIDetail.vue'),
        meta: { title: '配置项详情', permission: 'ci:read' },
      },
      {
        path: 'relations',
        name: 'RelationGraph',
        component: () => import('@/views/relation/RelationGraph.vue'),
        meta: { title: '关系图', permission: 'relation:read' },
      },
      {
        path: 'changes',
        name: 'ChangeList',
        component: () => import('@/views/change/ChangeList.vue'),
        meta: { title: '变更记录', permission: 'change:read' },
      },
      {
        path: 'changes/:id',
        name: 'ChangeDetail',
        component: () => import('@/views/change/ChangeDetail.vue'),
        meta: { title: '变更详情', permission: 'change:read' },
      },
      {
        path: 'reports',
        name: 'ReportSummary',
        component: () => import('@/views/report/ReportSummary.vue'),
        meta: { title: '资源统计', permission: 'report:view' },
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/user/UserList.vue'),
        meta: { title: '用户管理', permission: 'user:manage' },
      },
      {
        path: 'roles',
        name: 'RoleManage',
        component: () => import('@/views/system/RoleManage.vue'),
        meta: { title: '角色管理', permission: 'role:manage' },
      },
      {
        path: 'audit-logs',
        name: 'AuditLog',
        component: () => import('@/views/system/AuditLog.vue'),
        meta: { title: '审计日志', permission: 'audit:read' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  const hasToken = !!userStore.token
  const toName = to.name

  if (to.meta.title) {
    document.title = `${to.meta.title} - CMDB`
  }

  if (hasToken) {
    if (toName === 'Login') {
      next({ path: '/' })
      return
    }
    next()
    return
  }
  if (toName === 'Login') {
    next()
    return
  }
  next({
    name: 'Login',
    query: {
      from: to.fullPath,
    },
  })
})

export default router
