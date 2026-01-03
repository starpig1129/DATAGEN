<template>
  <div class="agent-monitor">
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">代理監控</h1>
          <p class="page-description">實時監控代理狀態和性能</p>
        </div>
        <div class="header-actions">
          <el-button
            type="primary"
            :icon="Refresh"
            :loading="isRefreshing"
            @click="refreshAgentStatus"
          >
            刷新狀態
          </el-button>
        </div>
      </div>
    </div>

    <!-- Status Summary -->
    <div class="status-summary">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" v-for="stat in statusSummary" :key="stat.label">
          <el-card class="summary-card" shadow="hover">
            <div class="summary-content">
              <div class="summary-icon" :style="{ backgroundColor: stat.color }">
                <el-icon :size="20" color="white">
                  <component :is="stat.icon" />
                </el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-value">{{ stat.value }}</span>
                <span class="summary-label">{{ stat.label }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Agent Grid -->
    <div class="agents-grid">
      <AgentCard
        v-for="agent in agents"
        :key="agent.id"
        :agent-id="agent.id"
        :name="agent.name"
        :status="agent.status"
        :progress="agent.progress"
        :current-task="agent.currentTask"
        :last-activity="agent.lastActivity"
      />
    </div>

    <!-- Connection Status -->
    <div class="connection-status" :class="{ connected: isConnected }">
      <el-icon><Connection /></el-icon>
      <span>{{ isConnected ? 'WebSocket \u5df2\u9023\u63a5' : 'WebSocket \u672a\u9023\u63a5' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Refresh, Connection, Check, Loading, Warning, CircleCheck } from '@element-plus/icons-vue'
import AgentCard from '@/components/agents/AgentCard.vue'
import { useRealTimeStore } from '@/stores/realtime'

// Realtime store for WebSocket connection
const realtimeStore = useRealTimeStore()


// State
const isRefreshing = ref(false)

// Computed
const isConnected = computed(() => realtimeStore.isConnected)

// Agent data
interface AgentStatus {
  id: string
  name: string
  status: 'idle' | 'processing' | 'completed' | 'error'
  progress: number
  currentTask: string
  lastActivity: string
}

const agents = ref<AgentStatus[]>([
  { id: 'hypothesis', name: '假設代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'process', name: '流程代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'searcher', name: '搜尋代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'code', name: '程式碼代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'visualization', name: '視覺化代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'report', name: '報告代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'quality_review', name: '品質審查代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'note', name: '筆記代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' },
  { id: 'refiner', name: '優化代理', status: 'idle', progress: 0, currentTask: '', lastActivity: '' }
])

// Status summary
const statusSummary = computed(() => {
  const counts = {
    idle: agents.value.filter(a => a.status === 'idle').length,
    processing: agents.value.filter(a => a.status === 'processing').length,
    completed: agents.value.filter(a => a.status === 'completed').length,
    error: agents.value.filter(a => a.status === 'error').length
  }

  return [
    { label: '總代理數', value: agents.value.length, color: '#409eff', icon: CircleCheck },
    { label: '處理中', value: counts.processing, color: '#e6a23c', icon: Loading },
    { label: '待機中', value: counts.idle, color: '#909399', icon: Check },
    { label: '錯誤', value: counts.error, color: '#f56c6c', icon: Warning }
  ]
})

// Methods
const refreshAgentStatus = async () => {
  isRefreshing.value = true
  try {
    // Request fresh status from WebSocket
    if (realtimeStore.isConnected) {
      realtimeStore.requestAgentStatus()
    }
    await new Promise(resolve => setTimeout(resolve, 500))
  } finally {
    isRefreshing.value = false
  }
}

// Handle WebSocket agent status updates
const handleAgentStatusUpdate = (data: any) => {
  // Normalize agent ID: handle formats like "hypothesis_agent", "Hypothesis Agent", etc.
  const normalizeId = (id: string): string => {
    if (!id) return ''
    return id
      .toLowerCase()
      .replace(/_agent$/, '')
      .replace(/ agent$/, '')
      .replace(/ /g, '_')
  }

  const incomingId = normalizeId(data.agentId)

  // Find matching agent
  const agent = agents.value.find(a => {
    const agentNormalizedId = normalizeId(a.id)
    return agentNormalizedId === incomingId || a.id === data.agentId
  })

  if (agent) {
    // Map backend status to our status types
    let status: 'idle' | 'processing' | 'completed' | 'error' = 'idle'
    if (data.status === 'processing' || data.status === 'running') {
      status = 'processing'
    } else if (data.status === 'completed' || data.status === 'done') {
      status = 'completed'
    } else if (data.status === 'error' || data.status === 'failed') {
      status = 'error'
    } else if (data.status === 'revision_required') {
      status = 'processing'
    }

    agent.status = status
    agent.progress = data.progress || 0
    agent.currentTask = data.currentTask || ''
    agent.lastActivity = data.lastActivity || new Date().toISOString()
  }
}


// Lifecycle
onMounted(() => {
  // Note: WebSocket connection is managed by the integration store
  // We only need to subscribe to agent status updates here

  // Subscribe to agent status updates
  realtimeStore.onAgentStatus(handleAgentStatusUpdate)
})


onUnmounted(() => {
  // Unsubscribe from agent status updates
  realtimeStore.offAgentStatus(handleAgentStatusUpdate)
})
</script>

<style scoped>
.agent-monitor {
  padding: 0;
  position: relative;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 8px 0;
}

.page-description {
  color: var(--el-text-color-regular);
  margin: 0;
}

.status-summary {
  margin-bottom: 24px;
}

.summary-card {
  border-radius: 12px;
}

.summary-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-info {
  display: flex;
  flex-direction: column;
}

.summary-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.summary-label {
  font-size: 12px;
  color: var(--el-text-color-regular);
  margin-top: 4px;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.connection-status {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 20px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.connection-status.connected {
  border-color: #67c23a;
  color: #67c23a;
}

.connection-status .el-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .agents-grid {
    grid-template-columns: 1fr;
  }
}

/* Dark mode */
.dark .connection-status {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}
</style>