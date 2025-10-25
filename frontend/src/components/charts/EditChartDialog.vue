<template>
  <el-dialog
    v-model="visible"
    title="編輯圖表"
    width="600px"
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
      <el-form-item label="圖表標題" prop="title">
        <el-input v-model="form.title" placeholder="請輸入圖表標題" />
      </el-form-item>

      <el-form-item label="圖表描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="請輸入圖表描述（可選）"
        />
      </el-form-item>

      <!-- 圖表設置 -->
      <el-divider content-position="left">顯示設置</el-divider>
      
      <el-row :gutter="20">
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
        <el-col :span="8">
          <el-form-item>
            <template #label>
              <span>顯示工具欄</span>
            </template>
            <el-switch v-model="form.showToolbar" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 顏色設置 -->
      <el-form-item label="顏色主題">
        <el-select v-model="form.colorScheme" style="width: 200px">
          <el-option label="默認色彩" value="default" />
          <el-option label="藍色系" value="blues" />
          <el-option label="綠色系" value="greens" />
          <el-option label="暖色系" value="warm" />
          <el-option label="冷色系" value="cool" />
        </el-select>
      </el-form-item>

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

      <!-- 高級設置 -->
      <el-divider content-position="left">高級設置</el-divider>
      
      <el-form-item label="動畫效果">
        <el-switch v-model="form.animation" />
      </el-form-item>

      <el-form-item label="響應式">
        <el-switch v-model="form.responsive" />
      </el-form-item>

      <!-- 圖表預覽 -->
      <el-divider content-position="left">預覽</el-divider>
      
      <div class="chart-preview">
        <div v-if="previewChart" class="preview-container">
          <PlotlyChart
            :chart-data="previewChart"
            :height="300"
          />
        </div>
        <el-empty v-else description="沒有圖表數據" :image-size="100" />
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="isSaving">
          保存更改
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { FormInstance } from 'element-plus'
import type { ChartData } from '@/types/visualization'
import PlotlyChart from './PlotlyChart.vue'

interface Props {
  modelValue: boolean
  chart?: ChartData | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', chart: ChartData): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 響應式狀態
const formRef = ref<FormInstance>()
const inputRef = ref()
const isSaving = ref(false)
const inputVisible = ref(false)
const inputValue = ref('')

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表單數據
const form = ref({
  title: '',
  description: '',
  showLegend: true,
  showGrid: true,
  showToolbar: true,
  colorScheme: 'default',
  animation: true,
  responsive: true,
  tags: [] as string[]
})

// 表單驗證規則
const rules = {
  title: [
    { required: true, message: '請輸入圖表標題', trigger: 'blur' }
  ]
}

// 預覽圖表
const previewChart = computed((): ChartData | null => {
  if (!props.chart) return null

  return {
    ...props.chart,
    title: form.value.title || props.chart.title,
    layout: {
      ...props.chart.layout,
      title: form.value.title || props.chart.title,
      showlegend: form.value.showLegend,
      xaxis: {
        ...props.chart.layout?.xaxis,
        showgrid: form.value.showGrid
      },
      yaxis: {
        ...props.chart.layout?.yaxis,
        showgrid: form.value.showGrid
      }
    },
    config: {
      ...props.chart.config,
      displayModeBar: form.value.showToolbar,
      responsive: form.value.responsive
    },
    metadata: {
      ...props.chart.metadata!,
      description: form.value.description,
      tags: form.value.tags
    }
  }
})

// 監聽圖表變化，更新表單
watch(() => props.chart, (newChart) => {
  if (newChart) {
    form.value = {
      title: newChart.title,
      description: newChart.metadata?.description || '',
      showLegend: newChart.layout?.showlegend ?? true,
      showGrid: newChart.layout?.xaxis?.showgrid ?? true,
      showToolbar: newChart.config?.displayModeBar ?? true,
      colorScheme: 'default', // 這裡可以根據實際顏色推斷
      animation: true,
      responsive: newChart.config?.responsive ?? true,
      tags: newChart.metadata?.tags || []
    }
  }
}, { immediate: true })

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
    description: '',
    showLegend: true,
    showGrid: true,
    showToolbar: true,
    colorScheme: 'default',
    animation: true,
    responsive: true,
    tags: []
  }
  formRef.value?.resetFields()
}

// 事件處理
const handleClose = () => {
  resetForm()
  visible.value = false
}

const handleSave = async () => {
  if (!formRef.value || !props.chart) return
  
  try {
    await formRef.value.validate()
    
    isSaving.value = true
    
    // 創建更新後的圖表數據
    const updatedChart: ChartData = {
      ...props.chart,
      title: form.value.title,
      layout: {
        ...props.chart.layout,
        title: form.value.title,
        showlegend: form.value.showLegend,
        xaxis: {
          ...props.chart.layout?.xaxis,
          showgrid: form.value.showGrid
        },
        yaxis: {
          ...props.chart.layout?.yaxis,
          showgrid: form.value.showGrid
        }
      },
      config: {
        ...props.chart.config,
        displayModeBar: form.value.showToolbar,
        responsive: form.value.responsive
      },
      metadata: {
        ...props.chart.metadata!,
        description: form.value.description,
        tags: form.value.tags,
        updatedAt: new Date().toISOString()
      }
    }
    
    emit('save', updatedChart)
    handleClose()
  } catch (error) {
    console.error('表單驗證失敗:', error)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
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