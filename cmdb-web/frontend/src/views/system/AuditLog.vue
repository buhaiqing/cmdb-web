<template>
  <div class="audit-log-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审计日志</span>
          <el-button type="primary" @click="handleExport" data-testid="audit-export-btn">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" data-testid="audit-search-form">
        <el-form-item label="用户">
          <el-input
            v-model="searchForm.username"
            placeholder="用户名"
            clearable
            style="width: 120px"
            data-testid="audit-search-user"
          />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.action" placeholder="全部" clearable style="width: 120px" data-testid="audit-search-action">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="查看" value="view" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="searchForm.resource_type" placeholder="全部" clearable style="width: 120px" data-testid="audit-search-resource">
            <el-option label="配置项" value="ci" />
            <el-option label="用户" value="user" />
            <el-option label="角色" value="role" />
            <el-option label="变更" value="change" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
            data-testid="audit-search-date"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" data-testid="audit-search-btn">搜索</el-button>
          <el-button @click="handleReset" data-testid="audit-reset-btn">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="logList" stripe border style="width: 100%" data-testid="audit-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionTag(row.action)" size="small">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100" />
        <el-table-column prop="resource_name" label="资源名称" width="150" show-overflow-tooltip />
        <el-table-column label="详情" min-width="200">
          <template #default="{ row }">
            <span class="detail-text" @click="showDetail(row)">{{ getDetailPreview(row.detail) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP 地址" width="140" />
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" fixed="right" width="80">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)" :data-testid="`audit-detail-${row.id}`">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
        data-testid="audit-pagination"
      />
    </el-card>

    <el-dialog v-model="showDetailDialog" title="审计日志详情" width="600px">
      <el-descriptions v-if="selectedLog" :column="1" border>
        <el-descriptions-item label="ID">{{ selectedLog.id }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ selectedLog.username }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionTag(selectedLog.action)">
            {{ getActionLabel(selectedLog.action) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="资源类型">{{ selectedLog.resource_type }}</el-descriptions-item>
        <el-descriptions-item label="资源ID">{{ selectedLog.resource_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="资源名称">{{ selectedLog.resource_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="IP 地址">{{ selectedLog.ip_address }}</el-descriptions-item>
        <el-descriptions-item label="User Agent">{{ selectedLog.user_agent || '-' }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ selectedLog.created_at }}</el-descriptions-item>
        <el-descriptions-item label="详细信息">
          <pre class="detail-json">{{ JSON.stringify(selectedLog.detail, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { AuditLog, AuditAction } from '@/api/audit'
import { getAuditLogList, exportAuditLogs } from '@/api/audit'

const loading = ref(false)
const showDetailDialog = ref(false)
const selectedLog = ref<AuditLog | null>(null)
const dateRange = ref<[Date, Date] | null>(null)

const logList = ref<AuditLog[]>([])
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const searchForm = reactive({
  username: '',
  action: '' as AuditAction | '',
  resource_type: '',
  start_date: '',
  end_date: '',
})

const getActionLabel = (action: AuditAction): string => {
  const labels: Record<AuditAction, string> = {
    create: '创建',
    update: '更新',
    delete: '删除',
    login: '登录',
    logout: '登出',
    view: '查看',
  }
  return labels[action] || action
}

const getActionTag = (action: AuditAction): string => {
  const tags: Record<AuditAction, string> = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
    login: 'primary',
    logout: 'info',
    view: '',
  }
  return tags[action] || ''
}

const getDetailPreview = (detail: unknown): string => {
  if (!detail) return '-'
  const str = JSON.stringify(detail)
  return str.length > 50 ? str.substring(0, 50) + '...' : str
}

const handleDateChange = (val: [Date, Date] | null) => {
  if (val) {
    searchForm.start_date = val[0].toISOString()
    searchForm.end_date = val[1].toISOString()
  } else {
    searchForm.start_date = ''
    searchForm.end_date = ''
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getAuditLogList({
      page: pagination.page,
      page_size: pagination.page_size,
      username: searchForm.username || undefined,
      action: searchForm.action || undefined,
      resource_type: searchForm.resource_type || undefined,
      start_date: searchForm.start_date || undefined,
      end_date: searchForm.end_date || undefined,
    })
    if (res.success && res.data) {
      logList.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取审计日志失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.username = ''
  searchForm.action = ''
  searchForm.resource_type = ''
  searchForm.start_date = ''
  searchForm.end_date = ''
  dateRange.value = null
  handleSearch()
}

const showDetail = (row: AuditLog) => {
  selectedLog.value = row
  showDetailDialog.value = true
}

const handleExport = async () => {
  try {
    const res = await exportAuditLogs({
      username: searchForm.username || undefined,
      action: searchForm.action || undefined,
      resource_type: searchForm.resource_type || undefined,
      start_date: searchForm.start_date || undefined,
      end_date: searchForm.end_date || undefined,
    })
    if (res.success && res.data) {
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
.audit-log-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.detail-text {
  color: #409eff;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  max-width: 100%;
}

.detail-text:hover {
  text-decoration: underline;
}

.detail-json {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
