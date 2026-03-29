<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="layout-aside">
      <div class="logo">
        <el-icon :size="24"><Setting /></el-icon>
        <span>CMDB</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard" data-testid="menu-dashboard">
          <el-icon><DataLine /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>

        <el-sub-menu index="ci" data-testid="menu-ci">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>配置项管理</span>
          </template>
          <el-menu-item index="/cis" data-testid="menu-ci-list">配置项列表</el-menu-item>
          <el-menu-item index="/relations" data-testid="menu-relation">关系图</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/changes" data-testid="menu-changes">
          <el-icon><Edit /></el-icon>
          <span>变更管理</span>
        </el-menu-item>

        <el-menu-item index="/reports" data-testid="menu-reports">
          <el-icon><TrendCharts /></el-icon>
          <span>报表统计</span>
        </el-menu-item>

        <el-sub-menu index="system" data-testid="menu-system">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/users" data-testid="menu-users">用户管理</el-menu-item>
          <el-menu-item index="/roles" data-testid="menu-roles">角色管理</el-menu-item>
          <el-menu-item index="/audit-logs" data-testid="menu-audit">审计日志</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <span class="breadcrumb" data-testid="layout-breadcrumb">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click" data-testid="layout-user-dropdown">
            <div class="user-info" data-testid="header-username">
              <span class="username">{{ userStore.username }}</span>
              <el-icon :size="20" class="user-avatar"><UserFilled /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout" data-testid="user-logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/cis')) return '/cis'
  if (path.startsWith('/changes')) return '/changes'
  if (path.startsWith('/users')) return '/users'
  if (path.startsWith('/roles')) return '/roles'
  if (path.startsWith('/audit-logs')) return '/audit-logs'
  return path
})

const currentTitle = computed(() => (route.meta.title as string) || '首页')

const handleCommand = (command: string) => {
  if (command === 'logout') {
    doLogout()
  }
}

const doLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow-y: auto;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 60px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb {
  font-size: 14px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #606266;
}

.user-avatar {
  color: #606266;
}

.user-info:hover .username,
.user-info:hover .user-avatar {
  color: #409eff;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
