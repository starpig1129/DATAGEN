import { createApp, markRaw } from 'vue'
import { createPinia } from 'pinia'
import { DefaultApolloClient } from '@vue/apollo-composable'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { apolloClient } from './graphql/client'
import { i18n } from './i18n'

// 樣式導入
import 'element-plus/dist/index.css'
import './assets/styles/main.css'
import './assets/styles/dark-mode-fix.css'

// 創建應用實例
const app = createApp(App)

// Pinia 狀態管理
const pinia = createPinia()
app.use(pinia)

// Vue I18n 國際化
app.use(i18n)

// Vue Router
app.use(router)

// Element Plus UI 庫
app.use(ElementPlus)

// Element Plus 圖標 - 使用 markRaw 避免響應式警告
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, markRaw(component))
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

// 初始化設定store
async function initializeApp() {
  const { useSettingsStore } = await import('./stores/settings')
  const { setLocale, getCurrentLocale } = await import('./i18n')
  const settingsStore = useSettingsStore()
  
  try {
    // 啟動語言強制更新器
    const { setupLanguageForcer } = await import('./utils/language-forcer')
    setupLanguageForcer()
    
    // 設定預設語言為繁體中文，避免初始化衝突
    await setLocale('zh-TW')
    
    // 初始化設定store（會自動應用保存的設定）
    await settingsStore.initialize()
    
    console.log('✅ 應用初始化完成:', {
      language: settingsStore.currentLanguage,
      theme: settingsStore.currentTheme,
      htmlClass: document.documentElement.className,
      htmlDataTheme: document.documentElement.getAttribute('data-theme')
    })
  } catch (error) {
    console.error('❌ 設定store初始化失敗:', error)
  }
  
  // 掛載應用
  app.mount('#app')
}

// 啟動應用
initializeApp()

// 熱模組替換
if (import.meta.hot) {
  import.meta.hot.accept()
}