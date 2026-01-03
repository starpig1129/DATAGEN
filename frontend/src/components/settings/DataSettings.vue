<template>
  <div class="data-settings">
    <!-- 上傳設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.data.upload.title') }}</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <el-form-item 
          :label="$t('settings.data.upload.maxFileSize.label')"
          prop="data.upload.maxFileSize"
        >
          <el-input-number
            v-model="localValue.upload.maxFileSize"
            :min="1"
            :max="1000"
            :step="10"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.upload.maxFileSize.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.upload.maxFilesPerUpload')"
          prop="data.upload.maxFilesPerUpload"
        >
          <el-input-number
            v-model="localValue.upload.maxFilesPerUpload"
            :min="1"
            :max="100"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="data.upload.autoScan">
          <el-checkbox
            v-model="localValue.upload.autoScan"
            :label="$t('settings.data.upload.autoScan')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="data.upload.compressImages">
          <el-checkbox
            v-model="localValue.upload.compressImages"
            :label="$t('settings.data.upload.compressImages')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.upload.allowedTypes')"
          prop="data.upload.allowedTypes"
          class="col-span-1 md:col-span-2"
        >
          <el-select
            v-model="localValue.upload.allowedTypes"
            multiple
            filterable
            allow-create
            :placeholder="$t('settings.data.upload.allowedTypes')"
            class="w-full"
            @change="handleChange"
          >
            <el-option
              v-for="type in commonFileTypes"
              :key="type"
              :value="type"
              :label="type"
            />
          </el-select>
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.upload.allowedTypesHelp') }}
            </el-text>
          </div>
        </el-form-item>
      </div>
    </div>
    
    <!-- 數據保留設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.data.retention.title') }}</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <el-form-item 
          :label="$t('settings.data.retention.chatHistory')"
          prop="data.retention.chatHistory"
        >
          <el-input-number
            v-model="localValue.retention.chatHistory"
            :min="1"
            :max="365"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.retention.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.retention.uploadedFiles')"
          prop="data.retention.uploadedFiles"
        >
          <el-input-number
            v-model="localValue.retention.uploadedFiles"
            :min="1"
            :max="365"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.retention.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.retention.analysisResults')"
          prop="data.retention.analysisResults"
        >
          <el-input-number
            v-model="localValue.retention.analysisResults"
            :min="1"
            :max="365"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.retention.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.retention.logs')"
          prop="data.retention.logs"
        >
          <el-input-number
            v-model="localValue.retention.logs"
            :min="1"
            :max="30"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.retention.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item prop="data.retention.autoDelete">
          <el-checkbox
            v-model="localValue.retention.autoDelete"
            :label="$t('settings.data.retention.autoDelete')"
            @change="handleChange"
          />
        </el-form-item>
      </div>
    </div>
    
    <!-- 快取設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.data.cache.title') }}</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <el-form-item prop="data.cache.enabled">
          <el-checkbox
            v-model="localValue.cache.enabled"
            :label="$t('settings.data.cache.enabled')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="data.cache.preloadData">
          <el-checkbox
            v-model="localValue.cache.preloadData"
            :label="$t('settings.data.cache.preloadData')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="data.cache.compressData">
          <el-checkbox
            v-model="localValue.cache.compressData"
            :label="$t('settings.data.cache.compressData')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.cache.maxSize.label')"
          prop="data.cache.maxSize"
        >
          <el-input-number
            v-model="localValue.cache.maxSize"
            :min="10"
            :max="5000"
            :step="50"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.cache.maxSize.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.cache.ttl.label')"
          prop="data.cache.ttl"
        >
          <el-input-number
            v-model="localValue.cache.ttl"
            :min="60"
            :max="86400"
            :step="300"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.cache.ttl.unit') }}
            </el-text>
          </div>
        </el-form-item>
      </div>
      
      <!-- 快取統計 -->
      <div v-if="localValue.cache.enabled" class="cache-stats">
        <div class="stats-header">
          <h5>{{ $t('settings.data.cache.stats.title') }}</h5>
          <el-button type="primary" link size="small" @click="clearCache">
            {{ $t('settings.data.cache.stats.clear') }}
          </el-button>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">{{ $t('settings.data.cache.stats.currentSize') }}</span>
            <span class="stat-value">{{ formatSize(cacheStats.currentSize) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">{{ $t('settings.data.cache.stats.hitRate') }}</span>
            <span class="stat-value">{{ cacheStats.hitRate }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">{{ $t('settings.data.cache.stats.itemCount') }}</span>
            <span class="stat-value">{{ cacheStats.itemCount }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 清理設定 -->
    <div class="settings-group">
      <h4 class="group-title">{{ $t('settings.data.cleanup.title') }}</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <el-form-item prop="data.cleanup.autoCleanup">
          <el-checkbox
            v-model="localValue.cleanup.autoCleanup"
            :label="$t('settings.data.cleanup.autoCleanup')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="data.cleanup.cleanupLogs">
          <el-checkbox
            v-model="localValue.cleanup.cleanupLogs"
            :label="$t('settings.data.cleanup.cleanupLogs')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item prop="data.cleanup.cleanupCache">
          <el-checkbox
            v-model="localValue.cleanup.cleanupCache"
            :label="$t('settings.data.cleanup.cleanupCache')"
            @change="handleChange"
          />
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.cleanup.cleanupInterval.label')"
          prop="data.cleanup.cleanupInterval"
        >
          <el-input-number
            v-model="localValue.cleanup.cleanupInterval"
            :min="1"
            :max="168"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.cleanup.cleanupInterval.unit') }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item 
          :label="$t('settings.data.cleanup.keepRecent.label')"
          prop="data.cleanup.keepRecent"
        >
          <el-input-number
            v-model="localValue.cleanup.keepRecent"
            :min="1"
            :max="30"
            controls-position="right"
            class="w-full"
            @change="handleChange"
          />
          <div class="form-help">
            <el-text size="small" type="info">
              {{ $t('settings.data.cleanup.keepRecent.unit') }}
            </el-text>
          </div>
        </el-form-item>
      </div>
      
      <!-- 手動清理操作 -->
      <div class="manual-cleanup">
        <div class="cleanup-header">
          <h5>{{ $t('settings.data.cleanup.manual.title') }}</h5>
          <el-text size="small" type="info">
            {{ $t('settings.data.cleanup.manual.description') }}
          </el-text>
        </div>
        <div class="cleanup-actions">
          <el-button @click="cleanupLogs" :loading="cleaning.logs">
            {{ $t('settings.data.cleanup.manual.cleanupLogs') }}
          </el-button>
          <el-button @click="cleanupCache" :loading="cleaning.cache">
            {{ $t('settings.data.cleanup.manual.cleanupCache') }}
          </el-button>
          <el-button @click="cleanupTempFiles" :loading="cleaning.temp">
            {{ $t('settings.data.cleanup.manual.cleanupTempFiles') }}
          </el-button>
          <el-button type="danger" @click="cleanupAll" :loading="cleaning.all">
            {{ $t('settings.data.cleanup.manual.cleanupAll') }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { DataSettings } from '@/types/settings'

interface Props {
  modelValue: DataSettings
  disabled?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: DataSettings): void
  (e: 'change', value: DataSettings): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<Emits>()

const { t } = useI18n()

// 本地狀態
const localValue = ref<DataSettings>({ ...props.modelValue })
const cleaning = ref({
  logs: false,
  cache: false,
  temp: false,
  all: false
})

// 常用文件類型
const commonFileTypes = [
  '.csv', '.xlsx', '.xls', '.json', '.txt', '.pdf', 
  '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg',
  '.md', '.py', '.js', '.html', '.css', '.zip'
]

// 模擬快取統計
const cacheStats = ref({
  currentSize: 125 * 1024 * 1024, // 125MB
  hitRate: 85,
  itemCount: 1247
})

// 監聽prop變化
watch(() => props.modelValue, (newValue) => {
  localValue.value = { ...newValue }
}, { deep: true })

// 處理變化
const handleChange = () => {
  emit('update:modelValue', { ...localValue.value })
  emit('change', { ...localValue.value })
}

// 格式化文件大小
const formatSize = (bytes: number) => {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 清除快取
const clearCache = async () => {
  try {
    await ElMessageBox.confirm(
      t('settings.data.cache.confirmClear'),
      t('settings.data.cache.stats.clear'),
      {
        type: 'warning',
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel')
      }
    )
    
    // 模擬清除快取
    cacheStats.value = {
      currentSize: 0,
      hitRate: 0,
      itemCount: 0
    }
    
    ElMessage.success(t('settings.data.cache.clearSuccess'))
  } catch {
    // 用戶取消
  }
}

// 清理日誌
const cleanupLogs = async () => {
  cleaning.value.logs = true
  try {
    // 模擬清理操作
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('日誌清理完成')
  } catch (error) {
    ElMessage.error('日誌清理失敗')
  } finally {
    cleaning.value.logs = false
  }
}

// 清理快取
const cleanupCache = async () => {
  cleaning.value.cache = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    cacheStats.value.currentSize = Math.floor(cacheStats.value.currentSize * 0.1)
    cacheStats.value.itemCount = Math.floor(cacheStats.value.itemCount * 0.1)
    ElMessage.success('快取清理完成')
  } catch (error) {
    ElMessage.error('快取清理失敗')
  } finally {
    cleaning.value.cache = false
  }
}

// 清理臨時文件
const cleanupTempFiles = async () => {
  cleaning.value.temp = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('臨時文件清理完成')
  } catch (error) {
    ElMessage.error('臨時文件清理失敗')
  } finally {
    cleaning.value.temp = false
  }
}

// 全部清理
const cleanupAll = async () => {
  try {
    await ElMessageBox.confirm(
      '確定要執行全部清理嗎？這將清除所有日誌、快取和臨時文件。',
      '全部清理',
      {
        type: 'warning',
        confirmButtonText: '確定清理',
        cancelButtonText: '取消'
      }
    )
    
    cleaning.value.all = true
    
    // 依次執行清理操作
    await cleanupLogs()
    await cleanupCache()
    await cleanupTempFiles()
    
    ElMessage.success('全部清理完成')
  } catch {
    // 用戶取消
  } finally {
    cleaning.value.all = false
  }
}
</script>

<style scoped>
.data-settings {
  @apply space-y-8;
}

.settings-group {
  @apply space-y-6;
}

.group-title {
  @apply text-lg font-semibold mb-4 pb-2 border-b;
  color: var(--text-primary);
  border-color: var(--border-color-light);
}

.form-help {
  @apply mt-1;
}

.cache-stats,
.manual-cleanup {
  @apply mt-6 p-4 rounded-lg;
  background-color: var(--bg-tertiary);
}

.stats-header,
.cleanup-header {
  @apply flex items-center justify-between mb-4;
}

.stats-header h5,
.cleanup-header h5 {
  @apply text-base font-medium text-gray-900 dark:text-white m-0;
}

.stats-grid {
  @apply grid grid-cols-1 md:grid-cols-3 gap-4;
}

.stat-item {
  @apply flex items-center justify-between p-3 rounded;
  background-color: var(--bg-secondary);
}

.stat-label {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

.stat-value {
  @apply font-medium text-gray-900 dark:text-white;
}

.cleanup-actions {
  @apply flex flex-wrap gap-3;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .stats-grid {
    @apply grid-cols-1;
  }
  
  .cleanup-actions {
    @apply flex-col;
  }
  
  .stats-header,
  .cleanup-header {
    @apply flex-col items-start gap-2;
  }
}
</style>