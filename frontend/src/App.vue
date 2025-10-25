<template>
  <div id="app" class="app">
    <AppLayout>
      <RouterView />
    </AppLayout>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAppStore } from '@/stores/app'
import { useSettingsStore } from '@/stores/settings'
import { setLocale } from '@/i18n'

// 應用程式 store
const appStore = useAppStore()
const settingsStore = useSettingsStore()

// 監聽設定變更，全域應用
watch(() => settingsStore.currentLanguage, async (newLanguage) => {
  try {
    await setLocale(newLanguage)
    console.log('全域語言已切換為:', newLanguage)
  } catch (error) {
    console.error('全域語言切換失敗:', error)
  }
})

watch(() => settingsStore.currentTheme, (newTheme) => {
  settingsStore.applyTheme()
  console.log('全域主題已切換為:', newTheme)
})

// 初始化應用程式
onMounted(() => {
  appStore.initialize()
  
  // 監聽視窗大小變化
  window.addEventListener('resize', handleResize)
  
  // 監聽網路狀態變化
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})

// 處理視窗大小變化
const handleResize = () => {
  appStore.updateViewport()
}

// 處理網路連接
const handleOnline = () => {
  appStore.setOnlineStatus(true)
}

const handleOffline = () => {
  appStore.setOnlineStatus(false)
}
</script>

<style scoped>
.app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>