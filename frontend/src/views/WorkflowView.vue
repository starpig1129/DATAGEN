<template>
  <div class="workflow-view">
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">工作流視覺化</h1>
          <p class="page-description">多代理協作流程圖 - 可拖曳、縮放</p>
        </div>
        <div class="header-actions">
          <el-button :icon="Refresh" @click="resetLayout">重置佈局</el-button>
        </div>
      </div>
    </div>

    <div class="workflow-container">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :node-types="(nodeTypes as any)"
        :default-viewport="{ x: 100, y: 50, zoom: 0.8 }"
        :min-zoom="0.3"
        :max-zoom="2"
        fit-view-on-init
        class="workflow-flow"
      >
        <Background pattern-color="#aaa" :gap="16" />
        <MiniMap />
        <Controls />
      </VueFlow>
    </div>

    <!-- Legend -->
    <el-card class="workflow-legend" shadow="never">
      <div class="legend-items">
        <div class="legend-item">
          <span class="legend-dot agent"></span>
          <span>代理節點</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot decision"></span>
          <span>條件路由</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot start"></span>
          <span>開始/結束</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { Refresh } from '@element-plus/icons-vue'
import type { Node, Edge } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

import AgentNode from '@/components/workflow/AgentNode.vue'

// Custom node types
// @ts-ignore - Vue Flow type compatibility workaround
const nodeTypes = {
  agent: markRaw(AgentNode)
}

// Node positions (arranged in a flow layout)
const initialNodes: Node[] = [
  // Start
  { id: 'start', type: 'agent', position: { x: 400, y: 0 }, data: { label: '開始', type: 'start' } },
  
  // Layer 1: Hypothesis
  { id: 'hypothesis', type: 'agent', position: { x: 400, y: 100 }, data: { label: '假設代理', type: 'agent', agentId: 'hypothesis' } },
  
  // Layer 2: Human Choice
  { id: 'humanchoice', type: 'agent', position: { x: 400, y: 220 }, data: { label: '人工選擇', type: 'decision', agentId: 'humanchoice' } },
  
  // Layer 3: Process
  { id: 'process', type: 'agent', position: { x: 400, y: 350 }, data: { label: '流程代理', type: 'agent', agentId: 'process' } },
  
  // Layer 4: Workers (spread out)
  { id: 'searcher', type: 'agent', position: { x: 50, y: 480 }, data: { label: '搜尋代理', type: 'agent', agentId: 'searcher' } },
  { id: 'coder', type: 'agent', position: { x: 230, y: 480 }, data: { label: '程式碼代理', type: 'agent', agentId: 'coder' } },
  { id: 'visualization', type: 'agent', position: { x: 410, y: 480 }, data: { label: '視覺化代理', type: 'agent', agentId: 'visualization' } },
  { id: 'report', type: 'agent', position: { x: 590, y: 480 }, data: { label: '報告代理', type: 'agent', agentId: 'report' } },
  { id: 'refiner', type: 'agent', position: { x: 770, y: 480 }, data: { label: '優化代理', type: 'agent', agentId: 'refiner' } },
  
  // Layer 5: Quality Review
  { id: 'qualityreview', type: 'agent', position: { x: 320, y: 610 }, data: { label: '品質審查', type: 'decision', agentId: 'quality_review' } },
  
  // Layer 6: Note Taker
  { id: 'notetaker', type: 'agent', position: { x: 320, y: 740 }, data: { label: '筆記代理', type: 'agent', agentId: 'notetaker' } },
  
  // Human Review (for refiner)
  { id: 'humanreview', type: 'agent', position: { x: 770, y: 610 }, data: { label: '人工審核', type: 'decision', agentId: 'humanreview' } },
  
  // End
  { id: 'end', type: 'agent', position: { x: 770, y: 740 }, data: { label: '結束', type: 'end' } }
]

// Edge definitions based on workflow.py - using consistent app colors
const initialEdges: Edge[] = [
  // Start -> Hypothesis (success green)
  { id: 'e-start-hypothesis', source: 'start', target: 'hypothesis', animated: true, style: { stroke: '#67c23a' } },
  
  // Hypothesis -> HumanChoice (primary blue)
  { id: 'e-hypothesis-humanchoice', source: 'hypothesis', target: 'humanchoice', style: { stroke: '#409eff' } },
  
  // HumanChoice -> Process or back to Hypothesis (warning for decisions)
  { id: 'e-humanchoice-process', source: 'humanchoice', target: 'process', label: '繼續', style: { stroke: '#e6a23c' } },
  { id: 'e-humanchoice-hypothesis', source: 'humanchoice', target: 'hypothesis', label: '修改', style: { stroke: '#e6a23c', strokeDasharray: '5,5' }, type: 'smoothstep' },
  
  // Process -> Workers (primary blue)
  { id: 'e-process-searcher', source: 'process', target: 'searcher', style: { stroke: '#409eff' } },
  { id: 'e-process-coder', source: 'process', target: 'coder', style: { stroke: '#409eff' } },
  { id: 'e-process-visualization', source: 'process', target: 'visualization', style: { stroke: '#409eff' } },
  { id: 'e-process-report', source: 'process', target: 'report', style: { stroke: '#409eff' } },
  { id: 'e-process-refiner', source: 'process', target: 'refiner', style: { stroke: '#409eff' } },
  
  // Workers -> Quality Review (primary blue)
  { id: 'e-searcher-qr', source: 'searcher', target: 'qualityreview', style: { stroke: '#409eff' } },
  { id: 'e-coder-qr', source: 'coder', target: 'qualityreview', style: { stroke: '#409eff' } },
  { id: 'e-visualization-qr', source: 'visualization', target: 'qualityreview', style: { stroke: '#409eff' } },
  { id: 'e-report-qr', source: 'report', target: 'qualityreview', style: { stroke: '#409eff' } },
  
  // Quality Review -> NoteTaker (success green for pass)
  { id: 'e-qr-notetaker', source: 'qualityreview', target: 'notetaker', label: '通過', style: { stroke: '#67c23a' } },
  
  // NoteTaker -> Process (loop back, info gray dashed)
  { id: 'e-notetaker-process', source: 'notetaker', target: 'process', type: 'smoothstep', style: { stroke: '#909399', strokeDasharray: '5,5' } },
  
  // Refiner -> Human Review (primary blue)
  { id: 'e-refiner-humanreview', source: 'refiner', target: 'humanreview', style: { stroke: '#409eff' } },
  
  // Human Review -> End or back to Process
  { id: 'e-humanreview-end', source: 'humanreview', target: 'end', label: '完成', style: { stroke: '#67c23a' } },
  { id: 'e-humanreview-process', source: 'humanreview', target: 'process', label: '修改', type: 'smoothstep', style: { stroke: '#e6a23c', strokeDasharray: '5,5' } }
]



const nodes = ref<Node[]>(initialNodes)
const edges = ref<Edge[]>(initialEdges)

const resetLayout = () => {
  nodes.value = [...initialNodes]
  edges.value = [...initialEdges]
}
</script>

<style scoped>
.workflow-view {
  padding: 0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

.page-header {
  margin-bottom: 16px;
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

.workflow-container {
  flex: 1;
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
}

.workflow-flow {
  width: 100%;
  height: 100%;
  background: var(--bg-secondary);
}


.workflow-legend {
  margin-top: 16px;
  border-radius: 8px;
}

.legend-items {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-dot.agent {
  background: var(--primary-color, #409eff);
}

.legend-dot.decision {
  background: var(--warning-color, #e6a23c);
  border-radius: 50%;
}

.legend-dot.start {
  background: var(--success-color, #67c23a);
  border-radius: 10px;
}



/* Vue Flow overrides */
:deep(.vue-flow__edge-path) {
  stroke: #909399;
  stroke-width: 2;
}

:deep(.vue-flow__edge-text) {
  font-size: 11px;
  fill: var(--el-text-color-regular);
}

:deep(.vue-flow__minimap) {
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color);
}

:deep(.vue-flow__controls) {
  border-radius: 8px;
  border: 1px solid var(--el-border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: var(--el-bg-color);
}

:deep(.vue-flow__controls button) {
  background: var(--el-bg-color);
  border-color: var(--el-border-color);
  color: var(--el-text-color-primary);
}

:deep(.vue-flow__controls button:hover) {
  background: var(--bg-tertiary);
}

:deep(.vue-flow__controls button svg) {
  fill: var(--el-text-color-primary);
}

.dark :deep(.vue-flow__controls) {
  background: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.dark :deep(.vue-flow__controls button) {
  background: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.dark :deep(.vue-flow__controls button svg) {
  fill: var(--text-primary);
}


/* Dark mode */
.dark .workflow-container {
  background: var(--bg-tertiary);
}

.dark .workflow-flow {
  background: var(--bg-tertiary);
}

:deep(.vue-flow__pane) {
  background: var(--bg-secondary) !important;
}

.dark :deep(.vue-flow__pane) {
  background: var(--bg-tertiary) !important;
}

:deep(.vue-flow__viewport) {
  background: transparent !important;
}
</style>

