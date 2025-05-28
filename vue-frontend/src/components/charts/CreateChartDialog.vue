<template>
  <el-dialog
    v-model="visible"
    title="創建新圖表"
    width="800px"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      @submit.prevent
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="圖表標題" prop="title">
            <el-input v-model="form.title" placeholder="請輸入圖表標題" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="圖表類型" prop="type">
            <el-select v-model="form.type" placeholder="選擇圖表類型" style="width: 100%">
              <el-option
                v-for="type in chartTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              >
                <div class="chart-type-option">
                  <el-icon><component :is="type.icon" /></el-icon>
                  <span>{{ type.label }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="數據源" prop="dataSource">
            <el-select v-model="form.dataSource" placeholder="選擇數據源" style="width: 100%">
              <el-option
                v-for="source in dataSources"
                :key="source.id"
                :label="source.name"
                :value="source.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="圖表描述">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="2"
              placeholder="請輸入圖表描述（可選）"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 數據配置 -->
      <el-divider content-position="left">數據配置</el-divider>
      
      <el-form-item label="X軸欄位" prop="xField">
        <el-select v-model="form.xField" placeholder="選擇X軸數據欄位" style="width: 100%">
          <el-option
            v-for="field in availableFields"
            :key="field.name"
            :label="field.description || field.name"
            :value="field.name"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="Y軸欄位" prop="yField">
        <el-select
          v-model="form.yFields"
          multiple
          placeholder="選擇Y軸數據欄位"
          style="width: 100%"
        >
          <el-option
            v-for="field in numericFields"
            :key="field.name"
            :label="field.description || field.name"
            :value="field.name"
          />
        </el-select>
      </el-form-item>

      <!-- 圖表設置 -->
      <el-divider content-position="left">圖表設置</el-divider>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="顏色主題">
            <el-select v-model="form.colorScheme" style="width: 100%">
              <el-option label="默認色彩" value="default" />
              <el-option label="藍色系" value="blues" />
              <el-option label="綠色系" value="greens" />
              <el-option label="暖色系" value="warm" />
              <el-option label="冷色系" value="cool" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              <span>顯示圖例</span>
            </template>
            <el-switch v-model="form.showLegend" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              <span>顯示網格</span>
            </template>
            <el-switch v-model="form.showGrid" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 預覽區域 -->
      <el-divider content-position="left">圖表預覽</el-divider>
      
      <div class="chart-preview">
        <div v-if="previewData" class="preview-container">
          <PlotlyChart
            :chart-data="previewChart"
            :height="300"
          />
        </div>
        <el-empty v-else description="請完成配置以預覽圖表" :image-size="100" />
      </div>

      <!-- 標籤設置 -->
      <el-divider content-position="left">標籤設置</el-divider>
      
      <el-form-item label="標籤">
        <el-tag
          v-for="tag in form.tags"
          :key="tag"
          closable
          type="info"
          @close="removeTag(tag)"
          style="margin-right: 8px; margin-bottom: 8px;"
        >
          {{ tag }}
        </el-tag>
        <el-input
          v-if="inputVisible"
          ref="inputRef"
          v-model="inputValue"
          size="small"
          style="width: 100px"
          @keyup.enter="handleInputConfirm"
          @blur="handleInputConfirm"
        />
        <el-button v-else size="small" @click="showInput">
          + 添加標籤
        </el-button>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="isCreating">
          創建圖表
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  TrendCharts,
  Histogram,
  PieChart,
  ScaleToOriginal,
  Grid
} from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { ChartType } from '@/types/visualization'
import type { ChartData } from '@/types/visualization'
import PlotlyChart from './PlotlyChart.vue'

interface Props {
  modelValue: boolean
  dataSources: Array<{ id: string; name: string }>
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'create', chart: Partial<ChartData>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 響應式狀態
const formRef = ref<FormInstance>()
const inputRef = ref()
const isCreating = ref(false)
const inputVisible = ref(false)
const inputValue = ref('')

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表單數據
const form = ref({
  title: '',
  type: ChartType.LINE,
  dataSource: '',
  description: '',
  xField: '',
  yFields: [] as string[],
  colorScheme: 'default',
  showLegend: true,
  showGrid: true,
  tags: [] as string[]
})

// 圖表類型選項
const chartTypes = [
  { value: ChartType.LINE, label: '線圖', icon: TrendCharts },
  { value: ChartType.BAR, label: '柱狀圖', icon: Histogram },
  { value: ChartType.PIE, label: '餅圖', icon: PieChart },
  { value: ChartType.SCATTER, label: '散點圖', icon: ScaleToOriginal },
  { value: ChartType.HEATMAP, label: '熱力圖', icon: Grid },
  { value: ChartType.HISTOGRAM, label: '直方圖', icon: Histogram }
]

// 表單驗證規則
const rules = {
  title: [
    { required: true, message: '請輸入圖表標題', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '請選擇圖表類型', trigger: 'change' }
  ],
  dataSource: [
    { required: true, message: '請選擇數據源', trigger: 'change' }
  ],
  xField: [
    { required: true, message: '請選擇X軸欄位', trigger: 'change' }
  ],
  yFields: [
    {
      required: true,
      message: '請至少選擇一個Y軸欄位',
      trigger: 'change',
      validator: (_rule: any, value: string[], callback: any) => {
        if (!value || value.length === 0) {
          callback(new Error('請至少選擇一個Y軸欄位'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 模擬的欄位數據
const availableFields = computed(() => {
  // 根據選擇的數據源返回可用欄位
  if (!form.value.dataSource) return []
  
  return [
    { name: 'timestamp', type: 'date', description: '時間戳' },
    { name: 'category', type: 'string', description: '類別' },
    { name: 'status', type: 'string', description: '狀態' },
    { name: 'value', type: 'number', description: '數值' },
    { name: 'count', type: 'number', description: '計數' },
    { name: 'percentage', type: 'number', description: '百分比' }
  ]
})

const numericFields = computed(() => {
  return availableFields.value.filter(field => field.type === 'number')
})

// 預覽數據
const previewData = computed(() => {
  return form.value.xField && form.value.yFields.length > 0
})

const previewChart = computed((): ChartData => {
  // 生成預覽圖表數據
  const mockData = generateMockData()
  
  return {
    id: 'preview',
    title: form.value.title || '預覽圖表',
    type: form.value.type,
    data: mockData,
    layout: {
      title: form.value.title || '預覽圖表',
      showlegend: form.value.showLegend,
      xaxis: { 
        title: form.value.xField,
        showgrid: form.value.showGrid
      },
      yaxis: { 
        title: form.value.yFields.join(', '),
        showgrid: form.value.showGrid
      }
    },
    metadata: {
      source: form.value.dataSource,
      description: form.value.description,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      tags: form.value.tags
    }
  }
})

// 生成模擬數據
const generateMockData = () => {
  const dataCount = 10
  const colors = getColorScheme(form.value.colorScheme)
  
  switch (form.value.type) {
    case ChartType.LINE:
    case ChartType.SCATTER:
      return form.value.yFields.map((field, index) => ({
        x: Array.from({length: dataCount}, (_, i) => i + 1),
        y: Array.from({length: dataCount}, () => Math.random() * 100),
        type: form.value.type === ChartType.LINE ? 'scatter' : 'scatter',
        mode: form.value.type === ChartType.LINE ? 'lines+markers' : 'markers',
        name: field,
        marker: { color: colors[index % colors.length] }
      }))
    
    case ChartType.BAR:
      return [{
        x: form.value.yFields,
        y: form.value.yFields.map(() => Math.random() * 100),
        type: 'bar',
        marker: { color: colors }
      }]
    
    case ChartType.PIE:
      return [{
        values: form.value.yFields.map(() => Math.random() * 100),
        labels: form.value.yFields,
        type: 'pie',
        marker: { colors: colors }
      }]
    
    default:
      return [{
        x: Array.from({length: dataCount}, (_, i) => i + 1),
        y: Array.from({length: dataCount}, () => Math.random() * 100),
        type: 'scatter',
        mode: 'lines+markers'
      }]
  }
}

// 獲取顏色方案
const getColorScheme = (scheme: string) => {
  const schemes: Record<string, string[]> = {
    default: ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399'],
    blues: ['#1f77b4', '#aec7e8', '#1b7fc7', '#5194c7', '#6baed6'],
    greens: ['#2ca02c', '#98df8a', '#2fb92f', '#5cb85c', '#7dcb7d'],
    warm: ['#ff7f0e', '#ffbb78', '#d62728', '#ff9896', '#ff7f0e'],
    cool: ['#17becf', '#9edae5', '#1f77b4', '#aec7e8', '#c5b0d5']
  }
  
  return schemes[scheme] || schemes.default
}

// 標籤管理
const removeTag = (tag: string) => {
  const index = form.value.tags.indexOf(tag)
  if (index > -1) {
    form.value.tags.splice(index, 1)
  }
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const handleInputConfirm = () => {
  const value = inputValue.value.trim()
  if (value && !form.value.tags.includes(value)) {
    form.value.tags.push(value)
  }
  inputVisible.value = false
  inputValue.value = ''
}

// 重置表單
const resetForm = () => {
  form.value = {
    title: '',
    type: ChartType.LINE,
    dataSource: '',
    description: '',
    xField: '',
    yFields: [],
    colorScheme: 'default',
    showLegend: true,
    showGrid: true,
    tags: []
  }
  formRef.value?.resetFields()
}

// 事件處理
const handleClose = () => {
  resetForm()
  visible.value = false
}

const handleCreate = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    isCreating.value = true
    
    const chartData = {
      title: form.value.title,
      type: form.value.type,
      data: generateMockData(),
      layout: {
        title: form.value.title,
        showlegend: form.value.showLegend,
        xaxis: {
          title: form.value.xField,
          showgrid: form.value.showGrid
        },
        yaxis: {
          title: form.value.yFields.join(', '),
          showgrid: form.value.showGrid
        }
      },
      config: {
        displayModeBar: true,
        responsive: true
      },
      metadata: {
        source: form.value.dataSource,
        description: form.value.description,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        tags: form.value.tags
      }
    }
    
    emit('create', chartData)
    handleClose()
  } catch (error) {
    console.error('表單驗證失敗:', error)
  } finally {
    isCreating.value = false
  }
}

// 監聽數據源變化，清除欄位選擇
watch(() => form.value.dataSource, () => {
  form.value.xField = ''
  form.value.yFields = []
})
</script>

<style scoped>
.chart-type-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-preview {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  background: var(--el-bg-color-page);
}

.preview-container {
  height: 300px;
}

.dialog-footer {
  text-align: right;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .el-dialog {
    width: 95% !important;
    margin: 0 auto;
  }
}
</style>