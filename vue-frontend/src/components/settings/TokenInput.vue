<template>
  <div class="token-input">
    <el-form-item 
      :label="$t('settings.api.token.label')"
      :prop="prop"
      :rules="rules"
    >
      <div class="token-field">
        <el-input
          v-model="localValue"
          :type="showToken ? 'text' : 'password'"
          :placeholder="$t('settings.api.token.placeholder')"
          :disabled="disabled"
          clearable
          show-password
          @input="handleInput"
          @blur="handleBlur"
          class="token-input-field"
        >
          <template #suffix>
            <div class="input-actions">
              <el-button
                v-if="localValue && !isValidating"
                type="primary"
                link
                size="small"
                @click="validateToken"
                :disabled="disabled"
                class="validate-btn"
              >
                {{ $t('settings.api.token.validate') }}
              </el-button>
              <el-icon 
                v-if="isValidating"
                class="is-loading"
              >
                <Loading />
              </el-icon>
              <el-icon 
                v-else-if="validationStatus === 'valid'"
                class="validation-icon valid"
              >
                <Check />
              </el-icon>
              <el-icon 
                v-else-if="validationStatus === 'invalid'"
                class="validation-icon invalid"
              >
                <Close />
              </el-icon>
            </div>
          </template>
        </el-input>
      </div>
      
      <div class="token-help" v-if="showHelp">
        <el-text size="small" type="info">
          {{ $t('settings.api.token.help') }}
        </el-text>
      </div>
      
      <div class="validation-message" v-if="validationMessage">
        <el-text 
          size="small" 
          :type="validationStatus === 'valid' ? 'success' : 'danger'"
        >
          {{ validationMessage }}
        </el-text>
      </div>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, Close, Loading } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'

interface Props {
  modelValue: string
  disabled?: boolean
  showHelp?: boolean
  prop?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'validate', valid: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  showHelp: true,
  prop: 'token'
})

const emit = defineEmits<Emits>()

const { t } = useI18n()
const settingsStore = useSettingsStore()

// 本地狀態
const localValue = ref(props.modelValue)
const showToken = ref(false)
const isValidating = ref(false)
const validationStatus = ref<'valid' | 'invalid' | null>(null)
const validationMessage = ref('')

// 計算屬性
const rules = computed(() => [
  {
    required: true,
    message: t('settings.api.token.required'),
    trigger: 'blur'
  },
  {
    min: 32,
    message: t('settings.api.token.tooShort'),
    trigger: 'blur'
  },
  {
    pattern: /^[A-Za-z0-9_\-]+$/,
    message: t('settings.api.token.invalidFormat'),
    trigger: 'blur'
  }
])

// 監聽prop變化
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
  // 清除驗證狀態
  if (newValue !== localValue.value) {
    clearValidation()
  }
})

// 監聽本地值變化
watch(localValue, (newValue) => {
  if (newValue !== props.modelValue) {
    clearValidation()
  }
})

// 方法
const handleInput = (value: string) => {
  emit('update:modelValue', value)
  clearValidation()
}

const handleBlur = () => {
  // 自動驗證Token（如果有值）
  if (localValue.value && localValue.value.length >= 32) {
    validateToken()
  }
}

const validateToken = async () => {
  if (!localValue.value) {
    return
  }

  isValidating.value = true
  validationStatus.value = null
  validationMessage.value = ''

  try {
    const isValid = await settingsStore.verifyToken(localValue.value)
    
    if (isValid) {
      validationStatus.value = 'valid'
      validationMessage.value = t('settings.api.token.valid')
      emit('validate', true)
    } else {
      validationStatus.value = 'invalid'
      validationMessage.value = t('settings.api.token.invalid')
      emit('validate', false)
    }
  } catch (error) {
    validationStatus.value = 'invalid'
    validationMessage.value = error instanceof Error ? error.message : t('settings.api.token.invalid')
    emit('validate', false)
  } finally {
    isValidating.value = false
  }
}

const clearValidation = () => {
  validationStatus.value = null
  validationMessage.value = ''
}

// 暴露方法
defineExpose({
  validateToken,
  clearValidation
})
</script>

<style scoped>
.token-input {
  @apply w-full;
}

.token-field {
  @apply relative;
}

.token-input-field {
  @apply w-full;
}

.token-input-field :deep(.el-input__inner) {
  @apply font-mono text-sm;
}

.input-actions {
  @apply flex items-center gap-2;
}

.validate-btn {
  @apply text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300;
  @apply text-xs px-2 py-1;
}

.validation-icon {
  @apply text-lg;
}

.validation-icon.valid {
  @apply text-green-500;
}

.validation-icon.invalid {
  @apply text-red-500;
}

.token-help {
  @apply mt-2;
}

.validation-message {
  @apply mt-2;
}

/* Loading 動畫 */
.is-loading {
  @apply animate-spin text-blue-500;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .validate-btn {
    @apply hidden;
  }
}
</style>