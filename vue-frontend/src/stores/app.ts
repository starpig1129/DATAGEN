import { defineStore } from 'pinia'
import type { AppConfig, User } from '@/types'

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
      graphqlUrl: import.meta.env.VITE_GRAPHQL_HTTP_URL || 'http://localhost:8000/graphql',
      wsUrl: import.meta.env.VITE_GRAPHQL_WS_URL || 'ws://localhost:8000/graphql/ws',
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
    handleNetworkReconnect() {
      // 這裡可以添加重新同步數據的邏輯
      console.log('網路連接已恢復，開始重新同步數據...')
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
    }
  }
})