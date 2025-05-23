import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { DefaultApolloClient } from '@vue/apollo-composable'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { apolloClient } from './graphql/client'

// 樣式導入
import 'element-plus/dist/index.css'
import './assets/styles/main.css'

// 創建應用實例
const app = createApp(App)

// Pinia 狀態管理
const pinia = createPinia()
app.use(pinia)

// Vue Router
app.use(router)

// Element Plus UI 庫
app.use(ElementPlus)

// Element Plus 圖標
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Apollo GraphQL 客戶端
app.provide(DefaultApolloClient, apolloClient)

// 全域配置
app.config.errorHandler = (err, vm, info) => {
  console.error('應用錯誤:', err)
  console.error('組件信息:', info)
  // 這裡可以集成錯誤追蹤服務如 Sentry
}

app.config.warnHandler = (msg, vm, trace) => {
  console.warn('應用警告:', msg)
  if (import.meta.env.DEV) {
    console.warn('組件追蹤:', trace)
  }
}

// 開發環境配置
if (import.meta.env.DEV) {
  app.config.performance = true
}

// 掛載應用
app.mount('#app')

// 熱模組替換
if (import.meta.hot) {
  import.meta.hot.accept()
}