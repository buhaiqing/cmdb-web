<template>
  <div class="report-summary-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资源统计报表</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
              data-testid="report-date-range"
              @change="handleDateChange"
            />
            <el-button type="primary" @click="fetchData" :loading="loading" data-testid="report-refresh">
              刷新
            </el-button>
            <el-button @click="handleExport" data-testid="report-export">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20" class="summary-row">
        <el-col :span="8">
          <el-card shadow="hover" class="summary-card" data-testid="report-ci-summary">
            <template #header>
              <span>配置项统计</span>
            </template>
            <div class="summary-content">
              <div class="summary-total">
                <span class="label">总数</span>
                <span class="value">{{ reportData?.ci_summary?.total || 0 }}</span>
              </div>
              <el-divider />
              <div class="summary-list">
                <div v-for="item in reportData?.ci_summary?.by_type" :key="item.type" class="summary-item">
                  <span class="item-label">{{ getTypeLabel(item.type) }}</span>
                  <span class="item-value">{{ item.count }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="summary-card" data-testid="report-change-summary">
            <template #header>
              <span>变更统计</span>
            </template>
            <div class="summary-content">
              <div class="summary-total">
                <span class="label">总数</span>
                <span class="value">{{ reportData?.change_summary?.total || 0 }}</span>
              </div>
              <el-divider />
              <div class="summary-list">
                <div v-for="item in reportData?.change_summary?.by_status" :key="item.status" class="summary-item">
                  <span class="item-label">{{ getStatusLabel(item.status) }}</span>
                  <span class="item-value">{{ item.count }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="summary-card" data-testid="report-user-summary">
            <template #header>
              <span>用户统计</span>
            </template>
            <div class="summary-content">
              <div class="summary-total">
                <span class="label">总数</span>
                <span class="value">{{ reportData?.user_summary?.total || 0 }}</span>
              </div>
              <el-divider />
              <div class="summary-list">
                <div class="summary-item">
                  <span class="item-label">活跃用户</span>
                  <span class="item-value">{{ reportData?.user_summary?.active || 0 }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="chart-row">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>配置项状态分布</span>
            </template>
            <div class="chart-container" data-testid="report-status-chart">
              <div v-if="reportData?.ci_summary?.by_status?.length" class="distribution-list">
                <div v-for="item in reportData.ci_summary.by_status" :key="item.status" class="distribution-item">
                  <span class="label">{{ getStatusLabel(item.status) }}</span>
                  <el-progress :percentage="getPercentage(item.count, reportData?.ci_summary?.total || 1)" :stroke-width="20" :format="() => `${item.count}`" />
                </div>
              </div>
              <el-empty v-else description="暂无数据" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>配置项环境分布</span>
            </template>
            <div class="chart-container" data-testid="report-env-chart">
              <div v-if="reportData?.ci_summary?.by_environment?.length" class="distribution-list">
                <div v-for="item in reportData.ci_summary.by_environment" :key="item.environment" class="distribution-item">
                  <span class="label">{{ getEnvLabel(item.environment) }}</span>
                  <el-progress
                    :percentage="getPercentage(item.count, reportData?.ci_summary?.total || 1)"
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

      <el-row :gutter="20" class="detail-row">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>变更类型分布</span>
            </template>
            <el-table :data="reportData?.change_summary?.by_type || []" stripe border data-testid="report-change-type-table">
              <el-table-column prop="type" label="变更类型">
                <template #default="{ row }">
                  {{ getChangeTypeLabel(row.type) }}
                </template>
              </el-table-column>
              <el-table-column prop="count" label="数量" width="100" />
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>用户角色分布</span>
            </template>
            <el-table :data="reportData?.user_summary?.by_role || []" stripe border data-testid="report-user-role-table">
              <el-table-column prop="role" label="角色" />
              <el-table-column prop="count" label="用户数" width="100" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getReportData, exportReport, type ReportData } from '@/api/dashboard'

const loading = ref(false)
const dateRange = ref<[Date, Date] | null>(null)
const reportData = ref<ReportData | null>(null)

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

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中',
    decommissioned: '已退役',
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    completed: '已完成',
  }
  return labels[status] || status
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

const getPercentage = (value: number, total: number): number => {
  if (total === 0) return 0
  return Math.round((value / total) * 100)
}

const handleDateChange = () => {
  fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    const params: { start_date?: string; end_date?: string } = {}
    if (dateRange.value) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }
    const res = await getReportData(params)
    if (res.success && res.data) {
      reportData.value = res.data
    }
  } catch (error) {
    console.error('获取报表数据失败:', error)
    ElMessage.error('获取报表数据失败')
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  try {
    const params: { start_date?: string; end_date?: string; format?: 'pdf' | 'excel' } = { format: 'excel' }
    if (dateRange.value) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }
    const res = await exportReport(params)
    if (res.success) {
      ElMessage.success('导出成功')
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.report-summary-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.summary-row {
  margin-bottom: 20px;
}

.summary-card {
  height: 100%;
}

.summary-content {
  padding: 10px 0;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.summary-total .label {
  font-size: 14px;
  color: #909399;
}

.summary-total .value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-item .item-label {
  font-size: 14px;
  color: #606266;
}

.summary-item .item-value {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.chart-row {
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

.detail-row {
  margin-bottom: 20px;
}
</style>
