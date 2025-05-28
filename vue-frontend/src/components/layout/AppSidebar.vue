<template>
  <aside class="app-sidebar">
    <!-- 導航菜單 -->
    <el-menu
      :default-active="activeMenuKey"
      :collapse="isCollapsed"
      :router="true"
      class="sidebar-menu"
      background-color="var(--el-bg-color)"
      text-color="var(--el-text-color-primary)"
      active-text-color="var(--el-color-primary)"
    >
      <!-- 儀表板 -->
      <el-menu-item index="/dashboard" route="/">
        <el-icon><DataBoard /></el-icon>
        <span>{{ $t('navigation.dashboard') }}</span>
      </el-menu-item>

      <!-- 聊天界面 -->
      <el-menu-item index="/chat" route="/chat">
        <el-icon><ChatDotRound /></el-icon>
        <span>{{ $t('navigation.chat') }}</span>
        <el-badge
          v-if="unreadCount > 0"
          :value="unreadCount"
          :hidden="isCollapsed"
          class="menu-badge"
        />
      </el-menu-item>

      <!-- 代理監控 -->
      <el-sub-menu index="agents">
        <template #title>
          <el-icon><Monitor /></el-icon>
          <span>{{ $t('navigation.agents.title') }}</span>
        </template>
        
        <el-menu-item index="/agents" route="/agents">
          <el-icon><View /></el-icon>
          <span>{{ $t('navigation.agents.monitor') }}</span>
        </el-menu-item>
        
        <el-menu-item index="/agents/workflow">
          <el-icon><Connection /></el-icon>
          <span>{{ $t('navigation.agents.workflow') }}</span>
        </el-menu-item>
        
        <el-menu-item index="/agents/performance">
          <el-icon><TrendCharts /></el-icon>
          <span>{{ $t('navigation.agents.performance') }}</span>
        </el-menu-item>
      </el-sub-menu>

      <!-- 數據視覺化 -->
      <el-sub-menu index="visualization">
        <template #title>
          <el-icon><PieChart /></el-icon>
          <span>{{ $t('navigation.visualization.title') }}</span>
        </template>
        
        <el-menu-item index="/visualization" route="/visualization">
          <el-icon><DataAnalysis /></el-icon>
          <span>{{ $t('navigation.visualization.charts') }}</span>
        </el-menu-item>
        
        <el-menu-item index="/visualization/dashboard">
          <el-icon><Grid /></el-icon>
          <span>{{ $t('navigation.visualization.dashboard') }}</span>
        </el-menu-item>
        
        <el-menu-item index="/visualization/reports">
          <el-icon><Document /></el-icon>
          <span>{{ $t('navigation.visualization.reports') }}</span>
        </el-menu-item>
      </el-sub-menu>

      <!-- 文件管理 -->
      <el-menu-item index="/files" route="/files">
        <el-icon><Folder /></el-icon>
        <span>{{ $t('navigation.files') }}</span>
      </el-menu-item>

      <!-- 系統設置 -->
      <el-menu-item index="/settings" route="/settings">
        <el-icon><Setting /></el-icon>
        <span>{{ $t('navigation.settings') }}</span>
      </el-menu-item>
    </el-menu>

    <!-- 摺疊控制按鈕 -->
    <div class="sidebar-footer">
      <el-button
        :icon="isCollapsed ? Expand : Fold"
        circle
        size="small"
        @click="toggleCollapse"
        class="collapse-btn"
      />
    </div>

    <!-- 代理狀態指示器 -->
    <div v-if="!isCollapsed" class="agent-status-panel">
      <div class="status-title">{{ $t('navigation.agentStatus') }}</div>
      <div class="status-list">
        <div
          v-for="agent in agentStatus"
          :key="agent.id"
          class="status-item"
        >
          <div class="status-indicator" :class="agent.status"></div>
          <span class="agent-name">{{ $t(`agents.names.${agent.nameKey}`) }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import {
  DataBoard,
  ChatDotRound,
  Monitor,
  View,
  Connection,
  TrendCharts,
  PieChart,
  DataAnalysis,
  Grid,
  Document,
  Folder,
  Setting,
  Expand,
  Fold
} from '@element-plus/icons-vue'

// Props
interface Props {
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false
})

// Store
const settingsStore = useSettingsStore()

// 響應式數據
const unreadCount = ref(2)

// 當前路由
const route = useRoute()

// 計算屬性
const activeMenuKey = computed(() => route.path)

// 側邊欄摺疊狀態 - 優先使用 props，其次使用設定 store
const isCollapsed = computed(() => {
  return props.collapsed ?? settingsStore.settings.user.interface.sidebarCollapsed
})

// 模擬代理狀態數據
const agentStatus = ref([
  { id: '1', nameKey: 'processing', status: 'active' },
  { id: '2', nameKey: 'hypothesis', status: 'idle' },
  { id: '3', nameKey: 'search', status: 'processing' },
  { id: '4', nameKey: 'code', status: 'idle' },
  { id: '5', nameKey: 'visualization', status: 'active' },
  { id: '6', nameKey: 'report', status: 'idle' },
  { id: '7', nameKey: 'qualityReview', status: 'idle' },
  { id: '8', nameKey: 'optimization', status: 'idle' }
])

// 方法
const toggleCollapse = () => {
  // 切換設定 store 中的側邊欄摺疊狀態
  settingsStore.updateInterfaceSettings({
    sidebarCollapsed: !isCollapsed.value
  })
}
</script>

<style scoped>
.app-sidebar {
  width: 260px;
  height: 100%;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* 摺疊狀態的側邊欄 */
.app-sidebar:has(.sidebar-menu.el-menu--collapse),
.sidebar-collapsed .app-sidebar {
  width: 64px;
}

.app-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(64, 158, 255, 0.05) 100%);
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.app-sidebar.collapsed {
  width: 64px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent !important;
}

.sidebar-menu .el-menu-item {
  position: relative;
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.sidebar-menu .el-menu-item:hover {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(103, 194, 58, 0.1)) !important;
  transform: translateX(4px);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.15), rgba(103, 194, 58, 0.15)) !important;
  border-left: 3px solid var(--el-color-primary);
}

.sidebar-menu .el-sub-menu .el-sub-menu__title {
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.sidebar-menu .el-sub-menu .el-sub-menu__title:hover {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(103, 194, 58, 0.1)) !important;
  transform: translateX(4px);
}

.menu-badge {
  position: absolute;
  top: 8px;
  right: 16px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-4px);
  }
  60% {
    transform: translateY(-2px);
  }
}

.sidebar-footer {
  padding: 16px;
  text-align: center;
  border-top: 1px solid var(--el-border-color-lighter);
  background: rgba(64, 158, 255, 0.05);
}

.collapse-btn {
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #409eff, #67c23a);
  border: none;
  color: white;
}

.collapse-btn:hover {
  transform: scale(1.1) rotate(180deg);
}

.agent-status-panel {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05), rgba(103, 194, 58, 0.05));
  backdrop-filter: blur(5px);
}

.status-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.status-item:hover {
  background: rgba(64, 158, 255, 0.1);
  transform: translateX(2px);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  position: relative;
}

.status-indicator::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  opacity: 0.3;
  background: inherit;
  animation: ripple 2s infinite;
}

@keyframes ripple {
  0% {
    transform: scale(1);
    opacity: 0.3;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.status-indicator.active {
  background-color: #67c23a;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.5);
}

.status-indicator.processing {
  background-color: #e6a23c;
  animation: pulse 2s infinite;
}

.status-indicator.idle {
  background-color: #909399;
}

.status-indicator.error {
  background-color: #f56c6c;
  box-shadow: 0 0 8px rgba(245, 108, 108, 0.5);
}

.agent-name {
  color: var(--el-text-color-regular);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;
}

.status-item:hover .agent-name {
  color: var(--el-text-color-primary);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

/* 摺疊狀態 */
.app-sidebar:not(.collapsed) .sidebar-menu {
  width: 260px;
}

.app-sidebar.collapsed .sidebar-menu {
  width: 64px;
}

.app-sidebar.collapsed .agent-status-panel {
  display: none;
}

/* 深色主題增強 */
.dark .app-sidebar {
  background: linear-gradient(180deg, rgba(31, 41, 55, 0.95), rgba(55, 65, 81, 0.95));
  border-right: 1px solid rgba(75, 85, 99, 0.5);
  backdrop-filter: blur(10px);
}

.dark .app-sidebar::before {
  background: linear-gradient(180deg, transparent 0%, rgba(96, 165, 250, 0.1) 100%);
}

.dark .sidebar-menu .el-menu-item:hover {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.15), rgba(52, 211, 153, 0.15)) !important;
}

.dark .sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(52, 211, 153, 0.2)) !important;
  border-left-color: #60a5fa;
}

.dark .sidebar-footer {
  border-top-color: rgba(75, 85, 99, 0.5);
  background: rgba(96, 165, 250, 0.1);
}

.dark .collapse-btn {
  background: linear-gradient(135deg, #60a5fa, #34d399);
}

.dark .agent-status-panel {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(52, 211, 153, 0.1));
  border-top-color: rgba(75, 85, 99, 0.5);
}

.dark .status-title {
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dark .status-item:hover {
  background: rgba(96, 165, 250, 0.15);
}

.dark .status-indicator.active {
  background-color: #34d399;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    top: 64px;
    left: 0;
    height: calc(100vh - 64px);
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .app-sidebar.mobile-open {
    transform: translateX(0);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
  }
}
</style>