<template>
  <div class="data-visualization">
    <!-- 頁面標題 -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">數據視覺化</h1>
          <p class="page-description">交互式數據分析和圖表展示</p>
        </div>
        <div class="header-actions">
          <el-button
            type="primary"
            :icon="Plus"
            @click="showCreateChartDialog = true"
          >
            新建圖表
          </el-button>
          <el-button
            :icon="Refresh"
            :loading="isRefreshing"
            @click="refreshAllData"
          >
            刷新數據
          </el-button>
        </div>
      </div>
    </div>

    <!-- 工具欄 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="selectedDataSource"
          placeholder="選擇數據源"
          style="width: 200px"
          @change="handleDataSourceChange"
        >
          <el-option
            v-for="source in dataSources"
            :key="source.id"
            :label="source.name"
            :value="source.id"
          />
        </el-select>
        
        <el-select
          v-model="viewMode"
          style="width: 150px; margin-left: 12px"
        >
          <el-option label="網格視圖" value="grid" />
          <el-option label="全屏視圖" value="fullscreen" />
          <el-option label="表格視圖" value="table" />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-button-group>
          <el-button
            :type="chartControls.showGrid ? 'primary' : 'default'"
            :icon="Grid"
            @click="chartControls.showGrid = !chartControls.showGrid"
          />
          <el-button
            :type="chartControls.showLegend ? 'primary' : 'default'"
            :icon="Menu"
            @click="chartControls.showLegend = !chartControls.showLegend"
          />
          <el-button
            :type="chartControls.animation ? 'primary' : 'default'"
            :icon="VideoPlay"
            @click="chartControls.animation = !chartControls.animation"
          />
        </el-button-group>
        
        <el-dropdown @command="handleExport">
          <el-button :icon="Download">
            導出<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="png">PNG 圖片</el-dropdown-item>
              <el-dropdown-item command="svg">SVG 向量圖</el-dropdown-item>
              <el-dropdown-item command="pdf">PDF 文件</el-dropdown-item>
              <el-dropdown-item command="html">HTML 報告</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="visualization-content" :class="viewMode">
      <!-- 網格視圖 -->
      <div v-if="viewMode === 'grid'" class="charts-grid">
        <div
          v-for="chart in visibleCharts"
          :key="chart.id"
          class="chart-item"
          :class="{ 'active': activeChartId === chart.id }"
        >
          <el-card
            class="chart-card"
            shadow="hover"
            @click="setActiveChart(chart.id)"
          >
            <template #header>
              <div class="chart-header">
                <span class="chart-title">{{ chart.title }}</span>
                <div class="chart-actions">
                  <el-button
                    type="text"
                    :icon="Edit"
                    @click.stop="editChart(chart)"
                  />
                  <el-button
                    type="text"
                    :icon="FullScreen"
                    @click.stop="openFullscreen(chart)"
                  />
                  <el-dropdown @command="(cmd) => handleChartAction(cmd, chart)">
                    <el-button type="text" :icon="MoreFilled" />
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="duplicate">複製</el-dropdown-item>
                        <el-dropdown-item command="export">導出</el-dropdown-item>
                        <el-dropdown-item command="delete" class="danger">刪除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </template>
            
            <div class="chart-container">
              <div v-if="isChartLoading(chart.id)" class="chart-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>載入中...</span>
              </div>
              <PlotlyChart
                v-else
                :chart-data="chart"
                :controls="chartControls"
                :height="300"
                @data-click="handleDataClick"
                @error="(error: any) => handleChartError(error, chart.id)"
              />
            </div>
          </el-card>
        </div>
        
        <!-- 空狀態 -->
        <div v-if="visibleCharts.length === 0" class="empty-state">
          <el-empty
            :image-size="120"
            description="尚無圖表數據"
          >
            <el-button type="primary" @click="showCreateChartDialog = true">
              創建第一個圖表
            </el-button>
          </el-empty>
        </div>
      </div>

      <!-- 全屏視圖 -->
      <div v-else-if="viewMode === 'fullscreen'" class="fullscreen-view">
        <div v-if="activeChart" class="fullscreen-chart">
          <div class="fullscreen-header">
            <h2>{{ activeChart.title }}</h2>
            <div class="fullscreen-controls">
              <el-button-group>
                <el-button
                  v-for="chart in charts"
                  :key="chart.id"
                  :type="chart.id === activeChartId ? 'primary' : 'default'"
                  @click="setActiveChart(chart.id)"
                >
                  {{ chart.title }}
                </el-button>
              </el-button-group>
            </div>
          </div>
          <PlotlyChart
            :chart-data="activeChart"
            :controls="chartControls"
            :height="600"
            @data-click="handleDataClick"
          />
        </div>
        <el-empty v-else description="請選擇一個圖表" />
      </div>

      <!-- 表格視圖 -->
      <div v-else-if="viewMode === 'table'" class="table-view">
        <DataTable
          :data="currentDataset?.data || []"
          :schema="currentDataset?.schema"
          :loading="isLoadingData"
          @row-select="handleRowSelect"
          @filter-change="handleTableFilter"
        />
      </div>
    </div>

    <!-- 創建圖表對話框 -->
    <CreateChartDialog
      v-model="showCreateChartDialog"
      :data-sources="dataSources"
      @create="handleCreateChart"
    />

    <!-- 編輯圖表對話框 -->
    <EditChartDialog
      v-model="showEditChartDialog"
      :chart="editingChart"
      @save="handleSaveChart"
    />

    <!-- 全屏圖表對話框 -->
    <el-dialog
      v-model="showFullscreenDialog"
      :title="fullscreenChart?.title"
      fullscreen
      destroy-on-close
    >
      <PlotlyChart
        v-if="fullscreenChart"
        :chart-data="fullscreenChart"
        :controls="chartControls"
        :height="800"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Edit,
  FullScreen,
  Download,
  Grid,
  Menu,
  VideoPlay,
  Loading,
  MoreFilled,
  ArrowDown
} from '@element-plus/icons-vue'
import type {
  ChartData,
  ChartControls,
  Dataset,
  ExportOptions
} from '@/types/visualization'
import { ChartType } from '@/types/visualization'
import PlotlyChart from '@/components/charts/PlotlyChart.vue'
import DataTable from '@/components/charts/DataTable.vue'
import CreateChartDialog from '@/components/charts/CreateChartDialog.vue'
import EditChartDialog from '@/components/charts/EditChartDialog.vue'

// Stores
const appStore = useAppStore()
// const router = useRouter()

// 響應式狀態
const isRefreshing = ref(false)
const isLoadingData = ref(false)
const viewMode = ref<'grid' | 'fullscreen' | 'table'>('grid')
const selectedDataSource = ref('')
const activeChartId = ref<string>()
const showCreateChartDialog = ref(false)
const showEditChartDialog = ref(false)
const showFullscreenDialog = ref(false)
const editingChart = ref<ChartData>()
const fullscreenChart = ref<ChartData>()

// 圖表控制
const chartControls = ref<ChartControls>({
  showLegend: true,
  showGrid: true,
  showToolbar: true,
  theme: appStore.theme,
  animation: true
})

// 數據狀態
const charts = ref<ChartData[]>([])
const dataSources = ref([
  { id: 'agents', name: '代理數據' },
  { id: 'performance', name: '性能指標' },
  { id: 'analysis', name: '分析結果' },
  { id: 'sample', name: '示例數據' }
])
const datasets = ref<Record<string, Dataset>>({})
const loadingCharts = ref<Set<string>>(new Set())

// 計算屬性
const visibleCharts = computed(() => {
  if (!selectedDataSource.value) return charts.value
  return charts.value.filter(chart => 
    chart.metadata?.source === selectedDataSource.value
  )
})

const activeChart = computed(() => {
  if (!activeChartId.value) return null
  return charts.value.find(chart => chart.id === activeChartId.value) || null
})

const currentDataset = computed(() => {
  if (!selectedDataSource.value) return null
  return datasets.value[selectedDataSource.value] || null
})

// 監聽主題變化
watch(() => appStore.theme, (newTheme) => {
  chartControls.value.theme = newTheme
})

// 圖表管理方法
const setActiveChart = (chartId: string) => {
  activeChartId.value = chartId
}

const isChartLoading = (chartId: string) => {
  return loadingCharts.value.has(chartId)
}

const editChart = (chart: ChartData) => {
  editingChart.value = { ...chart }
  showEditChartDialog.value = true
}

const openFullscreen = (chart: ChartData) => {
  fullscreenChart.value = chart
  showFullscreenDialog.value = true
}

const handleChartAction = async (command: string, chart: ChartData) => {
  switch (command) {
    case 'duplicate':
      await duplicateChart(chart)
      break
    case 'export':
      await exportChart(chart)
      break
    case 'delete':
      await deleteChart(chart.id)
      break
  }
}

// 數據操作方法
const handleDataSourceChange = async () => {
  isLoadingData.value = true
  try {
    await loadDatasetForSource(selectedDataSource.value)
    await loadChartsForSource(selectedDataSource.value)
  } finally {
    isLoadingData.value = false
  }
}

const refreshAllData = async () => {
  isRefreshing.value = true
  try {
    await Promise.all([
      loadAllDatasets(),
      loadAllCharts()
    ])
    appStore.addNotification({
      type: 'success',
      title: '刷新成功',
      message: '所有數據已更新'
    })
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '刷新失敗',
      message: error instanceof Error ? error.message : '未知錯誤'
    })
  } finally {
    isRefreshing.value = false
  }
}

// 圖表 CRUD 操作
const handleCreateChart = async (chartConfig: Partial<ChartData>) => {
  const newChart: ChartData = {
    id: `chart_${Date.now()}`,
    title: chartConfig.title || '新圖表',
    type: chartConfig.type || ChartType.LINE,
    data: chartConfig.data || [],
    layout: chartConfig.layout || {},
    config: chartConfig.config || {},
    metadata: {
      source: selectedDataSource.value,
      description: chartConfig.metadata?.description || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      tags: chartConfig.metadata?.tags || [],
      author: appStore.user?.username || 'Anonymous'
    }
  }

  charts.value.push(newChart)
  setActiveChart(newChart.id)
  showCreateChartDialog.value = false

  appStore.addNotification({
    type: 'success',
    title: '圖表創建成功',
    message: `圖表 "${newChart.title}" 已創建`
  })
}

const handleSaveChart = (updatedChart: ChartData) => {
  const index = charts.value.findIndex(c => c.id === updatedChart.id)
  if (index > -1) {
    updatedChart.metadata!.updatedAt = new Date().toISOString()
    charts.value[index] = updatedChart
    showEditChartDialog.value = false
    
    appStore.addNotification({
      type: 'success',
      title: '圖表保存成功',
      message: `圖表 "${updatedChart.title}" 已更新`
    })
  }
}

const duplicateChart = async (chart: ChartData) => {
  const duplicatedChart: ChartData = {
    ...chart,
    id: `chart_${Date.now()}`,
    title: `${chart.title} (副本)`,
    metadata: {
      ...chart.metadata!,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
  }
  
  charts.value.push(duplicatedChart)
  
  appStore.addNotification({
    type: 'success',
    title: '圖表複製成功',
    message: `已創建 "${duplicatedChart.title}"`
  })
}

const deleteChart = async (chartId: string) => {
  const chart = charts.value.find(c => c.id === chartId)
  if (!chart) return

  try {
    await ElMessageBox.confirm(
      `確定要刪除圖表 "${chart.title}" 嗎？此操作不可撤銷。`,
      '確認刪除',
      {
        confirmButtonText: '刪除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    charts.value = charts.value.filter(c => c.id !== chartId)
    
    if (activeChartId.value === chartId) {
      activeChartId.value = charts.value[0]?.id
    }

    appStore.addNotification({
      type: 'success',
      title: '圖表刪除成功',
      message: `圖表 "${chart.title}" 已刪除`
    })
  } catch {
    // 用戶取消刪除
  }
}

// 導出功能
const handleExport = async (format: string) => {
  const options: ExportOptions = {
    format: format as any,
    width: 1200,
    height: 800,
    scale: 2
  }

  try {
    if (viewMode.value === 'fullscreen' && activeChart.value) {
      await exportChart(activeChart.value, options)
    } else {
      await exportAllCharts(options)
    }
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '導出失敗',
      message: error instanceof Error ? error.message : '未知錯誤'
    })
  }
}

const exportChart = async (chart: ChartData, _options?: ExportOptions) => {
  // 實現單個圖表導出邏輯
  appStore.addNotification({
    type: 'info',
    title: '導出中',
    message: `正在導出圖表 "${chart.title}"`
  })
}

const exportAllCharts = async (_options: ExportOptions) => {
  // 實現所有圖表導出邏輯
  appStore.addNotification({
    type: 'info',
    title: '導出中',
    message: '正在導出所有圖表'
  })
}

// 事件處理
const handleDataClick = (data: any) => {
  console.log('數據點被點擊:', data)
  // 可以在這裡實現數據鑽取或詳細視圖
}

const handleChartError = (error: Error, chartId: string) => {
  console.error(`圖表 ${chartId} 載入錯誤:`, error)
  loadingCharts.value.delete(chartId)
  
  appStore.addNotification({
    type: 'error',
    title: '圖表載入失敗',
    message: error.message
  })
}

const handleRowSelect = (rows: any[]) => {
  console.log('選中的行:', rows)
  // 可以基於選中的行創建圖表
}

const handleTableFilter = (filters: any) => {
  console.log('表格篩選:', filters)
  // 實現表格數據篩選
}

// 數據載入方法
const loadDatasetForSource = async (sourceId: string) => {
  if (!sourceId || datasets.value[sourceId]) return

  // 模擬 API 請求
  const mockDataset: Dataset = {
    id: sourceId,
    name: dataSources.value.find(s => s.id === sourceId)?.name || sourceId,
    data: generateMockData(sourceId),
    schema: {
      fields: [
        { name: 'timestamp', type: 'date', description: '時間戳' },
        { name: 'value', type: 'number', description: '數值' },
        { name: 'category', type: 'string', description: '類別' },
        { name: 'status', type: 'string', description: '狀態' }
      ]
    }
  }

  datasets.value[sourceId] = mockDataset
}

const loadChartsForSource = async (sourceId: string) => {
  if (!sourceId) return

  loadingCharts.value.add('loading')

  try {
    // 生成示例圖表
    const sampleCharts = generateSampleCharts(sourceId)
    
    // 移除現有的該數據源圖表
    charts.value = charts.value.filter(c => c.metadata?.source !== sourceId)
    
    // 添加新圖表
    charts.value.push(...sampleCharts)
    
    // 設置第一個圖表為活動圖表
    if (sampleCharts.length > 0 && !activeChartId.value) {
      setActiveChart(sampleCharts[0].id)
    }
  } finally {
    loadingCharts.value.delete('loading')
  }
}

const loadAllDatasets = async () => {
  await Promise.all(
    dataSources.value.map(source => loadDatasetForSource(source.id))
  )
}

const loadAllCharts = async () => {
  if (selectedDataSource.value) {
    await loadChartsForSource(selectedDataSource.value)
  }
}

// 模擬數據生成
const generateMockData = (sourceId: string) => {
  const dataCount = 50
  const data: Record<string, any>[] = []
  
  for (let i = 0; i < dataCount; i++) {
    const timestamp = new Date(Date.now() - (dataCount - i) * 60000)
    
    switch (sourceId) {
      case 'agents':
        data.push({
          timestamp,
          agent_id: `agent_${(i % 5) + 1}`,
          cpu_usage: 20 + Math.random() * 60,
          memory_usage: 30 + Math.random() * 50,
          tasks_completed: Math.floor(Math.random() * 10),
          status: ['active', 'idle', 'busy'][Math.floor(Math.random() * 3)]
        })
        break
      case 'performance':
        data.push({
          timestamp,
          metric: ['cpu', 'memory', 'disk', 'network'][i % 4],
          value: Math.random() * 100,
          threshold: 80,
          status: Math.random() > 0.2 ? 'normal' : 'warning'
        })
        break
      case 'analysis':
        data.push({
          timestamp,
          analysis_type: ['sentiment', 'classification', 'clustering'][i % 3],
          accuracy: 0.7 + Math.random() * 0.3,
          samples: Math.floor(Math.random() * 1000),
          category: `category_${(i % 3) + 1}`
        })
        break
      default:
        data.push({
          timestamp,
          value: Math.random() * 100,
          category: `Category ${(i % 3) + 1}`,
          status: Math.random() > 0.5 ? 'success' : 'pending'
        })
    }
  }
  
  return data
}

const generateSampleCharts = (sourceId: string): ChartData[] => {
  const baseTime = new Date().toISOString()
  
  switch (sourceId) {
    case 'agents':
      return [
        {
          id: `${sourceId}_cpu_usage`,
          title: '代理 CPU 使用率',
          type: ChartType.LINE,
          data: [{
            x: Array.from({length: 20}, (_, i) => new Date(Date.now() - (20-i) * 60000)),
            y: Array.from({length: 20}, () => 20 + Math.random() * 60),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'CPU 使用率',
            line: { color: '#409eff' }
          }],
          layout: {
            title: '代理 CPU 使用率趨勢',
            xaxis: { title: '時間' },
            yaxis: { title: 'CPU 使用率 (%)' }
          },
          metadata: {
            source: sourceId,
            description: '顯示代理的 CPU 使用率變化',
            createdAt: baseTime,
            updatedAt: baseTime,
            tags: ['性能', 'CPU', '代理']
          }
        },
        {
          id: `${sourceId}_task_distribution`,
          title: '任務分布',
          type: ChartType.PIE,
          data: [{
            values: [30, 25, 20, 15, 10],
            labels: ['數據分析', '報告生成', '質量檢查', '搜索查詢', '其他'],
            type: 'pie',
            marker: {
              colors: ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
            }
          }],
          layout: {
            title: '代理任務類型分布'
          },
          metadata: {
            source: sourceId,
            description: '顯示不同類型任務的分布情況',
            createdAt: baseTime,
            updatedAt: baseTime,
            tags: ['任務', '分布', '代理']
          }
        }
      ]
    
    case 'performance':
      return [
        {
          id: `${sourceId}_system_metrics`,
          title: '系統性能指標',
          type: ChartType.BAR,
          data: [{
            x: ['CPU', '記憶體', '磁碟', '網路'],
            y: [45, 62, 38, 71],
            type: 'bar',
            marker: { color: '#67c23a' }
          }],
          layout: {
            title: '當前系統性能概覽',
            xaxis: { title: '指標類型' },
            yaxis: { title: '使用率 (%)' }
          },
          metadata: {
            source: sourceId,
            description: '系統各項性能指標的當前狀態',
            createdAt: baseTime,
            updatedAt: baseTime,
            tags: ['性能', '系統', '監控']
          }
        }
      ]
    
    case 'analysis':
      return [
        {
          id: `${sourceId}_accuracy_trend`,
          title: '分析準確率趨勢',
          type: ChartType.SCATTER,
          data: [{
            x: Array.from({length: 15}, (_, i) => i + 1),
            y: Array.from({length: 15}, () => 0.7 + Math.random() * 0.3),
            mode: 'markers',
            type: 'scatter',
            marker: {
              size: Array.from({length: 15}, () => 5 + Math.random() * 15),
              color: Array.from({length: 15}, () => Math.random() * 100),
              colorscale: 'Viridis'
            }
          }],
          layout: {
            title: '分析模型準確率散點圖',
            xaxis: { title: '模型版本' },
            yaxis: { title: '準確率' }
          },
          metadata: {
            source: sourceId,
            description: '不同版本模型的準確率比較',
            createdAt: baseTime,
            updatedAt: baseTime,
            tags: ['分析', '準確率', '模型']
          }
        }
      ]
    
    default:
      return [
        {
          id: `${sourceId}_sample_chart`,
          title: '示例數據圖表',
          type: ChartType.LINE,
          data: [{
            x: Array.from({length: 10}, (_, i) => i + 1),
            y: Array.from({length: 10}, () => Math.random() * 100),
            type: 'scatter',
            mode: 'lines+markers'
          }],
          layout: {
            title: '示例數據趨勢'
          },
          metadata: {
            source: sourceId,
            description: '示例數據圖表',
            createdAt: baseTime,
            updatedAt: baseTime,
            tags: ['示例']
          }
        }
      ]
  }
}

// 生命週期
onMounted(async () => {
  // 設置默認數據源
  selectedDataSource.value = dataSources.value[0]?.id || ''
  
  // 載入初始數據
  if (selectedDataSource.value) {
    await handleDataSourceChange()
  }
  
  // 監聽窗口大小變化
  window.addEventListener('resize', () => {
    // 觸發圖表重新渲染
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {})
})
</script>

<style scoped>
.data-visualization {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  margin-bottom: 24px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.visualization-content {
  flex: 1;
  overflow: hidden;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  height: 100%;
  overflow-y: auto;
}

.chart-item {
  min-height: 400px;
}

.chart-item.active .chart-card {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.12);
}

.chart-card {
  height: 100%;
  cursor: pointer;
  transition: all 0.3s;
}

.chart-card:hover {
  transform: translateY(-2px);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.chart-actions {
  display: flex;
  gap: 4px;
}

.chart-container {
  height: 300px;
  position: relative;
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

.fullscreen-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.fullscreen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.fullscreen-chart {
  flex: 1;
}

.table-view {
  height: 100%;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.danger {
  color: var(--el-color-danger);
}

/* 響應式設計 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 16px;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .chart-item {
    min-height: 350px;
  }
  
  .chart-container {
    height: 250px;
  }
}

@media (max-width: 480px) {
  .header-actions {
    width: 100%;
    justify-content: center;
  }
  
  .chart-actions {
    flex-wrap: wrap;
  }
}
</style>