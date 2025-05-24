<template>
  <div class="connection-test">
    <div class="test-header">
      <div class="test-info">
        <h4 class="test-title">連接測試</h4>
        <p class="test-description">測試與後端服務的連接狀態</p>
      </div>
      <el-button
        type="primary"
        :loading="testing"
        :disabled="!canTest || disabled"
        @click="runTest"
        class="test-button"
      >
        <el-icon class="mr-1">
          <Connection />
        </el-icon>
        {{ testing ? $t('settings.api.connectionTest.testing') : $t('settings.api.testConnection') }}
      </el-button>
    </div>
    
    <div class="test-results" v-if="lastResult">
      <div 
        :class="[
          'result-card',
          lastResult.success ? 'success' : 'error'
        ]"
      >
        <div class="result-header">
          <el-icon :size="20" class="result-icon">
            <Check v-if="lastResult.success" />
            <Close v-else />
          </el-icon>
          <div class="result-info">
            <div class="result-status">
              {{ lastResult.success ? $t('settings.api.connectionTest.success') : $t('settings.api.connectionTest.failed') }}
            </div>
            <div class="result-time">
              {{ formatTime(lastTestTime) }}
            </div>
          </div>
        </div>
        
        <div class="result-details" v-if="showDetails">
          <div class="detail-item" v-if="lastResult.status">
            <span class="detail-label">{{ $t('settings.api.connectionTest.status', { status: lastResult.status }) }}</span>
          </div>
          <div class="detail-item" v-if="lastResult.statusText">
            <span class="detail-label">{{ $t('settings.api.connectionTest.message', { message: lastResult.statusText }) }}</span>
          </div>
          <div class="detail-item" v-if="lastResult.data">
            <div class="detail-label">響應數據：</div>
            <pre class="detail-value">{{ JSON.stringify(lastResult.data, null, 2) }}</pre>
          </div>
        </div>
        
        <div class="result-actions">
          <el-button
            type="primary"
            link
            size="small"
            @click="showDetails = !showDetails"
            class="toggle-details"
          >
            {{ showDetails ? '隱藏詳情' : '顯示詳情' }}
            <el-icon class="ml-1">
              <ArrowDown v-if="!showDetails" />
              <ArrowUp v-else />
            </el-icon>
          </el-button>
          
          <el-button
            type="primary"
            link
            size="small"
            @click="copyResults"
            class="copy-results"
          >
            <el-icon class="mr-1">
              <CopyDocument />
            </el-icon>
            複製結果
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="test-history" v-if="testHistory.length > 0 && showHistory">
      <div class="history-header">
        <h5>測試歷史</h5>
        <el-button
          type="primary"
          link
          size="small"
          @click="clearHistory"
        >
          清除歷史
        </el-button>
      </div>
      
      <div class="history-list">
        <div 
          v-for="(result, index) in testHistory.slice(0, 5)"
          :key="index"
          :class="[
            'history-item',
            result.success ? 'success' : 'error'
          ]"
        >
          <el-icon :size="16" class="history-icon">
            <Check v-if="result.success" />
            <Close v-else />
          </el-icon>
          <span class="history-status">{{ result.success ? '成功' : '失敗' }}</span>
          <span class="history-time">{{ formatTime(result.timestamp) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { 
  Connection, 
  Check, 
  Close, 
  ArrowDown, 
  ArrowUp, 
  CopyDocument 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'
import { format } from 'date-fns'

interface TestResult {
  success: boolean
  status: number
  statusText: string
  data: any
  timestamp: number
}

interface Props {
  disabled?: boolean
  showHistory?: boolean
  autoTest?: boolean
}

interface Emits {
  (e: 'test-complete', result: TestResult): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  showHistory: true,
  autoTest: false
})

const emit = defineEmits<Emits>()

const { t } = useI18n()
const settingsStore = useSettingsStore()

// 狀態
const testing = ref(false)
const lastResult = ref<TestResult | null>(null)
const lastTestTime = ref<number | null>(null)
const showDetails = ref(false)
const testHistory = ref<TestResult[]>([])

// 計算屬性
const canTest = computed(() => {
  return settingsStore.settings.api.baseUrl && 
         settingsStore.settings.api.baseUrl.trim().length > 0
})

// 監聽設定變化，自動測試
watch(() => [settingsStore.settings.api.baseUrl, settingsStore.settings.api.token], () => {
  if (props.autoTest && canTest.value) {
    runTest()
  }
}, { deep: true })

// 運行連接測試
const runTest = async () => {
  if (testing.value || !canTest.value) {
    return
  }

  testing.value = true
  showDetails.value = false

  try {
    const result = await settingsStore.testConnection()
    
    const testResult: TestResult = {
      ...result,
      timestamp: Date.now()
    }
    
    lastResult.value = testResult
    lastTestTime.value = testResult.timestamp
    
    // 添加到歷史記錄
    testHistory.value.unshift(testResult)
    if (testHistory.value.length > 10) {
      testHistory.value = testHistory.value.slice(0, 10)
    }
    
    emit('test-complete', testResult)
    
    // 顯示結果消息
    if (result.success) {
      ElMessage.success(t('settings.messages.connectionSuccess'))
    } else {
      ElMessage.error(t('settings.messages.connectionFailed'))
    }
  } catch (error) {
    const errorResult: TestResult = {
      success: false,
      status: 0,
      statusText: error instanceof Error ? error.message : '連接失敗',
      data: null,
      timestamp: Date.now()
    }
    
    lastResult.value = errorResult
    lastTestTime.value = errorResult.timestamp
    testHistory.value.unshift(errorResult)
    
    emit('test-complete', errorResult)
    ElMessage.error(t('settings.messages.connectionFailed'))
  } finally {
    testing.value = false
  }
}

// 格式化時間
const formatTime = (timestamp: number | null) => {
  if (!timestamp) return ''
  return format(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss')
}

// 複製測試結果
const copyResults = async () => {
  if (!lastResult.value) return
  
  const resultText = JSON.stringify(lastResult.value, null, 2)
  
  try {
    await navigator.clipboard.writeText(resultText)
    ElMessage.success('測試結果已複製到剪貼板')
  } catch (error) {
    ElMessage.error('複製失敗')
  }
}

// 清除歷史記錄
const clearHistory = () => {
  testHistory.value = []
  ElMessage.success('測試歷史已清除')
}

// 暴露方法
defineExpose({
  runTest,
  clearHistory
})
</script>

<style scoped>
.connection-test {
  @apply space-y-4;
}

.test-header {
  @apply flex items-start justify-between gap-4;
}

.test-info {
  @apply flex-1;
}

.test-title {
  @apply text-base font-medium text-gray-900 dark:text-white mb-1;
}

.test-description {
  @apply text-sm text-gray-600 dark:text-gray-400 m-0;
}

.test-button {
  @apply flex-shrink-0;
}

.test-results {
  @apply mt-4;
}

.result-card {
  @apply rounded-lg border p-4;
}

.result-card.success {
  @apply border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20;
}

.result-card.error {
  @apply border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20;
}

.result-header {
  @apply flex items-center gap-3;
}

.result-icon {
  @apply flex-shrink-0;
}

.result-card.success .result-icon {
  @apply text-green-600 dark:text-green-400;
}

.result-card.error .result-icon {
  @apply text-red-600 dark:text-red-400;
}

.result-info {
  @apply flex-1;
}

.result-status {
  @apply font-medium;
}

.result-card.success .result-status {
  @apply text-green-800 dark:text-green-200;
}

.result-card.error .result-status {
  @apply text-red-800 dark:text-red-200;
}

.result-time {
  @apply text-sm text-gray-500 dark:text-gray-400;
}

.result-details {
  @apply mt-3 pt-3 border-t space-y-2;
}

.result-card.success .result-details {
  @apply border-green-200 dark:border-green-700;
}

.result-card.error .result-details {
  @apply border-red-200 dark:border-red-700;
}

.detail-item {
  @apply text-sm;
}

.detail-label {
  @apply font-medium;
}

.detail-value {
  @apply mt-1 p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono overflow-x-auto;
}

.result-actions {
  @apply mt-3 pt-3 border-t flex gap-2;
}

.result-card.success .result-actions {
  @apply border-green-200 dark:border-green-700;
}

.result-card.error .result-actions {
  @apply border-red-200 dark:border-red-700;
}

.toggle-details,
.copy-results {
  @apply text-xs;
}

.test-history {
  @apply mt-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg;
}

.history-header {
  @apply flex items-center justify-between mb-3;
}

.history-header h5 {
  @apply text-sm font-medium text-gray-900 dark:text-white m-0;
}

.history-list {
  @apply space-y-2;
}

.history-item {
  @apply flex items-center gap-2 text-sm;
}

.history-icon {
  @apply flex-shrink-0;
}

.history-item.success .history-icon {
  @apply text-green-500;
}

.history-item.error .history-icon {
  @apply text-red-500;
}

.history-status {
  @apply flex-1;
}

.history-time {
  @apply text-gray-500 dark:text-gray-400 text-xs;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .test-header {
    @apply flex-col gap-3;
  }
  
  .test-button {
    @apply self-stretch;
  }
  
  .result-actions {
    @apply flex-col gap-2;
  }
}
</style>