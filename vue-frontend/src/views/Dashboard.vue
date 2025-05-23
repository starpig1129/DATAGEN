<template>
  <div class="dashboard">
    <!-- 頁面標題 -->
    <div class="page-header">
      <h1 class="page-title">系統儀表板</h1>
      <p class="page-description">多代理數據分析系統總覽</p>
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
                <el-icon><Robot /></el-icon>
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
            <!-- 這裡將來整合 Plotly.js 圖表 -->
            <div class="chart-placeholder">
              <el-icon :size="48"><TrendCharts /></el-icon>
              <p>性能圖表將在此顯示</p>
            </div>
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
              :type="action.type"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Robot,
  TrendCharts,
  ChatDotRound,
  View,
  DataAnalysis,
  Folder,
  Setting,
  ArrowUp,
  ArrowDown,
  Monitor,
  DocumentCopy,
  Connection
} from '@element-plus/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

const router = useRouter()

// 系統統計數據
const systemStats = ref([
  {
    key: 'agents',
    label: '活躍代理',
    value: '6/8',
    change: '+2',
    trend: 'positive',
    color: '#67c23a',
    icon: Robot,
    trendIcon: ArrowUp
  },
  {
    key: 'tasks',
    label: '完成任務',
    value: '156',
    change: '+24',
    trend: 'positive',
    color: '#409eff',
    icon: DocumentCopy,
    trendIcon: ArrowUp
  },
  {
    key: 'performance',
    label: '系統性能',
    value: '95%',
    change: '-2%',
    trend: 'negative',
    color: '#e6a23c',
    icon: TrendCharts,
    trendIcon: ArrowDown
  },
  {
    key: 'connections',
    label: '連接數',
    value: '23',
    change: '+5',
    trend: 'positive',
    color: '#f56c6c',
    icon: Connection,
    trendIcon: ArrowUp
  }
])

// 代理狀態
const agentStatus = ref([
  { id: '1', name: '處理代理', status: 'active' },
  { id: '2', name: '假設代理', status: 'idle' },
  { id: '3', name: '搜索代理', status: 'processing' },
  { id: '4', name: '代碼代理', status: 'idle' },
  { id: '5', name: '視覺化代理', status: 'active' },
  { id: '6', name: '報告代理', status: 'processing' },
  { id: '7', name: '品質審查代理', status: 'idle' },
  { id: '8', name: '優化代理', status: 'error' }
])

// 最近活動
const recentActivities = ref([
  {
    id: '1',
    title: '假設生成完成',
    description: '假設代理成功生成了3個可行的研究假設',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    type: 'success'
  },
  {
    id: '2',
    title: '數據搜索啟動',
    description: '搜索代理開始收集相關數據資源',
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    type: 'primary'
  },
  {
    id: '3',
    title: '報告生成中',
    description: '報告代理正在編制分析報告',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    type: 'warning'
  }
])

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

// 生命週期
onMounted(() => {
  // 初始化儀表板數據
  console.log('儀表板已載入')
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--el-text-color-placeholder);
}

.chart-placeholder p {
  margin-top: 16px;
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