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
  
  // WebSocket 連接
  const wsConnection = ref<WebSocket | null>(null)
  const reconnectTimer = ref<number | null>(null)
  const heartbeatTimer = ref<number | null>(null)
  
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
  
  // WebSocket 連接管理
  const connectWebSocket = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        // 檢查是否已有連接
        if (wsConnection.value && wsConnection.value.readyState === WebSocket.OPEN) {
          console.log('🔄 WebSocket 已經連接')
          resolve()
          return
        }

        // 獲取 WebSocket URL
        const wsUrl = import.meta.env.VITE_WS_URL
        if (!wsUrl) {
          throw new Error('VITE_WS_URL 環境變數未設定')
        }

        console.log('🔌 正在連接 WebSocket:', wsUrl)
        state.value.connectionStatus = 'connecting'

        // 建立 WebSocket 連接
        wsConnection.value = new WebSocket(wsUrl)

        // 連接成功
        wsConnection.value.onopen = () => {
          console.log('✅ WebSocket 連接成功')
          state.value.isConnected = true
          state.value.connectionStatus = 'connected'
          state.value.lastConnected = new Date().toISOString()
          state.value.reconnectAttempts = 0
          state.value.connectionError = null

          // 啟動心跳機制
          startHeartbeat()

          // 設置事件監聽器
          setupMessageHandlers()

          resolve()
        }

        // 連接錯誤
        wsConnection.value.onerror = (error) => {
          console.error('❌ WebSocket 連接錯誤:', error)
          state.value.connectionStatus = 'error'
          state.value.connectionError = 'WebSocket 連接失敗'
          state.value.lastError = '連接錯誤'

          reject(error)
        }

        // 接收消息
        wsConnection.value.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            console.log('📨 收到 WebSocket 消息:', message)
            handleRealtimeMessage(message)
          } catch (error) {
            console.error('解析 WebSocket 消息失敗:', error)
            state.value.lastError = '消息解析錯誤'
          }
        }

        // 連接關閉
        wsConnection.value.onclose = (event) => {
          console.log('🔌 WebSocket 連接關閉:', event.code, event.reason)
          state.value.isConnected = false
          state.value.connectionStatus = 'disconnected'

          // 停止心跳
          stopHeartbeat()

          // 移除事件監聽器
          removeMessageHandlers()

          // 如果不是正常關閉，嘗試重新連接
          if (event.code !== 1000 && state.value.autoReconnect) {
            scheduleReconnect()
          }
        }

      } catch (error) {
        console.error('建立 WebSocket 連接失敗:', error)
        state.value.connectionStatus = 'error'
        state.value.connectionError = error instanceof Error ? error.message : '未知錯誤'
        reject(error)
      }
    })
  }
  
  const disconnectWebSocket = (): void => {
    console.log('🔌 斷開 WebSocket 連接')

    // 清理事件監聽器
    removeMessageHandlers()

    // 停止心跳
    stopHeartbeat()

    // 關閉 WebSocket 連接
    if (wsConnection.value) {
      wsConnection.value.close(1000, '正常關閉')
      wsConnection.value = null
    }

    clearReconnectTimer()

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
      connectWebSocket().catch((error: any) => {
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
  
  // WebSocket 消息處理器設置
  const setupMessageHandlers = (): void => {
    console.log('🔧 設置 WebSocket 消息處理器')
    // 消息處理器已經在 connectWebSocket 中設置
  }

  const removeMessageHandlers = (): void => {
    console.log('🧹 移除 WebSocket 消息處理器')
    // 消息處理器會在連接關閉時自動清理
  }

  // 心跳機制
  const startHeartbeat = (): void => {
    stopHeartbeat() // 確保沒有重複的心跳

    console.log('💓 啟動 WebSocket 心跳機制')

    heartbeatTimer.value = setInterval(() => {
      if (wsConnection.value && wsConnection.value.readyState === WebSocket.OPEN) {
        // 發送心跳消息
        wsConnection.value.send(JSON.stringify({
          type: 'ping',
          timestamp: Date.now()
        }))
        console.log('💓 發送心跳消息')
      }
    }, 30000) // 每30秒發送一次心跳
  }

  const stopHeartbeat = (): void => {
    if (heartbeatTimer.value) {
      clearInterval(heartbeatTimer.value)
      heartbeatTimer.value = null
      console.log('💔 停止 WebSocket 心跳機制')
    }
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
    try {
      if (wsConnection.value && wsConnection.value.readyState === WebSocket.OPEN) {
        wsConnection.value.send(JSON.stringify(message))
        console.log('📤 發送 WebSocket 消息:', message)
        return true
      } else {
        console.warn('WebSocket 未連接，無法發送消息')
        return false
      }
    } catch (error) {
      console.error('發送 WebSocket 消息失敗:', error)
      return false
    }
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
  
  // API 輪詢管理 (備用方案，當 WebSocket 不可用時使用)
  const startMetricsPolling = (): void => {
    if (heartbeatTimer.value) {
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
    heartbeatTimer.value = setInterval(pollMetrics, 10000) // 每10秒
  }

  const stopMetricsPolling = (): void => {
    if (heartbeatTimer.value) {
      clearInterval(heartbeatTimer.value)
      heartbeatTimer.value = null
    }
  }
  
  // 工具函數
  const generateClientId = (): string => {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  const generateDataId = (): string => {
    return `data_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  // 初始化和清理 - WebSocket 連接管理
  const initialize = async (): Promise<void> => {
    try {
      console.log('🚀 Realtime Store 初始化 (WebSocket 模式)')
      await connectWebSocket()

      appStore.addNotification({
        type: 'success',
        title: '實時連接已建立',
        message: '系統現在可以接收 WebSocket 實時更新'
      })
    } catch (error) {
      console.error('初始化 WebSocket 連接失敗:', error)

      appStore.addNotification({
        type: 'warning',
        title: 'WebSocket 連接失敗',
        message: '將使用定期輪詢模式作為備用方案'
      })

      // 如果 WebSocket 失敗，則使用定期輪詢作為備用
      startMetricsPolling()
    }
  }

  const destroy = (): void => {
    console.log('🧹 Realtime Store 清理資源')
    disconnectWebSocket()
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
    connectWebSocket,
    disconnectWebSocket,
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