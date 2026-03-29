<template>
  <div class="change-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button link @click="$router.back()" data-testid="change-detail-back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <span>变更详情</span>
          <div class="header-actions">
            <el-button
              v-if="change?.status === 'pending'"
              type="success"
              @click="handleApprove"
              data-testid="change-detail-approve"
            >
              批准
            </el-button>
            <el-button
              v-if="change?.status === 'pending'"
              type="danger"
              @click="handleReject"
              data-testid="change-detail-reject"
            >
              拒绝
            </el-button>
          </div>
        </div>
      </template>

      <el-descriptions v-if="change" title="基本信息" :column="2" border data-testid="change-detail-info">
        <el-descriptions-item label="ID">{{ change.id }}</el-descriptions-item>
        <el-descriptions-item label="配置项">
          <el-link type="primary" @click="goToCiDetail">{{ change.ci_name }}</el-link>
        </el-descriptions-item>
        <el-descriptions-item label="变更类型">
          <el-tag :type="getChangeTypeTag(change.change_type)">
            {{ getChangeTypeLabel(change.change_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(change.status)">
            {{ getStatusLabel(change.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交人">{{ change.created_by?.username }}</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ change.created_at }}</el-descriptions-item>
        <el-descriptions-item v-if="change.approved_by" label="审批人">
          {{ change.approved_by?.username }}
        </el-descriptions-item>
        <el-descriptions-item v-if="change.approved_at" label="审批时间">
          {{ change.approved_at }}
        </el-descriptions-item>
        <el-descriptions-item label="变更原因" :span="2">
          {{ change.change_reason }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <div class="diff-section">
        <h3>变更对比</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>
                <span>变更前</span>
              </template>
              <pre class="json-content" data-testid="change-old-value">{{ formatJson(change?.old_value) }}</pre>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="never">
              <template #header>
                <span>变更后</span>
              </template>
              <pre class="json-content" data-testid="change-new-value">{{ formatJson(change?.new_value) }}</pre>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <el-dialog v-model="showRejectDialog" title="拒绝原因" width="400px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="4"
        placeholder="请输入拒绝原因"
        data-testid="reject-reason-input"
      />
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmReject" :loading="rejecting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Change, ChangeType, ChangeStatus } from '@/api/change'
import { getChangeDetail, approveChange, rejectChange } from '@/api/change'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const rejecting = ref(false)
const showRejectDialog = ref(false)
const rejectReason = ref('')
const change = ref<Change | null>(null)

const getChangeTypeLabel = (type: ChangeType): string => {
  const labels: Record<ChangeType, string> = {
    create: '创建',
    update: '更新',
    delete: '删除',
  }
  return labels[type] || type
}

const getChangeTypeTag = (type: ChangeType): string => {
  const tags: Record<ChangeType, string> = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
  }
  return tags[type] || ''
}

const getStatusLabel = (status: ChangeStatus): string => {
  const labels: Record<ChangeStatus, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    completed: '已完成',
  }
  return labels[status] || status
}

const getStatusTag = (status: ChangeStatus): string => {
  const tags: Record<ChangeStatus, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    completed: 'info',
  }
  return tags[status] || ''
}

const formatJson = (data: unknown): string => {
  if (!data) return '无'
  return JSON.stringify(data, null, 2)
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getChangeDetail(Number(route.params.id))
    if (res.success && res.data) {
      change.value = res.data
    }
  } catch (error) {
    console.error('获取变更详情失败:', error)
    ElMessage.error('获取变更详情失败')
  } finally {
    loading.value = false
  }
}

const goToCiDetail = () => {
  if (change.value) {
    router.push(`/cis/${change.value.ci_id}`)
  }
}

const handleApprove = async () => {
  try {
    await ElMessageBox.confirm('确定要批准该变更申请吗？', '审批确认', {
      confirmButtonText: '批准',
      cancelButtonText: '取消',
      type: 'info',
    })
    await approveChange(change.value!.id)
    ElMessage.success('审批成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审批失败:', error)
    }
  }
}

const handleReject = () => {
  rejectReason.value = ''
  showRejectDialog.value = true
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }

  rejecting.value = true
  try {
    await rejectChange(change.value!.id, rejectReason.value)
    ElMessage.success('已拒绝该变更申请')
    showRejectDialog.value = false
    fetchData()
  } catch (error) {
    console.error('拒绝失败:', error)
    ElMessage.error('操作失败')
  } finally {
    rejecting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.change-detail-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.diff-section {
  margin-top: 20px;
}

.diff-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #303133;
}

.json-content {
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
