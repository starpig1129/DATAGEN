<template>
  <div class="skeleton-loader" :class="{ 'dark-mode': isDark }">
    <!-- 卡片骨架屏 -->
    <div v-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-header">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-text-group">
          <div class="skeleton-text skeleton-title"></div>
          <div class="skeleton-text skeleton-subtitle"></div>
        </div>
      </div>
      <div class="skeleton-content">
        <div v-for="i in lines" :key="i" class="skeleton-text" :style="getLineWidth(i)"></div>
      </div>
    </div>

    <!-- 圖表骨架屏 -->
    <div v-else-if="type === 'chart'" class="skeleton-chart">
      <div class="skeleton-chart-header">
        <div class="skeleton-text skeleton-chart-title"></div>
        <div class="skeleton-chart-controls">
          <div v-for="i in 3" :key="i" class="skeleton-control-btn"></div>
        </div>
      </div>
      <div class="skeleton-chart-body">
        <div class="skeleton-chart-area">
          <div class="skeleton-chart-bars">
            <div 
              v-for="i in 8" 
              :key="i" 
              class="skeleton-bar" 
              :style="{ height: `${Math.random() * 60 + 20}%` }"
            ></div>
          </div>
          <div class="skeleton-chart-axes">
            <div class="skeleton-axis skeleton-x-axis"></div>
            <div class="skeleton-axis skeleton-y-axis"></div>
          </div>
        </div>
        <div class="skeleton-chart-legend">
          <div v-for="i in 4" :key="i" class="skeleton-legend-item">
            <div class="skeleton-legend-color"></div>
            <div class="skeleton-legend-text"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 表格骨架屏 -->
    <div v-else-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table-header">
        <div v-for="i in columns" :key="i" class="skeleton-table-header-cell"></div>
      </div>
      <div class="skeleton-table-body">
        <div v-for="row in rows" :key="row" class="skeleton-table-row">
          <div v-for="col in columns" :key="col" class="skeleton-table-cell"></div>
        </div>
      </div>
    </div>

    <!-- 列表骨架屏 -->
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="i in items" :key="i" class="skeleton-list-item">
        <div class="skeleton-list-icon"></div>
        <div class="skeleton-list-content">
          <div class="skeleton-text skeleton-list-title"></div>
          <div class="skeleton-text skeleton-list-subtitle"></div>
        </div>
        <div class="skeleton-list-action"></div>
      </div>
    </div>

    <!-- 文字骨架屏 -->
    <div v-else-if="type === 'text'" class="skeleton-text-block">
      <div v-for="i in lines" :key="i" class="skeleton-text" :style="getLineWidth(i)"></div>
    </div>

    <!-- 自定義骨架屏 -->
    <div v-else class="skeleton-custom">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

interface Props {
  type?: 'card' | 'chart' | 'table' | 'list' | 'text' | 'custom'
  lines?: number
  rows?: number
  columns?: number
  items?: number
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'card',
  lines: 3,
  rows: 5,
  columns: 4,
  items: 5,
  animated: true
})

const appStore = useAppStore()

const isDark = computed(() => appStore.theme === 'dark')

const getLineWidth = (lineIndex: number) => {
  const widths = ['100%', '85%', '92%', '78%', '95%', '88%']
  return { width: widths[lineIndex % widths.length] }
}
</script>

<style scoped>
.skeleton-loader {
  --skeleton-color: #f2f2f2;
  --skeleton-highlight: #ffffff;
  --skeleton-duration: 1.5s;
}

.skeleton-loader.dark-mode {
  --skeleton-color: #374151;
  --skeleton-highlight: #4b5563;
}

/* 基礎骨架元素 */
.skeleton-text,
.skeleton-avatar,
.skeleton-control-btn,
.skeleton-legend-color,
.skeleton-table-header-cell,
.skeleton-table-cell,
.skeleton-list-icon,
.skeleton-list-action {
  background: linear-gradient(
    90deg,
    var(--skeleton-color) 25%,
    var(--skeleton-highlight) 50%,
    var(--skeleton-color) 75%
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: shimmer var(--skeleton-duration) infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 卡片骨架屏 */
.skeleton-card {
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-bg-color);
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.skeleton-text-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-title {
  height: 16px;
  width: 60%;
}

.skeleton-subtitle {
  height: 14px;
  width: 40%;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-text {
  height: 14px;
  border-radius: 4px;
}

/* 圖表骨架屏 */
.skeleton-chart {
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-bg-color);
}

.skeleton-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.skeleton-chart-title {
  height: 20px;
  width: 200px;
}

.skeleton-chart-controls {
  display: flex;
  gap: 8px;
}

.skeleton-control-btn {
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.skeleton-chart-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-chart-area {
  position: relative;
  height: 300px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 16px;
}

.skeleton-chart-bars {
  display: flex;
  align-items: end;
  justify-content: space-around;
  height: 100%;
  gap: 8px;
}

.skeleton-bar {
  flex: 1;
  background: linear-gradient(
    90deg,
    var(--skeleton-color) 25%,
    var(--skeleton-highlight) 50%,
    var(--skeleton-color) 75%
  );
  background-size: 200% 100%;
  border-radius: 2px;
  animation: shimmer var(--skeleton-duration) infinite;
  min-height: 20px;
}

.skeleton-chart-axes {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  top: 0;
  pointer-events: none;
}

.skeleton-x-axis {
  position: absolute;
  bottom: 16px;
  left: 16px;
  right: 16px;
  height: 1px;
  background: var(--skeleton-color);
}

.skeleton-y-axis {
  position: absolute;
  left: 16px;
  top: 16px;
  bottom: 16px;
  width: 1px;
  background: var(--skeleton-color);
}

.skeleton-chart-legend {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.skeleton-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skeleton-legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.skeleton-legend-text {
  height: 14px;
  width: 60px;
}

/* 表格骨架屏 */
.skeleton-table {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-bg-color);
}

.skeleton-table-header {
  display: grid;
  grid-template-columns: repeat(var(--columns, 4), 1fr);
  gap: 1px;
  background: var(--el-bg-color-page);
  padding: 12px;
}

.skeleton-table-header-cell {
  height: 16px;
}

.skeleton-table-body {
  display: flex;
  flex-direction: column;
}

.skeleton-table-row {
  display: grid;
  grid-template-columns: repeat(var(--columns, 4), 1fr);
  gap: 1px;
  padding: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.skeleton-table-row:last-child {
  border-bottom: none;
}

.skeleton-table-cell {
  height: 14px;
}

/* 列表骨架屏 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-bg-color);
}

.skeleton-list-icon {
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.skeleton-list-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-list-title {
  height: 16px;
  width: 70%;
}

.skeleton-list-subtitle {
  height: 14px;
  width: 50%;
}

.skeleton-list-action {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .skeleton-card,
  .skeleton-chart {
    padding: 16px;
  }
  
  .skeleton-chart-area {
    height: 200px;
  }
  
  .skeleton-chart-legend {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .skeleton-table-header,
  .skeleton-table-row {
    padding: 8px;
  }
  
  .skeleton-list-item {
    padding: 8px;
  }
}

/* 無動畫模式 */
@media (prefers-reduced-motion: reduce) {
  .skeleton-text,
  .skeleton-avatar,
  .skeleton-control-btn,
  .skeleton-legend-color,
  .skeleton-table-header-cell,
  .skeleton-table-cell,
  .skeleton-list-icon,
  .skeleton-list-action,
  .skeleton-bar {
    animation: none;
    background: var(--skeleton-color);
  }
}
</style>