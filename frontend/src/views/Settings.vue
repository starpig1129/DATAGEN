<template>
  <div class="settings-page">
    <!-- 頁面頭部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ $t('settings.title') }}</h1>
        <p class="page-description">{{ $t('settings.description') }}</p>
      </div>
      
      <div class="header-actions">
        <el-button
          v-if="settingsStore.isDirty"
          type="primary"
          :loading="saving"
          @click="saveSettings"
        >
          <el-icon class="mr-1"><Check /></el-icon>
          {{ $t('settings.actions.save') }}
        </el-button>
        
        <el-dropdown @command="handleCommand">
          <el-button>
            <el-icon class="mr-1"><More /></el-icon>
            {{ $t('settings.actions.more') }}
            <el-icon class="ml-1"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="reset">
                <el-icon><RefreshLeft /></el-icon>
                {{ $t('settings.actions.reset') }}
              </el-dropdown-item>
              <el-dropdown-item command="export">
                <el-icon><Download /></el-icon>
                {{ $t('settings.actions.export') }}
              </el-dropdown-item>
              <el-dropdown-item command="import">
                <el-icon><Upload /></el-icon>
                {{ $t('settings.actions.import') }}
              </el-dropdown-item>
              <el-dropdown-item divided command="backup">
                <el-icon><FolderAdd /></el-icon>
                {{ $t('settings.actions.backup') }}
              </el-dropdown-item>
              <el-dropdown-item command="restore">
                <el-icon><FolderOpened /></el-icon>
                {{ $t('settings.actions.restore') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
        @submit.prevent="saveSettings"
        @validate="handleValidation"
      >
        <!-- API配置區域 -->
        <SettingsSection
          :title="$t('settings.sections.api')"
          :description="$t('settings.api.description')"
          :icon="Connection"
          class="mb-6"
        >
          <template #actions>
            <ConnectionTest
              :disabled="!settingsStore.isApiConfigured"
              @test-complete="handleConnectionTest"
            />
          </template>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- OpenAI API Key (必填) -->
            <div class="col-span-1 lg:col-span-2">
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
                <div class="form-help">
                  <el-text size="small" type="info">
                    {{ $t('settings.api.openaiApiKey.help') }}
                  </el-text>
                </div>
              </el-form-item>
            </div>
            
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
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.api.firecrawlApiKey.help') }}
                </el-text>
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
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.api.langchainApiKey.help') }}
                </el-text>
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
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.api.baseUrl.help') }}
                </el-text>
              </div>
            </el-form-item>
            
            <el-form-item 
              :label="$t('settings.api.timeout.label')" 
              prop="api.timeout"
            >
              <el-input-number
                v-model="formData.api.timeout"
                :min="1000"
                :max="300000"
                :step="1000"
                controls-position="right"
                class="w-full"
              />
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.api.timeout.help') }} ({{ $t('settings.api.timeout.unit') }})
                </el-text>
              </div>
            </el-form-item>
            
            <el-form-item 
              :label="$t('settings.api.retryAttempts.label')" 
              prop="api.retryAttempts"
            >
              <el-input-number
                v-model="formData.api.retryAttempts"
                :min="0"
                :max="10"
                controls-position="right"
                class="w-full"
              />
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.api.retryAttempts.help') }}
                </el-text>
              </div>
            </el-form-item>
            
            <el-form-item 
              :label="$t('settings.api.enableLogging.label')" 
              prop="api.enableLogging"
            >
              <el-switch
                v-model="formData.api.enableLogging"
                :active-text="$t('common.yes')"
                :inactive-text="$t('common.no')"
              />
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.api.enableLogging.help') }}
                </el-text>
              </div>
            </el-form-item>
          </div>
        </SettingsSection>
        
        <!-- 系統路徑配置區域 -->
        <SettingsSection
          :title="$t('settings.sections.system')"
          :description="$t('settings.system.description')"
          :icon="Setting"
          class="mb-6"
        >
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
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.system.workingDirectory.help') }}
                </el-text>
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
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.system.condaPath.help') }}
                </el-text>
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
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.system.condaEnv.help') }}
                </el-text>
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
              <div class="form-help">
                <el-text size="small" type="info">
                  {{ $t('settings.system.chromedriverPath.help') }}
                </el-text>
              </div>
            </el-form-item>
          </div>
        </SettingsSection>
        
        <!-- 用戶偏好區域 -->
        <SettingsSection
          :title="$t('settings.sections.user')"
          :description="$t('settings.user.description')"
          :icon="User"
          class="mb-6"
        >
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="col-span-1 lg:col-span-2">
              <LanguageSelector
                v-model="formData.user.language"
                prop="user.language"
                @change="handleLanguageChange"
              />
            </div>
            
            <div class="col-span-1 lg:col-span-2">
              <ThemeToggle
                v-model="formData.user.theme"
                prop="user.theme"
                @change="handleThemeChange"
              />
            </div>
            
            <el-form-item 
              :label="$t('settings.user.timezone.label')" 
              prop="user.timezone"
            >
              <el-select
                v-model="formData.user.timezone"
                filterable
                :placeholder="$t('settings.user.timezone.help')"
                class="w-full"
              >
                <el-option
                  v-for="tz in availableTimezones"
                  :key="tz.value"
                  :value="tz.value"
                  :label="tz.label"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item 
              :label="$t('settings.user.dateFormat.label')" 
              prop="user.dateFormat"
            >
              <el-select
                v-model="formData.user.dateFormat"
                :placeholder="$t('settings.user.dateFormat.help')"
                class="w-full"
              >
                <el-option
                  v-for="format in availableDateFormats"
                  :key="format.value"
                  :value="format.value"
                  :label="format.label"
                />
              </el-select>
            </el-form-item>
          </div>
          
          <!-- 通知設定 -->
          <div class="mt-8">
            <h4 class="section-subtitle">{{ $t('settings.user.notifications.title') }}</h4>
            
            <div class="notification-settings">
              <el-form-item prop="user.notifications.enabled">
                <el-switch
                  v-model="formData.user.notifications.enabled"
                  :active-text="$t('settings.user.notifications.enabled')"
                  :inactive-text="$t('common.no')"
                  inline-prompt
                />
              </el-form-item>
              
              <div v-if="formData.user.notifications.enabled" class="notification-types">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <el-form-item
                    v-for="(label, type) in notificationTypeLabels"
                    :key="type"
                    :prop="`user.notifications.types.${type}`"
                  >
                    <el-checkbox
                      v-model="formData.user.notifications.types[type]"
                      :label="label"
                    />
                  </el-form-item>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                  <el-form-item prop="user.notifications.sound">
                    <el-checkbox
                      v-model="formData.user.notifications.sound"
                      :label="$t('settings.user.notifications.sound')"
                    />
                  </el-form-item>
                  
                  <el-form-item prop="user.notifications.vibration">
                    <el-checkbox
                      v-model="formData.user.notifications.vibration"
                      :label="$t('settings.user.notifications.vibration')"
                    />
                  </el-form-item>
                  
                  <el-form-item prop="user.notifications.desktop">
                    <el-checkbox
                      v-model="formData.user.notifications.desktop"
                      :label="$t('settings.user.notifications.desktop')"
                    />
                  </el-form-item>
                </div>
                
                <!-- 靜音時段 -->
                <div class="quiet-hours mt-6">
                  <el-form-item prop="user.notifications.quietHours.enabled">
                    <el-checkbox
                      v-model="formData.user.notifications.quietHours.enabled"
                      :label="$t('settings.user.notifications.quietHours.title')"
                    />
                  </el-form-item>
                  
                  <div v-if="formData.user.notifications.quietHours.enabled" class="grid grid-cols-2 gap-4 mt-4">
                    <el-form-item
                      :label="$t('settings.user.notifications.quietHours.startTime')"
                      prop="user.notifications.quietHours.startTime"
                    >
                      <el-time-select
                        v-model="formData.user.notifications.quietHours.startTime"
                        start="00:00"
                        step="00:30"
                        end="23:30"
                        :placeholder="$t('settings.user.notifications.quietHours.startTime')"
                        class="w-full"
                      />
                    </el-form-item>
                    
                    <el-form-item
                      :label="$t('settings.user.notifications.quietHours.endTime')"
                      prop="user.notifications.quietHours.endTime"
                    >
                      <el-time-select
                        v-model="formData.user.notifications.quietHours.endTime"
                        start="00:00"
                        step="00:30"
                        end="23:30"
                        :placeholder="$t('settings.user.notifications.quietHours.endTime')"
                        class="w-full"
                      />
                    </el-form-item>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 界面設定 -->
          <div class="mt-8">
            <h4 class="section-subtitle">{{ $t('settings.user.interface.title') }}</h4>
            
            <div class="interface-settings">
              <!-- 開關選項 -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <el-form-item
                  :label="$t('settings.user.interface.sidebarCollapsed')"
                  prop="user.interface.sidebarCollapsed"
                >
                  <el-switch
                    v-model="formData.user.interface.sidebarCollapsed"
                    :active-text="$t('common.yes')"
                    :inactive-text="$t('common.no')"
                    inline-prompt
                  />
                </el-form-item>
                
                <el-form-item
                  :label="$t('settings.user.interface.compactMode')"
                  prop="user.interface.compactMode"
                >
                  <el-switch
                    v-model="formData.user.interface.compactMode"
                    :active-text="$t('common.yes')"
                    :inactive-text="$t('common.no')"
                    inline-prompt
                  />
                </el-form-item>
                
                <el-form-item
                  :label="$t('settings.user.interface.showToolbar')"
                  prop="user.interface.showToolbar"
                >
                  <el-switch
                    v-model="formData.user.interface.showToolbar"
                    :active-text="$t('common.yes')"
                    :inactive-text="$t('common.no')"
                    inline-prompt
                  />
                </el-form-item>
                
                <el-form-item
                  :label="$t('settings.user.interface.animationsEnabled')"
                  prop="user.interface.animationsEnabled"
                >
                  <el-switch
                    v-model="formData.user.interface.animationsEnabled"
                    :active-text="$t('common.yes')"
                    :inactive-text="$t('common.no')"
                    inline-prompt
                  />
                </el-form-item>
              </div>
              
              <!-- 下拉選項 -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <el-form-item
                  :label="$t('settings.user.interface.fontSize.label')"
                  prop="user.interface.fontSize"
                >
                  <el-select
                    v-model="formData.user.interface.fontSize"
                    :placeholder="$t('settings.user.interface.fontSize.label')"
                    class="w-full"
                  >
                    <el-option
                      value="small"
                      :label="$t('settings.user.interface.fontSize.small')"
                    />
                    <el-option
                      value="medium"
                      :label="$t('settings.user.interface.fontSize.medium')"
                    />
                    <el-option
                      value="large"
                      :label="$t('settings.user.interface.fontSize.large')"
                    />
                  </el-select>
                </el-form-item>
                
                <el-form-item
                  :label="$t('settings.user.interface.density.label')"
                  prop="user.interface.density"
                >
                  <el-select
                    v-model="formData.user.interface.density"
                    :placeholder="$t('settings.user.interface.density.label')"
                    class="w-full"
                  >
                    <el-option
                      value="comfortable"
                      :label="$t('settings.user.interface.density.comfortable')"
                    />
                    <el-option
                      value="compact"
                      :label="$t('settings.user.interface.density.compact')"
                    />
                    <el-option
                      value="spacious"
                      :label="$t('settings.user.interface.density.spacious')"
                    />
                  </el-select>
                </el-form-item>
              </div>
            </div>
          </div>
        </SettingsSection>
        
        <!-- 代理設定區域 -->
        <SettingsSection
          :title="$t('settings.sections.agent')"
          :description="$t('settings.agent.description')"
          :icon="Robot"
          class="mb-6"
        >
          <AgentSettings
            v-model="formData.agent"
            @change="handleAgentSettingsChange"
          />
        </SettingsSection>
        
        <!-- 數據設定區域 -->
        <SettingsSection
          :title="$t('settings.sections.data')"
          :description="$t('settings.data.description')"
          :icon="Database"
          class="mb-6"
        >
          <DataSettings
            v-model="formData.data"
            @change="handleDataSettingsChange"
          />
        </SettingsSection>
      </el-form>
    </div>
    
    <!-- 固定底部操作欄 -->
    <div v-if="settingsStore.isDirty" class="fixed-actions">
      <div class="actions-content">
        <div class="actions-info">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ $t('settings.messages.unsavedChanges') }}</span>
        </div>
        <div class="actions-buttons">
          <el-button @click="cancelChanges">
            {{ $t('settings.actions.cancel') }}
          </el-button>
          <el-button 
            type="primary" 
            :loading="saving"
            @click="saveSettings"
          >
            {{ $t('settings.actions.save') }}
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 文件上傳輸入 -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".json"
      style="display: none"
      @change="handleFileImport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type FormItemProp } from 'element-plus'
import {
  Check,
  More,
  ArrowDown,
  RefreshLeft,
  Download,
  Upload,
  FolderAdd,
  FolderOpened,
  Connection,
  User,
  InfoFilled,
  Setting,
  Tools as Robot,
  DataBoard as Database
} from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'
import { setLocale } from '@/i18n'
import type { Settings, LanguageCode } from '@/types/settings'

// 組件
import SettingsSection from '@/components/settings/SettingsSection.vue'
import LanguageSelector from '@/components/settings/LanguageSelector.vue'
import ThemeToggle from '@/components/settings/ThemeToggle.vue'
import ConnectionTest from '@/components/settings/ConnectionTest.vue'
import AgentSettings from '@/components/settings/AgentSettings.vue'
import DataSettings from '@/components/settings/DataSettings.vue'

const { t } = useI18n()
const settingsStore = useSettingsStore()

// 表單引用
const formRef = ref<FormInstance>()
const fileInputRef = ref<HTMLInputElement>()

// 狀態
const saving = ref(false)
const loading = ref(false)
const validationErrors = ref<Record<string, string[]>>({})

// 表單數據
const formData = reactive<Settings>({ ...settingsStore.settings })

// 同步設定到表單
watch(() => settingsStore.settings, (newSettings) => {
  Object.assign(formData, newSettings)
}, { deep: true })

// 確保表單數據有適當的預設值
const ensureDefaultValues = () => {
  if (!formData.api.baseUrl) {
    formData.api.baseUrl = 'http://localhost:5001'
  }
  if (!formData.api.timeout) {
    formData.api.timeout = 30000
  }
  if (!formData.api.retryAttempts) {
    formData.api.retryAttempts = 3
  }
}

// 初始化時確保預設值
ensureDefaultValues()

// 監聽表單變化標記為髒數據（防抖處理）
let markDirtyTimeout: number | null = null
watch(formData, () => {
  if (markDirtyTimeout) {
    clearTimeout(markDirtyTimeout)
  }
  markDirtyTimeout = setTimeout(() => {
    if (!settingsStore.isDirty) {
      settingsStore.markDirty()
    }
  }, 300) // 300ms防抖
}, { deep: true })

// 語言變更通過LanguageSelector組件的@change事件處理，避免重複監聽

// 監聽主題變更，即時應用
watch(() => formData.user.theme, (newTheme) => {
  settingsStore.setTheme(newTheme)
  console.log('主題已切換為:', newTheme)
})

// 監聽界面設定變更，即時應用
watch(() => formData.user.interface, (newInterface) => {
  settingsStore.updateInterfaceSettings(newInterface)
  console.log('界面設定已更新:', newInterface)
}, { deep: true })

// 可用時區
const availableTimezones = computed(() => {
  // 常用時區列表
  const commonTimezones = [
    'Asia/Taipei',
    'Asia/Shanghai',
    'Asia/Hong_Kong',
    'Asia/Tokyo',
    'Asia/Seoul',
    'America/New_York',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'UTC'
  ]
  
  return commonTimezones.map((tz: string) => ({
    value: tz,
    label: tz.replace(/_/g, ' ')
  }))
})

// 可用日期格式
const availableDateFormats = [
  { value: 'YYYY-MM-DD', label: '2024-01-15 (YYYY-MM-DD)' },
  { value: 'DD/MM/YYYY', label: '15/01/2024 (DD/MM/YYYY)' },
  { value: 'MM/DD/YYYY', label: '01/15/2024 (MM/DD/YYYY)' },
  { value: 'DD-MM-YYYY', label: '15-01-2024 (DD-MM-YYYY)' }
]

// 通知類型標籤
const notificationTypeLabels = computed(() => ({
  email: t('settings.user.notifications.types.email'),
  browser: t('settings.user.notifications.types.browser'),
  system: t('settings.user.notifications.types.system'),
  chat: t('settings.user.notifications.types.chat'),
  agent: t('settings.user.notifications.types.agent')
}))

// 表單驗證規則
const formRules = computed<FormRules>(() => ({
  'api.openaiApiKey': [
    {
      validator: (_rule: any, value: string, callback: any) => {
        // 如果值為空且是初始狀態，不觸發驗證錯誤
        if (!value || value.trim() === '') {
          if (!settingsStore.isDirty) {
            callback() // 初始狀態不顯示錯誤
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
      validator: (_rule: any, value: string, callback: any) => {
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
      validator: (_rule: any, value: string, callback: any) => {
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
      validator: (_rule: any, value: string, callback: any) => {
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
  'user.notifications.quietHours.startTime': [
    {
      required: false,
      trigger: 'blur'
    }
  ],
  'user.notifications.quietHours.endTime': [
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
  if (!formRef.value) return false
  
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

// 保存時的嚴格驗證
const validateFormForSave = async (): Promise<boolean> => {
  if (!formRef.value) return false
  
  // 檢查必填欄位
  if (!formData.api.openaiApiKey || formData.api.openaiApiKey.trim() === '') {
    ElMessage.error(t('settings.validation.required') + ': OpenAI API Key')
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

// 保存設定
const saveSettings = async () => {
  // 在保存時進行嚴格驗證
  const strictValidation = await validateFormForSave()
  if (!strictValidation) {
    return
  }

  saving.value = true
  try {
    console.log('保存設定數據:', formData)
    
    // 更新設定store
    settingsStore.updateApiConfig(formData.api)
    settingsStore.updateUserPreferences(formData.user)
    settingsStore.updateAgentSettings(formData.agent)
    settingsStore.updateDataSettings(formData.data)
    
    // 應用語言變更
    if (formData.user.language !== settingsStore.currentLanguage) {
      await setLocale(formData.user.language)
    }
    
    // 保存到本地和服務器
    await settingsStore.saveSettings()
    
    // 清除防抖計時器
    if (markDirtyTimeout) {
      clearTimeout(markDirtyTimeout)
      markDirtyTimeout = null
    }
    
    // 清除驗證錯誤
    clearValidation()
    
    ElMessage.success(t('settings.messages.saveSuccess'))
  } catch (error) {
    console.error('Save settings error:', error)
    
    // 處理不同類型的錯誤
    let errorMessage = t('settings.messages.saveFailed', {
      error: t('settings.errors.serverError')
    })
    
    if (error instanceof Error) {
      if (error.message.includes('timeout') || error.message.includes('TIMEOUT')) {
        errorMessage = t('settings.messages.saveTimeout')
      } else if (error.message.includes('network') || error.message.includes('NETWORK_ERROR')) {
        errorMessage = t('settings.messages.saveNetworkError')
      } else if (error.message.includes('permission') || error.message.includes('PERMISSION')) {
        errorMessage = t('settings.messages.saveFailed', {
          error: t('settings.errors.permissionDenied')
        })
      } else if (error.message.includes('validation') || error.message.includes('VALIDATION')) {
        errorMessage = t('settings.messages.saveFailed', {
          error: t('settings.errors.validationError')
        })
      } else {
        errorMessage = t('settings.messages.saveFailed', {
          error: error.message
        })
      }
    }
    
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

// 取消修改
const cancelChanges = () => {
  // 清除防抖計時器
  if (markDirtyTimeout) {
    clearTimeout(markDirtyTimeout)
    markDirtyTimeout = null
  }
  Object.assign(formData, settingsStore.settings)
  settingsStore.isDirty = false
}

// 處理命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'reset':
      await handleReset()
      break
    case 'export':
      handleExport()
      break
    case 'import':
      handleImport()
      break
    case 'backup':
      handleBackup()
      break
    case 'restore':
      await handleRestore()
      break
  }
}

// 重置設定
const handleReset = async () => {
  try {
    await ElMessageBox.confirm(
      t('settings.confirm.resetMessage'),
      t('settings.confirm.resetTitle'),
      {
        type: 'warning',
        confirmButtonText: t('settings.confirm.resetConfirm'),
        cancelButtonText: t('settings.actions.cancel')
      }
    )
    
    settingsStore.resetToDefaults()
    Object.assign(formData, settingsStore.settings)
    ElMessage.success(t('settings.messages.resetSuccess'))
  } catch {
    // 用戶取消
  }
}

// 匯出設定
const handleExport = () => {
  const exportData = settingsStore.exportSettings()
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
    type: 'application/json' 
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `settings-export-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success(t('settings.messages.exportSuccess'))
}

// 匯入設定
const handleImport = () => {
  fileInputRef.value?.click()
}

// 處理文件匯入
const handleFileImport = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  try {
    const text = await file.text()
    const importData = JSON.parse(text)
    
    await settingsStore.importSettings(importData)
    Object.assign(formData, settingsStore.settings)
    
    ElMessage.success(t('settings.messages.importSuccess'))
  } catch (error) {
    let errorMessage = t('settings.messages.importFailed', {
      error: t('settings.errors.fileFormat')
    })
    
    if (error instanceof Error) {
      if (error.message.includes('JSON') || error.message.includes('parse')) {
        errorMessage = t('settings.messages.importFailed', {
          error: t('settings.errors.fileFormat')
        })
      } else if (error.message.includes('validation')) {
        errorMessage = t('settings.messages.importFailed', {
          error: t('settings.errors.validationError')
        })
      } else {
        errorMessage = t('settings.messages.importFailed', {
          error: error.message
        })
      }
    }
    
    ElMessage.error(errorMessage)
  } finally {
    // 清除文件輸入
    target.value = ''
  }
}

// 創建備份
const handleBackup = () => {
  settingsStore.createBackup()
  ElMessage.success(t('settings.messages.backupCreated'))
}

// 恢復備份
const handleRestore = async () => {
  try {
    await ElMessageBox.confirm(
      t('settings.confirm.restoreMessage'),
      t('settings.confirm.restoreTitle'),
      {
        type: 'warning',
        confirmButtonText: t('settings.confirm.restoreConfirm'),
        cancelButtonText: t('settings.actions.cancel')
      }
    )
    
    const restored = settingsStore.restoreBackup()
    if (restored) {
      Object.assign(formData, settingsStore.settings)
      ElMessage.success(t('settings.messages.backupRestored'))
    } else {
      ElMessage.warning(t('settings.messages.noBackupFound'))
    }
  } catch {
    // 用戶取消
  }
}

// 處理連接測試
const handleConnectionTest = (result: any) => {
  console.log('Connection test result:', result)
}


// 處理語言切換
const handleLanguageChange = async (language: LanguageCode) => {
  try {
    await setLocale(language)
    settingsStore.setLanguage(language)
    console.log('Language switched to:', language)
    ElMessage.success(t('settings.messages.languageChanged', { language }))
  } catch (error) {
    console.error('Language switch failed:', error)
    ElMessage.error(t('settings.messages.languageChangeFailed'))
  }
}

// 處理主題切換
const handleThemeChange = (theme: string) => {
  settingsStore.applyTheme()
  ElMessage.success(t('settings.messages.themeChanged', { theme }))
}

// 處理代理設定變更
const handleAgentSettingsChange = (agentSettings: typeof formData.agent) => {
  formData.agent = { ...agentSettings }
  settingsStore.markDirty()
  console.log('Agent settings changed:', agentSettings)
}

// 處理數據設定變更
const handleDataSettingsChange = (dataSettings: typeof formData.data) => {
  formData.data = { ...dataSettings }
  settingsStore.markDirty()
  console.log('Data settings changed:', dataSettings)
}

// 頁面離開前提醒
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (settingsStore.isDirty) {
    e.preventDefault()
    e.returnValue = t('settings.messages.unsavedChanges')
  }
}

// 生命週期
onMounted(async () => {
  loading.value = true
  try {
    await settingsStore.initialize()
    Object.assign(formData, settingsStore.settings)
    
    // 確保預設值正確設定
    ensureDefaultValues()
    
    // 確保語言設定正確應用
    if (formData.user.language) {
      await setLocale(formData.user.language)
    }
    
    // 確保主題設定正確應用
    settingsStore.applyTheme()
    
    // 等待一個 tick 後清除初始驗證錯誤
    await nextTick()
    clearValidation()
  } catch (error) {
    ElMessage.error(t('settings.messages.initializationFailed'))
  } finally {
    loading.value = false
  }
  
  // 監聽頁面離開
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding-bottom: 120px; /* 為固定底部操作欄留出更多空間 */
  transition: all 0.3s ease;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  padding: 24px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 16px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  line-height: 1.2;
}

.page-description {
  color: #64748b;
  margin-top: 8px;
  margin-bottom: 0;
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.settings-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section-subtitle {
  font-size: 1.25rem;
  font-weight: 600;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

.form-help {
  margin-top: 4px;
}

.form-help .el-text {
  color: #64748b;
}

.notification-settings,
.interface-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notification-types {
  margin-top: 16px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05), rgba(103, 194, 58, 0.05));
  border-radius: 12px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  backdrop-filter: blur(5px);
}

.quiet-hours {
  padding: 20px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  backdrop-filter: blur(5px);
}

.fixed-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.98);
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  padding: 16px 24px;
  backdrop-filter: blur(20px);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
  min-height: 80px;
}

.actions-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.actions-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f59e0b;
  font-weight: 500;
}

.actions-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 深色主題增強 */
.dark .settings-page {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.dark .page-header {
  background: rgba(30, 41, 59, 0.95);
  border-bottom-color: rgba(75, 85, 99, 0.5);
}

.dark .page-title {
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dark .page-description {
  color: #94a3b8;
}

.dark .section-subtitle {
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dark .notification-types {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(52, 211, 153, 0.1));
  border-color: rgba(96, 165, 250, 0.2);
}

.dark .quiet-hours {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(16, 185, 129, 0.15));
  border-color: rgba(59, 130, 246, 0.3);
}

.dark .fixed-actions {
  background: rgba(30, 41, 59, 0.98);
  border-top-color: rgba(75, 85, 99, 0.5);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.4);
}

.dark .actions-info {
  color: #fbbf24;
}

/* 深色模式下的字體顏色修復 */
.dark .form-help :deep(.el-text) {
  color: #94a3b8 !important;
}

.dark :deep(.el-form-item__label) {
  color: #f1f5f9 !important;
}

.dark :deep(.el-input__inner) {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
}

.dark :deep(.el-input__inner::placeholder) {
  color: #9ca3af !important;
}

.dark :deep(.el-select .el-input__inner) {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
}

.dark :deep(.el-checkbox__label) {
  color: #f1f5f9 !important;
}

.dark :deep(.el-text) {
  color: #94a3b8 !important;
}

.dark :deep(.el-text--info) {
  color: #94a3b8 !important;
}

.dark :deep(.el-text--success) {
  color: #34d399 !important;
}

.dark :deep(.el-text--danger) {
  color: #f87171 !important;
}

.dark :deep(.el-radio__label) {
  color: #f1f5f9 !important;
}

.dark :deep(.el-switch__label) {
  color: #f1f5f9 !important;
}

.dark :deep(.el-input-number .el-input__inner) {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
}

.dark :deep(.el-time-picker .el-input__inner) {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .page-header {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-actions {
    align-self: stretch;
  }
  
  .settings-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 1.75rem;
  }
  
  .actions-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .actions-buttons {
    align-self: stretch;
  }
  
  .fixed-actions {
    padding: 12px 16px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .settings-form {
    gap: 24px;
  }
  
  .notification-types,
  .quiet-hours {
    padding: 16px;
  }
}

/* 過渡動畫 */
.settings-page * {
  transition: all 0.3s ease;
}

/* 美化按鈕 */
.header-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.header-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.actions-buttons .el-button {
  border-radius: 8px;
  font-weight: 500;
  padding: 12px 24px;
  transition: all 0.3s ease;
}

.actions-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.actions-buttons .el-button--primary {
  background: linear-gradient(135deg, #409eff, #67c23a);
  border: none;
}

.actions-buttons .el-button--primary:hover {
  background: linear-gradient(135deg, #66b1ff, #85ce61);
}
</style>