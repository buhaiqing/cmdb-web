<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <el-icon :size="32"><Setting /></el-icon>
          <h2>CMDB 配置管理数据库</h2>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        label-width="80px"
        @submit.prevent="handleLogin"
        data-testid="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            data-testid="login-username"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            data-testid="login-password"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            data-testid="login-submit"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <el-link type="primary" @click="showRegister = !showRegister" data-testid="login-toggle-register">
          {{ showRegister ? '返回登录' : '注册账号' }}
        </el-link>
      </div>
    </el-card>

    <!-- 注册对话框 -->
    <el-dialog v-model="showRegister" title="用户注册" width="400px" data-testid="register-dialog">
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
        data-testid="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="3-50 个字符" data-testid="register-username" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" data-testid="register-email" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="至少 8 个字符"
            data-testid="register-password"
          />
        </el-form-item>

        <el-form-item label="全名" prop="full_name">
          <el-input v-model="registerForm.full_name" placeholder="可选" data-testid="register-fullname" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showRegister = false" data-testid="register-cancel">取消</el-button>
        <el-button type="primary" @click="handleRegister" data-testid="register-submit">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { login, register } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const showRegister = ref(false)
const formRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: '',
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  full_name: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerRules: FormRules = {
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

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const res = await login(loginForm)
      if (res.success && res.data) {
        userStore.setToken(res.data.access_token)
        // 获取用户信息
        const { getCurrentUser } = await import('@/api/auth')
        const userInfo = await getCurrentUser()
        if (userInfo.success && userInfo.data) {
          userStore.setUserInfo(userInfo.data)
        }
        ElMessage.success('登录成功')
        router.push((route.query.from as string) || '/')
      }
    } catch (error: any) {
      console.error('登录失败:', error)
      const message = error?.response?.data?.error?.message || error?.message || '登录失败'
      ElMessage.error(message)
    } finally {
      loading.value = false
    }
  })
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      const res = await register(registerForm)
      if (res.success) {
        ElMessage.success('注册成功，请登录')
        showRegister.value = false
      }
    } catch (error) {
      console.error('注册失败:', error)
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.login-header {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}

.login-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.login-footer {
  text-align: center;
  margin-top: 16px;
}
</style>
