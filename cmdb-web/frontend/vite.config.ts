import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0', // 允许外部访问，用于 Playwright 测试
    // 代理配置已移除，使用 MSW 进行 API Mock
  },
  optimizeDeps: {
    exclude: ['msw', '@mswjs/interceptors'],
  },
})
