<template>
  <div class="ci-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button link @click="$router.back()" data-testid="ci-detail-back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <span>配置项详情</span>
          <el-button type="primary" @click="handleEdit" data-testid="ci-detail-edit-btn">编辑</el-button>
        </div>
      </template>

      <el-descriptions v-if="ci" title="基本信息" :column="2" border data-testid="ci-detail-info">
        <el-descriptions-item label="ID">{{ ci.id }}</el-descriptions-item>
        <el-descriptions-item label="代码">{{ ci.code }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ ci.name }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag>{{ ci.ci_type }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(ci.status)">{{ ci.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="环境">{{ ci.environment }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ ci.owner || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ ci.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ ci.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ ci.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <!-- 关系图 -->
      <div class="relations-section">
        <h3>关联关系</h3>
        <el-empty v-if="relations.length === 0" description="暂无关联关系" />
        <el-table v-else :data="relations" stripe border data-testid="ci-relations-table">
          <el-table-column prop="source_ci_id" label="源配置项 ID" />
          <el-table-column prop="target_ci_id" label="目标配置项 ID" />
          <el-table-column prop="relation_type" label="关系类型" />
          <el-table-column prop="description" label="描述" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { CI } from '@/api/ci'
import { getCIDetail, getCIRelations } from '@/api/ci'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const ci = ref<CI | null>(null)
const relations = ref<unknown[]>([])

const getStatusTag = (status: string): string => {
  const tags: Record<string, string> = {
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
    const ciRes = await getCIDetail(Number(route.params.id))
    if (ciRes.success && ciRes.data) {
      ci.value = ciRes.data
    }

    const relationsRes = await getCIRelations(Number(route.params.id))
    if (relationsRes.success && relationsRes.data) {
      relations.value = relationsRes.data
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取配置项详情失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = () => {
  router.push(`/cis?edit=${ci.value?.id}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.ci-detail-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.relations-section {
  margin-top: 20px;
}

.relations-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #303133;
}
</style>
