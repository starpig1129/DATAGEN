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
      const { baseUrl } = state.settings.api
      return Boolean(baseUrl) // 只需要 baseUrl，不強制要求 openaiApiKey
    },

    // 檢查是否有完整的API配置（包括 openaiApiKey）
    hasFullApiConfig: (state) => {
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
        }
        
        // 確保主題設定正確應用
        await this.applyTheme()
        
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
        const error = new Error('API baseUrl 未配置，無法同步到伺服器')
        this.syncStatus.errors.push(error.message)
        throw error // 拋出錯誤讓 UI 能夠處理
      }

      this.syncStatus.syncing = true
      this.syncStatus.errors = []

      try {
        console.log('📤 發送設定到伺服器...')
        const response = await this.makeApiRequest('/api/settings', {
          method: 'POST',
          body: JSON.stringify({ settings: this.settings })
        })

        console.log('📨 伺服器響應狀態:', response.status, response.statusText)

        if (!response.ok) {
          const errorData = await response.text()
          
          let errorMessage = `同步失敗: ${response.statusText}`
          try {
            const parsedError = JSON.parse(errorData)
            errorMessage = parsedError.message || errorMessage
          } catch {
            // Use default error message
          }
          throw new Error(errorMessage)
        }

        this.syncStatus.lastSync = new Date().toISOString()
        localStorage.setItem(STORAGE_KEYS.LAST_SYNC, this.syncStatus.lastSync)
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '同步失敗'
        this.syncStatus.errors.push(errorMessage)
        console.error('同步設定到伺服器失敗:', error)
        throw error // Re-throw to allow UI to handle
      } finally {
        this.syncStatus.syncing = false
      }
    },

    // 從伺服器載入設定
    async loadFromServer() {
      if (!this.isApiConfigured) {
        throw new Error('API not configured')
      }

      this.isLoading = true
      try {
        const response = await this.makeApiRequest('/api/settings', {
          method: 'GET'
        })

        if (!response.ok) {
          const errorData = await response.text()
          let errorMessage = `Load failed: ${response.statusText}`
          try {
            const parsedError = JSON.parse(errorData)
            errorMessage = parsedError.message || errorMessage
          } catch {
            // Use default error message
          }
          throw new Error(errorMessage)
        }

        const responseData = await response.json()
        if (responseData && responseData.settings) {
          this.settings = this.mergeWithDefaults(responseData.settings)
          await this.saveSettings()
          console.log('Settings loaded from server successfully')
        } else {
          console.warn('Server response missing settings field', responseData)
        }
      } catch (error) {
        console.error('Failed to load settings from server:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    // 驗證Token有效性
    async verifyToken(token?: string) {
      const tokenToVerify = token || this.settings.api.openaiApiKey
      if (!tokenToVerify) {
        throw new Error('Token is empty')
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
        console.error('Token verification failed:', error)
        return false
      }
    },

    // 測試連接
    async testConnection() {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), this.settings.api.timeout)
        
        const response = await fetch(`${this.settings.api.baseUrl}/api/system/status`, {
          method: 'GET',
          headers: this.settings.api.openaiApiKey ? {
            'Authorization': `Bearer ${this.settings.api.openaiApiKey}`,
            'Content-Type': 'application/json'
          } : {
            'Content-Type': 'application/json'
          },
          signal: controller.signal
        })

        clearTimeout(timeoutId)

        const result = {
          success: response.ok,
          status: response.status,
          statusText: response.statusText,
          data: null as any
        }

        try {
          if (response.ok) {
            result.data = await response.json()
          } else {
            // Try to get error details from response
            const errorText = await response.text()
            try {
              result.data = JSON.parse(errorText)
            } catch {
              result.data = { error: errorText }
            }
          }
        } catch (parseError) {
          console.warn('Failed to parse response:', parseError)
        }

        return result
      } catch (error) {
        let errorMessage = 'Connection failed'
        let errorCode = 'NETWORK_ERROR'

        if (error instanceof Error) {
          if (error.name === 'AbortError') {
            errorMessage = 'Connection timeout'
            errorCode = 'TIMEOUT'
          } else if (error.message.includes('fetch')) {
            errorMessage = 'Network error - check your connection and server URL'
            errorCode = 'NETWORK_ERROR'
          } else {
            errorMessage = error.message
          }
        }

        return {
          success: false,
          status: 0,
          statusText: errorMessage,
          data: { error: errorMessage, code: errorCode }
        }
      }
    },

    // 增強的API請求方法，支持重試
    async makeApiRequest(endpoint: string, options: RequestInit = {}, retries = 0): Promise<Response> {
      const maxRetries = this.settings.api.retryAttempts || 3
      const baseUrl = this.settings.api.baseUrl
      
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), this.settings.api.timeout)
        
        const response = await fetch(`${baseUrl}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...(this.settings.api.openaiApiKey && {
              'Authorization': `Bearer ${this.settings.api.openaiApiKey}`
            }),
            ...options.headers
          },
          signal: controller.signal
        })

        clearTimeout(timeoutId)
        return response
      } catch (error) {
        if (retries < maxRetries && error instanceof Error) {
          // Retry on network errors, but not on timeout errors
          if (!error.name.includes('Abort') && !error.message.includes('timeout')) {
            console.warn(`API request failed, retrying... (${retries + 1}/${maxRetries})`)
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, retries) * 1000)) // Exponential backoff
            return this.makeApiRequest(endpoint, options, retries + 1)
          }
        }
        throw error
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
        } catch (error) {
          console.error('❌ 用戶偏好語言設定失敗:', error)
        }
      }
    },

    // 更新界面設定
    async updateInterfaceSettings(interfaceSettings: Partial<typeof defaultSettings.user.interface>) {
      this.settings.user.interface = { ...this.settings.user.interface, ...interfaceSettings }
      this.markDirty()
      
      // 自動保存界面設定變更
      try {
        await this.saveSettings()
      } catch (error) {
        console.error('❌ 界面設定自動保存失敗:', error)
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
      
      // 更新 HTML 屬性與類名
      html.setAttribute('data-theme', theme)
      
      if (theme === 'dark') {
        html.classList.add('dark')
        html.classList.remove('light')
        html.style.colorScheme = 'dark'
        injectDarkModeStyles()
      } else {
        html.classList.add('light')
        html.classList.remove('dark')
        html.style.colorScheme = 'light'
        removeDarkModeStyles()
      }
      
      console.log(`🎨 主題已切換為: ${theme}`)
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

      // 驗證OpenAI API Key (必填)
      if (!this.settings.api.openaiApiKey || this.settings.api.openaiApiKey.trim() === '') {
        errors.push({
          field: 'api.openaiApiKey',
          code: 'OPENAI_API_KEY_REQUIRED',
          message: 'OpenAI API Key是必填項目',
          value: this.settings.api.openaiApiKey
        })
      } else {
        // 使用更寬鬆的長度檢查
        if (this.settings.api.openaiApiKey.length < 20) {
          errors.push({
            field: 'api.openaiApiKey',
            code: 'OPENAI_API_KEY_TOO_SHORT',
            message: 'OpenAI API Key長度至少需要20字符',
            value: this.settings.api.openaiApiKey.length
          })
        }

        // 使用更寬鬆的格式檢查
        if (!/^sk-[a-zA-Z0-9_-]+$/.test(this.settings.api.openaiApiKey)) {
          errors.push({
            field: 'api.openaiApiKey',
            code: 'OPENAI_API_KEY_INVALID_FORMAT',
            message: 'OpenAI API Key格式無效，應以sk-開頭',
            value: this.settings.api.openaiApiKey
          })
        }
      }

      // 驗證API URL (更寬鬆的檢查)
      if (this.settings.api.baseUrl && this.settings.api.baseUrl.trim() !== '') {
        try {
          new URL(this.settings.api.baseUrl)
        } catch {
          // 如果不是完整 URL，檢查是否為有效的 http/https URL 格式
          if (!/^https?:\/\/.+/.test(this.settings.api.baseUrl)) {
            errors.push({
              field: 'api.baseUrl',
              code: 'INVALID_URL',
              message: 'API基礎URL格式無效',
              value: this.settings.api.baseUrl
            })
          }
        }
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

      // 驗證可選的 API Keys（只在非空時檢查格式）
      if (this.settings.api.firecrawlApiKey && this.settings.api.firecrawlApiKey.trim() !== '') {
        if (!/^fc-[a-zA-Z0-9_-]+$/.test(this.settings.api.firecrawlApiKey)) {
          warnings.push({
            field: 'api.firecrawlApiKey',
            code: 'INVALID_FORMAT',
            message: 'Firecrawl API Key格式可能無效',
            value: this.settings.api.firecrawlApiKey
          })
        }
      }

      if (this.settings.api.langchainApiKey && this.settings.api.langchainApiKey.trim() !== '') {
        if (!/^lsv2_pt_[a-zA-Z0-9_]+$/.test(this.settings.api.langchainApiKey)) {
          warnings.push({
            field: 'api.langchainApiKey',
            code: 'INVALID_FORMAT',
            message: 'LangChain API Key格式可能無效 (期望格式: lsv2_pt_開頭)',
            value: this.settings.api.langchainApiKey
          })
        }
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
    },



  }
})