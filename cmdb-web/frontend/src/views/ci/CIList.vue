<template>
  <div class="ci-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配置项列表</span>
          <el-button type="primary" @click="showCreateDialog = true" data-testid="ci-create-btn">
            <el-icon><Plus /></el-icon>
            新建配置项
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form" data-testid="ci-search-form">
        <el-form-item label="类型">
          <el-select v-model="searchForm.ci_type" placeholder="全部类型" clearable style="width: 150px" data-testid="ci-search-type">
            <el-option label="服务器" value="server" />
            <el-option label="网络设备" value="network_device" />
            <el-option label="数据库" value="database" />
            <el-option label="中间件" value="middleware" />
            <el-option label="应用" value="application" />
            <el-option label="容器" value="container" />
            <el-option label="K8s 资源" value="k8s_resource" />
            <el-option label="云资源" value="cloud_resource" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px" data-testid="ci-search-status">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="已退役" value="decommissioned" />
          </el-select>
        </el-form-item>

        <el-form-item label="环境">
          <el-select v-model="searchForm.environment" placeholder="全部环境" clearable style="width: 120px" data-testid="ci-search-environment">
            <el-option label="生产" value="production" />
            <el-option label="测试" value="int" />
            <el-option label="开发" value="dev" />
          </el-select>
        </el-form-item>

        <el-form-item label="名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入名称"
            clearable
            style="width: 200px"
            data-testid="ci-search-name"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" data-testid="ci-search-btn">搜索</el-button>
          <el-button @click="handleReset" data-testid="ci-reset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="ciList"
        stripe
        border
        style="width: 100%"
        data-testid="ci-table"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="代码" width="150" />
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.ci_type)">{{ getTypeLabel(row.ci_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" effect="plain">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="environment" label="环境" width="100" />
        <el-table-column prop="owner" label="负责人" width="120" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="handleViewDetail(row)"
              :data-testid="`ci-view-${row.id}`"
            >
              详情
            </el-button>
            <el-button link type="primary" @click="handleEdit(row)" :data-testid="`ci-edit-${row.id}`">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)" :data-testid="`ci-delete-${row.id}`">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
        data-testid="ci-pagination"
      />
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingCI ? '编辑配置项' : '新建配置项'"
      width="600px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="ciForm"
        :rules="rules"
        label-width="100px"
        data-testid="ci-form"
      >
        <el-form-item label="类型" prop="ci_type">
          <el-select v-model="ciForm.ci_type" placeholder="请选择类型" style="width: 100%" data-testid="ci-form-type">
            <el-option label="服务器" value="server" />
            <el-option label="网络设备" value="network_device" />
            <el-option label="数据库" value="database" />
            <el-option label="中间件" value="middleware" />
            <el-option label="应用" value="application" />
            <el-option label="容器" value="container" />
            <el-option label="K8s 资源" value="k8s_resource" />
            <el-option label="云资源" value="cloud_resource" />
          </el-select>
        </el-form-item>

        <el-form-item label="代码" prop="code">
          <el-input v-model="ciForm.code" placeholder="请输入唯一代码" data-testid="ci-form-code" />
        </el-form-item>

        <el-form-item label="名称" prop="name">
          <el-input v-model="ciForm.name" placeholder="请输入名称" data-testid="ci-form-name" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="ciForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
            data-testid="ci-form-description"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="ciForm.status" placeholder="请选择状态" style="width: 100%" data-testid="ci-form-status">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="已退役" value="decommissioned" />
          </el-select>
        </el-form-item>

        <el-form-item label="环境" prop="environment">
          <el-select v-model="ciForm.environment" placeholder="请选择环境" style="width: 100%" data-testid="ci-form-environment">
            <el-option label="生产" value="production" />
            <el-option label="测试" value="int" />
            <el-option label="开发" value="dev" />
          </el-select>
        </el-form-item>

        <el-form-item label="负责人" prop="owner">
          <el-input v-model="ciForm.owner" placeholder="请输入负责人" data-testid="ci-form-owner" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false" data-testid="ci-form-cancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting" data-testid="ci-form-submit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { CI, CIType, CIStatus } from '@/api/ci'
import { getCIList, createCI, updateCI, deleteCI, searchCIs } from '@/api/ci'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingCI = ref<CI | null>(null)
const formRef = ref<FormInstance>()

const ciList = ref<CI[]>([])
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const searchForm = reactive({
  ci_type: '' as CIType | '',
  status: '' as CIStatus | '',
  environment: '',
  name: '',
})

const ciForm = reactive({
  ci_type: '' as CIType,
  code: '',
  name: '',
  description: '',
  status: 'online' as CIStatus,
  environment: 'production',
  owner: '',
})

const rules: FormRules = {
  ci_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  code: [{ required: true, message: '请输入代码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  environment: [{ required: true, message: '请选择环境', trigger: 'change' }],
}

const getTypeLabel = (type: CIType): string => {
  const labels: Record<CIType, string> = {
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

const getTypeTag = (type: CIType): string => {
  const tags: Record<CIType, string> = {
    server: '',
    network_device: 'success',
    database: 'warning',
    middleware: 'info',
    application: 'primary',
    container: 'success',
    k8s_resource: 'warning',
    cloud_resource: 'danger',
  }
  return tags[type] || ''
}

const getStatusLabel = (status: CIStatus): string => {
  const labels: Record<CIStatus, string> = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中',
    decommissioned: '已退役',
  }
  return labels[status] || status
}

const getStatusTag = (status: CIStatus): string => {
  const tags: Record<CIStatus, string> = {
    online: 'success',
    offline: 'info',
    maintenance: 'warning',
    decommissioned: 'danger',
  }
  return tags[status] || ''
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getCIList({
      name: searchForm.name || undefined,
      ci_type: searchForm.ci_type || undefined,
      status: searchForm.status || undefined,
      environment: searchForm.environment || undefined,
      page: pagination.page,
      page_size: pagination.page_size,
    })
    if (res.success && res.data) {
      ciList.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取配置项列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.ci_type = ''
  searchForm.status = ''
  searchForm.environment = ''
  searchForm.name = ''
  handleSearch()
}

const handleViewDetail = (row: CI) => {
  router.push(`/cis/${row.id}`)
}

const handleEdit = (row: CI) => {
  editingCI.value = row
  ciForm.ci_type = row.ci_type
  ciForm.code = row.code
  ciForm.name = row.name
  ciForm.description = row.description || ''
  ciForm.status = row.status
  ciForm.environment = row.environment
  ciForm.owner = row.owner || ''
  showCreateDialog.value = true
}

const handleDelete = async (row: CI) => {
  try {
    await ElMessageBox.confirm(`确定要删除配置项 "${row.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteCI(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (editingCI.value) {
        await updateCI(editingCI.value.id, ciForm)
        ElMessage.success('更新成功')
      } else {
        await createCI(ciForm)
        ElMessage.success('创建成功')
      }
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
  editingCI.value = null
  ciForm.ci_type = '' as CIType
  ciForm.code = ''
  ciForm.name = ''
  ciForm.description = ''
  ciForm.status = 'online'
  ciForm.environment = 'production'
  ciForm.owner = ''
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.ci-list-container {
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
