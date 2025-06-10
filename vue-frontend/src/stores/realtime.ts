import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { useAppStore } from './app'
import { useChatStore } from './chat'

// 實時數據類型定義
export interface RealTimeData {
  id: string
  type: 'agent_status' | 'system_metrics' | 'data_update' | 'chart_data' | 'file_status' | 'chat_state'
  data: any
  timestamp: number
  source: string
}

export interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  activeConnections: number
  queueSize: number
  lastUpdate: string
}

export interface AgentStatus {
  agentId: string
  name: string
  status: 'idle' | 'processing' | 'error' | 'completed'
  progress: number
  lastActivity: string
  currentTask?: string
}

interface RealTimeState {
  // 連接狀態
  isConnected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  lastConnected: string | null
  reconnectAttempts: number
  
  // 實時數據
  systemMetrics: SystemMetrics | null
  agentStatuses: Map<string, AgentStatus>
  realtimeData: RealTimeData[]
  
  // 錯誤處理
  connectionError: string | null
  lastError: string | null
  
  // 配置
  autoReconnect: boolean
  reconnectInterval: number
  maxReconnectAttempts: number
  dataRetentionLimit: number
}

export const useRealTimeStore = defineStore('realtime', () => {
  const appStore = useAppStore()
  // 移除重複的 chatStore 導入，避免循環依賴
  // const chatStore = useChatStore()
  
  // 響應式狀態
  const state = ref<RealTimeState>({
    isConnected: false,
    connectionStatus: 'disconnected',
    lastConnected: null,
    reconnectAttempts: 0,
    
    systemMetrics: null,
    agentStatuses: new Map(),
    realtimeData: [],
    
    connectionError: null,
    lastError: null,
    
    autoReconnect: true,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    dataRetentionLimit: 100
  })
  
  // SSE 連接
  const sseConnection = ref<EventSource | null>(null)
  const reconnectTimer = ref<number | null>(null)
  const metricsTimer = ref<number | null>(null)
  
  // 計算屬性
  const isHealthy = computed(() => 
    state.value.isConnected && 
    state.value.connectionStatus === 'connected' &&
    !state.value.connectionError
  )
  
  const activeAgents = computed(() => 
    Array.from(state.value.agentStatuses.values()).filter(
      agent => agent.status === 'processing'
    )
  )
  
  const latestData = computed(() => 
    state.value.realtimeData.slice(-10).reverse()
  )
  
  const canReconnect = computed(() => 
    state.value.autoReconnect && 
    state.value.reconnectAttempts < state.value.maxReconnectAttempts
  )
  
  // SSE 連接管理 - 統一由 Chat Store 處理，Realtime Store 只負責非聊天相關的實時數據
  // 不再建立獨立的 SSE 連接，避免重複連接和事件處理衝突
  const connectSSE = (): Promise<void> => {
    console.log('⚠️  Realtime Store 不再建立獨立 SSE 連接')
    console.log('   所有 SSE 事件統一由 Chat Store 處理')
    console.log('   Realtime Store 通過事件監聽接收狀態更新')
    
    // 設置為已連接狀態，實際連接由 Chat Store 管理
    state.value.isConnected = true
    state.value.connectionStatus = 'connected'
    state.value.lastConnected = new Date().toISOString()
    state.value.reconnectAttempts = 0
    state.value.connectionError = null
    
    // 監聽來自 Chat Store 的狀態更新
    setupChatStoreEventListeners()
    
    return Promise.resolve()
  }
  
  const disconnectSSE = (): void => {
    console.log('Realtime Store 斷開連接 (實際連接由 Chat Store 管理)')
    
    // 清理事件監聽器
    removeChatStoreEventListeners()
    
    clearReconnectTimer()
    stopMetricsPolling()
    
    state.value.isConnected = false
    state.value.connectionStatus = 'disconnected'
  }
  
  // 重連管理
  const scheduleReconnect = (): void => {
    if (!canReconnect.value) {
      return
    }
    
    clearReconnectTimer()
    
    state.value.reconnectAttempts++
    const delay = Math.min(
      state.value.reconnectInterval * Math.pow(2, state.value.reconnectAttempts - 1),
      30000
    )
    
    console.log(`將在 ${delay}ms 後嘗試重新連接 (第 ${state.value.reconnectAttempts} 次)`)
    
    reconnectTimer.value = setTimeout(() => {
      connectSSE().catch(error => {
        console.error('重新連接失敗:', error)
        if (canReconnect.value) {
          scheduleReconnect()
        }
      })
    }, delay)
  }
  
  const clearReconnectTimer = (): void => {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
  }
  
  // 統一事件監聽器設置 - 監聽來自 Chat Store 的狀態更新
  const setupChatStoreEventListeners = (): void => {
    console.log('🔗 Realtime Store 設置 Chat Store 事件監聽器')
    
    // 監聽來自 Chat Store 的狀態更新事件
    document.addEventListener('realtime-state-update', handleChatStoreUpdate as EventListener)
    document.addEventListener('realtime-agent-status', handleAgentStatusUpdate as EventListener)
    document.addEventListener('realtime-system-metrics', handleSystemMetricsUpdate as EventListener)
  }
  
  const removeChatStoreEventListeners = (): void => {
    console.log('🔌 Realtime Store 移除事件監聽器')
    
    document.removeEventListener('realtime-state-update', handleChatStoreUpdate as EventListener)
    document.removeEventListener('realtime-agent-status', handleAgentStatusUpdate as EventListener)
    document.removeEventListener('realtime-system-metrics', handleSystemMetricsUpdate as EventListener)
  }
  
  // 事件處理函數
  const handleChatStoreUpdate = (event: Event): void => {
    try {
      const customEvent = event as CustomEvent
      console.log('📨 Realtime Store 收到 Chat Store 狀態更新:', customEvent.detail)
      handleRealtimeMessage(customEvent.detail)
    } catch (error) {
      console.error('處理 Chat Store 狀態更新失敗:', error)
    }
  }
  
  const handleAgentStatusUpdate = (event: Event): void => {
    try {
      const customEvent = event as CustomEvent
      console.log('🤖 Realtime Store 收到代理狀態更新:', customEvent.detail)
      updateAgentStatus(customEvent.detail)
    } catch (error) {
      console.error('處理代理狀態更新失敗:', error)
    }
  }
  
  const handleSystemMetricsUpdate = (event: Event): void => {
    try {
      const customEvent = event as CustomEvent
      console.log('📊 Realtime Store 收到系統指標更新:', customEvent.detail)
      updateSystemMetrics(customEvent.detail)
    } catch (error) {
      console.error('處理系統指標更新失敗:', error)
    }
  }

  // 消息處理 - 現在主要處理來自 Chat Store 轉發的消息
  const handleRealtimeMessage = (message: any): void => {
    try {
      const realTimeData: RealTimeData = {
        id: generateDataId(),
        type: message.type || 'data_update',
        data: message.data || message,
        timestamp: message.timestamp || Date.now(),
        source: message.source || 'chat_store'
      }
      
      // 添加到數據列表
      state.value.realtimeData.push(realTimeData)
      
      // 限制數據量
      if (state.value.realtimeData.length > state.value.dataRetentionLimit) {
        state.value.realtimeData = state.value.realtimeData.slice(-state.value.dataRetentionLimit)
      }
      
      // 根據消息類型處理
      switch (realTimeData.type) {
        case 'system_metrics':
          updateSystemMetrics(realTimeData.data)
          break
        case 'agent_status':
          updateAgentStatus(realTimeData.data)
          break
        case 'data_update':
          notifyDataUpdate(realTimeData.data)
          break
        case 'chart_data':
          notifyChartUpdate(realTimeData.data)
          break
        case 'file_status':
          notifyFileUpdate(realTimeData.data)
          break
        case 'chat_state':
          console.log('📞 Realtime Store 收到聊天狀態更新，已由 Chat Store 處理')
          break
      }
      
    } catch (error) {
      console.error('處理實時消息失敗:', error)
      state.value.lastError = '消息處理錯誤'
    }
  }
  
  const sendMessage = (message: any): boolean => {
    // SSE 是單向通信，不支持從客戶端發送消息
    // 如果需要發送消息，應該使用 HTTP API
    console.warn('SSE 不支持發送消息，請使用 HTTP API')
    return false
  }
  
  // 數據更新處理
  const updateSystemMetrics = (metrics: Partial<SystemMetrics>): void => {
    state.value.systemMetrics = {
      ...state.value.systemMetrics,
      ...metrics,
      lastUpdate: new Date().toISOString()
    } as SystemMetrics
  }
  
  const updateAgentStatus = (agentData: AgentStatus): void => {
    state.value.agentStatuses.set(agentData.agentId, {
      ...agentData,
      lastActivity: new Date().toISOString()
    })
  }
  
  const notifyDataUpdate = (data: any): void => {
    // 通知其他 stores 數據已更新
    console.log('數據更新通知:', data)
    
    // 可以在這裡觸發其他 stores 的數據刷新
    if (data.type === 'chat_state') {
      // 觸發聊天 store 更新
    }
  }
  
  const notifyChartUpdate = (chartData: any): void => {
    // 通知圖表組件數據已更新
    console.log('圖表數據更新:', chartData)
    
    // 可以通過事件總線或直接調用組件方法來更新圖表
    document.dispatchEvent(new CustomEvent('chart-data-update', {
      detail: chartData
    }))
  }
  
  const notifyFileUpdate = (fileData: any): void => {
    // 通知文件系統更新
    console.log('文件狀態更新:', fileData)
  }
  
  // API 輪詢管理
  const startMetricsPolling = (): void => {
    if (metricsTimer.value) {
      return
    }
    
    const pollMetrics = async () => {
      try {
        const response = await fetch(`${appStore.config.apiBaseUrl}/api/system/status`)
        if (response.ok) {
          const data = await response.json()
          updateSystemMetrics({
            cpu: 0, // 實際應從 API 獲取
            memory: 0,
            disk: 0,
            activeConnections: 1,
            queueSize: 0,
            lastUpdate: data.timestamp
          })
        }
      } catch (error) {
        console.error('獲取系統指標失敗:', error)
      }
    }
    
    // 立即執行一次
    pollMetrics()
    
    // 定期輪詢
    metricsTimer.value = setInterval(pollMetrics, 10000) // 每10秒
  }
  
  const stopMetricsPolling = (): void => {
    if (metricsTimer.value) {
      clearInterval(metricsTimer.value)
      metricsTimer.value = null
    }
  }
  
  // 工具函數
  const generateClientId = (): string => {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  const generateDataId = (): string => {
    return `data_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  // 初始化和清理 - 統一 SSE 連接管理
  const initialize = async (): Promise<void> => {
    try {
      console.log('🚀 Realtime Store 初始化 (統一連接模式)')
      await connectSSE()
      
      appStore.addNotification({
        type: 'success',
        title: '實時連接已建立',
        message: '系統現在可以接收實時更新 (統一管理模式)'
      })
    } catch (error) {
      console.error('初始化實時連接失敗:', error)
      
      appStore.addNotification({
        type: 'warning',
        title: '實時連接失敗',
        message: '將使用定期輪詢模式'
      })
      
      // 如果 SSE 失敗，則使用定期輪詢
      startMetricsPolling()
    }
  }
  
  const destroy = (): void => {
    console.log('🧹 Realtime Store 清理資源')
    disconnectSSE()
    clearReconnectTimer()
    stopMetricsPolling()
    
    state.value.realtimeData = []
    state.value.agentStatuses.clear()
    state.value.systemMetrics = null
  }
  
  // 手動刷新
  const refreshData = async (): Promise<void> => {
    try {
      // 刷新系統狀態
      const statusResponse = await fetch(`${appStore.config.apiBaseUrl}/api/system/status`)
      if (statusResponse.ok) {
        const statusData = await statusResponse.json()
        updateSystemMetrics(statusData.metrics || {})
      }
      
      // 刷新聊天狀態
      const stateResponse = await fetch(`${appStore.config.apiBaseUrl}/api/state`)
      if (stateResponse.ok) {
        const stateData = await stateResponse.json()
        notifyDataUpdate({ type: 'chat_state', data: stateData })
      }
      
      appStore.addNotification({
        type: 'success',
        title: '數據已刷新',
        message: '所有實時數據已更新'
      })
    } catch (error) {
      console.error('刷新數據失敗:', error)
      
      appStore.addNotification({
        type: 'error',
        title: '刷新失敗',
        message: error instanceof Error ? error.message : '未知錯誤'
      })
    }
  }
  
  return {
    // 狀態
    state: readonly(state),
    
    // 計算屬性
    isHealthy,
    activeAgents,
    latestData,
    canReconnect,
    
    // 方法
    initialize,
    destroy,
    connectSSE,
    disconnectSSE,
    sendMessage,
    refreshData,
    
    // 數據訪問
    getSystemMetrics: () => state.value.systemMetrics,
    getAgentStatus: (agentId: string) => state.value.agentStatuses.get(agentId),
    getAllAgentStatuses: () => Array.from(state.value.agentStatuses.values()),
    getRealtimeData: (type?: string) => type 
      ? state.value.realtimeData.filter(d => d.type === type)
      : state.value.realtimeData
  }
})