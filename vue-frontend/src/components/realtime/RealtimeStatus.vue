<template>
  <div class="realtime-status">
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span class="title">實時系統狀態</span>
          <div class="status-indicators">
            <el-badge 
              :value="isHealthy ? '正常' : '異常'" 
              :type="isHealthy ? 'success' : 'danger'"
              class="status-badge"
            />
            <el-button 
              :icon="RefreshRight" 
              size="small" 
              @click="handleRefresh"
              :loading="isRefreshing"
            />
          </div>
        </div>
      </template>

      <!-- 連接狀態 -->
      <div class="connection-status">
        <el-row :gutter="16">
          <el-col :span="8">
            <div class="connection-item">
              <el-icon class="connection-icon" :class="{ 'connected': realtimeStore.state.isConnected }">
                <Link />
              </el-icon>
              <div class="connection-info">
                <div class="connection-label">WebSocket</div>
                <div class="connection-value">
                  {{ realtimeStore.state.isConnected ? '已連接' : '未連接' }}
                </div>
              </div>
            </div>
          </el-col>
          
          <el-col :span="8">
            <div class="connection-item">
              <el-icon class="connection-icon" :class="{ 'connected': chatStore.isConnected }">
                <ChatDotRound />
              </el-icon>
              <div class="connection-info">
                <div class="connection-label">聊天服務</div>
                <div class="connection-value">
                  {{ chatStore.isConnected ? '已連接' : '未連接' }}
                </div>
              </div>
            </div>
          </el-col>
          
          <el-col :span="8">
            <div class="connection-item">
              <el-icon class="connection-icon" :class="{ 'connected': appStore.isOnline }">
                <Connection />
              </el-icon>
              <div class="connection-info">
                <div class="connection-label">網路狀態</div>
                <div class="connection-value">
                  {{ appStore.isOnline ? '在線' : '離線' }}
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 系統指標 -->
      <div class="system-metrics" v-if="systemMetrics">
        <el-divider content-position="left">系統指標</el-divider>
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">CPU 使用率</div>
              <el-progress 
                :percentage="systemMetrics.cpu" 
                :color="getProgressColor(systemMetrics.cpu)"
                :stroke-width="8"
              />
            </div>
          </el-col>
          
          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">記憶體使用率</div>
              <el-progress 
                :percentage="systemMetrics.memory" 
                :color="getProgressColor(systemMetrics.memory)"
                :stroke-width="8"
              />
            </div>
          </el-col>
          
          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">活躍連接</div>
              <div class="metric-value">{{ systemMetrics.activeConnections }}</div>
            </div>
          </el-col>
          
          <el-col :span="6">
            <div class="metric-item">
              <div class="metric-label">最後更新</div>
              <div class="metric-time">{{ formatTime(systemMetrics.lastUpdate) }}</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 代理狀態 -->
      <div class="agent-status" v-if="activeAgents.length > 0">
        <el-divider content-position="left">代理狀態</el-divider>
        <div class="agent-list">
          <div 
            v-for="agent in activeAgents" 
            :key="agent.agentId"
            class="agent-item"
          >
            <div class="agent-header">
              <span class="agent-name">{{ agent.name }}</span>
              <el-tag 
                :type="getAgentStatusType(agent.status)" 
                size="small"
              >
                {{ getAgentStatusText(agent.status) }}
              </el-tag>
            </div>
            
            <div class="agent-progress" v-if="agent.status === 'processing'">
              <el-progress
                :percentage="agent.progress"
                :status="agent.progress === 100 ? 'success' : undefined"
              />
              <div class="agent-task" v-if="agent.currentTask">
                {{ agent.currentTask }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近事件 -->
      <div class="recent-events">
        <el-divider content-position="left">最近事件</el-divider>
        <div class="event-list" v-if="latestData.length > 0">
          <div 
            v-for="event in latestData.slice(0, 5)" 
            :key="event.id"
            class="event-item"
          >
            <div class="event-icon">
              <el-icon :class="getEventIconClass(event.type)">
                <component :is="getEventIcon(event.type)" />
              </el-icon>
            </div>
            <div class="event-content">
              <div class="event-type">{{ getEventTypeText(event.type) }}</div>
              <div class="event-time">{{ formatTime(event.timestamp) }}</div>
            </div>
          </div>
        </div>
        <el-empty 
          v-else 
          description="暫無事件" 
          :image-size="60"
        />
      </div>
    </el-card>

    <!-- 詳細事件對話框 -->
    <el-dialog
      v-model="showEventDetails"
      title="事件詳情"
      width="600px"
    >
      <div v-if="selectedEvent" class="event-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="事件ID">
            {{ selectedEvent.id }}
          </el-descriptions-item>
          <el-descriptions-item label="事件類型">
            {{ getEventTypeText(selectedEvent.type) }}
          </el-descriptions-item>
          <el-descriptions-item label="來源">
            {{ selectedEvent.source }}
          </el-descriptions-item>
          <el-descriptions-item label="時間">
            {{ formatTime(selectedEvent.timestamp) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="event-data" v-if="selectedEvent.data">
          <h4>事件數據</h4>
          <el-scrollbar height="300px">
            <pre>{{ JSON.stringify(selectedEvent.data, null, 2) }}</pre>
          </el-scrollbar>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  RefreshRight, 
  Link, 
  ChatDotRound, 
  Connection,
  InfoFilled,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'
import { useRealTimeStore } from '@/stores/realtime'
import { useIntegrationStore } from '@/stores/integration'
import type { RealTimeData, SystemMetrics, AgentStatus } from '@/stores/realtime'

// Stores
const appStore = useAppStore()
const chatStore = useChatStore()
const realtimeStore = useRealTimeStore()
const integrationStore = useIntegrationStore()

// 響應式數據
const isRefreshing = ref(false)
const showEventDetails = ref(false)
const selectedEvent = ref<RealTimeData | null>(null)
const refreshTimer = ref<number | null>(null)

// 計算屬性
const isHealthy = computed(() => 
  realtimeStore.isHealthy && 
  chatStore.isConnected && 
  appStore.isOnline
)

const systemMetrics = computed(() => 
  realtimeStore.getSystemMetrics()
)

const activeAgents = computed(() => 
  realtimeStore.activeAgents
)

const latestData = computed(() => 
  realtimeStore.latestData
)

// 方法
const handleRefresh = async () => {
  isRefreshing.value = true
  try {
    await realtimeStore.refreshData()
    appStore.addNotification({
      type: 'success',
      title: '刷新完成',
      message: '實時數據已更新'
    })
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '刷新失敗',
      message: error instanceof Error ? error.message : '未知錯誤'
    })
  } finally {
    isRefreshing.value = false
  }
}

const getProgressColor = (percentage: number): string => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getAgentStatusType = (status: string): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  switch (status) {
    case 'processing': return 'warning'
    case 'completed': return 'success'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const getAgentStatusText = (status: string): string => {
  switch (status) {
    case 'idle': return '空閒'
    case 'processing': return '處理中'
    case 'completed': return '已完成'
    case 'error': return '錯誤'
    default: return status
  }
}

const getEventTypeText = (type: string): string => {
  switch (type) {
    case 'agent_status': return '代理狀態'
    case 'system_metrics': return '系統指標'
    case 'data_update': return '數據更新'
    case 'chart_data': return '圖表數據'
    case 'file_status': return '文件狀態'
    default: return type
  }
}

const getEventIcon = (type: string) => {
  switch (type) {
    case 'agent_status': return InfoFilled
    case 'system_metrics': return SuccessFilled
    case 'data_update': return WarningFilled
    case 'file_status': return CircleCloseFilled
    default: return InfoFilled
  }
}

const getEventIconClass = (type: string): string => {
  switch (type) {
    case 'agent_status': return 'event-icon-info'
    case 'system_metrics': return 'event-icon-success'
    case 'data_update': return 'event-icon-warning'
    case 'file_status': return 'event-icon-danger'
    default: return 'event-icon-info'
  }
}

const formatTime = (timestamp: number | string): string => {
  const date = new Date(typeof timestamp === 'number' ? timestamp : timestamp)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const showEventDetail = (event: RealTimeData) => {
  selectedEvent.value = event
  showEventDetails.value = true
}

const startAutoRefresh = () => {
  refreshTimer.value = setInterval(async () => {
    if (!isRefreshing.value) {
      await handleRefresh()
    }
  }, 30000) // 每30秒自動刷新
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

// 生命週期
onMounted(() => {
  // 初始化實時連接
  realtimeStore.initialize()
  
  // 開始自動刷新
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">
.realtime-status {
  .status-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
        font-size: 16px;
        font-weight: 600;
      }
      
      .status-indicators {
        display: flex;
        align-items: center;
        gap: 12px;
      }
    }
  }
  
  .connection-status {
    margin-bottom: 24px;
    
    .connection-item {
      display: flex;
      align-items: center;
      padding: 12px;
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 8px;
      
      .connection-icon {
        font-size: 24px;
        margin-right: 12px;
        color: var(--el-color-info);
        
        &.connected {
          color: var(--el-color-success);
        }
      }
      
      .connection-info {
        .connection-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-bottom: 2px;
        }
        
        .connection-value {
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
  }
  
  .system-metrics {
    margin-bottom: 24px;
    
    .metric-item {
      text-align: center;
      
      .metric-label {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-bottom: 8px;
      }
      
      .metric-value {
        font-size: 24px;
        font-weight: 600;
        color: var(--el-color-primary);
      }
      
      .metric-time {
        font-size: 12px;
        color: var(--el-text-color-regular);
      }
    }
  }
  
  .agent-status {
    margin-bottom: 24px;
    
    .agent-list {
      .agent-item {
        padding: 12px;
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 8px;
        margin-bottom: 8px;
        
        .agent-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          
          .agent-name {
            font-weight: 500;
          }
        }
        
        .agent-progress {
          .agent-task {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            margin-top: 4px;
          }
        }
      }
    }
  }
  
  .recent-events {
    .event-list {
      .event-item {
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid var(--el-border-color-lighter);
        cursor: pointer;
        transition: background-color 0.2s;
        
        &:hover {
          background-color: var(--el-fill-color-lighter);
        }
        
        &:last-child {
          border-bottom: none;
        }
        
        .event-icon {
          margin-right: 12px;
          
          .event-icon-info { color: var(--el-color-info); }
          .event-icon-success { color: var(--el-color-success); }
          .event-icon-warning { color: var(--el-color-warning); }
          .event-icon-danger { color: var(--el-color-danger); }
        }
        
        .event-content {
          flex: 1;
          
          .event-type {
            font-size: 14px;
            margin-bottom: 2px;
          }
          
          .event-time {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
      }
    }
  }
  
  .event-details {
    .event-data {
      margin-top: 16px;
      
      h4 {
        margin-bottom: 8px;
        color: var(--el-text-color-primary);
      }
      
      pre {
        background-color: var(--el-fill-color-lighter);
        padding: 12px;
        border-radius: 4px;
        font-size: 12px;
        line-height: 1.5;
      }
    }
  }
}
</style>