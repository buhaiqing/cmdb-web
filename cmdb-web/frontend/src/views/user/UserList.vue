<template>
  <div class="user-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showCreateDialog = true" data-testid="user-create-btn">
            <el-icon><Plus /></el-icon>
            新建用户
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="userList" stripe border style="width: 100%" data-testid="user-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="full_name" label="全名" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="超级管理员" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_superuser ? 'success' : 'info'">
              {{ row.is_superuser ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)" :data-testid="`user-edit-${row.id}`">编辑</el-button>
            <el-button
              v-if="!row.is_superuser"
              link
              type="danger"
              @click="handleDelete(row)"
              :data-testid="`user-delete-${row.id}`"
            >
              删除
            </el-button>
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
        data-testid="user-pagination"
      />
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '新建用户'"
      width="500px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="userForm" :rules="rules" label-width="80px" data-testid="user-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="3-50 个字符" data-testid="user-form-username" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" data-testid="user-form-email" />
        </el-form-item>

        <el-form-item v-if="!editingUser" label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="至少 8 个字符"
            data-testid="user-form-password"
          />
        </el-form-item>

        <el-form-item label="全名" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="可选" data-testid="user-form-fullname" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting" data-testid="user-form-submit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { UserInfo } from '@/api/auth'
import { getUserList } from '@/api/auth'

const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingUser = ref<UserInfo | null>(null)
const formRef = ref<FormInstance>()

const userList = ref<UserInfo[]>([])
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const userForm = reactive({
  username: '',
  email: '',
  password: '',
  full_name: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少 8 个字符', trigger: 'blur' },
  ],
}

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    active: '正常',
    inactive: '禁用',
    locked: '锁定',
  }
  return labels[status] || status
}

const getStatusTag = (status: string): string => {
  const tags: Record<string, string> = {
    active: 'success',
    inactive: 'danger',
    locked: 'warning',
  }
  return tags[status] || ''
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getUserList({
      page: pagination.page,
      page_size: pagination.page_size,
    })
    if (res.success && res.data) {
      userList.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleEdit = (row: UserInfo) => {
  editingUser.value = row
  userForm.username = row.username
  userForm.email = row.email
  userForm.full_name = row.full_name || ''
  showCreateDialog.value = true
}

const handleDelete = async (row: UserInfo) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    // TODO: 实现删除 API
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
      // TODO: 实现创建/更新 API
      ElMessage.success(editingUser.value ? '更新成功' : '创建成功')
      showCreateDialog.value = false
      fetchData()
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  editingUser.value = null
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.full_name = ''
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.user-list-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
