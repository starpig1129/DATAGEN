<template>
  <div class="error-boundary">
    <!-- 正常內容 -->
    <slot v-if="!hasError" :retry="retryOperation" :error="null"></slot>
    
    <!-- 錯誤狀態 -->
    <div v-else class="error-container" :class="errorTypeClass">
      <!-- 錯誤圖標和動畫 -->
      <div class="error-illustration">
        <div v-if="errorType === 'network'" class="network-error-icon">
          <svg viewBox="0 0 100 100" class="error-svg">
            <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"/>
            <path d="M30 30 L70 70 M70 30 L30 70" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            <animateTransform
              attributeName="transform"
              type="rotate"
              from="0 50 50"
              to="360 50 50"
              dur="3s"
              repeatCount="indefinite"
            />
          </svg>
        </div>
        
        <div v-else-if="errorType === 'permission'" class="permission-error-icon">
          <el-icon class="error-icon"><Lock /></el-icon>
        </div>
        
        <div v-else-if="errorType === 'notFound'" class="not-found-error-icon">
          <el-icon class="error-icon"><DocumentDelete /></el-icon>
        </div>
        
        <div v-else-if="errorType === 'timeout'" class="timeout-error-icon">
          <el-icon class="error-icon"><Timer /></el-icon>
        </div>
        
        <div v-else class="generic-error-icon">
          <el-icon class="error-icon"><WarningFilled /></el-icon>
        </div>
      </div>

      <!-- 錯誤信息 -->
      <div class="error-content">
        <h3 class="error-title">{{ errorTitle }}</h3>
        <p class="error-message">{{ displayMessage }}</p>
        
        <!-- 錯誤詳情（可展開） -->
        <div v-if="showDetails && errorDetails" class="error-details">
          <el-collapse v-model="detailsExpanded">
            <el-collapse-item title="技術詳情" name="details">
              <div class="error-details-content">
                <div class="error-field">
                  <strong>錯誤類型：</strong>{{ errorType }}
                </div>
                <div v-if="errorCode" class="error-field">
                  <strong>錯誤代碼：</strong>{{ errorCode }}
                </div>
                <div v-if="errorStack" class="error-field">
                  <strong>堆疊追蹤：</strong>
                  <pre class="error-stack">{{ errorStack }}</pre>
                </div>
                <div v-if="timestamp" class="error-field">
                  <strong>發生時間：</strong>{{ formatTimestamp(timestamp) }}
                </div>
                <div v-if="userAgent" class="error-field">
                  <strong>用戶代理：</strong>{{ userAgent }}
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 建議操作 -->
        <div class="error-suggestions">
          <h4>建議操作：</h4>
          <ul class="suggestions-list">
            <li v-for="suggestion in suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </div>

        <!-- 操作按鈕 -->
        <div class="error-actions">
          <el-button 
            type="primary" 
            :icon="Refresh"
            :loading="isRetrying"
            @click="handleRetry"
          >
            重試
          </el-button>
          
          <el-button 
            v-if="showReload"
            :icon="Refresh"
            @click="reloadPage"
          >
            重新載入頁面
          </el-button>
          
          <el-button 
            v-if="showGoBack"
            :icon="ArrowLeft"
            @click="goBack"
          >
            返回上一頁
          </el-button>
          
          <el-button 
            v-if="showReport"
            type="warning"
            :icon="Warning"
            @click="reportError"
          >
            回報問題
          </el-button>
          
          <el-button 
            v-if="showContact"
            :icon="ChatLineRound"
            @click="contactSupport"
          >
            聯繫支援
          </el-button>
        </div>

        <!-- 額外幫助鏈接 -->
        <div v-if="helpLinks.length > 0" class="help-links">
          <h4>相關幫助：</h4>
          <div class="links-container">
            <el-link
              v-for="link in helpLinks"
              :key="link.url"
              :href="link.url"
              :icon="link.icon"
              target="_blank"
              type="primary"
            >
              {{ link.text }}
            </el-link>
          </div>
        </div>
      </div>

      <!-- 連接狀態指示器 -->
      <div v-if="showConnectionStatus" class="connection-status">
        <div class="status-indicator" :class="connectionStatusClass">
          <el-icon><Connection /></el-icon>
          <span>{{ connectionStatusText }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Lock, 
  DocumentDelete, 
  Timer, 
  WarningFilled, 
  Refresh, 
  ArrowLeft, 
  Warning, 
  ChatLineRound,
  Connection 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'

interface ErrorInfo {
  type?: string
  message?: string
  code?: string | number
  stack?: string
  timestamp?: Date
  component?: string
  route?: string
}

interface HelpLink {
  text: string
  url: string
  icon?: any
}

interface Props {
  error?: Error | null
  errorInfo?: ErrorInfo
  showDetails?: boolean
  showReload?: boolean
  showGoBack?: boolean
  showReport?: boolean
  showContact?: boolean
  showConnectionStatus?: boolean
  customTitle?: string
  customMessage?: string
  customSuggestions?: string[]
  helpLinks?: HelpLink[]
  autoRetry?: boolean
  maxRetries?: number
  retryDelay?: number
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: true,
  showReload: true,
  showGoBack: true,
  showReport: true,
  showContact: false,
  showConnectionStatus: false,
  helpLinks: () => [],
  customSuggestions: () => [],
  autoRetry: false,
  maxRetries: 3,
  retryDelay: 1000
})

const emit = defineEmits<{
  retry: []
  report: [error: Error, info: ErrorInfo]
  contact: []
}>()

const router = useRouter()
const appStore = useAppStore()

const hasError = ref(false)
const currentError = ref<Error | null>(null)
const currentErrorInfo = ref<ErrorInfo>({})
const isRetrying = ref(false)
const retryCount = ref(0)
const detailsExpanded = ref([])
const connectionStatus = ref<'online' | 'offline' | 'checking'>('checking')

// 錯誤類型檢測
const errorType = computed(() => {
  if (currentErrorInfo.value.type) return currentErrorInfo.value.type
  if (currentError.value?.name === 'NetworkError') return 'network'
  if (currentError.value?.message.includes('fetch')) return 'network'
  if (currentError.value?.message.includes('timeout')) return 'timeout'
  if (currentError.value?.message.includes('permission')) return 'permission'
  if (currentError.value?.message.includes('not found')) return 'notFound'
  return 'generic'
})

const errorTypeClass = computed(() => `error-type-${errorType.value}`)

const errorTitle = computed(() => {
  if (props.customTitle) return props.customTitle
  
  const titles = {
    network: '網路連接錯誤',
    timeout: '請求超時',
    permission: '權限不足',
    notFound: '資源未找到',
    generic: '發生錯誤'
  }
  
  return titles[errorType.value as keyof typeof titles] || '未知錯誤'
})

const displayMessage = computed(() => {
  if (props.customMessage) return props.customMessage
  
  const messages = {
    network: '無法連接到伺服器，請檢查您的網路連接。',
    timeout: '請求處理時間過長，請稍後重試。',
    permission: '您沒有足夠的權限執行此操作。',
    notFound: '所請求的資源不存在或已被移除。',
    generic: '系統發生未預期的錯誤，請稍後重試。'
  }
  
  return currentError.value?.message || 
         messages[errorType.value as keyof typeof messages] || 
         '發生未知錯誤'
})

const suggestions = computed(() => {
  if (props.customSuggestions.length > 0) return props.customSuggestions
  
  const suggestionMap = {
    network: [
      '檢查您的網路連接',
      '確認伺服器地址是否正確',
      '嘗試重新整理頁面',
      '聯繫系統管理員'
    ],
    timeout: [
      '等待一段時間後重試',
      '檢查網路穩定性',
      '減少並發請求數量'
    ],
    permission: [
      '聯繫管理員獲取權限',
      '確認您已登入正確帳戶',
      '檢查帳戶權限設定'
    ],
    notFound: [
      '確認資源路徑是否正確',
      '檢查資源是否已被移動或刪除',
      '返回首頁重新導航'
    ],
    generic: [
      '重新整理頁面',
      '清除瀏覽器快取',
      '稍後重試',
      '聯繫技術支援'
    ]
  }
  
  return suggestionMap[errorType.value as keyof typeof suggestionMap] || []
})

const errorDetails = computed(() => ({
  type: errorType.value,
  code: currentErrorInfo.value.code || currentError.value?.name,
  stack: currentError.value?.stack,
  timestamp: currentErrorInfo.value.timestamp || new Date(),
  userAgent: navigator.userAgent,
  route: currentErrorInfo.value.route || router.currentRoute.value.path
}))

const errorCode = computed(() => errorDetails.value.code)
const errorStack = computed(() => errorDetails.value.stack)
const timestamp = computed(() => errorDetails.value.timestamp)
const userAgent = computed(() => errorDetails.value.userAgent)

const connectionStatusClass = computed(() => ({
  'status-online': connectionStatus.value === 'online',
  'status-offline': connectionStatus.value === 'offline',
  'status-checking': connectionStatus.value === 'checking'
}))

const connectionStatusText = computed(() => {
  const statusTexts = {
    online: '網路連接正常',
    offline: '網路連接中斷',
    checking: '檢查網路狀態...'
  }
  return statusTexts[connectionStatus.value]
})

// 錯誤捕獲
onErrorCaptured((error: Error, instance, info) => {
  console.error('ErrorBoundary caught error:', error, info)
  captureError(error, { 
    component: instance?.$?.type.name || 'Unknown',
    ...currentErrorInfo.value 
  })
  return false
})

// 方法
const captureError = (error: Error, info: ErrorInfo = {}) => {
  hasError.value = true
  currentError.value = error
  currentErrorInfo.value = {
    timestamp: new Date(),
    route: router.currentRoute.value.path,
    ...info
  }
  
  // 記錄錯誤到控制台和應用商店
  console.error('Error captured by ErrorBoundary:', error, info)
  appStore.addNotification({
    type: 'error',
    title: '系統錯誤',
    message: `${errorTitle.value}: ${error.message}`,
    duration: 0
  })
}

const handleRetry = async () => {
  if (isRetrying.value) return
  
  isRetrying.value = true
  retryCount.value++
  
  try {
    // 等待重試延遲
    await new Promise(resolve => setTimeout(resolve, props.retryDelay))
    
    // 重置錯誤狀態
    hasError.value = false
    currentError.value = null
    currentErrorInfo.value = {}
    
    // 觸發重試事件
    emit('retry')
    
    ElMessage.success('重試成功')
  } catch (error) {
    console.error('Retry failed:', error)
    ElMessage.error('重試失敗')
  } finally {
    isRetrying.value = false
  }
}

const retryOperation = () => {
  handleRetry()
}

const reloadPage = () => {
  window.location.reload()
}

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

const reportError = async () => {
  try {
    await ElMessageBox.confirm(
      '您確定要回報此錯誤嗎？系統將收集相關的診斷信息。',
      '回報錯誤',
      {
        confirmButtonText: '回報',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    emit('report', currentError.value!, currentErrorInfo.value)
    ElMessage.success('錯誤報告已提交')
  } catch {
    // 用戶取消
  }
}

const contactSupport = () => {
  emit('contact')
}

const formatTimestamp = (date: Date) => {
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

const checkConnection = async () => {
  connectionStatus.value = 'checking'
  
  try {
    const response = await fetch('/api/health', { 
      method: 'HEAD',
      cache: 'no-cache'
    })
    connectionStatus.value = response.ok ? 'online' : 'offline'
  } catch {
    connectionStatus.value = 'offline'
  }
}

// Auto retry logic (reserved for future auto-retry feature)
/*
const autoRetryTimer = ref<ReturnType<typeof setTimeout>>()

const _setupAutoRetry = () => {
  if (!props.autoRetry || retryCount.value >= props.maxRetries) return
  
  autoRetryTimer.value = setTimeout(() => {
    handleRetry()
  }, props.retryDelay * Math.pow(2, retryCount.value)) // Exponential backoff
}
*/

// 監聽錯誤屬性變化
const watchError = () => {
  if (props.error) {
    captureError(props.error, props.errorInfo)
  }
}

onMounted(() => {
  watchError()
  
  if (props.showConnectionStatus) {
    checkConnection()
    // 定期檢查連接狀態
    setInterval(checkConnection, 30000)
  }
  
  // 監聽在線狀態變化
  window.addEventListener('online', () => {
    connectionStatus.value = 'online'
  })
  
  window.addEventListener('offline', () => {
    connectionStatus.value = 'offline'
  })
})

// 暴露方法給父組件
defineExpose({
  captureError,
  retry: retryOperation,
  clearError: () => {
    hasError.value = false
    currentError.value = null
    currentErrorInfo.value = {}
  }
})
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  min-height: 400px;
  text-align: center;
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

/* 錯誤類型樣式 */
.error-type-network {
  border-left: 4px solid var(--el-color-warning);
}

.error-type-permission {
  border-left: 4px solid var(--el-color-danger);
}

.error-type-timeout {
  border-left: 4px solid var(--el-color-info);
}

.error-type-notFound {
  border-left: 4px solid var(--el-color-warning);
}

/* 錯誤插圖 */
.error-illustration {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  color: var(--el-color-danger);
}

.error-svg {
  width: 100%;
  height: 100%;
}

.error-icon {
  font-size: 80px;
}

.network-error-icon {
  color: var(--el-color-warning);
}

.permission-error-icon {
  color: var(--el-color-danger);
}

.timeout-error-icon {
  color: var(--el-color-info);
}

.not-found-error-icon {
  color: var(--el-color-warning);
}

/* 錯誤內容 */
.error-content {
  max-width: 600px;
  width: 100%;
}

.error-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 16px 0;
}

.error-message {
  font-size: 16px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
  margin: 0 0 24px 0;
}

/* 錯誤詳情 */
.error-details {
  margin: 24px 0;
  text-align: left;
}

.error-details-content {
  background: var(--el-bg-color-page);
  padding: 16px;
  border-radius: 6px;
  font-size: 14px;
}

.error-field {
  margin-bottom: 12px;
}

.error-field:last-child {
  margin-bottom: 0;
}

.error-stack {
  background: var(--el-bg-color);
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
}

/* 建議操作 */
.error-suggestions {
  margin: 24px 0;
  text-align: left;
}

.error-suggestions h4 {
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin: 0 0 12px 0;
}

.suggestions-list {
  margin: 0;
  padding-left: 20px;
  color: var(--el-text-color-regular);
}

.suggestions-list li {
  margin-bottom: 8px;
  line-height: 1.5;
}

/* 操作按鈕 */
.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin: 32px 0 24px 0;
}

/* 幫助鏈接 */
.help-links {
  margin-top: 24px;
  text-align: left;
}

.help-links h4 {
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin: 0 0 12px 0;
}

.links-container {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

/* 連接狀態 */
.connection-status {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-light);
  width: 100%;
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.status-online {
  background: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success-light-7);
}

.status-offline {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
  border: 1px solid var(--el-color-danger-light-7);
}

.status-checking {
  background: var(--el-color-info-light-9);
  color: var(--el-color-info);
  border: 1px solid var(--el-color-info-light-7);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .error-container {
    padding: 32px 16px;
    min-height: 300px;
  }
  
  .error-illustration {
    width: 60px;
    height: 60px;
  }
  
  .error-icon {
    font-size: 60px;
  }
  
  .error-title {
    font-size: 20px;
  }
  
  .error-message {
    font-size: 14px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .links-container {
    flex-direction: column;
    gap: 8px;
  }
}

/* 無障礙支援 */
@media (prefers-reduced-motion: reduce) {
  .error-svg animateTransform {
    animation-duration: 0s;
  }
}
</style>