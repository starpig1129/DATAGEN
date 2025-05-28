<template>
  <div class="progressive-loader" :class="loaderClasses">
    <!-- 載入進度指示器 -->
    <div v-if="showProgress" class="progress-container">
      <div class="progress-bar-wrapper">
        <div class="progress-bar" :style="progressStyle"></div>
        <div class="progress-shimmer"></div>
      </div>
      <div class="progress-info">
        <span class="progress-text">{{ currentStageText }}</span>
        <span class="progress-percentage">{{ Math.round(progress) }}%</span>
      </div>
    </div>

    <!-- 載入動畫 -->
    <div v-if="showAnimation" class="loading-animation">
      <div class="spinner-container">
        <div class="spinner" :class="spinnerType">
          <div v-if="spinnerType === 'dots'" class="spinner-dots">
            <div v-for="i in 3" :key="i" class="dot" :style="{ animationDelay: `${i * 0.1}s` }"></div>
          </div>
          <div v-else-if="spinnerType === 'wave'" class="spinner-wave">
            <div v-for="i in 5" :key="i" class="wave-bar" :style="{ animationDelay: `${i * 0.1}s` }"></div>
          </div>
          <div v-else-if="spinnerType === 'pulse'" class="spinner-pulse">
            <div class="pulse-ring"></div>
            <div class="pulse-ring"></div>
            <div class="pulse-ring"></div>
          </div>
          <div v-else class="spinner-circle">
            <svg viewBox="0 0 50 50">
              <circle
                cx="25"
                cy="25"
                r="20"
                fill="none"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="round"
                stroke-dasharray="31.416"
                stroke-dashoffset="31.416"
              >
                <animate
                  attributeName="stroke-dasharray"
                  dur="2s"
                  values="0 31.416;15.708 15.708;0 31.416"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="stroke-dashoffset"
                  dur="2s"
                  values="0;-15.708;-31.416"
                  repeatCount="indefinite"
                />
              </circle>
            </svg>
          </div>
        </div>
      </div>
      <div v-if="message" class="loading-message">{{ message }}</div>
    </div>

    <!-- 階段指示器 -->
    <div v-if="stages.length > 0" class="stages-indicator">
      <div
        v-for="(stage, index) in stages"
        :key="index"
        class="stage-item"
        :class="{
          'completed': index < currentStageIndex,
          'current': index === currentStageIndex,
          'pending': index > currentStageIndex
        }"
      >
        <div class="stage-icon">
          <el-icon v-if="index < currentStageIndex" class="success-icon">
            <Check />
          </el-icon>
          <el-icon v-else-if="index === currentStageIndex" class="loading-icon">
            <Loading />
          </el-icon>
          <span v-else class="stage-number">{{ index + 1 }}</span>
        </div>
        <div class="stage-content">
          <div class="stage-title">{{ stage.title }}</div>
          <div v-if="stage.description" class="stage-description">{{ stage.description }}</div>
        </div>
      </div>
    </div>

    <!-- 錯誤狀態 -->
    <div v-if="error" class="error-container">
      <div class="error-icon">
        <el-icon><WarningFilled /></el-icon>
      </div>
      <div class="error-content">
        <div class="error-title">載入失敗</div>
        <div class="error-message">{{ error }}</div>
        <div class="error-actions">
          <el-button type="primary" @click="retry" :loading="retrying">
            重試
          </el-button>
          <el-button v-if="showCancel" @click="cancel">
            取消
          </el-button>
        </div>
      </div>
    </div>

    <!-- 成功狀態 -->
    <div v-if="success" class="success-container">
      <div class="success-animation">
        <div class="success-checkmark">
          <svg viewBox="0 0 52 52">
            <circle cx="26" cy="26" r="25" fill="none" class="success-circle"/>
            <path fill="none" d="m14,27 l7,7 l16,-16" class="success-check"/>
          </svg>
        </div>
      </div>
      <div class="success-message">{{ successMessage || '載入完成' }}</div>
    </div>

    <!-- 自定義內容插槽 -->
    <slot
      v-if="!error && !success"
      :progress="progress"
      :current-stage="currentStage"
      :is-loading="isLoading"
    ></slot>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Check, Loading, WarningFilled } from '@element-plus/icons-vue'

interface LoadingStage {
  title: string
  description?: string
  duration?: number
}

interface Props {
  loading?: boolean
  progress?: number
  message?: string
  error?: string | null
  success?: boolean
  successMessage?: string
  stages?: LoadingStage[]
  currentStageIndex?: number
  spinnerType?: 'circle' | 'dots' | 'wave' | 'pulse'
  showProgress?: boolean
  showAnimation?: boolean
  showCancel?: boolean
  autoProgress?: boolean
  minDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  progress: 0,
  spinnerType: 'circle',
  showProgress: true,
  showAnimation: true,
  showCancel: false,
  autoProgress: false,
  minDuration: 500,
  stages: () => []
})

const emit = defineEmits<{
  retry: []
  cancel: []
  complete: []
  stageChange: [index: number, stage: LoadingStage]
}>()

const retrying = ref(false)
const internalProgress = ref(0)
const internalStageIndex = ref(0)
const startTime = ref(Date.now())
const animationId = ref<number>()

const isLoading = computed(() => props.loading && !props.error && !props.success)

const loaderClasses = computed(() => ({
  'is-loading': isLoading.value,
  'has-error': !!props.error,
  'is-success': props.success,
  'auto-progress': props.autoProgress
}))

const progress = computed(() => 
  props.autoProgress ? internalProgress.value : props.progress
)

const currentStageIndex = computed(() => 
  props.stages.length > 0 
    ? (props.currentStageIndex ?? internalStageIndex.value)
    : 0
)

const currentStage = computed(() => 
  props.stages[currentStageIndex.value]
)

const currentStageText = computed(() => {
  if (currentStage.value) {
    return currentStage.value.title
  }
  return props.message || '載入中...'
})

const progressStyle = computed(() => ({
  width: `${progress.value}%`,
  transition: props.autoProgress ? 'width 0.3s ease-out' : 'width 0.1s ease-out'
}))

// 自動進度更新
const updateAutoProgress = () => {
  if (!props.autoProgress || !isLoading.value) return

  const elapsedTime = Date.now() - startTime.value
  const stages = props.stages
  
  if (stages.length > 0) {
    // 基於階段的進度
    let totalDuration = 0
    let currentDuration = 0
    
    stages.forEach((stage, index) => {
      const stageDuration = stage.duration || 1000
      totalDuration += stageDuration
      
      if (index < internalStageIndex.value) {
        currentDuration += stageDuration
      } else if (index === internalStageIndex.value) {
        const stageProgress = Math.min(elapsedTime - currentDuration, stageDuration)
        currentDuration += stageProgress
      }
    })
    
    internalProgress.value = Math.min((currentDuration / totalDuration) * 100, 95)
    
    // 階段切換
    let accumulatedTime = 0
    for (let i = 0; i < stages.length; i++) {
      accumulatedTime += stages[i].duration || 1000
      if (elapsedTime >= accumulatedTime && i > internalStageIndex.value) {
        internalStageIndex.value = i
        emit('stageChange', i, stages[i])
        break
      }
    }
  } else {
    // 簡單的時間基礎進度
    const expectedDuration = props.minDuration
    internalProgress.value = Math.min((elapsedTime / expectedDuration) * 100, 95)
  }
  
  if (isLoading.value) {
    animationId.value = requestAnimationFrame(updateAutoProgress)
  }
}

const retry = async () => {
  retrying.value = true
  try {
    emit('retry')
    // 重置狀態
    internalProgress.value = 0
    internalStageIndex.value = 0
    startTime.value = Date.now()
  } finally {
    retrying.value = false
  }
}

const cancel = () => {
  emit('cancel')
}

// 監聽載入狀態變化
watch(() => props.loading, (newVal) => {
  if (newVal) {
    startTime.value = Date.now()
    internalProgress.value = 0
    internalStageIndex.value = 0
    
    if (props.autoProgress) {
      updateAutoProgress()
    }
  } else {
    if (animationId.value) {
      cancelAnimationFrame(animationId.value)
    }
  }
}, { immediate: true })

// 監聽成功狀態
watch(() => props.success, (newVal) => {
  if (newVal) {
    internalProgress.value = 100
    setTimeout(() => {
      emit('complete')
    }, 1000)
  }
})

onMounted(() => {
  if (props.loading && props.autoProgress) {
    updateAutoProgress()
  }
})

onUnmounted(() => {
  if (animationId.value) {
    cancelAnimationFrame(animationId.value)
  }
})
</script>

<style scoped>
.progressive-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  min-height: 200px;
  text-align: center;
}

/* 進度條 */
.progress-container {
  width: 100%;
  max-width: 400px;
  margin-bottom: 24px;
}

.progress-bar-wrapper {
  position: relative;
  width: 100%;
  height: 8px;
  background: var(--el-border-color-lighter);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 4px;
  position: relative;
}

.progress-shimmer {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: 30px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.progress-percentage {
  font-weight: 600;
  color: var(--el-color-primary);
}

/* 載入動畫 */
.loading-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner-container {
  width: 48px;
  height: 48px;
  color: var(--el-color-primary);
}

/* 圓形旋轉器 */
.spinner-circle {
  width: 100%;
  height: 100%;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  100% { transform: rotate(360deg); }
}

/* 點狀載入器 */
.spinner-dots {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
}

.dot {
  width: 12px;
  height: 12px;
  background: var(--el-color-primary);
  border-radius: 50%;
  animation: dot-bounce 1.4s infinite both;
}

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 波浪載入器 */
.spinner-wave {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
}

.wave-bar {
  width: 6px;
  height: 100%;
  background: var(--el-color-primary);
  border-radius: 3px;
  animation: wave-scale 1.2s infinite ease-in-out;
}

@keyframes wave-scale {
  0%, 40%, 100% { transform: scaleY(0.4); }
  20% { transform: scaleY(1); }
}

/* 脈衝載入器 */
.spinner-pulse {
  position: relative;
  width: 100%;
  height: 100%;
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border: 3px solid var(--el-color-primary);
  border-radius: 50%;
  animation: pulse-scale 1.5s infinite cubic-bezier(0.215, 0.61, 0.355, 1);
}

.pulse-ring:nth-child(2) { animation-delay: 0.5s; }
.pulse-ring:nth-child(3) { animation-delay: 1s; }

@keyframes pulse-scale {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
}

.loading-message {
  font-size: 16px;
  color: var(--el-text-color-regular);
  margin-top: 8px;
}

/* 階段指示器 */
.stages-indicator {
  width: 100%;
  max-width: 500px;
  margin-top: 32px;
}

.stage-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  position: relative;
}

.stage-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 20px;
  top: 50px;
  width: 2px;
  height: 32px;
  background: var(--el-border-color-light);
}

.stage-item.completed::after {
  background: var(--el-color-success);
}

.stage-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color);
  border: 2px solid var(--el-border-color-light);
  transition: all 0.3s ease;
}

.stage-item.completed .stage-icon {
  background: var(--el-color-success);
  border-color: var(--el-color-success);
  color: white;
}

.stage-item.current .stage-icon {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}

.stage-number {
  font-size: 14px;
  font-weight: 600;
}

.stage-content {
  flex: 1;
  text-align: left;
}

.stage-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.stage-item.current .stage-title {
  color: var(--el-color-primary);
}

.stage-description {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

/* 錯誤狀態 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--el-color-danger);
}

.error-icon {
  font-size: 48px;
}

.error-content {
  text-align: center;
}

.error-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.error-message {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-bottom: 16px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 成功狀態 */
.success-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.success-animation {
  width: 64px;
  height: 64px;
}

.success-checkmark svg {
  width: 100%;
  height: 100%;
}

.success-circle {
  stroke: var(--el-color-success);
  stroke-width: 2;
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  animation: circle-draw 0.6s ease-out forwards;
}

.success-check {
  stroke: var(--el-color-success);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: check-draw 0.3s ease-out 0.6s forwards;
}

@keyframes circle-draw {
  to { stroke-dashoffset: 0; }
}

@keyframes check-draw {
  to { stroke-dashoffset: 0; }
}

.success-message {
  font-size: 16px;
  color: var(--el-color-success);
  font-weight: 500;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .progressive-loader {
    padding: 24px 16px;
    min-height: 150px;
  }
  
  .progress-container {
    max-width: 300px;
  }
  
  .spinner-container {
    width: 40px;
    height: 40px;
  }
  
  .stage-item {
    gap: 12px;
  }
  
  .stage-icon {
    width: 32px;
    height: 32px;
  }
  
  .error-actions {
    flex-direction: column;
    width: 100%;
  }
}

/* 無障礙支援 */
@media (prefers-reduced-motion: reduce) {
  .progress-shimmer,
  .spinner-circle,
  .dot,
  .wave-bar,
  .pulse-ring {
    animation: none;
  }
  
  .progress-bar {
    transition: none;
  }
}
</style>