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
  background-color: var(--el-bg-color);
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
  background-color: var(--el-bg-color-page);
}

/* 移動端適配 */
@media (max-width: 768px) {
  .app-main {
    padding: 12px;
  }
}

/* 深色主題支持 */
.dark .app-layout {
  background-color: var(--el-bg-color);
}

.dark .app-main {
  background-color: var(--el-bg-color-page);
}
</style>