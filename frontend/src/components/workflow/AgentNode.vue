<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import {
  DataAnalysis,
  Setting,
  Search,
  Cpu,
  PieChart,
  Document,
  Check,
  DocumentCopy,
  EditPen,
  User,
  Flag,
  SuccessFilled
} from '@element-plus/icons-vue'

interface Props {
  data: {
    label: string
    type: 'agent' | 'decision' | 'start' | 'end'
    agentId?: string
    description?: string
  }
}

const props = defineProps<Props>()

// Icon mapping
const iconMap: Record<string, any> = {
  hypothesis: DataAnalysis,
  process: Setting,
  searcher: Search,
  search: Search,
  code: Cpu,
  coder: Cpu,
  visualization: PieChart,
  report: Document,
  quality_review: Check,
  qualityreview: Check,
  note: DocumentCopy,
  notetaker: DocumentCopy,
  refiner: EditPen,
  humanchoice: User,
  humanreview: User,
  start: Flag,
  end: SuccessFilled
}

const nodeIcon = computed(() => {
  if (props.data.type === 'start') return Flag
  if (props.data.type === 'end') return SuccessFilled
  if (props.data.type === 'decision') return User
  const key = props.data.agentId?.toLowerCase().replace(/_agent$/, '') || ''
  return iconMap[key] || Setting
})

const nodeClass = computed(() => `node-${props.data.type}`)
</script>

<template>
  <div class="agent-node" :class="nodeClass">
    <Handle type="target" :position="Position.Top" />
    
    <div class="node-content">
      <div class="node-icon">
        <el-icon :size="20">
          <component :is="nodeIcon" />
        </el-icon>
      </div>
      <div class="node-label">{{ data.label }}</div>
    </div>
    
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>

<style scoped>
.agent-node {
  padding: 12px 20px;
  border-radius: var(--radius-lg, 8px);
  background: var(--el-bg-color);
  border: 2px solid var(--el-border-color);
  box-shadow: var(--el-box-shadow-light);
  transition: var(--transition-base, all 0.3s ease);
  min-width: 120px;
}

.agent-node:hover {
  box-shadow: var(--el-box-shadow-base);
  transform: translateY(-2px);
}

/* Agent nodes - Use primary color */
.node-agent {
  border-color: var(--primary-color, #409eff);
  background: var(--el-bg-color);
}

.node-agent .node-icon {
  color: var(--primary-color, #409eff);
}

.node-agent .node-label {
  color: var(--el-text-color-primary);
}

/* Decision nodes - Use warning color */
.node-decision {
  border-color: var(--warning-color, #e6a23c);
  background: var(--el-bg-color);
  border-radius: 50%;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-decision .node-icon {
  color: var(--warning-color, #e6a23c);
}

.node-decision .node-label {
  color: var(--el-text-color-primary);
}

/* Start/End nodes - Use success color */
.node-start,
.node-end {
  border-color: var(--success-color, #67c23a);
  background: var(--el-bg-color);
  border-radius: 20px;
}

.node-start .node-icon,
.node-end .node-icon {
  color: var(--success-color, #67c23a);
}

.node-start .node-label,
.node-end .node-label {
  color: var(--el-text-color-primary);
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-decision .node-content {
  flex-direction: column;
  gap: 4px;
}

.node-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-label {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

/* Vue Flow handle styles */
:deep(.vue-flow__handle) {
  width: 10px;
  height: 10px;
  background: var(--el-bg-color);
  border: 2px solid var(--primary-color, #409eff);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.node-decision :deep(.vue-flow__handle) {
  border-color: var(--warning-color, #e6a23c);
}

.node-start :deep(.vue-flow__handle),
.node-end :deep(.vue-flow__handle) {
  border-color: var(--success-color, #67c23a);
}
</style>


