// 統一導出所有類型定義

export * from './api'
export * from './agent'
export * from './chat'
export * from './file'
export * from './visualization'
export * from './settings'

// 系統狀態相關類型
export interface SystemState {
  currentPhase: string
  activeAgents: string[]
  needsDecision: boolean
  hypothesis?: string
  processStatus?: string
  qualityReview?: string
  timestamp: string
}

// 應用程式配置
export interface AppConfig {
  apiBaseUrl: string
  graphqlUrl: string
  wsUrl: string
  enableDevtools: boolean
  theme: 'light' | 'dark'
  language: 'zh-TW' | 'en-US'
}

// 用戶相關
export interface User {
  id: string
  username: string
  email: string
  role: 'admin' | 'user' | 'viewer'
  preferences: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  notifications: boolean
  autoSave: boolean
}

// 通用工具類型
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// 事件類型
export interface CustomEvent<T = any> {
  type: string
  payload: T
  timestamp: number
}

// 錯誤處理
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: string
}