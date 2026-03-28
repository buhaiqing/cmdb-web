import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

async function bootstrap() {
  // 在开发环境下初始化 Mock 服务
  if ((import.meta as any).env.DEV) {
    const { initMocks } = await import('./mocks')
    await initMocks()
  }

  const app = createApp(App)
  const pinia = createPinia()

  // 注册 Element Plus 图标
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(pinia)
  app.use(router)
  app.use(ElementPlus, {
    locale: zhCn,
  })

  app.mount('#app')
}

bootstrap()
