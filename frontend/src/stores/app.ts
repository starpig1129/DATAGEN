import { defineStore } from 'pinia'
import type { AppConfig, User } from '@/types'
import { useRealTimeStore } from './realtime'

// 通知類型定義
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  persistent?: boolean
  timestamp: number
}

interface AppState {
  // 應用程式配置
  config: AppConfig
  
  // 用戶資訊
  user: User | null
  
  // 應用程式狀態
  isInitialized: boolean
  isLoading: boolean
  isOnline: boolean
  
  // 視窗資訊
  viewport: {
    width: number
    height: number
    isMobile: boolean
    isTablet: boolean
  }
  
  // 主題設置
  theme: 'light' | 'dark'
  
  // 錯誤狀態
  error: string | null
  
  // 通知系統
  notifications: Notification[]
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    config: {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
      wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:5001/stream',
      enableDevtools: import.meta.env.VITE_ENABLE_DEVTOOLS === 'true',
      theme: 'light',
      language: 'zh-TW'
    },
    
    user: null,
    
    isInitialized: false,
    isLoading: false,
    isOnline: navigator.onLine,
    
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight,
      isMobile: window.innerWidth < 768,
      isTablet: window.innerWidth >= 768 && window.innerWidth < 1024
    },
    
    theme: 'light',
    error: null,
    notifications: []
  }),

  getters: {
    // 應用程式是否準備就緒
    isReady: (state) => state.isInitialized && !state.isLoading,
    
    // 是否為移動設備
    isMobileDevice: (state) => state.viewport.isMobile,
    
    // 是否為平板設備
    isTabletDevice: (state) => state.viewport.isTablet,
    
    // 是否為桌面設備
    isDesktopDevice: (state) => !state.viewport.isMobile && !state.viewport.isTablet,
    
    // 當前用戶是否已登入
    isLoggedIn: (state) => state.user !== null,
    
    // 獲取用戶角色
    userRole: (state) => state.user?.role || 'viewer'
  },

  actions: {
    // 初始化應用程式
    async initialize() {
      this.isLoading = true
      this.error = null
      
      try {
        // 載入用戶偏好設置
        this.loadUserPreferences()
        
        // 更新視窗資訊
        this.updateViewport()
        
        // 檢查認證狀態
        await this.checkAuthStatus()
        
        // 初始化實時連接
        try {
          const realtimeStore = useRealTimeStore()
          await realtimeStore.initialize()
          console.log('實時連接初始化成功')
        } catch (realtimeError) {
          console.error('實時連接初始化失敗:', realtimeError)
          // 不阻止應用程式初始化，實時連接失敗不影響基本功能
        }
        
        this.isInitialized = true
      } catch (error) {
        this.error = error instanceof Error ? error.message : '初始化失敗'
        console.error('應用程式初始化失敗:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    // 更新視窗資訊
    updateViewport() {
      this.viewport = {
        width: window.innerWidth,
        height: window.innerHeight,
        isMobile: window.innerWidth < 768,
        isTablet: window.innerWidth >= 768 && window.innerWidth < 1024
      }
    },
    
    // 設置網路狀態
    setOnlineStatus(isOnline: boolean) {
      this.isOnline = isOnline
      
      if (isOnline) {
        // 網路恢復時重新同步數據
        this.handleNetworkReconnect()
      }
    },
    
    // 設置主題
    setTheme(theme: 'light' | 'dark') {
      this.theme = theme
      this.config.theme = theme
      
      // 保存到本地存儲
      localStorage.setItem('app_theme', theme)
      
      // 更新 HTML 類名
      document.documentElement.className = theme
    },
    
    // 設置用戶資訊
    setUser(user: User | null) {
      this.user = user
      
      if (user) {
        // 保存用戶偏好
        this.saveUserPreferences()
      } else {
        // 清除用戶資料
        localStorage.removeItem('user_preferences')
      }
    },
    
    // 設置錯誤
    setError(error: string | null) {
      this.error = error
    },
    
    // 清除錯誤
    clearError() {
      this.error = null
    },
    
    // 載入用戶偏好設置
    loadUserPreferences() {
      try {
        const savedTheme = localStorage.getItem('app_theme') as 'light' | 'dark'
        if (savedTheme) {
          this.setTheme(savedTheme)
        }
        
        const savedLanguage = localStorage.getItem('app_language')
        if (savedLanguage && (savedLanguage === 'zh-TW' || savedLanguage === 'en-US')) {
          this.config.language = savedLanguage
        }
      } catch (error) {
        console.warn('載入用戶偏好設置失敗:', error)
      }
    },
    
    // 保存用戶偏好設置
    saveUserPreferences() {
      try {
        if (this.user?.preferences) {
          localStorage.setItem('user_preferences', JSON.stringify(this.user.preferences))
        }
      } catch (error) {
        console.warn('保存用戶偏好設置失敗:', error)
      }
    },
    
    // 檢查認證狀態
    async checkAuthStatus() {
      try {
        const token = localStorage.getItem('auth_token')
        if (token) {
          // 這裡可以調用 API 驗證 token 是否有效
          // const user = await authApi.verifyToken(token)
          // this.setUser(user)
        }
      } catch (error) {
        console.warn('檢查認證狀態失敗:', error)
        // 清除無效的 token
        localStorage.removeItem('auth_token')
      }
    },
    
    // 處理網路重新連接
    async handleNetworkReconnect() {
      // 重新同步數據的邏輯
      console.log('網路連接已恢復，開始重新同步數據...')
      
      try {
        this.isLoading = true
        
        // 檢查後端 API 連接
        await this.testApiConnection()
        
        // 觸發其他 stores 的數據重新同步
        const event = new CustomEvent('network-reconnected', {
          detail: { timestamp: Date.now() }
        })
        document.dispatchEvent(event)
        
        this.addNotification({
          type: 'success',
          title: '網路已恢復',
          message: '數據同步已完成'
        })
        
      } catch (error) {
        console.error('網路重連後數據同步失敗:', error)
        this.addNotification({
          type: 'warning',
          title: '同步警告',
          message: '網路已恢復但部分數據同步失敗'
        })
      } finally {
        this.isLoading = false
      }
    },
    
    // 登出
    logout() {
      this.setUser(null)
      localStorage.removeItem('auth_token')
      
      // 重定向到登入頁面或首頁
      // router.push('/')
    },
    
    // 通知管理
    addNotification(notification: Omit<Notification, 'id' | 'timestamp'>) {
      const id = `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const newNotification: Notification = {
        ...notification,
        id,
        timestamp: Date.now(),
        duration: notification.duration ?? 5000
      }
      
      this.notifications.push(newNotification)
      
      // 自動移除非持久化通知
      if (!newNotification.persistent && newNotification.duration && newNotification.duration > 0) {
        setTimeout(() => {
          this.removeNotification(id)
        }, newNotification.duration)
      }
      
      return id
    },
    
    removeNotification(id: string) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },
    
    clearAllNotifications() {
      this.notifications = []
    },
    
    clearNotificationsByType(type: Notification['type']) {
      this.notifications = this.notifications.filter(n => n.type !== type)
    },

    // API 連接測試
    async testApiConnection(): Promise<boolean> {
      try {
        const response = await fetch(`${this.config.apiBaseUrl}/api/system/status`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          },
          signal: AbortSignal.timeout(5000) // 5秒超時
        })
        
        if (!response.ok) {
          throw new Error(`API 連接失敗: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('API 連接測試成功:', data)
        return true
        
      } catch (error) {
        console.error('API 連接測試失敗:', error)
        this.setError(error instanceof Error ? error.message : 'API 連接失敗')
        return false
      }
    },

    // API 請求重試機制
    async apiRequest<T = any>(
      endpoint: string,
      options: RequestInit = {},
      retryCount: number = 3
    ): Promise<T> {
      const url = `${this.config.apiBaseUrl}${endpoint}`
      
      for (let attempt = 0; attempt <= retryCount; attempt++) {
        try {
          const response = await fetch(url, {
            ...options,
            headers: {
              'Content-Type': 'application/json',
              ...options.headers
            }
          })
          
          if (!response.ok) {
            if (response.status >= 500 && attempt < retryCount) {
              // 伺服器錯誤，重試
              await this.delay(Math.pow(2, attempt) * 1000) // 指數退避
              continue
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
          }
          
          return await response.json()
          
        } catch (error) {
          if (attempt === retryCount) {
            // 最後一次嘗試失敗
            const errorMessage = error instanceof Error ? error.message : '請求失敗'
            this.addNotification({
              type: 'error',
              title: 'API 請求失敗',
              message: `${endpoint}: ${errorMessage}`
            })
            throw error
          }
          
          // 網路錯誤，重試
          if (error instanceof TypeError || error instanceof DOMException) {
            await this.delay(Math.pow(2, attempt) * 1000)
            continue
          }
          
          throw error
        }
      }
      
      throw new Error('重試次數已達上限')
    },

    // 延遲工具函數
    delay(ms: number): Promise<void> {
      return new Promise(resolve => setTimeout(resolve, ms))
    },

    // 批量 API 請求
    async batchApiRequest<T = any>(
      requests: Array<{ endpoint: string; options?: RequestInit }>,
      concurrency: number = 3
    ): Promise<Array<T | Error>> {
      const results: Array<T | Error> = []
      
      for (let i = 0; i < requests.length; i += concurrency) {
        const batch = requests.slice(i, i + concurrency)
        
        const batchPromises = batch.map(async (request) => {
          try {
            return await this.apiRequest<T>(request.endpoint, request.options)
          } catch (error) {
            return error instanceof Error ? error : new Error('未知錯誤')
          }
        })
        
        const batchResults = await Promise.all(batchPromises)
        results.push(...batchResults)
      }
      
      return results
    },

    // 定期健康檢查
    startHealthCheck(interval: number = 30000): void {
      // 清除現有的健康檢查
      this.stopHealthCheck()
      
      const healthCheckInterval = setInterval(async () => {
        if (!this.isOnline) {
          return // 如果離線，跳過健康檢查
        }
        
        try {
          const isHealthy = await this.testApiConnection()
          if (!isHealthy && this.isOnline) {
            // API 不健康但網路顯示在線，可能是後端問題
            this.addNotification({
              type: 'warning',
              title: '後端服務異常',
              message: '無法連接到後端服務，請檢查服務狀態'
            })
          }
        } catch (error) {
          console.error('健康檢查失敗:', error)
        }
      }, interval)
      
      // 儲存間隔 ID 以便後續清除
      ;(this as any).healthCheckInterval = healthCheckInterval
    },

    stopHealthCheck(): void {
      const intervalId = (this as any).healthCheckInterval
      if (intervalId) {
        clearInterval(intervalId)
        ;(this as any).healthCheckInterval = null
      }
    }
  }
})