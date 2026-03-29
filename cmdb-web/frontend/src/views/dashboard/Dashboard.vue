<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" data-testid="dashboard-stat-total">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dashboardData?.stats?.total_cis || 0 }}</div>
              <div class="stat-label">配置项总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" data-testid="dashboard-stat-online">
          <div class="stat-content">
            <div class="stat-icon online">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dashboardData?.stats?.online_cis || 0 }}</div>
              <div class="stat-label">在线配置项</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" data-testid="dashboard-stat-changes">
          <div class="stat-content">
            <div class="stat-icon changes">
              <el-icon :size="32"><Edit /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dashboardData?.stats?.pending_changes || 0 }}</div>
              <div class="stat-label">待审批变更</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" data-testid="dashboard-stat-users">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dashboardData?.stats?.active_users || 0 }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>配置项类型分布</span>
          </template>
          <div class="chart-container" data-testid="dashboard-chart-type">
            <div v-if="dashboardData?.ci_type_distribution?.length" class="distribution-list">
              <div
                v-for="item in dashboardData.ci_type_distribution"
                :key="item.ci_type"
                class="distribution-item"
              >
                <span class="label">{{ getTypeLabel(item.ci_type) }}</span>
                <el-progress
                  :percentage="item.percentage"
                  :stroke-width="20"
                  :format="() => `${item.count}`"
                />
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>环境分布</span>
          </template>
          <div class="chart-container" data-testid="dashboard-chart-env">
            <div v-if="dashboardData?.environment_distribution?.length" class="distribution-list">
              <div
                v-for="item in dashboardData.environment_distribution"
                :key="item.environment"
                class="distribution-item"
              >
                <span class="label">{{ getEnvLabel(item.environment) }}</span>
                <el-progress
                  :percentage="item.percentage"
                  :stroke-width="20"
                  :format="() => `${item.count}`"
                  :color="getEnvColor(item.environment)"
                />
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="recent-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近变更</span>
              <el-button link type="primary" @click="$router.push('/changes')" data-testid="dashboard-view-all-changes">
                查看全部
              </el-button>
            </div>
          </template>
          <el-table
            v-loading="loading"
            :data="dashboardData?.recent_changes || []"
            stripe
            data-testid="dashboard-recent-changes"
          >
            <el-table-column prop="ci_name" label="配置项名称" width="200" />
            <el-table-column label="变更类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getChangeTypeTag(row.change_type)">
                  {{ getChangeTypeLabel(row.change_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getChangeStatusTag(row.status)">
                  {{ getChangeStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_by" label="操作人" width="120" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
          <el-empty v-if="!loading && !dashboardData?.recent_changes?.length" description="暂无变更记录" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardData, type DashboardData } from '@/api/dashboard'

const loading = ref(false)
const dashboardData = ref<DashboardData | null>(null)

const getTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    server: '服务器',
    network_device: '网络设备',
    database: '数据库',
    middleware: '中间件',
    application: '应用',
    container: '容器',
    k8s_resource: 'K8s 资源',
    cloud_resource: '云资源',
  }
  return labels[type] || type
}

const getEnvLabel = (env: string): string => {
  const labels: Record<string, string> = {
    production: '生产环境',
    int: '测试环境',
    dev: '开发环境',
  }
  return labels[env] || env
}

const getEnvColor = (env: string): string => {
  const colors: Record<string, string> = {
    production: '#67C23A',
    int: '#E6A23C',
    dev: '#409EFF',
  }
  return colors[env] || '#409EFF'
}

const getChangeTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    create: '创建',
    update: '更新',
    delete: '删除',
  }
  return labels[type] || type
}

const getChangeTypeTag = (type: string): string => {
  const tags: Record<string, string> = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
  }
  return tags[type] || ''
}

const getChangeStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    completed: '已完成',
  }
  return labels[status] || status
}

const getChangeStatusTag = (status: string): string => {
  const tags: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    completed: 'info',
  }
  return tags[status] || ''
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDashboardData()
    if (res.success && res.data) {
      dashboardData.value = res.data
    }
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    ElMessage.error('获取仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.online {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-icon.changes {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.users {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-container {
  min-height: 200px;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.distribution-item .label {
  width: 80px;
  font-size: 14px;
  color: #606266;
}

.distribution-item .el-progress {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-row {
  margin-bottom: 20px;
}
</style>
