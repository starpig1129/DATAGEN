<template>
  <div class="app-layout">
    <!-- 頂部導航欄 -->
    <AppHeader />
    
    <!-- 主要內容區域 -->
    <div class="app-body">
      <!-- 側邊欄 -->
      <AppSidebar v-if="!isMobileDevice" />
      
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
import { computed, ref } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'

// 響應式狀態
const drawerVisible = ref(false)
const showFooter = ref(true)

// 模擬移動設備檢測 (實際上應該從store獲取)
const isMobileDevice = computed(() => {
  return window.innerWidth < 768
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
  transition: background-color 0.3s ease;
}

/* 移動端適配 */
@media (max-width: 768px) {
  .app-main {
    padding: 12px;
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
</style>