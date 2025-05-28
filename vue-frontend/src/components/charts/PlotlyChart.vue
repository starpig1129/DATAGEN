<template>
  <div class="plotly-chart-container" :style="{ height: height + 'px' }">
    <div v-if="isLoading" class="chart-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>載入圖表...</span>
    </div>
    <div
      v-else
      ref="plotlyContainer"
      class="plotly-chart"
      :style="{ height: '100%' }"
    />
    <div v-if="error" class="chart-error">
      <el-icon><Warning /></el-icon>
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Loading, Warning } from '@element-plus/icons-vue'
// 使用更具體的 Plotly.js 導入來避免 buffer 相關問題
import Plotly from 'plotly.js/lib/core'
import Bar from 'plotly.js/lib/bar'
import Scatter from 'plotly.js/lib/scatter'
import Pie from 'plotly.js/lib/pie'
import Histogram from 'plotly.js/lib/histogram'
import Box from 'plotly.js/lib/box'
import Heatmap from 'plotly.js/lib/heatmap'
import type { ChartData, ChartControls } from '@/types/visualization'

// 註冊常用的圖表類型
Plotly.register([Bar, Scatter, Pie, Histogram, Box, Heatmap])

interface Props {
  chartData: ChartData
  controls?: ChartControls
  height?: number
}

interface Emits {
  (e: 'data-click', data: any): void
  (e: 'error', error: Error): void
}

const props = withDefaults(defineProps<Props>(), {
  height: 400,
  controls: () => ({
    showLegend: true,
    showGrid: true,
    showToolbar: true,
    theme: 'light',
    animation: true
  })
})

const emit = defineEmits<Emits>()

// 響應式狀態
const plotlyContainer = ref<HTMLElement>()
const isLoading = ref(false)
const error = ref<string>()
let plotlyInstance: any = null

// 默認配置
const getDefaultConfig = () => ({
  responsive: true,
  displayModeBar: props.controls?.showToolbar ?? true,
  modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
  displaylogo: false,
  toImageButtonOptions: {
    format: 'png',
    filename: props.chartData.title || 'chart',
    height: props.height,
    width: Math.floor(props.height * 1.5),
    scale: 2
  }
})

// 獲取主題配置
const getThemeLayout = () => {
  const isDark = props.controls?.theme === 'dark'
  
  return {
    paper_bgcolor: isDark ? '#1a1a1a' : '#ffffff',
    plot_bgcolor: isDark ? '#2a2a2a' : '#ffffff',
    font: {
      color: isDark ? '#e4e7ed' : '#303133'
    },
    xaxis: {
      gridcolor: isDark ? '#3a3a3a' : '#e4e7ed',
      zerolinecolor: isDark ? '#4a4a4a' : '#d3d4d6',
      showgrid: props.controls?.showGrid ?? true
    },
    yaxis: {
      gridcolor: isDark ? '#3a3a3a' : '#e4e7ed',
      zerolinecolor: isDark ? '#4a4a4a' : '#d3d4d6',
      showgrid: props.controls?.showGrid ?? true
    },
    showlegend: props.controls?.showLegend ?? true
  }
}

// 渲染圖表
const renderChart = async () => {
  if (!plotlyContainer.value || !props.chartData) {
    return
  }

  isLoading.value = true
  error.value = undefined

  try {
    // 合併布局配置
    const layout = {
      ...getThemeLayout(),
      ...props.chartData.layout,
      autosize: true,
      margin: { l: 50, r: 50, t: 50, b: 50 }
    }

    // 合併配置
    const config = {
      ...getDefaultConfig(),
      ...props.chartData.config
    }

    // 如果已有實例，先清除
    if (plotlyInstance) {
      (Plotly as any).purge(plotlyContainer.value)
    }

    // 創建新圖表
    await (Plotly as any).newPlot(
      plotlyContainer.value,
      props.chartData.data,
      layout,
      config
    )

    plotlyInstance = plotlyContainer.value

    // 綁定事件
    bindEvents()

  } catch (err) {
    console.error('渲染圖表失敗:', err)
    error.value = err instanceof Error ? err.message : '渲染失敗'
    emit('error', err instanceof Error ? err : new Error('渲染失敗'))
  } finally {
    isLoading.value = false
  }
}

// 綁定事件
const bindEvents = () => {
  if (!plotlyContainer.value) return

  // 點擊事件
  (plotlyContainer.value as any).on('plotly_click', (data: any) => {
    emit('data-click', data)
  })

  // 懸停事件
  (plotlyContainer.value as any).on('plotly_hover', (_data: any) => {
    // 可以在這裡添加懸停邏輯
  })

  // 選擇事件
  (plotlyContainer.value as any).on('plotly_selected', (_data: any) => {
    // 可以在這裡添加選擇邏輯
  })
}

// 重新調整大小
const resizeChart = () => {
  if (plotlyInstance) {
    (Plotly as any).Plots.resize(plotlyInstance)
  }
}

// 更新圖表
const updateChart = async () => {
  if (!plotlyContainer.value || !props.chartData) return

  try {
    const layout = {
      ...getThemeLayout(),
      ...props.chartData.layout
    }

    await (Plotly as any).react(
      plotlyContainer.value,
      props.chartData.data,
      layout
    )
  } catch (err) {
    console.error('更新圖表失敗:', err)
    // 如果更新失敗，嘗試重新渲染
    await renderChart()
  }
}

// 監聽數據變化
watch(
  () => props.chartData,
  async () => {
    await nextTick()
    if (plotlyInstance) {
      await updateChart()
    } else {
      await renderChart()
    }
  },
  { deep: true }
)

// 監聽控制項變化
watch(
  () => props.controls,
  async () => {
    await nextTick()
    await updateChart()
  },
  { deep: true }
)

// 監聽窗口大小變化
const handleResize = () => {
  resizeChart()
}

// 生命週期
onMounted(async () => {
  await nextTick()
  await renderChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (plotlyInstance) {
    (Plotly as any).purge(plotlyInstance)
    plotlyInstance = null
  }
  window.removeEventListener('resize', handleResize)
})

// 公開方法
defineExpose({
  resizeChart,
  updateChart,
  renderChart
})
</script>

<style scoped>
.plotly-chart-container {
  position: relative;
  width: 100%;
}

.plotly-chart {
  width: 100%;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: var(--el-text-color-regular);
}

.chart-loading .el-icon {
  font-size: 24px;
}

.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: var(--el-color-danger);
}

.chart-error .el-icon {
  font-size: 24px;
}

/* Plotly 自定義樣式 */
:deep(.plotly) {
  width: 100% !important;
  height: 100% !important;
}

:deep(.modebar) {
  top: 8px !important;
  right: 8px !important;
}

:deep(.modebar-btn) {
  color: var(--el-text-color-regular) !important;
}

:deep(.modebar-btn:hover) {
  background: var(--el-color-primary-light-8) !important;
  color: var(--el-color-primary) !important;
}

:deep(.modebar-btn.active) {
  background: var(--el-color-primary) !important;
  color: white !important;
}
</style>