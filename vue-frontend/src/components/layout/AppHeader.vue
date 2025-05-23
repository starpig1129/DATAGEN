<template>
  <header class="app-header">
    <div class="header-left">
      <!-- 移動端菜單按鈕 -->
      <el-button
        v-if="isMobileDevice"
        :icon="Menu"
        circle
        @click="toggleSidebar"
        class="mobile-menu-btn"
      />
      
      <!-- Logo 和標題 -->
      <div class="logo-section">
        <img src="/logo.svg" alt="Logo" class="logo" />
        <h1 class="app-title">多代理數據分析系統</h1>
      </div>
    </div>

    <div class="header-center">
      <!-- 搜索框 -->
      <el-input
        v-model="searchQuery"
        placeholder="搜索..."
        :prefix-icon="Search"
        class="search-input"
        clearable
        @keyup.enter="handleSearch"
      />
    </div>

    <div class="header-right">
      <!-- 通知 -->
      <el-badge :value="notificationCount" :hidden="notificationCount === 0">
        <el-button :icon="Bell" circle @click="showNotifications" />
      </el-badge>

      <!-- 主題切換 -->
      <el-button
        :icon="isDarkMode ? Sunny : Moon"
        circle
        @click="toggleTheme"
        class="theme-toggle"
      />

      <!-- 用戶菜單 -->
      <el-dropdown @command="handleUserCommand">
        <el-avatar :size="32" :src="userAvatar" class="user-avatar">
          <el-icon><User /></el-icon>
        </el-avatar>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              個人資料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              設置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              登出
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 通知抽屜 -->
    <el-drawer
      v-model="notificationDrawer"
      title="通知"
      direction="rtl"
      size="320px"
    >
      <NotificationList />
    </el-drawer>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Menu,
  Search,
  Bell,
  Sunny,
  Moon,
  User,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import NotificationList from '@/components/common/NotificationList.vue'

// 響應式數據
const searchQuery = ref('')
const notificationDrawer = ref(false)
const notificationCount = ref(3)
const isDarkMode = ref(false)

// 計算屬性
const isMobileDevice = computed(() => window.innerWidth < 768)
const userAvatar = computed(() => 'https://avatars.githubusercontent.com/u/1?v=4')

// 事件處理
const emit = defineEmits<{
  toggleSidebar: []
}>()

const toggleSidebar = () => {
  emit('toggleSidebar')
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    console.log('搜索:', searchQuery.value)
    // 實現搜索邏輯
  }
}

const showNotifications = () => {
  notificationDrawer.value = true
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  // 實現主題切換邏輯
  document.documentElement.classList.toggle('dark', isDarkMode.value)
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      console.log('打開個人資料')
      break
    case 'settings':
      console.log('打開設置')
      break
    case 'logout':
      console.log('登出')
      break
  }
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 16px;
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 32px;
  height: 32px;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 400px;
  margin: 0 32px;
}

.search-input {
  width: 100%;
  max-width: 300px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.mobile-menu-btn {
  margin-right: 8px;
}

/* 移動端適配 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }
  
  .app-title {
    font-size: 18px;
  }
  
  .header-center {
    margin: 0 16px;
  }
  
  .search-input {
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .header-center {
    display: none;
  }
  
  .header-right {
    gap: 8px;
  }
}

/* 深色主題 */
.dark .app-header {
  background-color: var(--el-bg-color);
  border-bottom-color: var(--el-border-color-dark);
}
</style>