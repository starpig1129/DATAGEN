import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { useAppStore } from './app'
import { useChatStore } from './chat'

// 實時數據類型定義
export interface RealTimeData {
  id: string
  type: 'agent_status' | 'system_metrics' | 'data_update' | 'chart_data' | 'file_status'
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
  const chatStore = useChatStore()
  
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
  
  // WebSocket 連接管理
  const connectWebSocket = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = appStore.config.wsUrl.replace('/graphql/ws', '/ws')
        console.log('正在連接 WebSocket:', wsUrl)
        
        state.value.connectionStatus = 'connecting'
        state.value.connectionError = null
        
        const ws = new WebSocket(wsUrl)
        wsConnection.value = ws
        
        ws.onopen = () => {
          console.log('WebSocket 連接已建立')
          state.value.isConnected = true
          state.value.connectionStatus = 'connected'
          state.value.lastConnected = new Date().toISOString()
          state.value.reconnectAttempts = 0
          state.value.connectionError = null
          
          // 發送初始化消息
          sendMessage({
            type: 'init',
            clientId: generateClientId(),
            timestamp: Date.now()
          })
          
          startMetricsPolling()
          resolve()
        }
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            handleRealtimeMessage(data)
          } catch (error) {
            console.error('解析 WebSocket 消息失敗:', error)
            state.value.lastError = '消息解析錯誤'
          }
        }
        
        ws.onclose = (event) => {
          console.log('WebSocket 連接已關閉:', event.code, event.reason)
          state.value.isConnected = false
          state.value.connectionStatus = 'disconnected'
          
          stopMetricsPolling()
          
          if (event.code !== 1000 && canReconnect.value) {
            scheduleReconnect()
          }
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket 錯誤:', error)
          state.value.connectionStatus = 'error'
          state.value.connectionError = 'WebSocket 連接錯誤'
          state.value.lastError = 'WebSocket 連接失敗'
          reject(new Error('WebSocket 連接失敗'))
        }
        
        // 連接超時處理
        setTimeout(() => {
          if (state.value.connectionStatus === 'connecting') {
            ws.close()
            reject(new Error('連接超時'))
          }
        }, 10000)
        
      } catch (error) {
        console.error('創建 WebSocket 連接失敗:', error)
        state.value.connectionStatus = 'error'
        state.value.connectionError = error instanceof Error ? error.message : '未知錯誤'
        reject(error)
      }
    })
  }
  
  const disconnectWebSocket = (): void => {
    if (wsConnection.value) {
      state.value.autoReconnect = false
      wsConnection.value.close(1000, '用戶主動斷開')
      wsConnection.value = null
    }
    
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
      connectWebSocket().catch(error => {
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
  
  // 消息處理
  const handleRealtimeMessage = (message: any): void => {
    try {
      const realTimeData: RealTimeData = {
        id: generateDataId(),
        type: message.type || 'data_update',
        data: message.data || message,
        timestamp: message.timestamp || Date.now(),
        source: message.source || 'server'
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
      }
      
    } catch (error) {
      console.error('處理實時消息失敗:', error)
      state.value.lastError = '消息處理錯誤'
    }
  }
  
  const sendMessage = (message: any): boolean => {
    if (!wsConnection.value || state.value.connectionStatus !== 'connected') {
      console.warn('WebSocket 未連接，無法發送消息')
      return false
    }
    
    try {
      wsConnection.value.send(JSON.stringify(message))
      return true
    } catch (error) {
      console.error('發送 WebSocket 消息失敗:', error)
      state.value.lastError = '發送消息失敗'
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
  
  // 初始化和清理
  const initialize = async (): Promise<void> => {
    try {
      await connectWebSocket()
      
      appStore.addNotification({
        type: 'success',
        title: '實時連接已建立',
        message: '系統現在可以接收實時更新'
      })
    } catch (error) {
      console.error('初始化實時連接失敗:', error)
      
      appStore.addNotification({
        type: 'warning',
        title: '實時連接失敗',
        message: '將使用定期輪詢模式'
      })
      
      // 如果 WebSocket 失敗，則使用定期輪詢
      startMetricsPolling()
    }
  }
  
  const destroy = (): void => {
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