<template>
  <div class="dashboard">
    <!-- 頁面標題 -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">系統儀表板</h1>
          <p class="page-description">多代理數據分析系統總覽</p>
        </div>
        <el-button
          type="primary"
          :icon="Refresh"
          :loading="isRefreshing"
          @click="refreshDashboardData"
          circle
          title="刷新數據"
        />
      </div>
    </div>

    <!-- 統計卡片 -->
    <div class="stats-grid">
      <el-card
        v-for="stat in systemStats"
        :key="stat.key"
        class="stat-card"
        shadow="hover"
      >
        <div class="stat-content">
          <div class="stat-icon" :style="{ backgroundColor: stat.color }">
            <el-icon :size="24" :color="'white'">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-change" :class="stat.trend">
              <el-icon><component :is="stat.trendIcon" /></el-icon>
              <span>{{ stat.change }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主要內容區域 -->
    <div class="dashboard-content">
      <!-- 左側：代理狀態和活動 -->
      <div class="left-panel">
        <!-- 代理狀態總覽 -->
        <el-card class="agent-overview" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>代理狀態總覽</span>
              <el-button type="primary" text @click="navigateToAgents">
                查看詳情
              </el-button>
            </div>
          </template>
          
          <div class="agent-grid">
            <div
              v-for="agent in agentStatus"
              :key="agent.id"
              class="agent-item"
              :class="agent.status"
            >
              <div class="agent-avatar">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="agent-info">
                <div class="agent-name">{{ agent.name }}</div>
                <div class="agent-status">{{ getStatusText(agent.status) }}</div>
              </div>
              <div class="agent-indicator" :class="agent.status"></div>
            </div>
          </div>
        </el-card>

        <!-- 最近活動 -->
        <el-card class="recent-activity" shadow="hover">
          <template #header>
            <span>最近活動</span>
          </template>
          
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="formatTime(activity.timestamp)"
              :type="activity.type"
            >
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-description">{{ activity.description }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>

      <!-- 右側：圖表和快速操作 -->
      <div class="right-panel">
        <!-- 系統性能圖表 -->
        <el-card class="performance-chart" shadow="hover">
          <template #header>
            <span>系統性能監控</span>
          </template>
          
          <div class="chart-container">
            <PerformanceChart
              :height="300"
              :refresh-interval="5000"
              :is-dark="settingsStore.currentTheme === 'dark'"
            />
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card class="quick-actions" shadow="hover">
          <template #header>
            <span>快速操作</span>
          </template>
          
          <div class="action-grid">
            <el-button
              v-for="action in quickActions"
              :key="action.key"
              :type="action.type as 'primary' | 'success' | 'warning' | 'info' | 'danger'"
              :icon="action.icon"
              class="action-button"
              @click="handleQuickAction(action.key)"
            >
              {{ action.label }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Monitor,
  TrendCharts,
  ChatDotRound,
  View,
  DataAnalysis,
  Folder,
  Setting,
  ArrowUp,
  ArrowDown,
  DocumentCopy,
  Connection,
  Refresh
} from '@element-plus/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'
import { ElMessage } from 'element-plus'
import PerformanceChart from '@/components/charts/PerformanceChart.vue'

// Pinia Stores
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'
import { useFileStore } from '@/stores/file'
import { useSettingsStore } from '@/stores/settings'

// Types
import { MessageType } from '@/types/chat'

const router = useRouter()
const appStore = useAppStore()
const chatStore = useChatStore()
const fileStore = useFileStore()
const settingsStore = useSettingsStore()

// 載入狀態
const isRefreshing = ref(false)

// 系統統計數據 - 基於 stores 的動態計算
const systemStats = computed(() => {
  const activeAgents = agentStatus.value.filter(agent => agent.status === 'active').length
  const totalAgents = agentStatus.value.length
  const completedTasks = chatStore.messages.length
  const connectionStatus = chatStore.isConnected
  const systemPerformance = settingsStore.isApiConfigured ? 95 : 50

  return [
    {
      key: 'agents',
      label: '活躍代理',
      value: `${activeAgents}/${totalAgents}`,
      change: activeAgents > totalAgents / 2 ? `+${activeAgents - Math.floor(totalAgents / 2)}` : '0',
      trend: activeAgents > totalAgents / 2 ? 'positive' : 'negative',
      color: '#67c23a',
      icon: Monitor,
      trendIcon: activeAgents > totalAgents / 2 ? ArrowUp : ArrowDown
    },
    {
      key: 'tasks',
      label: '完成任務',
      value: completedTasks.toString(),
      change: `+${Math.max(0, completedTasks - 10)}`,
      trend: 'positive',
      color: '#409eff',
      icon: DocumentCopy,
      trendIcon: ArrowUp
    },
    {
      key: 'performance',
      label: '系統性能',
      value: `${systemPerformance}%`,
      change: systemPerformance >= 90 ? '+5%' : '-10%',
      trend: systemPerformance >= 90 ? 'positive' : 'negative',
      color: systemPerformance >= 90 ? '#67c23a' : '#e6a23c',
      icon: TrendCharts,
      trendIcon: systemPerformance >= 90 ? ArrowUp : ArrowDown
    },
    {
      key: 'connections',
      label: '連接狀態',
      value: connectionStatus ? '已連接' : '未連接',
      change: connectionStatus ? '穩定' : '斷開',
      trend: connectionStatus ? 'positive' : 'negative',
      color: connectionStatus ? '#67c23a' : '#f56c6c',
      icon: Connection,
      trendIcon: connectionStatus ? ArrowUp : ArrowDown
    }
  ]
})

// 代理狀態 - 基於聊天狀態和設定的動態計算
const agentStatus = computed(() => {
  const baseAgents = [
    { id: '1', name: '處理代理', status: 'idle' },
    { id: '2', name: '假設代理', status: 'idle' },
    { id: '3', name: '搜索代理', status: 'idle' },
    { id: '4', name: '代碼代理', status: 'idle' },
    { id: '5', name: '視覺化代理', status: 'idle' },
    { id: '6', name: '報告代理', status: 'idle' },
    { id: '7', name: '品質審查代理', status: 'idle' },
    { id: '8', name: '優化代理', status: 'idle' }
  ]

  // 根據當前代理狀態更新
  if (chatStore.currentTypingAgent) {
    const currentAgent = baseAgents.find(agent =>
      agent.name.includes(chatStore.currentTypingAgent?.split('_')[0] || '')
    )
    if (currentAgent) {
      currentAgent.status = 'processing'
    }
  }

  // 如果正在處理，隨機設置一些代理為活躍狀態
  if (chatStore.isProcessing) {
    baseAgents.forEach((agent, index) => {
      if (index % 3 === 0) agent.status = 'active'
    })
  }

  // 根據設定狀態調整代理狀態
  if (!settingsStore.isApiConfigured) {
    baseAgents[7].status = 'error' // 優化代理顯示錯誤，表示配置問題
  }

  return baseAgents
})

// 最近活動 - 基於聊天消息和應用通知
const recentActivities = computed(() => {
  const activities: Array<{
    id: string
    title: string
    description: string
    timestamp: Date
    type: 'success' | 'primary' | 'warning' | 'info' | 'danger'
  }> = []

  // 從聊天消息中提取活動
  const recentMessages = chatStore.messages.slice(-3).reverse()
  recentMessages.forEach((message, index) => {
    if (message.type === MessageType.AGENT) {
      activities.push({
        id: `msg_${message.id}`,
        title: `${message.sender}回應`,
        description: message.content.length > 50
          ? `${message.content.substring(0, 50)}...`
          : message.content,
        timestamp: new Date(message.timestamp),
        type: 'success'
      })
    }
  })

  // 從應用通知中提取活動
  const recentNotifications = appStore.notifications.slice(-2)
  recentNotifications.forEach(notification => {
    activities.push({
      id: `notif_${notification.id}`,
      title: notification.title,
      description: notification.message,
      timestamp: new Date(notification.timestamp),
      type: notification.type === 'error' ? 'danger' : notification.type
    })
  })

  // 添加文件相關活動
  if (fileStore.files.length > 0) {
    const latestFile = fileStore.files[fileStore.files.length - 1]
    activities.push({
      id: `file_${latestFile.id}`,
      title: '文件更新',
      description: `最新文件: ${latestFile.name}`,
      timestamp: new Date(latestFile.updatedAt),
      type: 'info'
    })
  }

  // 如果沒有活動，添加預設活動
  if (activities.length === 0) {
    activities.push(
      {
        id: 'default_1',
        title: '系統啟動',
        description: '多代理數據分析系統已成功啟動',
        timestamp: new Date(Date.now() - 1000 * 60 * 5),
        type: 'success'
      },
      {
        id: 'default_2',
        title: '等待用戶輸入',
        description: '系統準備就緒，等待用戶開始對話',
        timestamp: new Date(Date.now() - 1000 * 60 * 2),
        type: 'info'
      }
    )
  }

  // 按時間排序並限制數量
  return activities
    .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    .slice(0, 5)
})

// 快速操作
const quickActions = ref([
  { key: 'chat', label: '開始對話', type: 'primary', icon: ChatDotRound },
  { key: 'agents', label: '代理監控', type: 'success', icon: Monitor },
  { key: 'visualization', label: '數據視覺化', type: 'warning', icon: DataAnalysis },
  { key: 'files', label: '文件管理', type: 'info', icon: Folder }
])

// 方法
const getStatusText = (status: string) => {
  const statusMap = {
    active: '活躍',
    idle: '待機',
    processing: '處理中',
    error: '錯誤'
  }
  return statusMap[status as keyof typeof statusMap] || '未知'
}

const formatTime = (date: Date) => {
  return formatDistanceToNow(date, {
    addSuffix: true,
    locale: zhTW
  })
}

const navigateToAgents = () => {
  router.push('/agents')
}

const handleQuickAction = (actionKey: string) => {
  switch (actionKey) {
    case 'chat':
      router.push('/chat')
      break
    case 'agents':
      router.push('/agents')
      break
    case 'visualization':
      router.push('/visualization')
      break
    case 'files':
      router.push('/files')
      break
  }
}

// 數據刷新機制
const refreshDashboardData = async () => {
  if (isRefreshing.value) return
  
  isRefreshing.value = true
  try {
    // 刷新各個 store 的數據
    await Promise.allSettled([
      // 初始化聊天連接（如果尚未連接）
      chatStore.isConnected ? Promise.resolve() : chatStore.initializeChat(),
      // 獲取文件列表
      fileStore.fetchFiles(),
      // 驗證設定
      settingsStore.validateSettings()
    ])
    
    // 顯示成功訊息
    ElMessage.success('儀表板數據已更新')
  } catch (error) {
    console.error('刷新儀表板數據失敗:', error)
    // 使用 app store 的通知系統
    appStore.addNotification({
      type: 'error',
      title: '刷新失敗',
      message: '儀表板數據刷新失敗，請檢查網路連接'
    })
  } finally {
    isRefreshing.value = false
  }
}

// 自動刷新定時器
let autoRefreshTimer: number | null = null

const startAutoRefresh = () => {
  // 每30秒自動刷新一次
  autoRefreshTimer = setInterval(() => {
    if (!document.hidden) { // 只在頁面可見時刷新
      refreshDashboardData()
    }
  }, 30000)
}

const stopAutoRefresh = () => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

// 生命週期
onMounted(async () => {
  console.log('儀表板載入中...')
  
  try {
    // 初始化應用程式（如果尚未初始化）
    if (!appStore.isInitialized) {
      await appStore.initialize()
    }
    
    // 初始化設定（如果尚未初始化）
    if (!settingsStore.isApiConfigured) {
      await settingsStore.initialize()
    }
    
    // 執行初始數據載入
    await refreshDashboardData()
    
    // 啟動自動刷新
    startAutoRefresh()
    
    console.log('儀表板已成功載入')
    
    // 顯示歡迎通知
    appStore.addNotification({
      type: 'success',
      title: '歡迎使用',
      message: '多代理數據分析系統儀表板已載入完成',
      duration: 3000
    })
  } catch (error) {
    console.error('儀表板初始化失敗:', error)
    appStore.addNotification({
      type: 'error',
      title: '初始化失敗',
      message: '儀表板初始化時發生錯誤，部分功能可能無法正常使用'
    })
  }
})

onUnmounted(() => {
  console.log('儀表板正在卸載...')
  
  // 停止自動刷新
  stopAutoRefresh()
  
  // 清理資源（如需要）
  console.log('儀表板已卸載')
})
</script>

<style scoped>
.dashboard {
  padding: 0;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin: 4px 0;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.stat-change.positive {
  color: var(--el-color-success);
}

.stat-change.negative {
  color: var(--el-color-danger);
}

.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: between;
  align-items: center;
}

.agent-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.2s;
}

.agent-item:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.agent-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--el-color-primary-light-8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
}

.agent-info {
  flex: 1;
}

.agent-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.agent-status {
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.agent-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.agent-indicator.active {
  background-color: var(--el-color-success);
}

.agent-indicator.idle {
  background-color: var(--el-color-info);
}

.agent-indicator.processing {
  background-color: var(--el-color-warning);
  animation: pulse 2s infinite;
}

.agent-indicator.error {
  background-color: var(--el-color-danger);
}

.activity-content {
  margin-left: 8px;
}

.activity-title {
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.activity-description {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.chart-container {
  height: 300px;
}

.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-button {
  height: 48px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 響應式設計 */
@media (max-width: 1024px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>