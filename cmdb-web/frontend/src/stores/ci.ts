import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CI } from '@/api/ci'

export const useCIStore = defineStore('ci', () => {
  // 状态
  const ciList = ref<CI[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentCI = ref<CI | null>(null)

  // 方法
  const setCIList = (items: CI[], totalCount: number) => {
    ciList.value = items
    total.value = totalCount
  }

  const setCurrentCI = (ci: CI | null) => {
    currentCI.value = ci
  }

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  return {
    ciList,
    total,
    loading,
    currentCI,
    setCIList,
    setCurrentCI,
    setLoading,
  }
})
