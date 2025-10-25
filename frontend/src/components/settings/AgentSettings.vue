<template>
  <div class="agent-settings">
    <!-- 工作流程設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.agent.workflow.title') }}</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <el-form-item prop="agent.workflow.autoStart">
          <el-checkbox
            v-model="localValue.workflow.autoStart"
            :label="$t('settings.agent.workflow.autoStart')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="agent.workflow.parallelExecution">
          <el-checkbox
            v-model="localValue.workflow.parallelExecution"
            :label="$t('settings.agent.workflow.parallelExecution')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="agent.workflow.retryFailedTasks">
          <el-checkbox
            v-model="localValue.workflow.retryFailedTasks"
            :label="$t('settings.agent.workflow.retryFailedTasks')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="agent.workflow.saveIntermediateResults">
          <el-checkbox
            v-model="localValue.workflow.saveIntermediateResults"
            :label="$t('settings.agent.workflow.saveIntermediateResults')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.agent.workflow.maxConcurrentAgents')"
          prop="agent.workflow.maxConcurrentAgents"
        >
          <el-input-number
            v-model="localValue.workflow.maxConcurrentAgents"
            :min="1"
            :max="10"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
        </el-form-item>
      </div>
    </div>
    
    <!-- 代理優先級設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.agent.priorities.title') }}</h4>
      
      <div class="priority-settings">
        <div 
          v-for="(label, agent) in priorityLabels"
          :key="agent"
          class="priority-item"
        >
          <div class="priority-info">
            <span class="priority-label">{{ label }}</span>
            <span class="priority-desc">{{ $t('settings.agent.priorities.level') }}: {{ localValue.priorities[agent] }}</span>
          </div>
          <el-slider
            v-model="localValue.priorities[agent]"
            :min="1"
            :max="10"
            :step="1"
            show-stops
            @change="handleChange"
            class="priority-slider"
          />
        </div>
      </div>
    </div>
    
    <!-- 超時設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.agent.timeout.title') }}</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <el-form-item 
          :label="$t('settings.agent.timeout.agentResponse')"
          prop="agent.timeout.agentResponse"
        >
          <el-input-number
            v-model="localValue.timeout.agentResponse"
            :min="5000"
            :max="300000"
            :step="5000"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.agent.timeout.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.agent.timeout.fileUpload')"
          prop="agent.timeout.fileUpload"
        >
          <el-input-number
            v-model="localValue.timeout.fileUpload"
            :min="30000"
            :max="600000"
            :step="30000"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.agent.timeout.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.agent.timeout.apiRequest')"
          prop="agent.timeout.apiRequest"
        >
          <el-input-number
            v-model="localValue.timeout.apiRequest"
            :min="5000"
            :max="120000"
            :step="5000"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.agent.timeout.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.agent.timeout.websocketConnection')"
          prop="agent.timeout.websocketConnection"
        >
          <el-input-number
            v-model="localValue.timeout.websocketConnection"
            :min="5000"
            :max="60000"
            :step="5000"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.agent.timeout.unit') }}
            </el-text>
          </div>
        </el-form-item>
      </div>
    </div>
    
    <!-- 調試設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.agent.debugging.title') }}</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <el-form-item prop="agent.debugging.enabled">
          <el-checkbox
            v-model="localValue.debugging.enabled"
            :label="$t('settings.agent.debugging.enabled')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="agent.debugging.saveLogsToFile">
          <el-checkbox
            v-model="localValue.debugging.saveLogsToFile"
            :label="$t('settings.agent.debugging.saveLogsToFile')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="agent.debugging.showAgentSteps">
          <el-checkbox
            v-model="localValue.debugging.showAgentSteps"
            :label="$t('settings.agent.debugging.showAgentSteps')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="agent.debugging.verboseOutput">
          <el-checkbox
            v-model="localValue.debugging.verboseOutput"
            :label="$t('settings.agent.debugging.verboseOutput')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.agent.debugging.logLevel.label')"
          prop="agent.debugging.logLevel"
          class="col-span-1 md:col-span-2"
        >
          <el-select
            v-model="localValue.debugging.logLevel"
            class="w-full"
            @change="handleChange"
          >
            <el-option
              value="debug"
              :label="$t('settings.agent.debugging.logLevel.debug')"
            />
            <el-option
              value="info"
              :label="$t('settings.agent.debugging.logLevel.info')"
            />
            <el-option
              value="warn"
              :label="$t('settings.agent.debugging.logLevel.warn')"
            />
            <el-option
              value="error"
              :label="$t('settings.agent.debugging.logLevel.error')"
            />
          </el-select>
        </el-form-item>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AgentSettings } from '@/types/settings'

interface Props {
  modelValue: AgentSettings
  disabled?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: AgentSettings): void
  (e: 'change', value: AgentSettings): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<Emits>()

const { t } = useI18n()

// 本地狀態
const localValue = ref<AgentSettings>({ ...props.modelValue })

// 代理優先級標籤
const priorityLabels = computed(() => ({
  searchAgent: t('settings.agent.priorities.searchAgent'),
  analysisAgent: t('settings.agent.priorities.analysisAgent'),
  visualizationAgent: t('settings.agent.priorities.visualizationAgent'),
  reportAgent: t('settings.agent.priorities.reportAgent'),
  qualityReviewAgent: t('settings.agent.priorities.qualityReviewAgent')
}))

// 監聽prop變化
watch(() => props.modelValue, (newValue) => {
  localValue.value = { ...newValue }
}, { deep: true })

// 處理變化
const handleChange = () => {
  emit('update:modelValue', { ...localValue.value })
  emit('change', { ...localValue.value })
}
</script>

<style scoped>
.agent-settings {
  @apply space-y-8;
}

.settings-group {
  @apply space-y-6;
}

.group-title {
  @apply text-lg font-semibold text-gray-900 dark:text-white mb-4;
  @apply pb-2 border-b border-gray-200 dark:border-gray-700;
}

.form-help {
  @apply mt-1;
}

.priority-settings {
  @apply space-y-6;
}

.priority-item {
  @apply p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg;
}

.priority-info {
  @apply flex items-center justify-between mb-3;
}

.priority-label {
  @apply font-medium text-gray-900 dark:text-white;
}

.priority-desc {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

.priority-slider {
  @apply w-full;
}

.priority-slider :deep(.el-slider__runway) {
  @apply bg-gray-200 dark:bg-gray-700;
}

.priority-slider :deep(.el-slider__bar) {
  @apply bg-blue-500;
}

.priority-slider :deep(.el-slider__button) {
  @apply border-blue-500;
}

.priority-slider :deep(.el-slider__stop) {
  @apply bg-gray-300 dark:bg-gray-600;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .priority-info {
    @apply flex-col items-start gap-1;
  }
}
</style>