<template>
  <footer class="app-footer">
    <div class="footer-left">
      <!-- 系統狀態 -->
      <div class="status-section">
        <el-tag
          :type="systemStatus.type"
          size="small"
          :icon="systemStatus.icon"
          class="status-tag"
        >
          {{ systemStatus.text }}
        </el-tag>
        
        <!-- 網路狀態 -->
        <el-tag
          :type="isOnline ? 'success' : 'danger'"
          size="small"
          :icon="isOnline ? 'Connection' : 'Failed'"
          class="network-tag"
        >
          {{ isOnline ? '已連線' : '離線' }}
        </el-tag>
      </div>
    </div>

    <div class="footer-center">
      <!-- 活躍代理計數 -->
      <div class="active-agents">
        <el-icon class="agent-icon"><Monitor /></el-icon>
        <span>活躍代理: {{ activeAgentCount }}/{{ totalAgentCount }}</span>
      </div>
      
      <!-- 處理中任務 -->
      <div class="processing-tasks">
        <el-icon class="task-icon"><Loading /></el-icon>
        <span>處理中: {{ processingTaskCount }}</span>
      </div>
    </div>

    <div class="footer-right">
      <!-- 版本信息 -->
      <div class="version-info">
        <span class="version-text">v{{ appVersion }}</span>
      </div>
      
      <!-- 最後更新時間 -->
      <div class="last-update">
        <el-icon><Clock /></el-icon>
        <span>{{ lastUpdateTime }}</span>
      </div>
      
      <!-- 性能指標 -->
      <el-popover
        placement="top"
        title="性能指標"
        :width="280"
        trigger="hover"
      >
        <template #reference>
          <div class="performance-indicator">
            <el-icon><TrendCharts /></el-icon>
            <span>{{ cpuUsage }}%</span>
          </div>
        </template>
        
        <div class="performance-details">
          <div class="metric-item">
            <span class="metric-label">CPU 使用率:</span>
            <el-progress
              :percentage="cpuUsage"
              :color="getPerformanceColor(cpuUsage)"
              :show-text="false"
              :stroke-width="6"
            />
            <span class="metric-value">{{ cpuUsage }}%</span>
          </div>
          
          <div class="metric-item">
            <span class="metric-label">內存使用:</span>
            <el-progress
              :percentage="memoryUsage"
              :color="getPerformanceColor(memoryUsage)"
              :show-text="false"
              :stroke-width="6"
            />
            <span class="metric-value">{{ memoryUsage }}%</span>
          </div>
          
          <div class="metric-item">
            <span class="metric-label">網路延遲:</span>
            <span class="metric-value">{{ networkLatency }}ms</span>
          </div>
        </div>
      </el-popover>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Monitor,
  Loading,
  Clock,
  TrendCharts,
  // Connection,  // Reserved - icons used as strings in template
  // Failed       // Reserved - icons used as strings in template
} from '@element-plus/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

// Reactive data
const isOnline = ref(navigator.onLine)
const activeAgentCount = ref(3)
const totalAgentCount = ref(8)
const processingTaskCount = ref(2)
const appVersion = ref('1.0.0')
const lastUpdate = ref(new Date())
const cpuUsage = ref(45)
const memoryUsage = ref(68)
const networkLatency = ref(12)

// Computed properties
const systemStatus = computed(() => {
  if (processingTaskCount.value > 0) {
    return {
      type: 'warning' as const,
      icon: 'Loading',
      text: '處理中'
    }
  } else if (activeAgentCount.value > 0) {
    return {
      type: 'success' as const,
      icon: 'CircleCheck',
      text: '運行中'
    }
  } else {
    return {
      type: 'info' as const,
      icon: 'Clock',
      text: '待機中'
    }
  }
})

const lastUpdateTime = computed(() => {
  return formatDistanceToNow(lastUpdate.value, {
    addSuffix: true,
    locale: zhTW
  })
})

// Methods
const getPerformanceColor = (percentage: number) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const updatePerformanceMetrics = () => {
  // Simulate performance data updates
  cpuUsage.value = Math.floor(Math.random() * 30) + 30
  memoryUsage.value = Math.floor(Math.random() * 40) + 40
  networkLatency.value = Math.floor(Math.random() * 20) + 5
  lastUpdate.value = new Date()
}

const handleOnlineStatusChange = () => {
  isOnline.value = navigator.onLine
}

// Lifecycle
let performanceTimer: ReturnType<typeof setInterval>

onMounted(() => {
  // 監聽網路狀態變化
  window.addEventListener('online', handleOnlineStatusChange)
  window.addEventListener('offline', handleOnlineStatusChange)
  
  // 定期更新性能指標
  performanceTimer = setInterval(updatePerformanceMetrics, 5000)
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnlineStatusChange)
  window.removeEventListener('offline', handleOnlineStatusChange)
  
  if (performanceTimer) {
    clearInterval(performanceTimer)
  }
})
</script>

<style scoped>
.app-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 32px;
  padding: 0 16px;
  background-color: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-light);
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.footer-left,
.footer-center,
.footer-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer-center {
  flex: 1;
  justify-content: center;
}

.status-section {
  display: flex;
  gap: 8px;
}

.status-tag,
.network-tag {
  font-size: 11px;
}

.active-agents,
.processing-tasks {
  display: flex;
  align-items: center;
  gap: 4px;
}

.agent-icon,
.task-icon {
  font-size: 14px;
}

.version-info {
  font-weight: 500;
}

.last-update {
  display: flex;
  align-items: center;
  gap: 4px;
}

.performance-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 4px;
  background-color: var(--el-bg-color-page);
  cursor: pointer;
  transition: background-color 0.2s;
}

.performance-indicator:hover {
  background-color: var(--el-color-primary-light-9);
}

.performance-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-label {
  width: 70px;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.metric-value {
  width: 40px;
  text-align: right;
  font-size: 12px;
  font-weight: 500;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .app-footer {
    padding: 0 12px;
    font-size: 11px;
  }
  
  .footer-left,
  .footer-center,
  .footer-right {
    gap: 8px;
  }
  
  .version-info,
  .last-update {
    display: none;
  }
}

@media (max-width: 480px) {
  .status-section {
    gap: 4px;
  }
  
  .footer-center {
    gap: 8px;
  }
  
  .processing-tasks {
    display: none;
  }
}

/* 深色主題 */
.dark .app-footer {
  background-color: var(--el-bg-color);
  border-top-color: var(--el-border-color-dark);
}

.dark .performance-indicator {
  background-color: var(--el-bg-color-page);
}

.dark .performance-indicator:hover {
  background-color: var(--el-color-primary-dark-2);
}
</style>