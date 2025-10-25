<template>
  <div
    class="app-layout"
    :class="layoutClasses"
  >
    <!-- 頂部導航欄 -->
    <AppHeader />
    
    <!-- 主要內容區域 -->
    <div class="app-body">
      <!-- 側邊欄 -->
      <AppSidebar
        v-if="!isMobileDevice"
        :collapsed="settingsStore.settings.user.interface.sidebarCollapsed"
      />
      
      <!-- 主內容區 -->
      <main class="app-main">
        <slot />
      </main>
    </div>
    
    <!-- 底部狀態欄 -->
    <AppFooter v-if="showFooter" />
    
    <!-- 移動端抽屜側邊欄 -->
    <el-drawer
      v-model="drawerVisible"
      title="導航菜單"
      :size="280"
      direction="ltr"
      class="mobile-sidebar"
    >
      <AppSidebar />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'

// Store
const settingsStore = useSettingsStore()

// 響應式狀態
const drawerVisible = ref(false)
const showFooter = ref(true)

// 模擬移動設備檢測 (實際上應該從store獲取)
const isMobileDevice = computed(() => {
  return window.innerWidth < 768
})

// 計算界面設定相關的 CSS 類別
const layoutClasses = computed(() => {
  const classes: string[] = []
  const interfaceSettings = settingsStore.settings.user.interface
  
  if (interfaceSettings.sidebarCollapsed) {
    classes.push('sidebar-collapsed')
  }
  
  if (interfaceSettings.compactMode) {
    classes.push('compact-mode')
  }
  
  if (!interfaceSettings.showToolbar) {
    classes.push('hide-toolbar')
  }
  
  if (!interfaceSettings.animationsEnabled) {
    classes.push('no-animations')
  }
  
  classes.push(`font-size-${interfaceSettings.fontSize}`)
  classes.push(`density-${interfaceSettings.density}`)
  
  return classes
})

// 暴露給父組件的方法
defineExpose({
  toggleDrawer: () => {
    drawerVisible.value = !drawerVisible.value
  }
})
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background: var(--el-bg-color);
  transition: background-color 0.3s ease;
}

/* 界面設定 - 側邊欄摺疊 */
.app-layout.sidebar-collapsed .app-body {
  /* 當側邊欄摺疊時，主內容區域會自動調整 */
}

/* 界面設定 - 緊湊模式 */
.app-layout.compact-mode .app-main {
  padding: 8px;
  font-size: 0.9em;
}

.app-layout.compact-mode .app-body {
  gap: 0;
}

/* 界面設定 - 隱藏工具欄 */
.app-layout.hide-toolbar .app-header {
  display: none;
}

.app-layout.hide-toolbar .app-body {
  height: 100vh; /* 佔據整個視窗高度 */
}

/* 界面設定 - 禁用動畫 */
.app-layout.no-animations,
.app-layout.no-animations * {
  transition: none !important;
  animation: none !important;
}

/* 界面設定 - 字體大小 */
.app-layout.font-size-small {
  font-size: 0.875rem; /* 14px */
}

.app-layout.font-size-medium {
  font-size: 1rem; /* 16px */
}

.app-layout.font-size-large {
  font-size: 1.125rem; /* 18px */
}

/* 界面設定 - 密度控制 */
.app-layout.density-compact .app-main {
  padding: 8px;
  line-height: 1.3;
}

.app-layout.density-compact .el-form-item {
  margin-bottom: 12px;
}

.app-layout.density-comfortable .app-main {
  padding: 16px;
  line-height: 1.5;
}

.app-layout.density-spacious .app-main {
  padding: 24px;
  line-height: 1.7;
}

.app-layout.density-spacious .el-form-item {
  margin-bottom: 28px;
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: 16px;
  background: var(--el-bg-color-page);
  transition: background-color 0.3s ease, padding 0.3s ease;
}

/* 移動端適配 */
@media (max-width: 768px) {
  .app-main {
    padding: 12px;
  }
  
  .app-layout.compact-mode .app-main {
    padding: 6px;
  }
  
  .app-layout.density-spacious .app-main {
    padding: 16px;
  }
}

/* 深色主題優化配色 */
.dark .app-layout {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

.dark .app-main {
  background: rgba(31, 41, 55, 0.8);
  backdrop-filter: blur(10px);
}

/* 滾動條美化 */
.app-main::-webkit-scrollbar {
  width: 8px;
}

.app-main::-webkit-scrollbar-track {
  background: transparent;
}

.app-main::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.5);
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.app-main::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.7);
}

.dark .app-main::-webkit-scrollbar-thumb {
  background: rgba(75, 85, 99, 0.6);
}

.dark .app-main::-webkit-scrollbar-thumb:hover {
  background: rgba(75, 85, 99, 0.8);
}

/* 移動端抽屜優化 */
.mobile-sidebar {
  --el-drawer-bg-color: var(--el-bg-color);
}

.dark .mobile-sidebar {
  --el-drawer-bg-color: rgba(31, 41, 55, 0.95);
  backdrop-filter: blur(20px);
}

/* 緊湊模式下的特殊樣式 */
.app-layout.compact-mode .mobile-sidebar {
  --el-drawer-size: 240px;
}

/* 字體大小影響整體佈局 */
.app-layout.font-size-small .app-main {
  line-height: 1.4;
}

.app-layout.font-size-large .app-main {
  line-height: 1.6;
}
</style>