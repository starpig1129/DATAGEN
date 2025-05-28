<template>
  <div class="settings-page">
    <!-- 頁面頭部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ $t('settings.title') }}</h1>
        <p class="page-description">{{ $t('settings.description') }}</p>
      </div>
    </div>
    
    <!-- 主要內容 -->
    <div class="settings-content">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        class="settings-form"
        @validate="handleValidation"
      >
        <!-- API配置區域 -->
        <div class="settings-section">
          <div class="section-header">
            <div class="section-info">
              <h3 class="section-title">{{ $t('settings.sections.api') }}</h3>
              <p class="section-description">{{ $t('settings.api.description') }}</p>
            </div>
          </div>
          
          <div class="section-content">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- OpenAI API Key (必填) -->
              <el-form-item
                :label="$t('settings.api.openaiApiKey.label')"
                prop="api.openaiApiKey"
                :required="true"
              >
                <el-input
                  v-model="formData.api.openaiApiKey"
                  type="password"
                  :placeholder="$t('settings.api.openaiApiKey.placeholder')"
                  show-password
                  clearable
                />
                <div class="form-help-text">
                  {{ $t('settings.api.openaiApiKey.help') }}
                </div>
              </el-form-item>
              
              <!-- Firecrawl API Key (可選) -->
              <el-form-item
                :label="$t('settings.api.firecrawlApiKey.label')"
                prop="api.firecrawlApiKey"
              >
                <el-input
                  v-model="formData.api.firecrawlApiKey"
                  type="password"
                  :placeholder="$t('settings.api.firecrawlApiKey.placeholder')"
                  show-password
                  clearable
                />
                <div class="form-help-text">
                  {{ $t('settings.api.firecrawlApiKey.help') }}
                </div>
              </el-form-item>
              
              <!-- LangChain API Key (可選) -->
              <el-form-item
                :label="$t('settings.api.langchainApiKey.label')"
                prop="api.langchainApiKey"
              >
                <el-input
                  v-model="formData.api.langchainApiKey"
                  type="password"
                  :placeholder="$t('settings.api.langchainApiKey.placeholder')"
                  show-password
                  clearable
                />
                <div class="form-help-text">
                  {{ $t('settings.api.langchainApiKey.help') }}
                </div>
              </el-form-item>
              
              <el-form-item
                :label="$t('settings.api.baseUrl.label')"
                prop="api.baseUrl"
              >
                <el-input
                  v-model="formData.api.baseUrl"
                  :placeholder="$t('settings.api.baseUrl.placeholder')"
                  clearable
                />
              </el-form-item>
            </div>
          </div>
        </div>
        
        <!-- 系統路徑配置區域 -->
        <div class="settings-section">
          <div class="section-header">
            <div class="section-info">
              <h3 class="section-title">{{ $t('settings.sections.system') }}</h3>
              <p class="section-description">{{ $t('settings.system.description') }}</p>
            </div>
          </div>
          
          <div class="section-content">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <el-form-item
                :label="$t('settings.system.workingDirectory.label')"
                prop="api.workingDirectory"
              >
                <el-input
                  v-model="formData.api.workingDirectory"
                  :placeholder="$t('settings.system.workingDirectory.placeholder')"
                  clearable
                />
                <div class="form-help-text">
                  {{ $t('settings.system.workingDirectory.help') }}
                </div>
              </el-form-item>
              
              <el-form-item
                :label="$t('settings.system.condaPath.label')"
                prop="api.condaPath"
              >
                <el-input
                  v-model="formData.api.condaPath"
                  :placeholder="$t('settings.system.condaPath.placeholder')"
                  clearable
                />
                <div class="form-help-text">
                  {{ $t('settings.system.condaPath.help') }}
                </div>
              </el-form-item>
              
              <el-form-item
                :label="$t('settings.system.condaEnv.label')"
                prop="api.condaEnv"
              >
                <el-input
                  v-model="formData.api.condaEnv"
                  :placeholder="$t('settings.system.condaEnv.placeholder')"
                  clearable
                />
                <div class="form-help-text">
                  {{ $t('settings.system.condaEnv.help') }}
                </div>
              </el-form-item>
              
              <el-form-item
                :label="$t('settings.system.chromedriverPath.label')"
                prop="api.chromedriverPath"
              >
                <el-input
                  v-model="formData.api.chromedriverPath"
                  :placeholder="$t('settings.system.chromedriverPath.placeholder')"
                  clearable
                />
                <div class="form-help-text">
                  {{ $t('settings.system.chromedriverPath.help') }}
                </div>
              </el-form-item>
            </div>
          </div>
        </div>
        
        <!-- 用戶偏好區域 -->
        <div class="settings-section">
          <div class="section-header">
            <div class="section-info">
              <h3 class="section-title">{{ $t('settings.sections.user') }}</h3>
              <p class="section-description">{{ $t('settings.user.description') }}</p>
            </div>
          </div>
          
          <div class="section-content">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <el-form-item 
                :label="$t('settings.user.language.label')"
                prop="user.language"
              >
                <el-select
                  v-model="formData.user.language"
                  :placeholder="$t('settings.user.language.help')"
                  class="w-full"
                >
                  <el-option value="zh-TW" label="繁體中文" />
                  <el-option value="zh-CN" label="简体中文" />
                  <el-option value="en-US" label="English" />
                </el-select>
              </el-form-item>
              
              <el-form-item 
                :label="$t('settings.user.theme.label')"
                prop="user.theme"
              >
                <el-select
                  v-model="formData.user.theme"
                  :placeholder="$t('settings.user.theme.help')"
                  class="w-full"
                >
                  <el-option value="light" :label="$t('settings.user.theme.light')" />
                  <el-option value="dark" :label="$t('settings.user.theme.dark')" />
                  <el-option value="auto" :label="$t('settings.user.theme.auto')" />
                </el-select>
              </el-form-item>
            </div>
          </div>
        </div>
      </el-form>
    </div>
    
    <!-- 保存按鈕 -->
    <div class="fixed-actions">
      <div class="actions-content">
        <el-button type="primary" @click="saveSettings" :loading="saving">
          {{ $t('settings.actions.save') }}
        </el-button>
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, type FormInstance, type FormRules, type FormItemProp } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'
import { setLocale } from '@/i18n'
import type { Settings } from '@/types/settings'

const { t } = useI18n()
const settingsStore = useSettingsStore()

// 表單引用
const formRef = ref<FormInstance>()

// 狀態
const saving = ref(false)
const validationErrors = ref<Record<string, string[]>>({})

// 表單數據
const formData = reactive<Settings>({ ...settingsStore.settings })

// 確保表單數據有適當的預設值
const ensureFormDataIntegrity = () => {
  // 確保 api 物件完整
  if (!formData.api) {
    formData.api = { ...settingsStore.settings.api }
  }
  
  // 確保必要的數值有預設值
  if (!formData.api.baseUrl) {
    formData.api.baseUrl = 'http://localhost:5001'
  }
  if (!formData.api.timeout) {
    formData.api.timeout = 30000
  }
  if (!formData.api.retryAttempts) {
    formData.api.retryAttempts = 3
  }
  
  // 確保 user 物件完整
  if (!formData.user) {
    formData.user = { ...settingsStore.settings.user }
  }
  
  // 確保 agent 和 data 物件存在（即使 SettingsSimple 不顯示）
  if (!formData.agent) {
    formData.agent = { ...settingsStore.settings.agent }
  }
  if (!formData.data) {
    formData.data = { ...settingsStore.settings.data }
  }
  
}

// 初始化時確保預設值
ensureFormDataIntegrity()



// 表單驗證規則
const formRules = computed<FormRules>(() => ({
  'api.openaiApiKey': [
    {
      validator: (rule: any, value: string, callback: any) => {
        // 如果值為空，只有在用戶已經開始編輯時才要求必填
        if (!value || value.trim() === '') {
          // 檢查是否有任何表單欄位被修改過
          const hasAnyInput = formData.api.firecrawlApiKey ||
                             formData.api.langchainApiKey ||
                             formData.api.baseUrl !== 'http://localhost:5001' ||
                             formData.user.language !== 'zh-TW' ||
                             formData.user.theme !== 'auto'
          
          if (!hasAnyInput && !settingsStore.isDirty) {
            callback() // 初始狀態且無其他輸入時不要求必填
          } else {
            callback(new Error(t('settings.validation.required')))
          }
        } else if (value.length < 20) {
          callback(new Error(t('settings.validation.tooShort')))
        } else if (!/^sk-[a-zA-Z0-9_-]+$/.test(value)) {
          callback(new Error(t('settings.validation.invalidFormat')))
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change']
    }
  ],
  'api.firecrawlApiKey': [
    {
      validator: (rule: any, value: string, callback: any) => {
        if (!value || value.trim() === '') {
          callback() // 空值時不驗證
        } else if (!/^fc-[a-zA-Z0-9_-]+$/.test(value)) {
          callback(new Error(t('settings.validation.invalidFormat')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  'api.langchainApiKey': [
    {
      validator: (rule: any, value: string, callback: any) => {
        if (!value || value.trim() === '') {
          callback() // 空值時不驗證
        } else if (!/^lsv2_pt_[a-zA-Z0-9_]+$/.test(value)) {
          callback(new Error(t('settings.validation.invalidFormat')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  'api.baseUrl': [
    {
      validator: (rule: any, value: string, callback: any) => {
        if (!value || value.trim() === '') {
          callback() // 空值時不驗證，使用預設值
        } else {
          // 檢查是否為有效的 URL 格式
          try {
            new URL(value)
            callback()
          } catch {
            // 如果不是完整 URL，檢查是否為有效的 http/https URL 格式
            if (!/^https?:\/\/.+/.test(value)) {
              callback(new Error(t('settings.validation.invalidUrl')))
            } else {
              callback()
            }
          }
        }
      },
      trigger: 'blur'
    }
  ],
  // 添加 Settings.vue 中存在的其他驗證規則
  'api.timeout': [
    {
      type: 'number',
      min: 1000,
      max: 300000,
      message: t('settings.validation.outOfRange'),
      trigger: 'blur'
    }
  ],
  'api.retryAttempts': [
    {
      type: 'number',
      min: 0,
      max: 10,
      message: t('settings.validation.outOfRange'),
      trigger: 'blur'
    }
  ],
  // 用戶設定驗證規則
  'user.language': [
    {
      required: false,
      trigger: 'change'
    }
  ],
  'user.theme': [
    {
      required: false,
      trigger: 'change'
    }
  ],
  // 系統路徑驗證（較寬鬆）
  'api.workingDirectory': [
    {
      required: false,
      trigger: 'blur'
    }
  ],
  'api.condaPath': [
    {
      required: false,
      trigger: 'blur'
    }
  ],
  'api.condaEnv': [
    {
      required: false,
      trigger: 'blur'
    }
  ],
  'api.chromedriverPath': [
    {
      required: false,
      trigger: 'blur'
    }
  ]
}))

// 處理驗證事件
const handleValidation = (prop: FormItemProp, isValid: boolean, message: string) => {
  const propKey = Array.isArray(prop) ? prop.join('.') : String(prop)
  if (!isValid) {
    if (!validationErrors.value[propKey]) {
      validationErrors.value[propKey] = []
    }
    if (!validationErrors.value[propKey].includes(message)) {
      validationErrors.value[propKey].push(message)
    }
  } else {
    delete validationErrors.value[propKey]
  }
}

// 驗證整個表單
const validateForm = async (): Promise<boolean> => {
  if (!formRef.value) {
    return false
  }
  
  try {
    await formRef.value.validate()
    return true
  } catch (error) {
    ElMessage.error(t('settings.validation.formHasErrors'))
    return false
  }
}

// 驗證特定字段
const validateField = async (prop: string): Promise<boolean> => {
  if (!formRef.value) return false
  
  try {
    await formRef.value.validateField(prop)
    return true
  } catch (error) {
    return false
  }
}

// 清除驗證錯誤
const clearValidation = () => {
  validationErrors.value = {}
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 監聽語言變更
watch(() => formData.user.language, async (newLanguage) => {
  try {
    await setLocale(newLanguage)
    console.log('語言已切換為:', newLanguage)
  } catch (error) {
    console.error('語言切換失敗:', error)
  }
})

// 保存設定
const saveSettings = async () => {
  // 先標記為髒數據，確保驗證邏輯正確工作
  if (!settingsStore.isDirty) {
    settingsStore.markDirty()
  }
  
  // 檢查基本配置
  if (!formData.api.baseUrl || formData.api.baseUrl.trim() === '') {
    ElMessage.error('API 基礎 URL 是必填項目，無法保存設定')
    return
  }
  
  // 如果 OpenAI API Key 為空，提示用戶是否繼續
  if (!formData.api.openaiApiKey || formData.api.openaiApiKey.trim() === '') {
    const shouldContinue = confirm('OpenAI API Key 為空，這將影響系統功能。是否仍要保存設定？')
    if (!shouldContinue) {
      return
    }
  }
  
  // 先驗證表單
  const isValid = await validateForm()
  if (!isValid) {
    // 如果只是 OpenAI API Key 的問題，允許用戶選擇繼續
    const errors = Object.keys(validationErrors.value)
    if (errors.length === 1 && errors[0] === 'api.openaiApiKey') {
      const shouldContinue = confirm('僅 OpenAI API Key 驗證失敗。是否仍要保存其他設定？')
      if (!shouldContinue) {
        return
      }
    } else {
      return
    }
  }

  saving.value = true
  try {
    // 更新設定store
    settingsStore.updateApiConfig(formData.api)
    settingsStore.updateUserPreferences(formData.user)
    
    // 應用語言變更
    if (formData.user.language !== settingsStore.currentLanguage) {
      await setLocale(formData.user.language)
    }
    
    // 保存到本地和服務器
    await settingsStore.saveSettings()
    
    // 清除驗證錯誤
    clearValidation()
    
    ElMessage.success(t('settings.messages.saveSuccess'))
    
  } catch (error) {
    console.error('保存設定錯誤:', error)
    
    // 處理不同類型的錯誤
    let errorMessage = '保存設定失敗'
    
    if (error instanceof Error) {
      if (error.message.includes('baseUrl') || error.message.includes('API baseUrl')) {
        errorMessage = 'API 基礎 URL 配置錯誤，請檢查設定'
      } else if (error.message.includes('timeout') || error.message.includes('TIMEOUT')) {
        errorMessage = '請求超時，請檢查網絡連接和伺服器狀態'
      } else if (error.message.includes('network') || error.message.includes('NETWORK_ERROR')) {
        errorMessage = '網絡錯誤，請檢查連接和伺服器 URL'
      } else if (error.message.includes('同步失敗') || error.message.includes('Sync failed')) {
        errorMessage = `伺服器同步失敗: ${error.message}`
      } else {
        errorMessage = `保存失敗: ${error.message}`
      }
    }
    
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}


// 生命週期
onMounted(async () => {
  try {
    await settingsStore.initialize()
    
    // 重新同步 formData
    Object.assign(formData, settingsStore.settings)
    
    // 再次確保完整性
    ensureFormDataIntegrity()
    
    // 確保語言設定正確應用
    if (formData.user.language) {
      await setLocale(formData.user.language)
    }
    
    // 清除任何初始驗證錯誤
    if (formRef.value) {
      await nextTick()
      formRef.value.clearValidate()
    }
  } catch (error) {
    console.error('設定初始化失敗:', error)
    ElMessage.error('設定初始化失敗')
  }
})
</script>

<style scoped>
.settings-page {
  @apply min-h-screen bg-gray-50 dark:bg-gray-900 pb-20;
}

.page-header {
  @apply bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4;
}

.header-content {
  @apply max-w-7xl mx-auto;
}

.page-title {
  @apply text-2xl font-bold text-gray-900 dark:text-white m-0;
}

.page-description {
  @apply text-gray-600 dark:text-gray-400 mt-1 m-0;
}

.settings-content {
  @apply max-w-7xl mx-auto px-6 py-6;
}

.settings-form {
  @apply space-y-8;
}

.settings-section {
  @apply bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden;
}

.section-header {
  @apply flex items-start justify-between gap-4 p-6 border-b border-gray-200 dark:border-gray-700;
}

.section-info {
  @apply flex-1;
}

.section-title {
  @apply text-lg font-semibold text-gray-900 dark:text-white mb-1;
}

.section-description {
  @apply text-sm text-gray-600 dark:text-gray-400 m-0;
}

.section-content {
  @apply p-6;
}

.fixed-actions {
  @apply fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4 shadow-lg;
}

.actions-content {
  @apply max-w-7xl mx-auto flex justify-end;
}

.form-help-text {
  @apply text-xs text-gray-500 dark:text-gray-400 mt-1;
}

</style>