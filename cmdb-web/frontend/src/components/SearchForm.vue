<template>
  <div class="search-form" :data-testid="testId">
    <el-form
      :model="formData"
      :inline="inline"
      label-width="80px"
      size="default"
    >
      <el-form-item
        v-for="field in fields"
        :key="field.prop"
        :label="field.label"
        :prop="field.prop"
        :data-testid="`form-item-${field.prop}`"
      >
        <!-- 文本输入 -->
        <el-input
          v-if="field.type === 'text'"
          v-model="formData[field.prop]"
          :placeholder="field.placeholder"
          :clearable="field.clearable ?? true"
          :data-testid="`input-${field.prop}`"
          @keyup.enter="handleSearch"
        />

        <!-- 数字输入 -->
        <el-input-number
          v-else-if="field.type === 'number'"
          v-model="formData[field.prop]"
          :placeholder="field.placeholder"
          :min="field.min"
          :max="field.max"
          :step="field.step || 1"
          :controls="field.controls ?? true"
          style="width: 100%"
          :data-testid="`input-number-${field.prop}`"
        />

        <!-- 下拉选择 -->
        <el-select
          v-else-if="field.type === 'select'"
          v-model="formData[field.prop]"
          :placeholder="field.placeholder"
          :clearable="field.clearable ?? true"
          :multiple="field.multiple"
          style="width: 100%"
          :data-testid="`select-${field.prop}`"
        >
          <el-option
            v-for="opt in field.options"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>

        <!-- 日期选择 -->
        <el-date-picker
          v-else-if="field.type === 'date'"
          v-model="formData[field.prop]"
          :type="field.dateType || 'date'"
          :placeholder="field.placeholder"
          :value-format="field.valueFormat || 'YYYY-MM-DD'"
          style="width: 100%"
          :data-testid="`date-picker-${field.prop}`"
        />

        <!-- 日期范围选择 -->
        <el-date-picker
          v-else-if="field.type === 'daterange'"
          v-model="formData[field.prop]"
          type="daterange"
          range-separator="至"
          :start-placeholder="field.startPlaceholder || '开始日期'"
          :end-placeholder="field.endPlaceholder || '结束日期'"
          :value-format="field.valueFormat || 'YYYY-MM-DD'"
          style="width: 100%"
          :data-testid="`date-range-${field.prop}`"
        />
      </el-form-item>

      <!-- 操作按钮 -->
      <el-form-item data-testid="form-actions">
        <el-button
          type="primary"
          :icon="Search"
          @click="handleSearch"
          :loading="loading"
          data-testid="btn-search"
        >
          搜索
        </el-button>
        <el-button
          :icon="Refresh"
          @click="handleReset"
          data-testid="btn-reset"
        >
          重置
        </el-button>
        <slot name="extra-actions" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'

// 字段配置接口
export interface SearchField {
  prop: string
  label: string
  type: 'text' | 'number' | 'select' | 'date' | 'daterange'
  placeholder?: string
  startPlaceholder?: string
  endPlaceholder?: string
  options?: Array<{ label: string; value: any }>
  clearable?: boolean
  multiple?: boolean
  dateType?: 'date' | 'datetime' | 'week' | 'month' | 'year'
  valueFormat?: string
  min?: number
  max?: number
  step?: number
  controls?: boolean
}

// Props 定义
interface Props {
  fields: SearchField[]
  inline?: boolean
  loading?: boolean
  testId?: string
}

const props = withDefaults(defineProps<Props>(), {
  inline: true,
  loading: false,
  testId: 'search-form'
})

// Emits 定义
const emit = defineEmits<{
  'search': [values: Record<string, any>]
  'reset': []
}>()

// 表单数据
const formData = reactive<Record<string, any>>({})

// 初始化表单数据
props.fields.forEach(field => {
  if (field.multiple) {
    formData[field.prop] = []
  } else {
    formData[field.prop] = field.type === 'daterange' ? [] : undefined
  }
})

// 处理搜索
const handleSearch = () => {
  const values = { ...formData }
  // 过滤空值
  Object.keys(values).forEach(key => {
    if (
      values[key] === undefined ||
      values[key] === null ||
      values[key] === '' ||
      (Array.isArray(values[key]) && values[key].length === 0)
    ) {
      delete values[key]
    }
  })
  emit('search', values)
}

// 处理重置
const handleReset = () => {
  props.fields.forEach(field => {
    if (field.multiple) {
      formData[field.prop] = []
    } else {
      formData[field.prop] = field.type === 'daterange' ? [] : undefined
    }
  })
  emit('reset')
  handleSearch()
}

// 暴露方法给父组件
defineExpose({
  getFormData: () => ({ ...formData }),
  setFieldValue: (prop: string, value: any) => {
    formData[prop] = value
  }
})
</script>

<style scoped>
.search-form {
  padding: 16px;
  background: #fff;
  border-radius: 4px;
  margin-bottom: 16px;
}
</style>
