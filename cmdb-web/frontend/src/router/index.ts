import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext } from 'vue-router'
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
    redirect: '/cis',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'cis',
        name: 'CIList',
        component: () => import('@/views/ci/CIList.vue'),
        meta: { title: '配置项列表' },
      },
      {
        path: 'cis/:id',
        name: 'CIDetail',
        component: () => import('@/views/ci/CIDetail.vue'),
        meta: { title: '配置项详情' },
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/user/UserList.vue'),
        meta: { title: '用户管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const hasToken = userStore.token
  const toName = to.name

  // 设置页面标题
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
