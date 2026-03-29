<template>
  <div class="relation-graph-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配置项关系图</span>
          <div class="header-actions">
            <el-select
              v-model="selectedCiId"
              placeholder="选择配置项"
              clearable
              filterable
              style="width: 200px"
              data-testid="relation-select-ci"
              @change="handleCiChange"
            >
              <el-option
                v-for="ci in ciList"
                :key="ci.id"
                :label="ci.name"
                :value="ci.id"
              />
            </el-select>
            <el-input-number
              v-model="depth"
              :min="1"
              :max="5"
              style="width: 100px; margin-left: 12px"
              data-testid="relation-depth"
              @change="handleDepthChange"
            />
            <el-button type="primary" @click="fetchGraphData" :loading="loading" data-testid="relation-refresh">
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <div class="graph-wrapper" v-loading="loading" data-testid="relation-graph">
        <div v-if="graphData.nodes.length === 0" class="empty-state">
          <el-empty description="请选择一个配置项查看关系图" />
        </div>
        <div v-else ref="graphContainer" class="graph-canvas"></div>
      </div>

      <el-divider />

      <div class="legend-section">
        <span class="legend-title">图例：</span>
        <div class="legend-items">
          <div class="legend-item">
            <span class="legend-color server"></span>
            <span>服务器</span>
          </div>
          <div class="legend-item">
            <span class="legend-color database"></span>
            <span>数据库</span>
          </div>
          <div class="legend-item">
            <span class="legend-color application"></span>
            <span>应用</span>
          </div>
          <div class="legend-item">
            <span class="legend-color network"></span>
            <span>网络设备</span>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="showNodeDetail" title="配置项详情" width="500px" data-testid="relation-node-detail">
      <el-descriptions v-if="selectedNode" :column="1" border>
        <el-descriptions-item label="ID">{{ selectedNode.id }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ selectedNode.name }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ selectedNode.ci_type }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(selectedNode.status)">{{ selectedNode.status }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showNodeDetail = false">关闭</el-button>
        <el-button type="primary" @click="goToCiDetail">查看详情</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRelationGraph, type RelationGraphData, type RelationNode } from '@/api/dashboard'
import { getCIList } from '@/api/ci'

const router = useRouter()

const loading = ref(false)
const selectedCiId = ref<number | null>(null)
const depth = ref(2)
const ciList = ref<Array<{ id: number; name: string }>>([])
const graphContainer = ref<HTMLElement | null>(null)
const showNodeDetail = ref(false)
const selectedNode = ref<RelationNode | null>(null)

const graphData = ref<RelationGraphData>({
  nodes: [],
  edges: [],
})

const getStatusTag = (status: string): string => {
  const tags: Record<string, string> = {
    online: 'success',
    offline: 'info',
    maintenance: 'warning',
    decommissioned: 'danger',
  }
  return tags[status] || ''
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

const fetchGraphData = async () => {
  if (!selectedCiId.value) {
    ElMessage.warning('请先选择一个配置项')
    return
  }

  loading.value = true
  try {
    const res = await getRelationGraph({
      ci_id: selectedCiId.value,
      depth: depth.value,
    })
    if (res.success && res.data) {
      graphData.value = res.data
      await nextTick()
      renderGraph()
    }
  } catch (error) {
    console.error('获取关系图数据失败:', error)
    ElMessage.error('获取关系图数据失败')
  } finally {
    loading.value = false
  }
}

const handleCiChange = () => {
  if (selectedCiId.value) {
    fetchGraphData()
  } else {
    graphData.value = { nodes: [], edges: [] }
  }
}

const handleDepthChange = () => {
  if (selectedCiId.value) {
    fetchGraphData()
  }
}

const renderGraph = () => {
  if (!graphContainer.value || graphData.value.nodes.length === 0) return

  const container = graphContainer.value
  container.innerHTML = ''

  const width = container.clientWidth
  const height = 500

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('width', String(width))
  svg.setAttribute('height', String(height))
  svg.style.background = '#f5f7fa'
  container.appendChild(svg)

  const nodePositions: Record<number, { x: number; y: number }> = {}
  const centerX = width / 2
  const centerY = height / 2
  const radius = Math.min(width, height) / 3

  graphData.value.nodes.forEach((node, index) => {
    const angle = (2 * Math.PI * index) / graphData.value.nodes.length
    nodePositions[node.id] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    }
  })

  graphData.value.edges.forEach((edge) => {
    const source = nodePositions[edge.source]
    const target = nodePositions[edge.target]
    if (!source || !target) return

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
    line.setAttribute('x1', String(source.x))
    line.setAttribute('y1', String(source.y))
    line.setAttribute('x2', String(target.x))
    line.setAttribute('y2', String(target.y))
    line.setAttribute('stroke', '#dcdfe6')
    line.setAttribute('stroke-width', '2')
    svg.appendChild(line)

    const midX = (source.x + target.x) / 2
    const midY = (source.y + target.y) / 2
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', String(midX))
    text.setAttribute('y', String(midY))
    text.setAttribute('text-anchor', 'middle')
    text.setAttribute('font-size', '10')
    text.setAttribute('fill', '#909399')
    text.textContent = edge.relation_type
    svg.appendChild(text)
  })

  graphData.value.nodes.forEach((node) => {
    const pos = nodePositions[node.id]
    if (!pos) return

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    g.style.cursor = 'pointer'
    g.addEventListener('click', () => handleNodeClick(node))

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    circle.setAttribute('cx', String(pos.x))
    circle.setAttribute('cy', String(pos.y))
    circle.setAttribute('r', '30')
    circle.setAttribute('fill', getNodeColor(node.ci_type))
    circle.setAttribute('stroke', '#fff')
    circle.setAttribute('stroke-width', '2')
    g.appendChild(circle)

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', String(pos.x))
    text.setAttribute('y', String(pos.y + 4))
    text.setAttribute('text-anchor', 'middle')
    text.setAttribute('font-size', '12')
    text.setAttribute('fill', '#fff')
    text.textContent = node.name.length > 6 ? node.name.substring(0, 6) + '...' : node.name
    g.appendChild(text)

    svg.appendChild(g)
  })
}

const getNodeColor = (ciType: string): string => {
  const colors: Record<string, string> = {
    server: '#409EFF',
    database: '#E6A23C',
    application: '#67C23A',
    network_device: '#909399',
    middleware: '#F56C6C',
    container: '#00d4aa',
    k8s_resource: '#9c27b0',
    cloud_resource: '#ff9800',
  }
  return colors[ciType] || '#409EFF'
}

const handleNodeClick = (node: RelationNode) => {
  selectedNode.value = node
  showNodeDetail.value = true
}

const goToCiDetail = () => {
  if (selectedNode.value) {
    router.push(`/cis/${selectedNode.value.id}`)
    showNodeDetail.value = false
  }
}

onMounted(() => {
  fetchCiList()
})

watch(
  () => graphData.value,
  () => {
    nextTick(() => {
      renderGraph()
    })
  }
)
</script>

<style scoped>
.relation-graph-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.graph-wrapper {
  min-height: 500px;
  position: relative;
}

.graph-canvas {
  width: 100%;
  height: 500px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 500px;
}

.legend-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.legend-title {
  font-weight: bold;
  color: #606266;
}

.legend-items {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.server {
  background-color: #409EFF;
}

.legend-color.database {
  background-color: #E6A23C;
}

.legend-color.application {
  background-color: #67C23A;
}

.legend-color.network {
  background-color: #909399;
}
</style>
