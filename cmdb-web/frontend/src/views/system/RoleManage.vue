<template>
  <div class="role-manage-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="showCreateDialog = true" data-testid="role-create-btn">
            <el-icon><Plus /></el-icon>
            新建角色
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" data-testid="role-search-form">
        <el-form-item label="角色名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入角色名称"
            clearable
            style="width: 200px"
            data-testid="role-search-name"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" data-testid="role-search-btn">搜索</el-button>
          <el-button @click="handleReset" data-testid="role-reset-btn">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="roleList" stripe border style="width: 100%" data-testid="role-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="权限数量" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.permissions?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)" :data-testid="`role-edit-${row.id}`">
              编辑
            </el-button>
            <el-button link type="primary" @click="handleViewPermissions(row)" :data-testid="`role-perms-${row.id}`">
              权限
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)" :data-testid="`role-delete-${row.id}`">
              删除
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
        data-testid="role-pagination"
      />
    </el-card>

    <el-dialog v-model="showCreateDialog" :title="editingRole ? '编辑角色' : '新建角色'" width="600px" @closed="resetForm">
      <el-form ref="formRef" :model="roleForm" :rules="rules" label-width="100px" data-testid="role-form">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" data-testid="role-form-name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input
            v-model="roleForm.code"
            placeholder="请输入角色编码（如 admin, operator）"
            :disabled="!!editingRole"
            data-testid="role-form-code"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="roleForm.description" type="textarea" :rows="3" placeholder="请输入描述" data-testid="role-form-desc" />
        </el-form-item>
        <el-form-item label="权限" prop="permission_ids">
          <el-transfer
            v-model="roleForm.permission_ids"
            :data="permissionOptions"
            :titles="['可用权限', '已选权限']"
            :props="{ key: 'id', label: 'name' }"
            data-testid="role-form-permissions"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false" data-testid="role-form-cancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting" data-testid="role-form-submit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPermissionDialog" title="角色权限" width="500px">
      <el-table :data="selectedRole?.permissions || []" stripe border>
        <el-table-column prop="name" label="权限名称" width="150" />
        <el-table-column prop="code" label="权限编码" width="150" />
        <el-table-column prop="module" label="所属模块" width="100" />
      </el-table>
      <el-empty v-if="!selectedRole?.permissions?.length" description="暂无权限" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Role, Permission } from '@/api/role'
import { getRoleList, createRole, updateRole, deleteRole, getPermissionList } from '@/api/role'

const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showPermissionDialog = ref(false)
const editingRole = ref<Role | null>(null)
const selectedRole = ref<Role | null>(null)
const formRef = ref<FormInstance>()

const roleList = ref<Role[]>([])
const permissionList = ref<Permission[]>([])
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const searchForm = reactive({
  name: '',
})

const roleForm = reactive({
  name: '',
  code: '',
  description: '',
  permission_ids: [] as number[],
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[a-z_]+$/, message: '角色编码只能包含小写字母和下划线', trigger: 'blur' },
  ],
}

const permissionOptions = computed(() => {
  return permissionList.value.map((p) => ({
    id: p.id,
    name: `${p.module} - ${p.name}`,
  }))
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getRoleList({
      page: pagination.page,
      page_size: pagination.page_size,
      name: searchForm.name || undefined,
    })
    if (res.success && res.data) {
      roleList.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('获取角色列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchPermissions = async () => {
  try {
    const res = await getPermissionList()
    if (res.success && res.data) {
      permissionList.value = res.data
    }
  } catch (error) {
    console.error('获取权限列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.name = ''
  handleSearch()
}

const handleEdit = (row: Role) => {
  editingRole.value = row
  roleForm.name = row.name
  roleForm.code = row.code
  roleForm.description = row.description || ''
  roleForm.permission_ids = row.permissions?.map((p) => p.id) || []
  showCreateDialog.value = true
}

const handleViewPermissions = (row: Role) => {
  selectedRole.value = row
  showPermissionDialog.value = true
}

const handleDelete = async (row: Role) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色 "${row.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteRole(row.id)
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
      if (editingRole.value) {
        await updateRole(editingRole.value.id, {
          name: roleForm.name,
          description: roleForm.description,
          permission_ids: roleForm.permission_ids,
        })
        ElMessage.success('更新成功')
      } else {
        await createRole({
          name: roleForm.name,
          code: roleForm.code,
          description: roleForm.description,
          permission_ids: roleForm.permission_ids,
        })
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
  editingRole.value = null
  roleForm.name = ''
  roleForm.code = ''
  roleForm.description = ''
  roleForm.permission_ids = []
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
  fetchPermissions()
})
</script>

<style scoped>
.role-manage-container {
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
