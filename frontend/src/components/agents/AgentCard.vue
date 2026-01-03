<template>
  <el-card class="agent-card" :class="statusClass" shadow="hover">
    <div class="agent-header">
      <div class="agent-icon" :style="{ backgroundColor: statusColor }">
        <el-icon :size="24" color="white">
          <component :is="agentIcon" />
        </el-icon>
      </div>
      <div class="agent-info">
        <h3 class="agent-name">{{ displayName }}</h3>
        <el-tag :type="tagType" size="small">{{ statusText }}</el-tag>
      </div>
    </div>

    <div class="agent-body">
      <div v-if="currentTask" class="current-task">
        <el-icon><Loading /></el-icon>
        <span>{{ currentTask }}</span>
      </div>
      <div v-else class="current-task idle">
        <span>待機中</span>
      </div>

      <el-progress
        v-if="status === 'processing'"
        :percentage="progress"
        :stroke-width="6"
        :show-text="false"
        class="agent-progress"
      />
    </div>

    <div class="agent-footer">
      <span class="last-activity">{{ lastActivityText }}</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Cpu,
  Search,
  DocumentCopy,
  PieChart,
  Document,
  Check,
  Loading,
  Setting,
  DataAnalysis,
  EditPen
} from '@element-plus/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

interface Props {
  agentId: string
  name: string
  status: 'idle' | 'processing' | 'completed' | 'error'
  progress?: number
  currentTask?: string
  lastActivity?: string
}

const props = withDefaults(defineProps<Props>(), {
  status: 'idle',
  progress: 0,
  currentTask: '',
  lastActivity: ''
})

// Display name mapping
const agentNameMap: Record<string, string> = {
  'hypothesis': '假設代理',
  'process': '流程代理',
  'visualization': '視覺化代理',
  'search': '搜尋代理',
  'searcher': '搜尋代理',
  'code': '程式碼代理',
  'coder': '程式碼代理',
  'report': '報告代理',
  'quality_review': '品質審查代理',
  'qualityreview': '品質審查代理',
  'note': '筆記代理',
  'notetaker': '筆記代理',
  'refiner': '優化代理'
}

const displayName = computed(() => {
  const key = props.agentId.toLowerCase().replace(/_agent$/, '')
  return agentNameMap[key] || props.name
})

// Icon mapping
const agentIcons: Record<string, any> = {
  'hypothesis': DataAnalysis,
  'process': Setting,
  'visualization': PieChart,
  'search': Search,
  'searcher': Search,
  'code': Cpu,
  'coder': Cpu,
  'report': Document,
  'quality_review': Check,
  'qualityreview': Check,
  'note': DocumentCopy,
  'notetaker': DocumentCopy,
  'refiner': EditPen
}

const agentIcon = computed(() => {
  const key = props.agentId.toLowerCase().replace(/_agent$/, '')
  return agentIcons[key] || Cpu
})

// Status styling
const statusClass = computed(() => `status-${props.status}`)

const statusColor = computed(() => {
  const colors: Record<string, string> = {
    idle: '#909399',
    processing: '#409eff',
    completed: '#67c23a',
    error: '#f56c6c'
  }
  return colors[props.status] || '#909399'
})

const tagType = computed(() => {
  const types: Record<string, 'info' | 'primary' | 'success' | 'danger' | 'warning'> = {
    idle: 'info',
    processing: 'primary',
    completed: 'success',
    error: 'danger'
  }
  return types[props.status] || 'info'
})

const statusText = computed(() => {
  const texts: Record<string, string> = {
    idle: '待機',
    processing: '處理中',
    completed: '完成',
    error: '錯誤'
  }
  return texts[props.status] || '未知'
})

const lastActivityText = computed(() => {
  if (!props.lastActivity) return '無活動紀錄'
  try {
    return formatDistanceToNow(new Date(props.lastActivity), {
      addSuffix: true,
      locale: zhTW
    })
  } catch {
    return props.lastActivity
  }
})
</script>

<style scoped>
.agent-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.agent-card.status-idle {
  border-left-color: #909399;
}

.agent-card.status-processing {
  border-left-color: #409eff;
  animation: pulse-border 2s infinite;
}

.agent-card.status-completed {
  border-left-color: #67c23a;
}

.agent-card.status-error {
  border-left-color: #f56c6c;
}

@keyframes pulse-border {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.agent-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.agent-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.agent-info {
  flex: 1;
}

.agent-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.agent-body {
  min-height: 60px;
}

.current-task {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--el-text-color-regular);
  padding: 8px 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.current-task.idle {
  color: var(--el-text-color-placeholder);
}

.current-task .el-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.agent-progress {
  margin-top: 12px;
}

.agent-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.last-activity {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

/* Dark mode */
.dark .agent-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
</style>
