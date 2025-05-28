<template>
  <div class="performance-chart-wrapper">
    <div class="chart-controls">
      <el-radio-group v-model="timeRange" size="small" @change="updateTimeRange">
        <el-radio-button label="1h">1小時</el-radio-button>
        <el-radio-button label="6h">6小時</el-radio-button>
        <el-radio-button label="24h">24小時</el-radio-button>
      </el-radio-group>
    </div>
    
    <div class="chart-container" :class="{ 'loading': isLoading }">
      <div v-if="isLoading" class="chart-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>載入圖表數據...</span>
      </div>
      
      <div v-else class="svg-chart-container">
        <div class="chart-legend">
          <div class="legend-item">
            <div class="legend-color cpu"></div>
            <span>CPU</span>
          </div>
          <div class="legend-item">
            <div class="legend-color memory"></div>
            <span>記憶體</span>
          </div>
          <div class="legend-item">
            <div class="legend-color network"></div>
            <span>網路</span>
          </div>
        </div>
        
        <svg 
          ref="chartSvg" 
          :width="chartWidth" 
          :height="chartHeight - 60" 
          class="performance-svg"
        >
          <!-- 網格線 -->
          <g class="grid">
            <line
              v-for="i in 5"
              :key="`h-grid-${i}`"
              :x1="40"
              :x2="chartWidth - 20"
              :y1="(chartHeight - 100) * i / 5 + 10"
              :y2="(chartHeight - 100) * i / 5 + 10"
              class="grid-line"
            />
            <line
              v-for="i in 6"
              :key="`v-grid-${i}`"
              :x1="40 + (chartWidth - 60) * i / 6"
              :x2="40 + (chartWidth - 60) * i / 6"
              :y1="10"
              :y2="chartHeight - 90"
              class="grid-line"
            />
          </g>
          
          <!-- Y軸標籤 -->
          <g class="y-axis">
            <text
              v-for="i in 6"
              :key="`y-label-${i}`"
              :x="35"
              :y="(chartHeight - 100) * (5 - i) / 5 + 15"
              class="axis-label"
              text-anchor="end"
            >
              {{ (i - 1) * 20 }}%
            </text>
          </g>
          
          <!-- CPU 線圖 -->
          <polyline
            :points="cpuPoints"
            class="chart-line cpu"
            fill="none"
          />
          
          <!-- 記憶體線圖 -->
          <polyline
            :points="memoryPoints"
            class="chart-line memory"
            fill="none"
          />
          
          <!-- 網路線圖 -->
          <polyline
            :points="networkPoints"
            class="chart-line network"
            fill="none"
          />
          
          <!-- 數據點 -->
          <circle
            v-for="(point, index) in performanceData"
            :key="`cpu-point-${index}`"
            :cx="40 + (chartWidth - 60) * index / (performanceData.length - 1)"
            :cy="(chartHeight - 100) * (1 - point.cpu / 100) + 10"
            r="2"
            class="data-point cpu"
            @mouseenter="showTooltip($event, point, 'CPU')"
            @mouseleave="hideTooltip"
          />
          
          <circle
            v-for="(point, index) in performanceData"
            :key="`memory-point-${index}`"
            :cx="40 + (chartWidth - 60) * index / (performanceData.length - 1)"
            :cy="(chartHeight - 100) * (1 - point.memory / 100) + 10"
            r="2"
            class="data-point memory"
            @mouseenter="showTooltip($event, point, 'Memory')"
            @mouseleave="hideTooltip"
          />
        </svg>
        
        <!-- 提示框 -->
        <div 
          v-if="tooltip.visible" 
          ref="tooltipRef"
          class="chart-tooltip"
          :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        >
          <div class="tooltip-content">
            <div>{{ tooltip.type }}: {{ tooltip.value }}%</div>
            <div>{{ tooltip.time }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 性能指標概覽 -->
    <div class="metrics-summary">
      <div
        v-for="metric in currentMetrics"
        :key="metric.name"
        class="metric-item"
      >
        <div class="metric-value" :style="{ color: metric.color }">
          {{ metric.value }}{{ metric.unit }}
        </div>
        <div class="metric-label">{{ metric.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

interface PerformanceData {
  timestamp: Date
  cpu: number
  memory: number
  network: number
  disk: number
}

interface MetricSummary {
  name: string
  label: string
  value: number
  unit: string
  color: string
}

interface Tooltip {
  visible: boolean
  x: number
  y: number
  type: string
  value: number
  time: string
}

// Props
interface Props {
  height?: number
  refreshInterval?: number
  isDark?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 280,
  refreshInterval: 5000,
  isDark: false
})

// Reactive state
const isLoading = ref(true)
const timeRange = ref<'1h' | '6h' | '24h'>('1h')
const performanceData = ref<PerformanceData[]>([])
const chartSvg = ref<SVGElement>()
const tooltipRef = ref<HTMLElement>()
const chartWidth = ref(600)
const chartHeight = computed(() => props.height)

const tooltip = ref<Tooltip>({
  visible: false,
  x: 0,
  y: 0,
  type: '',
  value: 0,
  time: ''
})

// 時間範圍配置
const timeRangeConfig: Record<'1h' | '6h' | '24h', { points: number; interval: number }> = {
  '1h': { points: 20, interval: 180000 }, // 20點，每3分鐘一個
  '6h': { points: 24, interval: 900000 }, // 24點，每15分鐘一個
  '24h': { points: 24, interval: 3600000 } // 24點，每小時一個
}

// 當前性能指標摘要
const currentMetrics = computed<MetricSummary[]>(() => {
  if (performanceData.value.length === 0) {
    return [
      { name: 'cpu', label: 'CPU使用率', value: 0, unit: '%', color: '#409eff' },
      { name: 'memory', label: '記憶體使用率', value: 0, unit: '%', color: '#67c23a' },
      { name: 'network', label: '網路流量', value: 0, unit: 'MB/s', color: '#e6a23c' },
      { name: 'disk', label: '磁碟I/O', value: 0, unit: 'MB/s', color: '#f56c6c' }
    ]
  }

  const latest = performanceData.value[performanceData.value.length - 1]
  return [
    {
      name: 'cpu',
      label: 'CPU使用率',
      value: Math.round(latest.cpu),
      unit: '%',
      color: '#409eff'
    },
    {
      name: 'memory',
      label: '記憶體使用率',
      value: Math.round(latest.memory),
      unit: '%',
      color: '#67c23a'
    },
    {
      name: 'network',
      label: '網路流量',
      value: Math.round(latest.network * 10) / 10,
      unit: 'MB/s',
      color: '#e6a23c'
    },
    {
      name: 'disk',
      label: '磁碟I/O',
      value: Math.round(latest.disk * 10) / 10,
      unit: 'MB/s',
      color: '#f56c6c'
    }
  ]
})

// SVG 路徑點
const cpuPoints = computed(() => {
  if (performanceData.value.length === 0) return ''
  return performanceData.value
    .map((point, index) => {
      const x = 40 + (chartWidth.value - 60) * index / (performanceData.value.length - 1)
      const y = (chartHeight.value - 100) * (1 - point.cpu / 100) + 10
      return `${x},${y}`
    })
    .join(' ')
})

const memoryPoints = computed(() => {
  if (performanceData.value.length === 0) return ''
  return performanceData.value
    .map((point, index) => {
      const x = 40 + (chartWidth.value - 60) * index / (performanceData.value.length - 1)
      const y = (chartHeight.value - 100) * (1 - point.memory / 100) + 10
      return `${x},${y}`
    })
    .join(' ')
})

const networkPoints = computed(() => {
  if (performanceData.value.length === 0) return ''
  return performanceData.value
    .map((point, index) => {
      const x = 40 + (chartWidth.value - 60) * index / (performanceData.value.length - 1)
      const y = (chartHeight.value - 100) * (1 - (point.network * 10) / 100) + 10
      return `${x},${y}`
    })
    .join(' ')
})

// 生成模擬性能數據
const generatePerformanceData = (): PerformanceData[] => {
  const config = timeRangeConfig[timeRange.value]
  const data: PerformanceData[] = []
  const now = new Date()
  
  for (let i = config.points - 1; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * config.interval)
    
    // 生成帶有趨勢和隨機變化的數據
    const timeProgress = (config.points - 1 - i) / config.points
    const baseCpu = 30 + Math.sin(timeProgress * Math.PI * 4) * 15
    const baseMemory = 50 + Math.cos(timeProgress * Math.PI * 3) * 20
    const baseNetwork = 5 + Math.sin(timeProgress * Math.PI * 6) * 3
    const baseDisk = 2 + Math.cos(timeProgress * Math.PI * 5) * 1.5
    
    data.push({
      timestamp,
      cpu: Math.max(5, Math.min(95, baseCpu + (Math.random() - 0.5) * 10)),
      memory: Math.max(10, Math.min(90, baseMemory + (Math.random() - 0.5) * 8)),
      network: Math.max(0, baseNetwork + (Math.random() - 0.5) * 2),
      disk: Math.max(0, baseDisk + (Math.random() - 0.5) * 1)
    })
  }
  
  return data
}

// 提示框
const showTooltip = (event: MouseEvent, point: PerformanceData, type: string) => {
  const value = type === 'CPU' ? point.cpu : point.memory
  tooltip.value = {
    visible: true,
    x: event.offsetX + 10,
    y: event.offsetY - 30,
    type,
    value: Math.round(value),
    time: formatDistanceToNow(point.timestamp, { addSuffix: true, locale: zhTW })
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

// 更新時間範圍
const updateTimeRange = () => {
  loadPerformanceData()
}

// 載入性能數據
const loadPerformanceData = async () => {
  isLoading.value = true
  
  try {
    // 模擬API請求延遲
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 生成新數據
    performanceData.value = generatePerformanceData()
  } catch (error) {
    console.error('載入性能數據失敗:', error)
  } finally {
    isLoading.value = false
  }
}

// 更新圖表寬度
const updateChartSize = () => {
  if (chartSvg.value) {
    const container = chartSvg.value.parentElement
    if (container) {
      chartWidth.value = container.clientWidth
    }
  }
}

// 定時刷新
let refreshTimer: number | null = null

const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    if (!document.hidden) {
      // 添加新數據點並移除舊數據
      const newDataPoint = generatePerformanceData().slice(-1)[0]
      performanceData.value.push(newDataPoint)
      
      const config = timeRangeConfig[timeRange.value]
      if (performanceData.value.length > config.points) {
        performanceData.value.shift()
      }
    }
  }, props.refreshInterval)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命週期
onMounted(async () => {
  await loadPerformanceData()
  updateChartSize()
  startAutoRefresh()
  
  // 監聽窗口大小變化
  window.addEventListener('resize', updateChartSize)
})

onUnmounted(() => {
  stopAutoRefresh()
  window.removeEventListener('resize', updateChartSize)
})
</script>

<style scoped>
.performance-chart-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-controls {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.chart-container {
  flex: 1;
  position: relative;
  min-height: 200px;
}

.chart-container.loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--el-text-color-regular);
}

.chart-loading .el-icon {
  font-size: 24px;
}

.svg-chart-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.legend-color {
  width: 12px;
  height: 3px;
  border-radius: 1px;
}

.legend-color.cpu {
  background-color: #409eff;
}

.legend-color.memory {
  background-color: #67c23a;
}

.legend-color.network {
  background-color: #e6a23c;
}

.performance-svg {
  width: 100%;
  display: block;
}

.grid-line {
  stroke: var(--el-border-color-lighter);
  stroke-width: 1;
  opacity: 0.5;
}

.axis-label {
  fill: var(--el-text-color-regular);
  font-size: 10px;
}

.chart-line {
  stroke-width: 2;
  stroke-linejoin: round;
  stroke-linecap: round;
}

.chart-line.cpu {
  stroke: #409eff;
}

.chart-line.memory {
  stroke: #67c23a;
}

.chart-line.network {
  stroke: #e6a23c;
}

.data-point {
  fill: white;
  stroke-width: 2;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.data-point:hover {
  opacity: 1;
}

.data-point.cpu {
  stroke: #409eff;
}

.data-point.memory {
  stroke: #67c23a;
}

.chart-tooltip {
  position: absolute;
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  box-shadow: var(--el-box-shadow);
  z-index: 1000;
  pointer-events: none;
}

.tooltip-content {
  color: var(--el-text-color-primary);
  line-height: 1.4;
}

.metrics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.metric-item {
  text-align: center;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  line-height: 1;
}

.metric-label {
  font-size: 12px;
  color: var(--el-text-color-regular);
  margin-top: 4px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .metrics-summary {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-controls {
    justify-content: center;
  }
  
  .chart-legend {
    gap: 12px;
  }
}
</style>