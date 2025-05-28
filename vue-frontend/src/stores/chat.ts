import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { Message, ChatState, DecisionType } from '@/types/chat'
import { MessageType } from '@/types/chat'
import { useAppStore } from '@/stores/app'

interface BackendMessage {
  content: string
  type: 'human' | 'assistant'
  sender: string
}

interface BackendState {
  messages: BackendMessage[]
  needs_decision: boolean
  sender: string
  hypothesis: string
  process: string
  process_decision: string
  visualization_state: string
  searcher_state: string
  code_state: string
  report_section: string
  quality_review: string
  needs_revision: boolean
}

export const useChatStore = defineStore('chat', () => {
  const appStore = useAppStore()
  
  // 響應式狀態
  const messages = ref<Message[]>([])
  const isProcessing = ref(false)
  const needsDecision = ref(false)
  const currentTypingAgent = ref<string | undefined>()
  const lastMessageId = ref<string | undefined>()
  const sseConnection = ref<EventSource | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const reconnectDelay = ref(1000) // 1秒

  // 計算屬性
  const chatState = computed<ChatState>(() => ({
    messages: messages.value,
    isProcessing: isProcessing.value,
    needsDecision: needsDecision.value,
    currentTypingAgent: currentTypingAgent.value,
    lastMessageId: lastMessageId.value
  }))

  const canSendMessage = computed(() => 
    !isProcessing.value && !needsDecision.value && isConnected.value
  )

  // 私有方法
  const generateMessageId = (): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  const convertBackendMessage = (backendMsg: BackendMessage): Message => {
    return {
      id: generateMessageId(),
      content: backendMsg.content,
      sender: backendMsg.sender,
      timestamp: new Date().toISOString(),
      type: backendMsg.type === 'human' ? MessageType.USER : MessageType.AGENT
    }
  }

  // SSE連接管理
  const connectSSE = () => {
    if (sseConnection.value) {
      disconnectSSE()
    }

    const sseUrl = `${appStore.config.apiBaseUrl}/stream`
    console.log('連接SSE:', sseUrl)
    
    try {
      const eventSource = new EventSource(sseUrl)
      sseConnection.value = eventSource
      
      eventSource.onopen = () => {
        console.log('SSE連接已成功建立')
        console.log('設置isConnected為true (onopen)')
        isConnected.value = true
        console.log('onopen後isConnected狀態:', isConnected.value)
        console.log('onopen後canSendMessage狀態:', canSendMessage.value)
        reconnectAttempts.value = 0
        reconnectDelay.value = 1000
      }

      // 監聽連接建立事件
      eventSource.addEventListener('connection_established', (event) => {
        console.log('收到SSE連接確認事件')
        console.log('設置isConnected為true (connection_established)')
        isConnected.value = true
        console.log('connection_established後isConnected狀態:', isConnected.value)
        console.log('connection_established後canSendMessage狀態:', canSendMessage.value)
        reconnectAttempts.value = 0
        reconnectDelay.value = 1000
      })

      eventSource.addEventListener('state_update', (event) => {
        try {
          console.log('收到SSE事件:', event.type)
          // 確保連接狀態為true
          if (!isConnected.value) {
            console.log('通過state_update事件確認SSE連接已建立')
            isConnected.value = true
            reconnectAttempts.value = 0
            reconnectDelay.value = 1000
          }
          
          const backendState: BackendState = JSON.parse(event.data)
          console.log('=== SSE state_update 調試 ===')
          console.log('原始事件數據:', event.data)
          console.log('解析後的數據:', backendState)
          console.log('sender:', backendState.sender)
          console.log('needs_decision:', backendState.needs_decision)
          console.log('解析SSE數據成功，代理狀態:', backendState.sender)
          updateFromBackendState(backendState)
        } catch (error) {
          console.error('解析SSE數據失敗:', error)
        }
      })

      eventSource.onerror = (error) => {
        console.error('SSE連接錯誤:', error, '連接狀態:', eventSource.readyState)
        console.error('SSE URL:', sseUrl)
        isConnected.value = false
        
        // 延遲重連，避免立即重試
        setTimeout(() => {
          if (eventSource.readyState === EventSource.CLOSED || eventSource.readyState === EventSource.CONNECTING) {
            handleSSEReconnect()
          }
        }, 1000)
      }
    } catch (error) {
      console.error('創建SSE連接失敗:', error)
      isConnected.value = false
      handleSSEReconnect()
    }
  }

  const disconnectSSE = () => {
    if (sseConnection.value) {
      sseConnection.value.close()
      sseConnection.value = null
      isConnected.value = false
    }
  }

  const handleSSEReconnect = () => {
    if (reconnectAttempts.value < maxReconnectAttempts) {
      reconnectAttempts.value++
      console.log(`嘗試重新連接SSE (${reconnectAttempts.value}/${maxReconnectAttempts})`)
      
      setTimeout(() => {
        connectSSE()
      }, reconnectDelay.value)
      
      // 指數退避
      reconnectDelay.value = Math.min(reconnectDelay.value * 2, 30000)
    } else {
      console.error('SSE重連次數已達上限')
    }
  }

  // 狀態更新
  const updateFromBackendState = (backendState: BackendState) => {
    console.log('收到後端狀態更新:', backendState)
    console.log('當前前端狀態:', {
      消息數量: messages.value.length,
      處理中: isProcessing.value,
      需要決策: needsDecision.value,
      當前代理: currentTypingAgent.value
    })
    
    // 更新消息列表
    if (backendState.messages && Array.isArray(backendState.messages)) {
      const newMessages = backendState.messages.map(convertBackendMessage)
      console.log(`後端消息數量: ${backendState.messages.length}, 前端消息數量: ${messages.value.length}`)
      
      // 只添加新消息，避免重複
      if (newMessages.length > messages.value.length) {
        const newCount = newMessages.length - messages.value.length
        const latestMessages = newMessages.slice(-newCount)
        console.log(`添加 ${latestMessages.length} 條新消息`)
        messages.value.push(...latestMessages)
        
        if (latestMessages.length > 0) {
          lastMessageId.value = latestMessages[latestMessages.length - 1].id
          console.log(`更新最新消息ID: ${lastMessageId.value}`)
        }
      } else if (newMessages.length === messages.value.length) {
        console.log('消息數量相同，檢查是否有內容更新')
        // 檢查最後一條消息是否有更新
        const lastBackendMsg = backendState.messages[backendState.messages.length - 1]
        const lastFrontendMsg = messages.value[messages.value.length - 1]
        if (lastBackendMsg && lastFrontendMsg &&
            lastBackendMsg.content !== lastFrontendMsg.content) {
          console.log('最後一條消息內容已更新，替換該消息')
          const updatedMsg = convertBackendMessage(lastBackendMsg)
          updatedMsg.id = lastFrontendMsg.id // 保持ID不變
          messages.value[messages.value.length - 1] = updatedMsg
        }
      }
    }

    // 更新決策狀態
    const oldNeedsDecision = needsDecision.value
    needsDecision.value = Boolean(backendState.needs_decision)
    if (oldNeedsDecision !== needsDecision.value) {
      console.log(`決策狀態變更: ${oldNeedsDecision} -> ${needsDecision.value}`)
    }
    
    // 更新處理狀態
    if (backendState.sender) {
      console.log(`後端發送者: ${backendState.sender}`)
      if (backendState.sender === 'human_choice' || backendState.sender === 'human_review') {
        console.log('需要用戶決策，停止處理')
        isProcessing.value = false
        needsDecision.value = true
      } else {
        const oldAgent = currentTypingAgent.value
        currentTypingAgent.value = backendState.sender
        if (oldAgent !== currentTypingAgent.value) {
          console.log(`當前代理變更: ${oldAgent || 'None'} -> ${currentTypingAgent.value}`)
        }
        isProcessing.value = false // 收到更新意味著處理完成
        console.log('處理完成，isProcessing設為false')
      }
    }
    
    // 在updateFromBackendState結尾檢查所有狀態
    console.log('updateFromBackendState完成後的狀態:', {
      isConnected: isConnected.value,
      isProcessing: isProcessing.value,
      needsDecision: needsDecision.value,
      canSendMessage: canSendMessage.value
    })
  }

  // 公共方法
  const sendMessage = async (content: string): Promise<void> => {
    console.log('開始發送消息:', content)
    console.log('當前狀態:', {
      canSend: canSendMessage.value,
      isProcessing: isProcessing.value,
      isConnected: isConnected.value,
      needsDecision: needsDecision.value
    })
    
    if (!canSendMessage.value || !content.trim()) {
      console.log('發送被阻止 - canSendMessage:', canSendMessage.value, 'content:', content.trim())
      return
    }

    console.log('設置處理狀態為true')
    isProcessing.value = true
    
    // 立即添加用戶消息到界面
    const userMessage: Message = {
      id: generateMessageId(),
      content: content.trim(),
      sender: 'User',
      timestamp: new Date().toISOString(),
      type: MessageType.USER
    }
    
    messages.value.push(userMessage)
    lastMessageId.value = userMessage.id

    try {
      const apiUrl = `${appStore.config.apiBaseUrl}/api/send_message`
      const requestBody = {
        message: content.trim(),
        process_decision: ''
      }
      
      console.log('發送HTTP請求到:', apiUrl)
      console.log('請求內容:', requestBody)
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })

      console.log('收到HTTP響應，狀態:', response.status)
      
      if (!response.ok) {
        throw new Error(`HTTP錯誤! 狀態: ${response.status}`)
      }

      const result = await response.json()
      console.log('消息發送成功:', result)
      
      if (result.status !== 'processing') {
        console.warn('意外的API回應狀態:', result.status)
      }
    } catch (error) {
      console.error('發送消息失敗:', error)
      
      // 添加錯誤消息
      const errorMessage: Message = {
        id: generateMessageId(),
        content: `錯誤: 發送消息失敗 (${error instanceof Error ? error.message : '未知錯誤'})`,
        sender: 'System',
        timestamp: new Date().toISOString(),
        type: MessageType.SYSTEM
      }
      
      messages.value.push(errorMessage)
      isProcessing.value = false
    }
  }

  const sendDecision = async (decision: DecisionType): Promise<void> => {
    if (!needsDecision.value) {
      return
    }

    needsDecision.value = false
    isProcessing.value = true

    // 映射決策類型到後端格式
    const decisionCode = decision === 'REGENERATE_HYPOTHESIS' ? '1' : '2'
    const decisionText = decision === 'REGENERATE_HYPOTHESIS' ? '重新生成假設' : '繼續研究'

    // 添加決策消息到界面
    const decisionMessage: Message = {
      id: generateMessageId(),
      content: `已選擇: ${decisionText}`,
      sender: 'User',
      timestamp: new Date().toISOString(),
      type: MessageType.USER
    }
    
    messages.value.push(decisionMessage)
    lastMessageId.value = decisionMessage.id

    try {
      const response = await fetch(`${appStore.config.apiBaseUrl}/api/send_message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: '',
          process_decision: decisionCode
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP錯誤! 狀態: ${response.status}`)
      }

      const result = await response.json()
      console.log('決策發送成功:', result)
    } catch (error) {
      console.error('發送決策失敗:', error)
      
      // 添加錯誤消息並恢復決策狀態
      const errorMessage: Message = {
        id: generateMessageId(),
        content: `錯誤: 發送決策失敗 (${error instanceof Error ? error.message : '未知錯誤'})`,
        sender: 'System',
        timestamp: new Date().toISOString(),
        type: MessageType.SYSTEM
      }
      
      messages.value.push(errorMessage)
      needsDecision.value = true
      isProcessing.value = false
    }
  }

  const clearMessages = (): void => {
    messages.value = []
    lastMessageId.value = undefined
    currentTypingAgent.value = undefined
  }

  const initializeChat = async (): Promise<void> => {
    console.log('初始化聊天界面...')
    console.log('當前前端狀態:', {
      處理中: isProcessing.value,
      需要決策: needsDecision.value,
      已連接: isConnected.value,
      可發送消息: canSendMessage.value
    })
    
    // 首先嘗試獲取初始狀態來測試後端連接
    try {
      const response = await fetch(`${appStore.config.apiBaseUrl}/api/state`, {
        timeout: 5000
      } as RequestInit)
      
      if (response.ok) {
        const backendState: BackendState = await response.json()
        console.log('獲取到後端初始狀態:', backendState)
        console.log('後端needs_decision值:', backendState.needs_decision)
        
        updateFromBackendState(backendState)
        
        console.log('更新後的前端狀態:', {
          處理中: isProcessing.value,
          需要決策: needsDecision.value,
          已連接: isConnected.value,
          可發送消息: canSendMessage.value
        })
        
        // 後端可用，建立SSE連接
        connectSSE()
      } else {
        console.warn('後端API不可用，狀態碼:', response.status)
        handleOfflineMode()
      }
    } catch (error) {
      console.error('後端服務不可用:', error)
      handleOfflineMode()
    }
  }

  const handleOfflineMode = () => {
    console.log('進入離線模式')
    isConnected.value = false
    reconnectAttempts.value = maxReconnectAttempts
    
    // 添加離線提示消息
    const offlineMessage: Message = {
      id: generateMessageId(),
      content: '⚠️ 無法連接到後端服務。您仍可以輸入消息，但需要等待後端服務恢復後才能獲得回應。\n\n請檢查：\n1. 後端服務是否運行在 http://localhost:5001\n2. 網路連接是否正常\n3. 後端服務是否正確配置',
      sender: 'System',
      timestamp: new Date().toISOString(),
      type: MessageType.SYSTEM
    }
    
    messages.value.push(offlineMessage)
  }

  const destroyChat = (): void => {
    console.log('銷毀聊天界面...')
    disconnectSSE()
    clearMessages()
    isProcessing.value = false
    needsDecision.value = false
    currentTypingAgent.value = undefined
  }

  // 實時數據同步
  const syncWithRealtime = (realtimeData: any): void => {
    try {
      if (realtimeData.type === 'chat_state' && realtimeData.data) {
        console.log('從實時數據同步聊天狀態:', realtimeData.data)
        updateFromBackendState(realtimeData.data)
      }
    } catch (error) {
      console.error('同步實時數據失敗:', error)
    }
  }

  // 增強的錯誤處理和重試
  const sendMessageWithRetry = async (content: string, maxRetries: number = 3): Promise<boolean> => {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        await sendMessage(content)
        return true
      } catch (error) {
        console.error(`發送消息失敗 (嘗試 ${attempt + 1}/${maxRetries}):`, error)
        
        if (attempt < maxRetries - 1) {
          // 等待後重試
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000))
          
          // 檢查連接狀態
          if (!isConnected.value) {
            console.log('嘗試重新建立 SSE 連接...')
            connectSSE()
            await new Promise(resolve => setTimeout(resolve, 2000)) // 等待連接建立
          }
        }
      }
    }
    return false
  }

  // 批量消息處理
  const processBatchMessages = async (messages: string[]): Promise<boolean[]> => {
    const results: boolean[] = []
    
    for (const message of messages) {
      const success = await sendMessageWithRetry(message)
      results.push(success)
      
      // 如果不是最後一條消息，等待一段時間避免過載
      if (message !== messages[messages.length - 1]) {
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
    
    return results
  }

  // 連接狀態監控
  const startConnectionMonitoring = (): void => {
    // 監聽網路狀態變化
    const handleOnline = () => {
      console.log('網路已恢復，重新建立 SSE 連接')
      if (!isConnected.value) {
        connectSSE()
      }
    }

    const handleOffline = () => {
      console.log('網路已斷開')
      isConnected.value = false
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // 監聽自定義重連事件
    const handleNetworkReconnect = () => {
      console.log('收到網路重連事件，檢查 SSE 連接狀態')
      if (!isConnected.value) {
        connectSSE()
      }
    }

    document.addEventListener('network-reconnected', handleNetworkReconnect)

    // 儲存事件監聽器引用以便清理
    ;(window as any).chatEventListeners = {
      handleOnline,
      handleOffline,
      handleNetworkReconnect
    }
  }

  const stopConnectionMonitoring = (): void => {
    const listeners = (window as any).chatEventListeners
    if (listeners) {
      window.removeEventListener('online', listeners.handleOnline)
      window.removeEventListener('offline', listeners.handleOffline)
      document.removeEventListener('network-reconnected', listeners.handleNetworkReconnect)
      ;(window as any).chatEventListeners = null
    }
  }

  // 性能優化：消息去重
  const deduplicateMessages = (): void => {
    const seen = new Set<string>()
    const uniqueMessages: Message[] = []
    
    for (const message of messages.value) {
      const key = `${message.content}-${message.sender}-${message.type}`
      if (!seen.has(key)) {
        seen.add(key)
        uniqueMessages.push(message)
      }
    }
    
    if (uniqueMessages.length !== messages.value.length) {
      console.log(`去除了 ${messages.value.length - uniqueMessages.length} 條重複消息`)
      messages.value = uniqueMessages
    }
  }

  // 增強初始化
  const initializeChatEnhanced = async (): Promise<void> => {
    console.log('增強聊天界面初始化...')
    
    // 啟動連接監控
    startConnectionMonitoring()
    
    // 執行原有初始化
    await initializeChat()
    
    // 定期去重消息
    setInterval(deduplicateMessages, 30000) // 每30秒去重一次
  }

  // 增強銷毀
  const destroyChatEnhanced = (): void => {
    console.log('增強聊天界面銷毀...')
    
    stopConnectionMonitoring()
    destroyChat()
  }

  return {
    // 狀態
    messages: readonly(messages),
    isProcessing: readonly(isProcessing),
    needsDecision: readonly(needsDecision),
    currentTypingAgent: readonly(currentTypingAgent),
    lastMessageId: readonly(lastMessageId),
    isConnected: readonly(isConnected),
    reconnectAttempts: readonly(reconnectAttempts),
    
    // 計算屬性
    chatState,
    canSendMessage,
    
    // 基礎方法
    sendMessage,
    sendDecision,
    clearMessages,
    initializeChat,
    destroyChat,
    connectSSE,
    disconnectSSE,
    
    // 增強方法
    syncWithRealtime,
    sendMessageWithRetry,
    processBatchMessages,
    startConnectionMonitoring,
    stopConnectionMonitoring,
    deduplicateMessages,
    initializeChatEnhanced,
    destroyChatEnhanced
  }
})