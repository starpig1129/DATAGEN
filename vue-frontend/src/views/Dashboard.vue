<template>
  <ResponsiveContainer
    title="系統儀表板"
    layout="default"
    :loading="isInitialLoading"
    loading-text="正在載入儀表板數據..."
    :error="initError"
    @retry="initializeDashboard"
    show-skip-link
    auto-focus
  >
    <template #header="{ isMobile }">
      <div class="dashboard-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">系統儀表板</h1>
            <p class="page-description">多代理數據分析系統總覽</p>
          </div>
          <div class="header-actions">
            <InteractiveElement
              effect="scale"
              enable-ripple
              :tooltip="isRefreshing ? '正在刷新...' : '刷新數據'"
            >
              <el-button
                type="primary"
                :icon="Refresh"
                :loading="isRefreshing"
                @click="refreshDashboardData"
                circle
                :disabled="isRefreshing"
              />
            </InteractiveElement>
          </div>
        </div>
      </div>
    </template>

    <template #default="{ isMobile }">
      <!-- 載入狀態 - 骨架屏 -->
      <div v-if="isDataLoading" class="dashboard-loading">
        <ProgressiveLoader
          :loading="true"
          :stages="loadingStages"
          :current-stage-index="currentLoadingStage"
          auto-progress
          show-animation
          spinner-type="pulse"
        />
      </div>

      <!-- 主要內容 -->
      <div v-else class="dashboard-content">
        <!-- 統計卡片 -->
        <div class="stats-section">
          <transition-group name="card-fade" tag="div" class="stats-grid">
            <InteractiveElement
              v-for="(stat, index) in systemStats"
              :key="stat.key"
              effect="scale"
              intensity="subtle"
              enable-scale
              enable-glow
              :tooltip="`${stat.label}: ${stat.value}`"
              :animate-on-mount="true"
              :delay="index * 100"
            >
              <el-card
                class="stat-card"
                shadow="hover"
                :class="{ 'stat-error': stat.trend === 'negative' }"
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
            </InteractiveElement>
          </transition-group>
        </div>

        <!-- 主要內容區域 -->
        <div class="dashboard-main" :class="{ 'mobile-stack': isMobile }">
          <!-- 左側：代理狀態和活動 -->
          <div class="left-panel">
            <!-- 代理狀態總覽 -->
            <ErrorBoundary
              :show-details="false"
              :show-go-back="false"
              @retry="loadAgentStatus"
            >
              <el-card class="agent-overview" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>代理狀態總覽</span>
                    <InteractiveElement
                      effect="scale"
                      enable-ripple
                      tooltip="查看詳細代理狀態"
                    >
                      <el-button type="primary" text @click="navigateToAgents">
                        查看詳情
                      </el-button>
                    </InteractiveElement>
                  </div>
                </template>
                
                <div v-if="agentStatusLoading" class="agent-loading">
                  <SkeletonLoader type="list" :items="8" />
                </div>
                
                <div v-else class="agent-grid">
                  <transition-group name="agent-fade" tag="div">
                    <InteractiveElement
                      v-for="(agent, index) in agentStatus"
                      :key="agent.id"
                      effect="slide"
                      enable-scale
                      :tooltip="`${agent.name} - ${getStatusText(agent.status)}`"
                      :animate-on-mount="true"
                      :delay="index * 50"
                    >
                      <div
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
                    </InteractiveElement>
                  </transition-group>
                </div>
              </el-card>
            </ErrorBoundary>

            <!-- 最近活動 -->
            <ErrorBoundary
              :show-details="false"
              :show-go-back="false"
              @retry="loadRecentActivities"
            >
              <el-card class="recent-activity" shadow="hover">
                <template #header>
                  <span>最近活動</span>
                </template>
                
                <div v-if="activitiesLoading" class="activities-loading">
                  <SkeletonLoader type="list" :items="5" />
                </div>
                
                <el-timeline v-else>
                  <transition-group name="timeline-fade">
                    <el-timeline-item
                      v-for="(activity, index) in recentActivities"
                      :key="activity.id"
                      :timestamp="formatTime(activity.timestamp)"
                      :type="activity.type"
                      :style="{ animationDelay: `${index * 100}ms` }"
                      class="timeline-item-animated"
                    >
                      <div class="activity-content">
                        <div class="activity-title">{{ activity.title }}</div>
                        <div class="activity-description">{{ activity.description }}</div>
                      </div>
                    </el-timeline-item>
                  </transition-group>
                </el-timeline>
              </el-card>
            </ErrorBoundary>
          </div>

          <!-- 右側：圖表和快速操作 -->
          <div class="right-panel">
            <!-- 系統性能圖表 -->
            <ErrorBoundary
              :show-details="false"
              error-type="chart"
              @retry="loadPerformanceData"
            >
              <el-card class="performance-chart" shadow="hover">
                <template #header>
                  <span>系統性能監控</span>
                </template>
                
                <div class="chart-container">
                  <div v-if="chartLoading" class="chart-loading">
                    <SkeletonLoader type="chart" />
                  </div>
                  
                  <PerformanceChart
                    v-else
                    :height="300"
                    :refresh-interval="5000"
                    :is-dark="isDarkMode"
                  />
                </div>
              </el-card>
            </ErrorBoundary>

            <!-- 快速操作 -->
            <el-card class="quick-actions" shadow="hover">
              <template #header>
                <span>快速操作</span>
              </template>
              
              <div class="action-grid">
                <InteractiveElement
                  v-for="(action, index) in quickActions"
                  :key="action.key"
                  effect="bounce"
                  enable-ripple
                  enable-scale
                  :tooltip="action.description || action.label"
                  :animate-on-mount="true"
                  :delay="index * 100"
                >
                  <el-button
                    :type="action.type as 'primary' | 'success' | 'warning' | 'info' | 'danger'"
                    :icon="action.icon"
                    class="action-button"
                    @click="handleQuickAction(action.key)"
                  >
                    {{ action.label }}
                  </el-button>
                </InteractiveElement>
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </template>
  </ResponsiveContainer>

  <!-- 鍵盤快捷鍵支援 - 移到容器外 -->
  <KeyboardShortcuts
    :shortcuts="dashboardShortcuts"
    :commands="dashboardCommands"
    @shortcut="handleShortcut"
    @command="handleCommand"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Monitor,
  TrendCharts,
  ChatDotRound,
  DataAnalysis,
  Folder,
  ArrowUp,
  ArrowDown,
  DocumentCopy,
  Connection,
  Refresh
} from '@element-plus/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'
import { ElMessage } from 'element-plus'

// 新的 UX 組件
import ResponsiveContainer from '@/components/common/ResponsiveContainer.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import ProgressiveLoader from '@/components/common/ProgressiveLoader.vue'
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
import InteractiveElement from '@/components/common/InteractiveElement.vue'
import KeyboardShortcuts from '@/components/common/KeyboardShortcuts.vue'

// 現有組件
import PerformanceChart from '@/components/charts/PerformanceChart.vue'

// Pinia Stores
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'
import { useFileStore } from '@/stores/file'

// Types
import { MessageType } from '@/types/chat'

const router = useRouter()
const appStore = useAppStore()
const chatStore = useChatStore()
const fileStore = useFileStore()

// 響應式數據
const isDarkMode = computed(() => {
  // 從 localStorage 或系統偏好檢測深色模式
  return document.documentElement.classList.contains('dark') || 
         (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
})

// 載入狀態
const isInitialLoading = ref(true)
const isDataLoading = ref(false)
const isRefreshing = ref(false)
const agentStatusLoading = ref(false)
const activitiesLoading = ref(false)
const chartLoading = ref(false)
const initError = ref<string | null>(null)

// 載入階段
const loadingStages = ref([
  { title: '初始化應用', description: '準備系統組件', duration: 800 },
  { title: '載入設定', description: '驗證配置信息', duration: 600 },
  { title: '連接服務', description: '建立後端連接', duration: 1000 },
  { title: '獲取數據', description: '載入儀表板數據', duration: 1200 },
  { title: '完成', description: '準備就緒', duration: 400 }
])

const currentLoadingStage = ref(0)

// 計算屬性保持原有邏輯
const systemStats = computed(() => {
  const activeAgents = agentStatus.value.filter(agent => agent.status === 'active').length
  const totalAgents = agentStatus.value.length
  const completedTasks = chatStore.messages.length
  const connectionStatus = chatStore.isConnected
  const systemPerformance = connectionStatus ? 95 : 50

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

// 代理狀態 - 保持原有邏輯
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

  return baseAgents
})

// 最近活動 - 保持原有邏輯
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

// 快速操作 - 增強版
const quickActions = ref([
  { 
    key: 'chat', 
    label: '開始對話', 
    description: '與 AI 代理開始新的對話',
    type: 'primary', 
    icon: ChatDotRound 
  },
  { 
    key: 'agents', 
    label: '代理監控', 
    description: '查看代理狀態和性能',
    type: 'success', 
    icon: Monitor 
  },
  { 
    key: 'visualization', 
    label: '數據視覺化', 
    description: '創建和管理數據圖表',
    type: 'warning', 
    icon: DataAnalysis 
  },
  { 
    key: 'files', 
    label: '文件管理', 
    description: '上傳和管理文件',
    type: 'info', 
    icon: Folder 
  }
])

// 快捷鍵配置
const dashboardShortcuts = ref({
  'ctrl+shift+r': {
    keys: 'ctrl+shift+r',
    description: '刷新儀表板數據',
    action: () => refreshDashboardData()
  },
  'ctrl+1': {
    keys: 'ctrl+1',
    description: '跳轉到聊天界面',
    action: () => handleQuickAction('chat')
  },
  'ctrl+2': {
    keys: 'ctrl+2',
    description: '跳轉到代理監控',
    action: () => handleQuickAction('agents')
  }
})

// 命令配置
const dashboardCommands = ref([
  {
    id: 'refresh-dashboard',
    title: '刷新儀表板',
    subtitle: '重新載入所有數據',
    icon: '🔄',
    action: () => refreshDashboardData(),
    keywords: ['refresh', 'reload', '刷新', '重新載入']
  },
  {
    id: 'view-agents',
    title: '查看代理狀態',
    subtitle: '打開代理監控頁面',
    icon: '🤖',
    action: () => navigateToAgents(),
    keywords: ['agents', 'monitor', '代理', '監控']
  }
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

// 增強的數據刷新機制
const refreshDashboardData = async () => {
  if (isRefreshing.value) return
  
  isRefreshing.value = true
  try {
    // 並行載入不同數據源
    await Promise.allSettled([
      loadAgentStatus(),
      loadRecentActivities(),
      loadPerformanceData(),
      // 刷新各個 store 的數據
      chatStore.isConnected ? Promise.resolve() : chatStore.initializeChat(),
      fileStore.fetchFiles()
    ])
    
    ElMessage.success('儀表板數據已更新')
  } catch (error) {
    console.error('刷新儀表板數據失敗:', error)
    appStore.addNotification({
      type: 'error',
      title: '刷新失敗',
      message: '儀表板數據刷新失敗，請檢查網路連接'
    })
  } finally {
    isRefreshing.value = false
  }
}

// 分段載入方法
const loadAgentStatus = async () => {
  agentStatusLoading.value = true
  try {
    // 模擬 API 請求
    await new Promise(resolve => setTimeout(resolve, 500))
    // 實際的代理狀態載入邏輯會在這裡
  } finally {
    agentStatusLoading.value = false
  }
}

const loadRecentActivities = async () => {
  activitiesLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 300))
    // 實際的活動載入邏輯會在這裡
  } finally {
    activitiesLoading.value = false
  }
}

const loadPerformanceData = async () => {
  chartLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    // 實際的性能數據載入邏輯會在這裡
  } finally {
    chartLoading.value = false
  }
}

// 初始化儀表板
const initializeDashboard = async () => {
  isInitialLoading.value = true
  isDataLoading.value = true
  initError.value = null
  
  try {
    // 階段 1: 初始化應用程式
    currentLoadingStage.value = 0
    if (!appStore.isInitialized) {
      await appStore.initialize()
    }
    
    // 階段 2: 載入設定
    currentLoadingStage.value = 1
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // 階段 3: 連接服務
    currentLoadingStage.value = 2
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 階段 4: 獲取數據
    currentLoadingStage.value = 3
    await refreshDashboardData()
    
    // 階段 5: 完成
    currentLoadingStage.value = 4
    await new Promise(resolve => setTimeout(resolve, 200))
    
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
    initError.value = '儀表板初始化時發生錯誤，部分功能可能無法正常使用'
    appStore.addNotification({
      type: 'error',
      title: '初始化失敗',
      message: initError.value
    })
  } finally {
    isInitialLoading.value = false
    isDataLoading.value = false
  }
}

// 快捷鍵和命令處理
const handleShortcut = (keys: string, event: KeyboardEvent) => {
  console.log('快捷鍵觸發:', keys)
}

const handleCommand = (command: any) => {
  console.log('命令執行:', command.title)
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
  console.log('儀表板組件載入中...')
  await initializeDashboard()
  startAutoRefresh()
})

onUnmounted(() => {
  console.log('儀表板正在卸載...')
  stopAutoRefresh()
  console.log('儀表板已卸載')
})
</script>

<style scoped>
/* 儀表板佈局 */
.dashboard-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  flex: 1;
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

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 載入狀態 */
.dashboard-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

/* 統計卡片區域 */
.stats-section {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow-light);
}

.stat-card.stat-error {
  border-left: 4px solid var(--el-color-danger);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 4px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
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

/* 主要內容區域 */
.dashboard-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.dashboard-main.mobile-stack {
  grid-template-columns: 1fr;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片標題 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 代理網格 */
.agent-loading,
.activities-loading,
.chart-loading {
  padding: 16px;
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
  background: var(--el-bg-color-page);
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s ease;
  position: relative;
}

.agent-item:hover {
  background: var(--el-bg-color);
  border-color: var(--el-border-color-light);
}

.agent-item.active {
  border-color: var(--el-color-success);
  background: var(--el-color-success-light-9);
}

.agent-item.processing {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.agent-item.error {
  border-color: var(--el-color-danger);
  background: var(--el-color-danger-light-9);
}

.agent-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--el-color-info-light-7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-info);
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.agent-status {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.agent-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-info);
}

.agent-indicator.active {
  background: var(--el-color-success);
  box-shadow: 0 0 6px var(--el-color-success);
}

.agent-indicator.processing {
  background: var(--el-color-primary);
  animation: pulse 2s infinite;
}

.agent-indicator.error {
  background: var(--el-color-danger);
}

/* 圖表容器 */
.chart-container {
  min-height: 300px;
  position: relative;
}

/* 快速操作 */
.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.action-button {
  height: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border-radius: 8px;
}

/* 活動時間線 */
.activity-content {
  padding: 4px 0;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.activity-description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

/* 動畫 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 過渡動畫 */
.card-fade-enter-active,
.card-fade-leave-active,
.agent-fade-enter-active,
.agent-fade-leave-active,
.timeline-fade-enter-active,
.timeline-fade-leave-active {
  transition: all 0.3s ease;
}

.card-fade-enter-from,
.card-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.agent-fade-enter-from,
.agent-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.timeline-fade-enter-from,
.timeline-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.timeline-item-animated {
  animation: slideInUp 0.5s ease forwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .dashboard-main {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-title {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .stat-content {
    gap: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
}

/* 無障礙支援 */
@media (prefers-reduced-motion: reduce) {
  .stat-card,
  .agent-item,
  .timeline-item-animated {
    transition: none;
    animation: none;
  }
  
  .agent-indicator.processing {
    animation: none;
  }
}

/* 高對比度模式 */
@media (prefers-contrast: high) {
  .stat-card,
  .agent-item {
    border-width: 2px;
  }
  
  .stat-change.positive {
    color: #008000;
  }
  
  .stat-change.negative {
    color: #ff0000;
  }
}
</style>