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
        label-position="top"
        class="settings-form"
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
import { ref, reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, type FormInstance } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'
import { setLocale } from '@/i18n'
import type { Settings } from '@/types/settings'

const { t } = useI18n()
const settingsStore = useSettingsStore()

// 表單引用
const formRef = ref<FormInstance>()

// 狀態
const saving = ref(false)

// 表單數據
const formData = reactive<Settings>({ ...settingsStore.settings })

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
    
    ElMessage.success(t('settings.messages.saveSuccess'))
  } catch (error) {
    ElMessage.error(t('settings.messages.saveFailed', {
      error: error instanceof Error ? error.message : '未知錯誤'
    }))
  } finally {
    saving.value = false
  }
}

// 生命週期
onMounted(async () => {
  try {
    await settingsStore.initialize()
    Object.assign(formData, settingsStore.settings)
    
    // 確保語言設定正確應用
    if (formData.user.language) {
      await setLocale(formData.user.language)
    }
  } catch (error) {
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