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
        <span>儀表板</span>
      </el-menu-item>

      <!-- 聊天界面 -->
      <el-menu-item index="/chat" route="/chat">
        <el-icon><ChatDotRound /></el-icon>
        <span>聊天界面</span>
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
          <span>代理管理</span>
        </template>
        
        <el-menu-item index="/agents" route="/agents">
          <el-icon><View /></el-icon>
          <span>代理監控</span>
        </el-menu-item>
        
        <el-menu-item index="/agents/workflow">
          <el-icon><Connection /></el-icon>
          <span>工作流</span>
        </el-menu-item>
        
        <el-menu-item index="/agents/performance">
          <el-icon><TrendCharts /></el-icon>
          <span>性能分析</span>
        </el-menu-item>
      </el-sub-menu>

      <!-- 數據視覺化 -->
      <el-sub-menu index="visualization">
        <template #title>
          <el-icon><PieChart /></el-icon>
          <span>數據視覺化</span>
        </template>
        
        <el-menu-item index="/visualization" route="/visualization">
          <el-icon><DataAnalysis /></el-icon>
          <span>圖表分析</span>
        </el-menu-item>
        
        <el-menu-item index="/visualization/dashboard">
          <el-icon><Grid /></el-icon>
          <span>儀表板</span>
        </el-menu-item>
        
        <el-menu-item index="/visualization/reports">
          <el-icon><Document /></el-icon>
          <span>報告生成</span>
        </el-menu-item>
      </el-sub-menu>

      <!-- 文件管理 -->
      <el-menu-item index="/files" route="/files">
        <el-icon><Folder /></el-icon>
        <span>文件管理</span>
      </el-menu-item>

      <!-- 系統設置 -->
      <el-menu-item index="/settings" route="/settings">
        <el-icon><Setting /></el-icon>
        <span>系統設置</span>
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
      <div class="status-title">代理狀態</div>
      <div class="status-list">
        <div
          v-for="agent in agentStatus"
          :key="agent.id"
          class="status-item"
        >
          <div class="status-indicator" :class="agent.status"></div>
          <span class="agent-name">{{ agent.name }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
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

// 響應式數據
const isCollapsed = ref(false)
const unreadCount = ref(2)

// 當前路由
const route = useRoute()

// 計算屬性
const activeMenuKey = computed(() => route.path)

// 模擬代理狀態數據
const agentStatus = ref([
  { id: '1', name: '處理代理', status: 'active' },
  { id: '2', name: '假設代理', status: 'idle' },
  { id: '3', name: '搜索代理', status: 'processing' },
  { id: '4', name: '代碼代理', status: 'idle' },
  { id: '5', name: '視覺化代理', status: 'active' },
  { id: '6', name: '報告代理', status: 'idle' },
  { id: '7', name: '品質審查代理', status: 'idle' },
  { id: '8', name: '優化代理', status: 'idle' }
])

// 方法
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.app-sidebar {
  width: 260px;
  height: 100%;
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.app-sidebar.collapsed {
  width: 64px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-menu .el-menu-item {
  position: relative;
}

.menu-badge {
  position: absolute;
  top: 8px;
  right: 16px;
}

.sidebar-footer {
  padding: 16px;
  text-align: center;
  border-top: 1px solid var(--el-border-color-lighter);
}

.collapse-btn {
  transition: transform 0.3s ease;
}

.agent-status-panel {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color-page);
}

.status-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
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
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.active {
  background-color: var(--el-color-success);
  box-shadow: 0 0 4px var(--el-color-success);
}

.status-indicator.processing {
  background-color: var(--el-color-warning);
  animation: pulse 2s infinite;
}

.status-indicator.idle {
  background-color: var(--el-color-info);
}

.status-indicator.error {
  background-color: var(--el-color-danger);
}

.agent-name {
  color: var(--el-text-color-regular);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
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

/* 深色主題 */
.dark .app-sidebar {
  background-color: var(--el-bg-color);
  border-right-color: var(--el-border-color-dark);
}

.dark .agent-status-panel {
  background-color: var(--el-bg-color-page);
  border-top-color: var(--el-border-color-dark);
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
  }
}
</style>