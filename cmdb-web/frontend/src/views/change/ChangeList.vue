<template>
  <div class="change-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>变更记录</span>
          <el-button type="primary" @click="showCreateDialog = true" data-testid="change-create-btn">
            <el-icon><Plus /></el-icon>
            提交变更
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" data-testid="change-search-form">
        <el-form-item label="配置项">
          <el-input
            v-model="searchForm.ci_name"
            placeholder="配置项名称"
            clearable
            style="width: 150px"
            data-testid="change-search-ci"
          />
        </el-form-item>
        <el-form-item label="变更类型">
          <el-select v-model="searchForm.change_type" placeholder="全部类型" clearable style="width: 120px" data-testid="change-search-type">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px" data-testid="change-search-status">
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" data-testid="change-search-btn">搜索</el-button>
          <el-button @click="handleReset" data-testid="change-reset-btn">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="changeList" stripe border style="width: 100%" data-testid="change-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="ci_name" label="配置项" width="150" />
        <el-table-column label="变更类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getChangeTypeTag(row.change_type)">
              {{ getChangeTypeLabel(row.change_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="change_reason" label="变更原因" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by.username" label="提交人" width="100" />
        <el-table-column prop="created_at" label="提交时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)" :data-testid="`change-view-${row.id}`">
              详情
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              link
              type="success"
              @click="handleApprove(row)"
              :data-testid="`change-approve-${row.id}`"
            >
              审批
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
        data-testid="change-pagination"
      />
    </el-card>

    <el-dialog v-model="showCreateDialog" title="提交变更申请" width="600px" @closed="resetForm">
      <el-form ref="formRef" :model="changeForm" :rules="rules" label-width="100px" data-testid="change-form">
        <el-form-item label="配置项" prop="ci_id">
          <el-select v-model="changeForm.ci_id" placeholder="选择配置项" filterable style="width: 100%" data-testid="change-form-ci">
            <el-option v-for="ci in ciList" :key="ci.id" :label="ci.name" :value="ci.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更类型" prop="change_type">
          <el-select v-model="changeForm.change_type" placeholder="选择变更类型" style="width: 100%" data-testid="change-form-type">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更原因" prop="change_reason">
          <el-input
            v-model="changeForm.change_reason"
            type="textarea"
            :rows="4"
            placeholder="请详细描述变更原因"
            data-testid="change-form-reason"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false" data-testid="change-form-cancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting" data-testid="change-form-submit">
          提交
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Change, ChangeType, ChangeStatus } from '@/api/change'
import { getChangeList, createChange, approveChange } from '@/api/change'
import { getCIList } from '@/api/ci'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const formRef = ref<FormInstance>()

const changeList = ref<Change[]>([])
const ciList = ref<Array<{ id: number; name: string }>>([])
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const searchForm = reactive({
  ci_name: '',
  change_type: '' as ChangeType | '',
  status: '' as ChangeStatus | '',
})

const changeForm = reactive({
  ci_id: null as number | null,
  change_type: '' as ChangeType,
  change_reason: '',
})

const rules: FormRules = {
  ci_id: [{ required: true, message: '请选择配置项', trigger: 'change' }],
  change_type: [{ required: true, message: '请选择变更类型', trigger: 'change' }],
  change_reason: [{ required: true, message: '请输入变更原因', trigger: 'blur' }],
}

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

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getChangeList({
      page: pagination.page,
      page_size: pagination.page_size,
      change_type: searchForm.change_type || undefined,
      status: searchForm.status || undefined,
    })
    if (res.success && res.data) {
      changeList.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取变更列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchCiList = async () => {
  try {
    const res = await getCIList({ page: 1, page_size: 100 })
    if (res.success && res.data) {
      ciList.value = res.data.items.map((ci) => ({
        id: ci.id,
        name: ci.name,
      }))
    }
  } catch (error) {
    console.error('获取配置项列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.ci_name = ''
  searchForm.change_type = ''
  searchForm.status = ''
  handleSearch()
}

const handleViewDetail = (row: Change) => {
  router.push(`/changes/${row.id}`)
}

const handleApprove = async (row: Change) => {
  try {
    await ElMessageBox.confirm('确定要批准该变更申请吗？', '审批确认', {
      confirmButtonText: '批准',
      cancelButtonText: '取消',
      type: 'info',
    })
    await approveChange(row.id)
    ElMessage.success('审批成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审批失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await createChange({
        ci_id: changeForm.ci_id!,
        change_type: changeForm.change_type,
        change_reason: changeForm.change_reason,
      })
      ElMessage.success('变更申请提交成功')
      showCreateDialog.value = false
      fetchData()
    } catch (error: any) {
      console.error('提交失败:', error)
      const msg = error.response?.data?.detail || '提交失败'
      ElMessage.error(msg)
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  changeForm.ci_id = null
  changeForm.change_type = '' as ChangeType
  changeForm.change_reason = ''
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
  fetchCiList()
})
</script>

<style scoped>
.change-list-container {
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
</style>
