<template>
  <div class="theme-toggle">
    <el-form-item 
      :label="$t('settings.user.theme.label')"
      :prop="prop"
    >
      <el-radio-group
        v-model="localValue"
        @change="handleChange"
        :disabled="disabled"
        class="theme-options"
      >
        <el-radio 
          v-for="option in themeOptions"
          :key="option.value"
          :value="option.value"
          class="theme-option"
        >
          <div class="theme-option-content">
            <el-icon :size="18" class="theme-icon">
              <component :is="option.icon" />
            </el-icon>
            <div class="theme-info">
              <div class="theme-name">{{ option.label }}</div>
              <div class="theme-desc">{{ option.description }}</div>
            </div>
          </div>
        </el-radio>
      </el-radio-group>
      
      <div class="theme-help" v-if="showHelp">
        <el-text size="small" type="info">
          {{ $t('settings.user.theme.help') }}
        </el-text>
      </div>
      
      <div class="theme-preview" v-if="showPreview">
        <div class="preview-label">
          <el-text size="small">預覽效果：</el-text>
        </div>
        <div class="preview-cards">
          <div 
            v-for="theme in ['light', 'dark']"
            :key="theme"
            :class="[
              'preview-card',
              theme,
              { active: (localValue === theme) || (localValue === 'auto' && systemTheme === theme) }
            ]"
          >
            <div class="preview-header">
              <div class="preview-dots">
                <span class="dot red"></span>
                <span class="dot yellow"></span>
                <span class="dot green"></span>
              </div>
            </div>
            <div class="preview-content">
              <div class="preview-sidebar"></div>
              <div class="preview-main">
                <div class="preview-nav"></div>
                <div class="preview-body">
                  <div class="preview-text"></div>
                  <div class="preview-text short"></div>
                </div>
              </div>
            </div>
            <div class="preview-label-text">
              {{ theme === 'light' ? '淺色' : '深色' }}
            </div>
          </div>
        </div>
      </div>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Sunny, Moon, Monitor } from '@element-plus/icons-vue'
import type { ThemeMode } from '@/types/settings'

interface Props {
  modelValue: ThemeMode
  disabled?: boolean
  showHelp?: boolean
  showPreview?: boolean
  prop?: string
}

interface Emits {
  (e: 'update:modelValue', value: ThemeMode): void
  (e: 'change', value: ThemeMode): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  showHelp: true,
  showPreview: true,
  prop: 'theme'
})

const emit = defineEmits<Emits>()

const { t } = useI18n()

// 本地狀態
const localValue = ref<ThemeMode>(props.modelValue)
const systemTheme = ref<'light' | 'dark'>('light')

// 主題選項
const themeOptions = computed(() => [
  {
    value: 'light' as ThemeMode,
    label: t('settings.user.theme.light'),
    description: '始終使用淺色主題',
    icon: Sunny
  },
  {
    value: 'dark' as ThemeMode,
    label: t('settings.user.theme.dark'),
    description: '始終使用深色主題',
    icon: Moon
  },
  {
    value: 'auto' as ThemeMode,
    label: t('settings.user.theme.auto'),
    description: '跟隨系統設定自動切換',
    icon: Monitor
  }
])

// 監聽prop變化
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})

// 監聽系統主題變化
const updateSystemTheme = () => {
  systemTheme.value = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

onMounted(() => {
  updateSystemTheme()
  
  // 監聽系統主題變化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', updateSystemTheme)
})

// 處理主題變化
const handleChange = (value: string | number | boolean | undefined) => {
  const themeValue = value as ThemeMode
  localValue.value = themeValue
  emit('update:modelValue', themeValue)
  emit('change', themeValue)
}
</script>

<style scoped>
.theme-toggle {
  @apply w-full;
}

.theme-options {
  @apply w-full;
}

.theme-options :deep(.el-radio-group) {
  @apply flex flex-col gap-3 w-full;
}

.theme-option {
  @apply w-full block;
}

.theme-option :deep(.el-radio) {
  @apply w-full flex items-start;
}

.theme-option :deep(.el-radio__input) {
  @apply mt-1 flex-shrink-0;
}

.theme-option :deep(.el-radio__label) {
  @apply w-full pl-2 flex-1;
}

.theme-option-content {
  @apply flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer w-full;
  background-color: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.theme-option :deep(.el-radio.is-checked) .theme-option-content {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.theme-icon {
  @apply flex-shrink-0 text-gray-600 dark:text-gray-400;
}

.theme-option :deep(.el-radio.is-checked) .theme-icon {
  @apply text-blue-600 dark:text-blue-400;
}

.theme-info {
  @apply flex-1 min-w-0;
}

.theme-name {
  @apply font-medium text-gray-900 dark:text-white mb-1;
}

.theme-desc {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

.theme-help {
  @apply mt-3;
}

.theme-preview {
  @apply mt-4 p-4 rounded-lg;
  background-color: var(--bg-tertiary);
}

.preview-label {
  @apply mb-3;
}

.preview-cards {
  @apply flex gap-4;
}

.preview-card {
  @apply flex-1 rounded-lg border-2 overflow-hidden transition-all duration-200;
  @apply hover:scale-105 cursor-pointer;
}

.preview-card.active {
  @apply border-blue-500 shadow-lg;
}

.preview-card.light {
  @apply bg-white border-gray-200;
}

.preview-card.dark {
  @apply bg-gray-900 border-gray-700;
}

.preview-header {
  @apply h-6 px-3 py-2 flex items-center;
}

.preview-card.light .preview-header {
  @apply bg-gray-100;
}

.preview-card.dark .preview-header {
  @apply bg-gray-800;
}

.preview-dots {
  @apply flex gap-1;
}

.dot {
  @apply w-2 h-2 rounded-full;
}

.dot.red {
  @apply bg-red-500;
}

.dot.yellow {
  @apply bg-yellow-500;
}

.dot.green {
  @apply bg-green-500;
}

.preview-content {
  @apply h-16 flex;
}

.preview-sidebar {
  @apply w-4;
}

.preview-card.light .preview-sidebar {
  @apply bg-gray-200;
}

.preview-card.dark .preview-sidebar {
  @apply bg-gray-700;
}

.preview-main {
  @apply flex-1 flex flex-col;
}

.preview-nav {
  @apply h-2;
}

.preview-card.light .preview-nav {
  @apply bg-gray-100;
}

.preview-card.dark .preview-nav {
  @apply bg-gray-800;
}

.preview-body {
  @apply flex-1 p-2 space-y-1;
}

.preview-text {
  @apply h-1 rounded;
}

.preview-text.short {
  @apply w-3/4;
}

.preview-card.light .preview-text {
  @apply bg-gray-300;
}

.preview-card.dark .preview-text {
  @apply bg-gray-600;
}

.preview-label-text {
  @apply text-center py-2 text-xs font-medium;
}

.preview-card.light .preview-label-text {
  @apply text-gray-700 bg-gray-50;
}

.preview-card.dark .preview-label-text {
  @apply text-gray-300 bg-gray-800;
}

/* 深色主題增強 */
.dark .theme-option-content {
  background-color: var(--bg-secondary);
  border-color: var(--border-color-light) !important;
}

.dark .theme-option :deep(.el-radio.is-checked) .theme-option-content {
  border-color: var(--el-color-primary) !important;
  background-color: rgba(64, 158, 255, 0.1) !important;
}


/* 響應式設計 */
@media (max-width: 768px) {
  .theme-option-content {
    @apply gap-2 p-2;
  }
  
  .preview-cards {
    @apply gap-2;
  }
  
  .preview-card {
    @apply hover:scale-100;
  }
}
</style>