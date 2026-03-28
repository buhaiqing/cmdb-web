<template>
  <div
    class="loading-spinner"
    :class="[{ 'is-fullscreen': fullscreen, 'is-overlay': overlay }, sizeClass]"
    :data-testid="testId"
  >
    <div class="loading-content">
      <el-icon class="loading-icon" :class="{ 'is-loading': true }">
        <Loading />
      </el-icon>
      <p v-if="text" class="loading-text">{{ text }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface Props {
  size?: 'small' | 'default' | 'large'
  color?: string
  text?: string
  fullscreen?: boolean
  overlay?: boolean
  testId?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'default',
  color: '#409eff',
  text: '',
  fullscreen: false,
  overlay: false,
  testId: 'loading-spinner'
})

// 尺寸类名
const sizeClass = computed(() => {
  return {
    'is-small': props.size === 'small',
    'is-large': props.size === 'large'
  }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner.is-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

.loading-spinner.is-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  z-index: 1000;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-icon {
  font-size: var(--loading-size, 32px);
  color: var(--loading-color, #409eff);
  animation: rotating 2s linear infinite;
}

.loading-text {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 尺寸变量 */
.loading-spinner.is-small {
  --loading-size: 24px;
}

.loading-spinner.is-large {
  --loading-size: 48px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
