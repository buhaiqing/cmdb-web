<template>
  <div class="data-table" :data-testid="testId">
    <el-table
      :data="data"
      :loading="loading"
      :stripe="stripe"
      :border="border"
      @sort-change="handleSortChange"
      @selection-change="handleSelectionChange"
      style="width: 100%"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="selectable"
        type="selection"
        width="55"
        data-testid="table-selection"
      />

      <!-- 动态列 -->
      <el-table-column
        v-for="col in columns"
        :key="col.prop"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
        :min-width="col.minWidth"
        :sortable="col.sortable"
        :align="col.align || 'left'"
        :data-testid="`table-column-${col.prop}`"
      >
        <template #default="{ row }">
          <!-- 自定义渲染插槽 -->
          <slot :name="col.prop" :row="row" :value="row[col.prop]">
            <!-- 默认渲染：格式化器或原始值 -->
            <span v-if="col.formatter">
              {{ col.formatter(row[col.prop], row, col) }}
            </span>
            <span v-else-if="col.prop === 'status'">
              <el-tag :type="getStatusType(row[col.prop])">
                {{ getStatusLabel(row[col.prop]) }}
              </el-tag>
            </span>
            <span v-else>
              {{ row[col.prop] }}
            </span>
          </slot>
        </template>
      </el-table-column>

      <!-- 操作列 -->
      <el-table-column
        v-if="showActions"
        label="操作"
        width="200"
        fixed="right"
        data-testid="table-actions"
      >
        <template #default="{ row }">
          <slot name="actions" :row="row">
            <el-button
              link
              type="primary"
              size="small"
              @click="handleView(row)"
              data-testid="action-view"
            >
              查看
            </el-button>
            <el-button
              link
              type="primary"
              size="small"
              @click="handleEdit(row)"
              data-testid="action-edit"
            >
              编辑
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="handleDelete(row)"
              data-testid="action-delete"
            >
              删除
            </el-button>
          </slot>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div
      v-if="pagination"
      class="table-pagination"
      data-testid="table-pagination"
    >
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        data-testid="pagination"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 列配置接口
export interface TableColumn {
  prop: string
  label: string
  width?: number
  minWidth?: number
  sortable?: boolean | 'custom'
  align?: 'left' | 'center' | 'right'
  formatter?: (value: any, row: any, column: TableColumn) => string
}

// Props 定义
interface Props {
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  stripe?: boolean
  border?: boolean
  selectable?: boolean
  showActions?: boolean
  pagination?: boolean
  total?: number
  pageSizes?: number[]
  testId?: string
}

withDefaults(defineProps<Props>(), {
  loading: false,
  stripe: true,
  border: false,
  selectable: false,
  showActions: true,
  pagination: true,
  total: 0,
  pageSizes: () => [10, 20, 50, 100],
  testId: 'data-table'
})

// Emits 定义
const emit = defineEmits<{
  'sort-change': [{ prop: string; order: string }]
  'selection-change': [selection: any[]]
  'view': [row: any]
  'edit': [row: any]
  'delete': [row: any]
  'page-change': [{ page: number; size: number }]
}>()

// 响应式状态
const currentPage = ref(1)
const pageSize = ref(10)

// 状态类型映射
const statusTypeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
  active: 'success',
  inactive: 'info',
  pending: 'warning',
  error: 'danger'
}

const statusLabelMap: Record<string, string> = {
  active: '活跃',
  inactive: '未激活',
  pending: '待处理',
  error: '错误'
}

// 获取状态标签类型
const getStatusType = (status: string): 'success' | 'warning' | 'danger' | 'info' => {
  return statusTypeMap[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: string): string => {
  return statusLabelMap[status] || status
}

// 事件处理
const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  emit('sort-change', { prop, order })
}

const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

const handleView = (row: any) => {
  emit('view', row)
}

const handleEdit = (row: any) => {
  emit('edit', row)
}

const handleDelete = (row: any) => {
  emit('delete', row)
}

const handleSizeChange = (size: number) => {
  emit('page-change', { page: currentPage.value, size })
}

const handleCurrentChange = (page: number) => {
  emit('page-change', { page, size: pageSize.value })
}
</script>

<style scoped>
.data-table {
  width: 100%;
}

.table-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding: 8px 0;
}
</style>
