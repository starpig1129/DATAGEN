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
import { useRouter } from 'vue-router'
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
import { useSettingsStore } from '@/stores/settings'
import NotificationList from '@/components/common/NotificationList.vue'

// Store 和路由
const settingsStore = useSettingsStore()
const router = useRouter()

// 響應式數據
const searchQuery = ref('')
const notificationDrawer = ref(false)
const notificationCount = ref(3)

// 計算屬性
const isMobileDevice = computed(() => window.innerWidth < 768)
const userAvatar = computed(() => 'https://avatars.githubusercontent.com/u/1?v=4')
const isDarkMode = computed(() => settingsStore.currentTheme === 'dark')

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
  const newTheme = settingsStore.currentTheme === 'dark' ? 'light' : 'dark'
  settingsStore.setTheme(newTheme)
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      console.log('打開個人資料')
      break
    case 'settings':
      router.push('/settings')
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
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  z-index: 1000;
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
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: rotate(360deg);
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

.theme-toggle {
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  transform: scale(1.1);
  background: linear-gradient(135deg, #ffd700, #ff8c00);
}

.user-avatar {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.user-avatar:hover {
  transform: scale(1.1);
  border-color: var(--el-color-primary);
  box-shadow: 0 0 15px rgba(64, 158, 255, 0.3);
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

/* 深色主題增強 */
.dark .app-header {
  background: linear-gradient(135deg, rgba(31, 41, 55, 0.9), rgba(55, 65, 81, 0.9));
  border-bottom: 1px solid rgba(75, 85, 99, 0.5);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
}

.dark .app-title {
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dark .theme-toggle:hover {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.dark .user-avatar:hover {
  border-color: #60a5fa;
  box-shadow: 0 0 15px rgba(96, 165, 250, 0.4);
}

/* 毛玻璃效果 */
.app-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: inherit;
  backdrop-filter: blur(10px);
  z-index: -1;
}
</style>