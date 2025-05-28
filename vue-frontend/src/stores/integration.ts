import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAppStore } from './app'
import { useChatStore } from './chat'
import { useFileStore } from './file'
import { useDataStore } from './data'
import { useRealTimeStore } from './realtime'

// 系統集成狀態
interface IntegrationState {
  isInitialized: boolean
  allStoresReady: boolean
  integrationError: string | null
  lastSyncTime: string | null
  activeSystems: string[]
  systemHealth: Record<string, 'healthy' | 'warning' | 'error'>
}

// 系統事件類型
interface SystemEvent {
  id: string
  type: 'store_ready' | 'sync_complete' | 'error' | 'health_check'
  source: string
  data?: any
  timestamp: number
}

export const useIntegrationStore = defineStore('integration', () => {
  // 狀態
  const state = ref<IntegrationState>({
    isInitialized: false,
    allStoresReady: false,
    integrationError: null,
    lastSyncTime: null,
    activeSystems: [],
    systemHealth: {}
  })
  
  const events = ref<SystemEvent[]>([])
  const healthCheckInterval = ref<number | null>(null)
  
  // Store 實例引用
  const stores = {
    app: null as ReturnType<typeof useAppStore> | null,
    chat: null as ReturnType<typeof useChatStore> | null,
    file: null as ReturnType<typeof useFileStore> | null,
    data: null as ReturnType<typeof useDataStore> | null,
    realtime: null as ReturnType<typeof useRealTimeStore> | null
  }
  
  // 計算屬性
  const healthyStores = computed(() => 
    Object.keys(state.value.systemHealth).filter(
      store => state.value.systemHealth[store] === 'healthy'
    )
  )
  
  const errorStores = computed(() =>
    Object.keys(state.value.systemHealth).filter(
      store => state.value.systemHealth[store] === 'error'
    )
  )
  
  const overallHealth = computed(() => {
    const healths = Object.values(state.value.systemHealth)
    if (healths.includes('error')) return 'error'
    if (healths.includes('warning')) return 'warning'
    return 'healthy'
  })
  
  const recentEvents = computed(() => 
    events.value.slice(-20).reverse()
  )
  
  // 初始化系統集成
  const initialize = async (): Promise<void> => {
    try {
      console.log('開始初始化系統集成...')
      addEvent('system_init', 'integration', { message: '開始初始化' })
      
      // 初始化各個 stores
      await initializeStores()
      
      // 設置實時數據流
      setupDataFlows()
      
      // 設置健康監控
      startHealthMonitoring()
      
      // 設置事件監聽
      setupEventListeners()
      
      state.value.isInitialized = true
      state.value.lastSyncTime = new Date().toISOString()
      
      console.log('系統集成初始化完成')
      addEvent('system_ready', 'integration', { 
        message: '系統集成已就緒',
        healthyStores: healthyStores.value.length,
        totalStores: Object.keys(stores).length
      })
      
      // 通知應用系統已就緒
      if (stores.app) {
        stores.app.addNotification({
          type: 'success',
          title: '系統已就緒',
          message: '所有模組已成功初始化並建立實時連接'
        })
      }
      
    } catch (error) {
      console.error('系統集成初始化失敗:', error)
      state.value.integrationError = error instanceof Error ? error.message : '初始化失敗'
      
      addEvent('system_error', 'integration', { 
        error: state.value.integrationError 
      })
      
      if (stores.app) {
        stores.app.addNotification({
          type: 'error',
          title: '系統初始化失敗',
          message: state.value.integrationError
        })
      }
    }
  }
  
  // 初始化各個 stores
  const initializeStores = async (): Promise<void> => {
    try {
      // 初始化 app store
      stores.app = useAppStore()
      await stores.app.initialize()
      updateStoreHealth('app', 'healthy')
      
      // 初始化 realtime store
      stores.realtime = useRealTimeStore()
      await stores.realtime.initialize()
      updateStoreHealth('realtime', 'healthy')
      
      // 初始化 chat store
      stores.chat = useChatStore()
      await stores.chat.initializeChatEnhanced()
      updateStoreHealth('chat', 'healthy')
      
      // 初始化 file store
      stores.file = useFileStore()
      await stores.file.fetchFiles()
      stores.file.enableAutoSync()
      updateStoreHealth('file', 'healthy')
      
      // 初始化 data store
      stores.data = useDataStore()
      stores.data.initialize()
      updateStoreHealth('data', 'healthy')
      
      state.value.allStoresReady = true
      state.value.activeSystems = Object.keys(stores)
      
      console.log('所有 stores 初始化完成')
      
    } catch (error) {
      console.error('Stores 初始化失敗:', error)
      throw error
    }
  }
  
  // 設置數據流
  const setupDataFlows = (): void => {
    if (!stores.realtime || !stores.chat || !stores.file || !stores.data) {
      return
    }
    
    // 設置實時數據到聊天的流
    const handleRealtimeToChat = (data: any) => {
      if (data.type === 'chat_state' && stores.chat) {
        stores.chat.syncWithRealtime(data)
      }
    }
    
    // 設置實時數據到文件的流
    const handleRealtimeToFile = (data: any) => {
      if (data.type === 'file_status' && stores.file) {
        stores.file.syncFileStatus(data)
      }
    }
    
    // 設置實時數據到數據管理的流
    const handleRealtimeToData = (data: any) => {
      if (data.type === 'data_update' && stores.data) {
        // 觸發數據同步
        stores.data.syncAllData()
      }
    }
    
    console.log('數據流設置完成')
  }
  
  // 設置事件監聽器
  const setupEventListeners = (): void => {
    // 監聽網路狀態變化
    window.addEventListener('online', handleNetworkOnline)
    window.addEventListener('offline', handleNetworkOffline)
    
    // 監聽應用級事件
    document.addEventListener('store-error', handleStoreError)
    document.addEventListener('data-sync-complete', handleDataSyncComplete)
    
    console.log('事件監聽器設置完成')
  }
  
  // 網路事件處理
  const handleNetworkOnline = async (): Promise<void> => {
    console.log('網路已恢復，重新初始化連接...')
    addEvent('network_online', 'system')
    
    try {
      // 重新建立實時連接
      if (stores.realtime) {
        await stores.realtime.connectWebSocket()
      }
      
      // 重新建立聊天連接
      if (stores.chat) {
        stores.chat.connectSSE()
      }
      
      // 同步所有數據
      if (stores.data) {
        await stores.data.syncAllData()
      }
      
      // 刷新文件列表
      if (stores.file) {
        await stores.file.fetchFiles(false)
      }
      
      if (stores.app) {
        stores.app.addNotification({
          type: 'success',
          title: '網路已恢復',
          message: '所有服務已重新連接並同步數據'
        })
      }
      
    } catch (error) {
      console.error('網路恢復後重連失敗:', error)
      if (stores.app) {
        stores.app.addNotification({
          type: 'warning',
          title: '部分服務重連失敗',
          message: '請手動刷新頁面以確保所有功能正常'
        })
      }
    }
  }
  
  const handleNetworkOffline = (): void => {
    console.log('網路已斷開')
    addEvent('network_offline', 'system')
    
    // 更新所有 stores 的健康狀態
    Object.keys(stores).forEach(storeName => {
      updateStoreHealth(storeName, 'warning')
    })
    
    if (stores.app) {
      stores.app.addNotification({
        type: 'warning',
        title: '網路連接中斷',
        message: '部分功能可能不可用，請檢查網路連接'
      })
    }
  }
  
  // Store 錯誤處理
  const handleStoreError = (event: Event): void => {
    const customEvent = event as CustomEvent
    const { store, error, details } = customEvent.detail
    
    console.error(`Store 錯誤 [${store}]:`, error)
    updateStoreHealth(store, 'error')
    
    addEvent('store_error', store, { error, details })
    
    if (stores.app) {
      stores.app.addNotification({
        type: 'error',
        title: `${store} 模組錯誤`,
        message: error,
        persistent: true
      })
    }
  }
  
  // 數據同步完成處理
  const handleDataSyncComplete = (event: Event): void => {
    const customEvent = event as CustomEvent
    const { source, timestamp, results } = customEvent.detail
    
    console.log(`數據同步完成 [${source}]:`, results)
    state.value.lastSyncTime = new Date(timestamp).toISOString()
    
    addEvent('sync_complete', source, results)
  }
  
  // 健康監控
  const startHealthMonitoring = (): void => {
    healthCheckInterval.value = setInterval(async () => {
      await performHealthCheck()
    }, 60000) // 每分鐘檢查一次
    
    console.log('健康監控已啟動')
  }
  
  const stopHealthMonitoring = (): void => {
    if (healthCheckInterval.value) {
      clearInterval(healthCheckInterval.value)
      healthCheckInterval.value = null
    }
  }
  
  const performHealthCheck = async (): Promise<void> => {
    try {
      // 檢查各個 store 的健康狀態
      const healthChecks = await Promise.allSettled([
        checkAppStoreHealth(),
        checkRealtimeStoreHealth(),
        checkChatStoreHealth(),
        checkFileStoreHealth(),
        checkDataStoreHealth()
      ])
      
      healthChecks.forEach((result, index) => {
        const storeNames = ['app', 'realtime', 'chat', 'file', 'data']
        const storeName = storeNames[index]
        
        if (result.status === 'fulfilled') {
          updateStoreHealth(storeName, result.value ? 'healthy' : 'warning')
        } else {
          updateStoreHealth(storeName, 'error')
        }
      })
      
      addEvent('health_check', 'system', {
        overall: overallHealth.value,
        details: state.value.systemHealth
      })
      
    } catch (error) {
      console.error('健康檢查失敗:', error)
    }
  }
  
  // 各 store 健康檢查
  const checkAppStoreHealth = async (): Promise<boolean> => {
    if (!stores.app) return false
    try {
      return await stores.app.testApiConnection()
    } catch {
      return false
    }
  }
  
  const checkRealtimeStoreHealth = async (): Promise<boolean> => {
    if (!stores.realtime) return false
    return stores.realtime.isHealthy
  }
  
  const checkChatStoreHealth = async (): Promise<boolean> => {
    if (!stores.chat) return false
    return stores.chat.isConnected
  }
  
  const checkFileStoreHealth = async (): Promise<boolean> => {
    if (!stores.file) return false
    return !stores.file.isLoading
  }
  
  const checkDataStoreHealth = async (): Promise<boolean> => {
    if (!stores.data) return false
    return !stores.data.state.syncInProgress
  }
  
  // 工具方法
  const updateStoreHealth = (storeName: string, health: 'healthy' | 'warning' | 'error'): void => {
    state.value.systemHealth[storeName] = health
  }
  
  const addEvent = (type: string, source: string, data?: any): void => {
    const event: SystemEvent = {
      id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: type as any,
      source,
      data,
      timestamp: Date.now()
    }
    
    events.value.push(event)
    
    // 限制事件歷史長度
    if (events.value.length > 1000) {
      events.value = events.value.slice(-1000)
    }
  }
  
  // 手動同步所有數據
  const syncAllSystems = async (): Promise<void> => {
    try {
      console.log('開始手動同步所有系統...')
      addEvent('manual_sync_start', 'integration')
      
      const syncPromises = []
      
      if (stores.chat) {
        syncPromises.push(stores.chat.connectSSE())
      }
      
      if (stores.file) {
        syncPromises.push(stores.file.fetchFiles(false))
      }
      
      if (stores.data) {
        syncPromises.push(stores.data.syncAllData())
      }
      
      if (stores.realtime) {
        syncPromises.push(stores.realtime.refreshData())
      }
      
      await Promise.allSettled(syncPromises)
      
      state.value.lastSyncTime = new Date().toISOString()
      
      addEvent('manual_sync_complete', 'integration', {
        timestamp: state.value.lastSyncTime
      })
      
      if (stores.app) {
        stores.app.addNotification({
          type: 'success',
          title: '系統同步完成',
          message: '所有數據已成功同步'
        })
      }
      
    } catch (error) {
      console.error('系統同步失敗:', error)
      
      if (stores.app) {
        stores.app.addNotification({
          type: 'error',
          title: '系統同步失敗',
          message: error instanceof Error ? error.message : '未知錯誤'
        })
      }
    }
  }
  
  // 重啟系統
  const restartIntegration = async (): Promise<void> => {
    try {
      console.log('重啟系統集成...')
      addEvent('system_restart', 'integration')
      
      // 清理現有資源
      await destroy()
      
      // 重新初始化
      await initialize()
      
      if (stores.app) {
        stores.app.addNotification({
          type: 'success',
          title: '系統已重啟',
          message: '所有模組已重新初始化'
        })
      }
      
    } catch (error) {
      console.error('系統重啟失敗:', error)
      
      if (stores.app) {
        stores.app.addNotification({
          type: 'error',
          title: '系統重啟失敗',
          message: error instanceof Error ? error.message : '重啟過程中發生錯誤'
        })
      }
    }
  }
  
  // 清理資源
  const destroy = async (): Promise<void> => {
    try {
      console.log('清理系統集成資源...')
      
      // 停止健康監控
      stopHealthMonitoring()
      
      // 清理事件監聽器
      window.removeEventListener('online', handleNetworkOnline)
      window.removeEventListener('offline', handleNetworkOffline)
      document.removeEventListener('store-error', handleStoreError)
      document.removeEventListener('data-sync-complete', handleDataSyncComplete)
      
      // 清理各個 stores
      if (stores.chat) {
        stores.chat.destroyChatEnhanced()
      }
      
      if (stores.file) {
        stores.file.disableAutoSync()
      }
      
      if (stores.data) {
        stores.data.destroy()
      }
      
      if (stores.realtime) {
        stores.realtime.destroy()
      }
      
      if (stores.app) {
        stores.app.stopHealthCheck()
      }
      
      // 重置狀態
      state.value = {
        isInitialized: false,
        allStoresReady: false,
        integrationError: null,
        lastSyncTime: null,
        activeSystems: [],
        systemHealth: {}
      }
      
      events.value = []
      
      // 清空 store 引用
      Object.keys(stores).forEach(key => {
        (stores as any)[key] = null
      })
      
      console.log('系統集成資源清理完成')
      
    } catch (error) {
      console.error('清理系統資源失敗:', error)
    }
  }
  
  return {
    // 狀態
    state,
    events,
    
    // 計算屬性
    healthyStores,
    errorStores,
    overallHealth,
    recentEvents,
    
    // 方法
    initialize,
    destroy,
    syncAllSystems,
    restartIntegration,
    performHealthCheck,
    
    // Store 訪問
    getStores: () => stores,
    getStoreHealth: (storeName: string) => state.value.systemHealth[storeName],
    
    // 系統狀態
    isReady: () => state.value.isInitialized && state.value.allStoresReady,
    getSystemInfo: () => ({
      initialized: state.value.isInitialized,
      allReady: state.value.allStoresReady,
      health: overallHealth.value,
      lastSync: state.value.lastSyncTime,
      activeSystems: state.value.activeSystems.length,
      errors: errorStores.value.length
    })
  }
})