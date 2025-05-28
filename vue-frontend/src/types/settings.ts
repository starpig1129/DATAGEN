// 設定相關類型定義

export type ThemeMode = 'light' | 'dark' | 'auto'
export type LanguageCode = 'zh-TW' | 'zh-CN' | 'en-US'
export type NotificationType = 'email' | 'browser' | 'system' | 'chat' | 'agent'

// API配置介面
export interface ApiConfig {
  token: string
  baseUrl: string
  timeout: number
  retryAttempts: number
  enableLogging: boolean
  // 新增的API Keys
  openaiApiKey: string
  firecrawlApiKey?: string
  langchainApiKey?: string
  // 系統路徑配置
  workingDirectory: string
  condaPath: string
  condaEnv: string
  chromedriverPath: string
}

// 用戶偏好設定
export interface UserPreferencesSettings {
  language: LanguageCode
  theme: ThemeMode
  timezone: string
  dateFormat: string
  notifications: NotificationSettings
  interface: InterfaceSettings
}

// 通知設定
export interface NotificationSettings {
  enabled: boolean
  types: Record<NotificationType, boolean>
  sound: boolean
  vibration: boolean
  desktop: boolean
  quietHours: {
    enabled: boolean
    startTime: string
    endTime: string
  }
}

// 介面設定
export interface InterfaceSettings {
  sidebarCollapsed: boolean
  compactMode: boolean
  showToolbar: boolean
  animationsEnabled: boolean
  fontSize: 'small' | 'medium' | 'large'
  density: 'comfortable' | 'compact' | 'spacious'
}

// 代理設定
export interface AgentSettings {
  workflow: WorkflowSettings
  priorities: AgentPriorities
  timeout: TimeoutSettings
  debugging: DebuggingSettings
}

// 工作流程設定
export interface WorkflowSettings {
  autoStart: boolean
  parallelExecution: boolean
  maxConcurrentAgents: number
  retryFailedTasks: boolean
  saveIntermediateResults: boolean
}

// 代理優先級設定
export interface AgentPriorities {
  searchAgent: number
  analysisAgent: number
  visualizationAgent: number
  reportAgent: number
  qualityReviewAgent: number
}

// 超時設定
export interface TimeoutSettings {
  agentResponse: number
  fileUpload: number
  apiRequest: number
  websocketConnection: number
}

// 調試設定
export interface DebuggingSettings {
  enabled: boolean
  logLevel: 'debug' | 'info' | 'warn' | 'error'
  saveLogsToFile: boolean
  showAgentSteps: boolean
  verboseOutput: boolean
}

// 數據設定
export interface DataSettings {
  upload: UploadSettings
  retention: RetentionSettings
  cache: CacheSettings
  cleanup: CleanupSettings
}

// 上傳設定
export interface UploadSettings {
  maxFileSize: number // MB
  allowedTypes: string[]
  maxFilesPerUpload: number
  autoScan: boolean
  compressImages: boolean
}

// 數據保留設定
export interface RetentionSettings {
  chatHistory: number // days
  uploadedFiles: number // days
  analysisResults: number // days
  logs: number // days
  autoDelete: boolean
}

// 快取設定
export interface CacheSettings {
  enabled: boolean
  maxSize: number // MB
  ttl: number // seconds
  preloadData: boolean
  compressData: boolean
}

// 清理設定
export interface CleanupSettings {
  autoCleanup: boolean
  cleanupInterval: number // hours
  keepRecent: number // days
  cleanupLogs: boolean
  cleanupCache: boolean
}

// 完整設定介面
export interface Settings {
  api: ApiConfig
  user: UserPreferencesSettings
  agent: AgentSettings
  data: DataSettings
  version: string
  lastModified: string
}

// 設定驗證規則
export interface SettingsValidationRules {
  api: {
    token: {
      required: boolean
      minLength: number
      pattern?: RegExp
    }
    baseUrl: {
      required: boolean
      pattern: RegExp
    }
    timeout: {
      min: number
      max: number
    }
    openaiApiKey: {
      required: boolean
      minLength: number
      pattern?: RegExp
    }
  }
  data: {
    upload: {
      maxFileSize: {
        min: number
        max: number
      }
      maxFilesPerUpload: {
        min: number
        max: number
      }
    }
  }
}

// 設定錯誤類型
export interface SettingsError {
  field: string
  code: string
  message: string
  value?: any
}

// 設定驗證結果
export interface SettingsValidationResult {
  valid: boolean
  errors: SettingsError[]
  warnings: SettingsError[]
}

// 設定匯入/匯出
export interface SettingsExport {
  settings: Partial<Settings>
  exportDate: string
  version: string
  metadata: {
    source: string
    description?: string
  }
}

// 設定同步狀態
export interface SettingsSyncStatus {
  lastSync: string
  syncing: boolean
  conflicts: string[]
  errors: string[]
}

// 預設設定
export const DEFAULT_SETTINGS: Settings = {
  api: {
    token: '',
    baseUrl: 'http://localhost:5001',
    timeout: 30000,
    retryAttempts: 3,
    enableLogging: true,
    // 新增的API Keys
    openaiApiKey: '',
    firecrawlApiKey: '',
    langchainApiKey: '',
    // 系統路徑配置
    workingDirectory: './data_storage/',
    condaPath: '/home/user/anaconda3',
    condaEnv: 'data_assistant',
    chromedriverPath: './chromedriver-linux64/chromedriver'
  },
  user: {
    language: 'zh-TW',
    theme: 'auto',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    dateFormat: 'YYYY-MM-DD',
    notifications: {
      enabled: true,
      types: {
        email: true,
        browser: true,
        system: true,
        chat: true,
        agent: true
      },
      sound: true,
      vibration: false,
      desktop: true,
      quietHours: {
        enabled: false,
        startTime: '22:00',
        endTime: '08:00'
      }
    },
    interface: {
      sidebarCollapsed: false,
      compactMode: false,
      showToolbar: true,
      animationsEnabled: true,
      fontSize: 'medium',
      density: 'comfortable'
    }
  },
  agent: {
    workflow: {
      autoStart: false,
      parallelExecution: true,
      maxConcurrentAgents: 3,
      retryFailedTasks: true,
      saveIntermediateResults: true
    },
    priorities: {
      searchAgent: 1,
      analysisAgent: 2,
      visualizationAgent: 3,
      reportAgent: 4,
      qualityReviewAgent: 5
    },
    timeout: {
      agentResponse: 60000,
      fileUpload: 300000,
      apiRequest: 30000,
      websocketConnection: 10000
    },
    debugging: {
      enabled: false,
      logLevel: 'info',
      saveLogsToFile: false,
      showAgentSteps: false,
      verboseOutput: false
    }
  },
  data: {
    upload: {
      maxFileSize: 100,
      allowedTypes: ['.csv', '.xlsx', '.json', '.txt', '.pdf'],
      maxFilesPerUpload: 10,
      autoScan: true,
      compressImages: true
    },
    retention: {
      chatHistory: 30,
      uploadedFiles: 90,
      analysisResults: 180,
      logs: 7,
      autoDelete: false
    },
    cache: {
      enabled: true,
      maxSize: 500,
      ttl: 3600,
      preloadData: false,
      compressData: true
    },
    cleanup: {
      autoCleanup: true,
      cleanupInterval: 24,
      keepRecent: 7,
      cleanupLogs: true,
      cleanupCache: true
    }
  },
  version: '1.0.0',
  lastModified: new Date().toISOString()
}

// 設定驗證規則
export const SETTINGS_VALIDATION_RULES: SettingsValidationRules = {
  api: {
    token: {
      required: false,
      minLength: 10,
      pattern: /^[A-Za-z0-9_\-]+$/
    },
    baseUrl: {
      required: false, // 改為非必填，使用預設值
      pattern: /^https?:\/\/.+/
    },
    timeout: {
      min: 1000,
      max: 300000
    },
    openaiApiKey: {
      required: true,
      minLength: 20, // 降低最小長度要求
      pattern: /^sk-[A-Za-z0-9_-]+$/ // 允許底線和連字符
    }
  },
  data: {
    upload: {
      maxFileSize: {
        min: 1,
        max: 1000
      },
      maxFilesPerUpload: {
        min: 1,
        max: 100
      }
    }
  }
}