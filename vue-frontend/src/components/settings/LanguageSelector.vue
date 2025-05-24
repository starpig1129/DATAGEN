<template>
  <div class="language-selector">
    <el-form-item 
      :label="$t('settings.user.language.label')"
      :prop="prop"
    >
      <el-select
        v-model="localValue"
        :placeholder="$t('settings.user.language.help')"
        :disabled="disabled"
        @change="handleChange"
        class="language-select"
      >
        <el-option
          v-for="(config, code) in LANGUAGES"
          :key="code"
          :value="code"
          :label="config.nativeName"
          class="language-option"
        >
          <div class="language-option-content">
            <span class="language-flag">{{ config.flag }}</span>
            <div class="language-info">
              <div class="language-native">{{ config.nativeName }}</div>
              <div class="language-english">{{ config.name }}</div>
            </div>
          </div>
        </el-option>
      </el-select>
      
      <div class="language-help" v-if="showHelp">
        <el-text size="small" type="info">
          {{ $t('settings.user.language.help') }}
        </el-text>
      </div>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { LANGUAGES, setLocale } from '@/i18n'
import type { LanguageCode } from '@/types/settings'

interface Props {
  modelValue: LanguageCode
  disabled?: boolean
  showHelp?: boolean
  prop?: string
  immediate?: boolean // 是否立即切換語言
}

interface Emits {
  (e: 'update:modelValue', value: LanguageCode): void
  (e: 'change', value: LanguageCode): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  showHelp: true,
  prop: 'language',
  immediate: true
})

const emit = defineEmits<Emits>()

const { t } = useI18n()

// 本地狀態
const localValue = ref<LanguageCode>(props.modelValue)

// 監聽prop變化
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})

// 處理選擇變化
const handleChange = async (value: LanguageCode) => {
  localValue.value = value
  emit('update:modelValue', value)
  emit('change', value)
  
  // 立即切換語言
  if (props.immediate) {
    await setLocale(value)
    
    // 確保組件重新渲染以顯示新語言
    await nextTick()
  }
}

// 計算當前語言的顯示信息
const currentLanguageInfo = computed(() => {
  return LANGUAGES[localValue.value]
})
</script>

<style scoped>
.language-selector {
  @apply w-full;
}

.language-select {
  @apply w-full;
}

.language-option-content {
  @apply flex items-center gap-3;
}

.language-flag {
  @apply text-lg flex-shrink-0;
}

.language-info {
  @apply flex-1 min-w-0;
}

.language-native {
  @apply font-medium text-gray-900 dark:text-white;
}

.language-english {
  @apply text-sm text-gray-500 dark:text-gray-400;
}

.language-help {
  @apply mt-2;
}

/* 自定義選項樣式 */
.language-selector :deep(.el-select-dropdown__item) {
  @apply py-3;
}

.language-selector :deep(.el-select-dropdown__item.selected) {
  @apply bg-blue-50 dark:bg-blue-900/20;
}

.language-selector :deep(.el-select-dropdown__item:hover) {
  @apply bg-gray-50 dark:bg-gray-700;
}

/* 深色模式下的下拉選單樣式 */
.dark .language-selector :deep(.el-select-dropdown) {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
}

.dark .language-selector :deep(.el-select-dropdown__item) {
  color: #f9fafb !important;
}

.dark .language-selector :deep(.el-select-dropdown__item.selected) {
  background-color: rgba(59, 130, 246, 0.2) !important;
  color: #60a5fa !important;
}

.dark .language-selector :deep(.el-select-dropdown__item:hover) {
  background-color: #4b5563 !important;
}

.dark .language-selector :deep(.el-input__inner) {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
}

.dark .language-selector :deep(.el-input__suffix) {
  color: #9ca3af !important;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .language-option-content {
    @apply gap-2;
  }
  
  .language-flag {
    @apply text-base;
  }
  
  .language-native {
    @apply text-sm;
  }
  
  .language-english {
    @apply text-xs;
  }
}
</style>