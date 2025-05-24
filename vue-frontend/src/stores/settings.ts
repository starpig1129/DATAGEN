import { defineStore } from 'pinia'
import type {
  Settings,
  SettingsValidationResult,
  SettingsError,
  SettingsSyncStatus
} from '@/types/settings'
import { DEFAULT_SETTINGS as defaultSettings, SETTINGS_VALIDATION_RULES as validationRules } from '@/types/settings'
import { injectDarkModeStyles, removeDarkModeStyles } from '@/utils/theme-injector'
import { setLocale, getCurrentLocale } from '@/i18n'

// 設定狀態介面
interface SettingsState {
  settings: Settings
  isLoading: boolean
  isDirty: boolean
  syncStatus: SettingsSyncStatus
  validationErrors: SettingsError[]
  lastSaved: string | null
}

// 本地存儲鍵名
const STORAGE_KEYS = {
  SETTINGS: 'app_settings',
  LAST_SYNC: 'settings_last_sync',
  BACKUP: 'settings_backup'
} as const

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    settings: { ...defaultSettings },
    isLoading: false,
    isDirty: false,
    syncStatus: {
      lastSync: '',
      syncing: false,
      conflicts: [],
      errors: []
    },
    validationErrors: [],
    lastSaved: null
  }),

  getters: {
    // 獲取當前主題
    currentTheme: (state) => {
      if (state.settings.user.theme === 'auto') {
        // 檢測系統主題
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return state.settings.user.theme
    },

    // 獲取當前語言
    currentLanguage: (state) => state.settings.user.language,

    // 檢查API是否已配置
    isApiConfigured: (state) => {
      const { openaiApiKey, baseUrl } = state.settings.api
      return Boolean(openaiApiKey && baseUrl)
    },

    // 檢查設定是否有效
    isValid: (state) => state.validationErrors.length === 0,

    // 獲取通知設定
    notificationSettings: (state) => state.settings.user.notifications,

    // 獲取代理設定
    agentSettings: (state) => state.settings.agent,

    // 獲取數據設定
    dataSettings: (state) => state.settings.data,

    // 檢查是否需要同步
    needsSync: (state) => {
      const lastModified = new Date(state.settings.lastModified).getTime()
      const lastSync = state.syncStatus.lastSync ? new Date(state.syncStatus.lastSync).getTime() : 0
      return lastModified > lastSync
    }
  },

  actions: {
    // 初始化設定
    async initialize() {
      this.isLoading = true
      try {
        await this.loadSettings()
        await this.validateSettings()
        
        // 監聽系統主題變化
        this.setupThemeListener()
        
        // 確保語言設定正確應用（避免重複切換）
        const currentLocale = getCurrentLocale()
        if (this.settings.user.language !== currentLocale) {
          await setLocale(this.settings.user.language)
          document.documentElement.setAttribute('lang', this.settings.user.language)
          console.log('✅ 初始化語言已設定為:', this.settings.user.language)
        }
        
        // 確保主題設定正確應用
        await this.applyTheme()
        
        console.log('設定初始化完成，語言:', this.settings.user.language, '主題:', this.currentTheme)
      } catch (error) {
        console.error('設定初始化失敗:', error)
        // 使用預設設定
        this.resetToDefaults()
      } finally {
        this.isLoading = false
      }
    },

    // 從本地存儲載入設定
    async loadSettings() {
      try {
        const savedSettings = localStorage.getItem(STORAGE_KEYS.SETTINGS)
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings) as Settings
          
          // 合併預設設定以確保所有屬性存在
          this.settings = this.mergeWithDefaults(parsed)
          
          console.log('設定已從本地存儲載入')
        } else {
          console.log('未找到已保存的設定，使用預設值')
        }

        // 載入同步狀態
        const lastSync = localStorage.getItem(STORAGE_KEYS.LAST_SYNC)
        if (lastSync) {
          this.syncStatus.lastSync = lastSync
        }
      } catch (error) {
        console.error('載入設定失敗:', error)
        throw error
      }
    },

    // 保存設定到本地存儲
    async saveSettings() {
      try {
        // 創建備份
        this.createBackup()

        // 更新最後修改時間
        this.settings.lastModified = new Date().toISOString()

        // 保存到本地存儲
        localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(this.settings))
        
        this.lastSaved = new Date().toISOString()
        this.isDirty = false

        console.log('設定已保存到本地存儲')

        // 嘗試同步到後端
        await this.syncToServer()
      } catch (error) {
        console.error('保存設定失敗:', error)
        throw error
      }
    },

    // 同步設定到伺服器
    async syncToServer() {
      if (!this.isApiConfigured) {
        console.warn('API未配置，跳過伺服器同步')
        return
      }

      this.syncStatus.syncing = true
      this.syncStatus.errors = []

      try {
        const response = await fetch(`${this.settings.api.baseUrl}/api/settings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.settings.api.token}`
          },
          body: JSON.stringify(this.settings)
        })

        if (!response.ok) {
          throw new Error(`同步失敗: ${response.statusText}`)
        }

        this.syncStatus.lastSync = new Date().toISOString()
        localStorage.setItem(STORAGE_KEYS.LAST_SYNC, this.syncStatus.lastSync)

        console.log('設定已同步到伺服器')
      } catch (error) {
        this.syncStatus.errors.push(error instanceof Error ? error.message : '同步失敗')
        console.error('同步設定到伺服器失敗:', error)
      } finally {
        this.syncStatus.syncing = false
      }
    },

    // 從伺服器載入設定
    async loadFromServer() {
      if (!this.isApiConfigured) {
        throw new Error('API未配置')
      }

      this.isLoading = true
      try {
        const response = await fetch(`${this.settings.api.baseUrl}/api/settings`, {
          headers: {
            'Authorization': `Bearer ${this.settings.api.token}`
          }
        })

        if (!response.ok) {
          throw new Error(`載入失敗: ${response.statusText}`)
        }

        const serverSettings = await response.json() as Settings
        this.settings = this.mergeWithDefaults(serverSettings)
        
        await this.saveSettings()
        console.log('設定已從伺服器載入')
      } catch (error) {
        console.error('從伺服器載入設定失敗:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // 驗證Token有效性
    async verifyToken(token?: string) {
      const tokenToVerify = token || this.settings.api.openaiApiKey
      if (!tokenToVerify) {
        throw new Error('Token為空')
      }

      try {
        const response = await fetch(`${this.settings.api.baseUrl}/api/auth/verify-token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${tokenToVerify}`
          }
        })

        return response.ok
      } catch (error) {
        console.error('Token驗證失敗:', error)
        return false
      }
    },

    // 測試連接
    async testConnection() {
      try {
        const response = await fetch(`${this.settings.api.baseUrl}/api/system/status`, {
          method: 'GET',
          headers: this.settings.api.openaiApiKey ? {
            'Authorization': `Bearer ${this.settings.api.openaiApiKey}`
          } : {},
          signal: AbortSignal.timeout(this.settings.api.timeout)
        })

        return {
          success: response.ok,
          status: response.status,
          statusText: response.statusText,
          data: response.ok ? await response.json() : null
        }
      } catch (error) {
        return {
          success: false,
          status: 0,
          statusText: error instanceof Error ? error.message : '連接失敗',
          data: null
        }
      }
    },

    // 更新API配置
    updateApiConfig(config: Partial<typeof defaultSettings.api>) {
      this.settings.api = { ...this.settings.api, ...config }
      this.markDirty()
    },

    // 更新用戶偏好
    async updateUserPreferences(preferences: Partial<typeof defaultSettings.user>) {
      this.settings.user = { ...this.settings.user, ...preferences }
      this.markDirty()

      // 立即應用主題變更
      if (preferences.theme) {
        await this.applyTheme()
      }
      
      // 立即應用語言變更
      if (preferences.language) {
        try {
          await setLocale(preferences.language)
          document.documentElement.setAttribute('lang', preferences.language)
          window.dispatchEvent(new CustomEvent('language-changed', {
            detail: { language: preferences.language }
          }))
          console.log('✅ 用戶偏好語言已應用:', preferences.language)
        } catch (error) {
          console.error('❌ 用戶偏好語言設定失敗:', error)
        }
      }
    },

    // 更新代理設定
    updateAgentSettings(agentSettings: Partial<typeof defaultSettings.agent>) {
      this.settings.agent = { ...this.settings.agent, ...agentSettings }
      this.markDirty()
    },

    // 更新數據設定
    updateDataSettings(dataSettings: Partial<typeof defaultSettings.data>) {
      this.settings.data = { ...this.settings.data, ...dataSettings }
      this.markDirty()
    },

    // 設定語言
    async setLanguage(language: typeof defaultSettings.user.language) {
      this.settings.user.language = language
      this.markDirty()
      
      // 立即應用語言變更到 i18n
      try {
        await setLocale(language)
        console.log('✅ 語言已設定並應用:', language)
        
        // 強制觸發全域語言更新
        document.documentElement.setAttribute('lang', language)
        
        // 觸發自定義事件通知所有組件
        window.dispatchEvent(new CustomEvent('language-changed', {
          detail: { language }
        }))
      } catch (error) {
        console.error('❌ 語言設定失敗:', error)
      }
    },

    // 設定主題
    async setTheme(theme: typeof defaultSettings.user.theme) {
      this.settings.user.theme = theme
      this.markDirty()
      await this.applyTheme()
    },

    // 應用主題
    async applyTheme() {
      const theme = this.currentTheme
      const html = document.documentElement
      
      // 移除舊的主題類
      html.classList.remove('light', 'dark')
      
      // 設定新的主題
      html.setAttribute('data-theme', theme)
      html.classList.add(theme)
      
      // 強制觸發樣式重新計算
      html.style.colorScheme = theme
      
      // 強制注入深色模式樣式
      try {
        if (theme === 'dark') {
          injectDarkModeStyles()
          console.log('✅ 深色模式樣式已強制注入')
        } else {
          removeDarkModeStyles()
          console.log('✅ 深色模式樣式已移除')
        }
      } catch (error) {
        console.error('❌ 樣式注入失敗:', error)
      }
      
      console.log('🎨 主題已應用:', theme, 'HTML classes:', html.className)
    },

    // 設置系統主題監聽器
    setupThemeListener() {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', () => {
        if (this.settings.user.theme === 'auto') {
          this.applyTheme()
        }
      })
    },

    // 驗證設定
    async validateSettings(): Promise<SettingsValidationResult> {
      const errors: SettingsError[] = []
      const warnings: SettingsError[] = []

      // 舊的token驗證已移除，改用openaiApiKey驗證

      // 驗證OpenAI API Key (必填)
      if (!this.settings.api.openaiApiKey) {
        errors.push({
          field: 'api.openaiApiKey',
          code: 'OPENAI_API_KEY_REQUIRED',
          message: 'OpenAI API Key是必填項目',
          value: this.settings.api.openaiApiKey
        })
      } else {
        if (this.settings.api.openaiApiKey.length < validationRules.api.openaiApiKey.minLength) {
          errors.push({
            field: 'api.openaiApiKey',
            code: 'OPENAI_API_KEY_TOO_SHORT',
            message: `OpenAI API Key長度至少需要${validationRules.api.openaiApiKey.minLength}字符`,
            value: this.settings.api.openaiApiKey.length
          })
        }

        if (validationRules.api.openaiApiKey.pattern && !validationRules.api.openaiApiKey.pattern.test(this.settings.api.openaiApiKey)) {
          errors.push({
            field: 'api.openaiApiKey',
            code: 'OPENAI_API_KEY_INVALID_FORMAT',
            message: 'OpenAI API Key格式無效，應以sk-開頭',
            value: this.settings.api.openaiApiKey
          })
        }
      }

      // 驗證API URL
      if (!validationRules.api.baseUrl.pattern.test(this.settings.api.baseUrl)) {
        errors.push({
          field: 'api.baseUrl',
          code: 'INVALID_URL',
          message: 'API基礎URL格式無效',
          value: this.settings.api.baseUrl
        })
      }

      // 驗證數值範圍
      if (this.settings.api.timeout < validationRules.api.timeout.min) {
        errors.push({
          field: 'api.timeout',
          code: 'VALUE_TOO_SMALL',
          message: `超時時間不能小於${validationRules.api.timeout.min}毫秒`,
          value: this.settings.api.timeout
        })
      }

      this.validationErrors = errors
      
      return {
        valid: errors.length === 0,
        errors,
        warnings
      }
    },

    // 重置為預設值
    resetToDefaults() {
      this.settings = { ...defaultSettings }
      this.validationErrors = []
      this.markDirty()
      console.log('設定已重置為預設值')
    },

    // 匯出設定
    exportSettings() {
      return {
        settings: this.settings,
        exportDate: new Date().toISOString(),
        version: this.settings.version,
        metadata: {
          source: 'Multi-Agent Analysis System',
          description: '系統設定備份'
        }
      }
    },

    // 匯入設定
    async importSettings(exportedSettings: any) {
      try {
        if (!exportedSettings.settings) {
          throw new Error('無效的設定檔案格式')
        }

        // 驗證版本兼容性
        if (exportedSettings.version !== this.settings.version) {
          console.warn('設定檔案版本不匹配，可能需要手動調整')
        }

        // 合併設定
        this.settings = this.mergeWithDefaults(exportedSettings.settings)
        
        // 驗證匯入的設定
        const validation = await this.validateSettings()
        if (!validation.valid) {
          throw new Error(`匯入的設定驗證失敗: ${validation.errors.map(e => e.message).join(', ')}`)
        }

        this.markDirty()
        await this.saveSettings()
        
        console.log('設定匯入成功')
      } catch (error) {
        console.error('匯入設定失敗:', error)
        throw error
      }
    },

    // 創建備份
    createBackup() {
      try {
        const backup = {
          settings: this.settings,
          timestamp: new Date().toISOString()
        }
        localStorage.setItem(STORAGE_KEYS.BACKUP, JSON.stringify(backup))
      } catch (error) {
        console.warn('創建備份失敗:', error)
      }
    },

    // 恢復備份
    restoreBackup() {
      try {
        const backup = localStorage.getItem(STORAGE_KEYS.BACKUP)
        if (backup) {
          const parsed = JSON.parse(backup)
          this.settings = this.mergeWithDefaults(parsed.settings)
          this.markDirty()
          console.log('已從備份恢復設定')
          return true
        }
        return false
      } catch (error) {
        console.error('恢復備份失敗:', error)
        return false
      }
    },

    // 合併預設設定
    mergeWithDefaults(settings: Partial<Settings>): Settings {
      return {
        ...defaultSettings,
        ...settings,
        api: {
          ...defaultSettings.api,
          ...settings.api,
          // 確保新的API配置項目有預設值
          openaiApiKey: settings.api?.openaiApiKey || defaultSettings.api.openaiApiKey,
          firecrawlApiKey: settings.api?.firecrawlApiKey || defaultSettings.api.firecrawlApiKey,
          langchainApiKey: settings.api?.langchainApiKey || defaultSettings.api.langchainApiKey,
          workingDirectory: settings.api?.workingDirectory || defaultSettings.api.workingDirectory,
          condaPath: settings.api?.condaPath || defaultSettings.api.condaPath,
          condaEnv: settings.api?.condaEnv || defaultSettings.api.condaEnv,
          chromedriverPath: settings.api?.chromedriverPath || defaultSettings.api.chromedriverPath
        },
        user: {
          ...defaultSettings.user,
          ...settings.user,
          notifications: { ...defaultSettings.user.notifications, ...settings.user?.notifications },
          interface: { ...defaultSettings.user.interface, ...settings.user?.interface }
        },
        agent: {
          ...defaultSettings.agent,
          ...settings.agent,
          workflow: { ...defaultSettings.agent.workflow, ...settings.agent?.workflow },
          priorities: { ...defaultSettings.agent.priorities, ...settings.agent?.priorities },
          timeout: { ...defaultSettings.agent.timeout, ...settings.agent?.timeout },
          debugging: { ...defaultSettings.agent.debugging, ...settings.agent?.debugging }
        },
        data: {
          ...defaultSettings.data,
          ...settings.data,
          upload: { ...defaultSettings.data.upload, ...settings.data?.upload },
          retention: { ...defaultSettings.data.retention, ...settings.data?.retention },
          cache: { ...defaultSettings.data.cache, ...settings.data?.cache },
          cleanup: { ...defaultSettings.data.cleanup, ...settings.data?.cleanup }
        }
      }
    },

    // 標記為已修改
    markDirty() {
      this.isDirty = true
    },

    // 清除驗證錯誤
    clearValidationErrors() {
      this.validationErrors = []
    }
  }
})