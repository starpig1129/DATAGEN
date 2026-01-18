import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { Message, ChatState, DecisionType } from '@/types/chat'
import { MessageType } from '@/types/chat'
import { useAppStore } from '@/stores/app'
import { useSettingsStore } from '@/stores/settings'

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

// 內部使用的聊天訊息介面
interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  agentId?: string
  metadata?: Record<string, any>
}

// 決策選項介面
interface DecisionOption {
  id: string
  label: string
  value: string
}

export const useChatStore = defineStore('chat', () => {
  const appStore = useAppStore()
  const settingsStore = useSettingsStore()

  // 獲取 API Base URL (優先使用 settings 中的配置)
  const getApiBaseUrl = () => {
    return settingsStore.settings.api.baseUrl || appStore.config.apiBaseUrl
  }
  
  // 響應式狀態
  const messages = ref<Message[]>([])
  const isProcessing = ref(false)
  const needsDecision = ref(false)
  const currentTypingAgent = ref<string | undefined>()
  const lastMessageId = ref<string | undefined>()
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const reconnectDelay = ref(1000) // 1秒
  
  // 添加決策處理鎖定機制，防止狀態競爭
  const isProcessingDecision = ref(false)
  
  // 添加狀態版本號，防止舊狀態覆蓋新狀態
  const stateVersion = ref(0)
  const lastStateUpdateTime = ref(0)
  
  // 決策選項與 ID
  const decisionOptions = ref<DecisionOption[]>([])
  const currentDecisionId = ref<string | null>(null)

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

  // WebSocket 連接管理
  const connectWebSocket = () => {
    if (socket.value) {
      disconnectWebSocket()
    }

    const baseUrl = getApiBaseUrl()
    // 簡單替換 http->ws, https->wss
    const wsUrl = baseUrl.replace(/^http/, 'ws') + '/stream'
    console.log('連接 WebSocket:', wsUrl)
    
    try {
      const ws = new WebSocket(wsUrl)
      socket.value = ws
      
      ws.onopen = () => {
        console.log('WebSocket 連接已成功建立')
        // 發送初始化消息
        const initData = {
          type: 'init',
          clientId: `client-${Date.now()}`
        }
        ws.send(JSON.stringify(initData))
        
        isConnected.value = true
        reconnectAttempts.value = 0
        reconnectDelay.value = 1000
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        } catch (error) {
          console.error('解析 WebSocket 消息失敗:', error)
          // 嘗試直接處理可能非JSON的消息（雖然這不應該發生在定義良好的API中）
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket 連接錯誤:', error)
        isConnected.value = false
      }

      ws.onclose = () => {
        console.log('WebSocket 連接已關閉')
        isConnected.value = false
        socket.value = null
        handleWebSocketReconnect()
      }

    } catch (error) {
      console.error('建立 WebSocket 連接失敗:', error)
      handleWebSocketReconnect()
    }
  }

  const disconnectWebSocket = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
      isConnected.value = false
    }
  }

  const handleWebSocketReconnect = () => {
    if (reconnectAttempts.value < maxReconnectAttempts) {
      reconnectAttempts.value++
      const delay = reconnectDelay.value * Math.pow(1.5, reconnectAttempts.value - 1)
      console.log(`將在 ${delay}ms 後嘗試重新連接 WebSocket (${reconnectAttempts.value}/${maxReconnectAttempts})`)
      setTimeout(connectWebSocket, delay)
    } else {
      console.log('WebSocket 重連次數已達上限，進入離線模式')
      isConnected.value = false
    }
  }

  const handleWebSocketMessage = (data: any) => {
    console.log('收到 WebSocket 消息:', data.type) // 減少日誌量，僅印出類型
    
    switch (data.type) {
      case 'connection_established':
        console.log('收到 WebSocket 連接確認')
        isConnected.value = true
        // 可以在這裡處理 client_id 等初始化數據
        break
        
      case 'state_update':
        if (data.data) {
           // 兼容後端格式
           const state = typeof data.data === 'string' ? JSON.parse(data.data) : data.data
           updateFromBackendState(state)
           notifyRealtimeStore(state)
        }
        break
    
      case 'user_message_received':
      case 'decision_received':
        // 確認消息已達後端
        console.log('收到消息確認 (Ack)')
        break
        
      case 'agent_message':
        // 處理 AI 代理訊息
        if (data.data) {
          const { agentName, content, messageType } = data.data
          console.log(`收到 AI 訊息 (${agentName}):`, content.substring(0, 100) + '...')
          
          // 新增 AI 訊息到訊息列表 (使用 Message 類型)
          const aiMessage: Message = {
            id: data.id || `msg-${Date.now()}`,
            content: content,
            sender: agentName || 'assistant',
            timestamp: new Date().toISOString(),
            type: MessageType.AGENT,
            metadata: {
              agentType: messageType
            }
          }
          messages.value.push(aiMessage)
          isProcessing.value = false
        }
        break
        
      case 'decision_required':
        // 處理需要用戶決策的選項
        if (data.data) {
          const { decisionId, options } = data.data
          console.log('收到決策請求:', decisionId, options)
          
          needsDecision.value = true
          decisionOptions.value = options.map((opt: any) => ({
            id: opt.id,
            label: opt.label,
            value: opt.value || opt.id
          }))
          // 儲存決策 ID 以便回應時使用
          currentDecisionId.value = decisionId
          isProcessing.value = false
        }
        break
        
      case 'agent_status':
        // 處理代理狀態更新 (進度條等)
        if (data.data) {
          console.log('代理狀態更新:', data.data.agentId, data.data.status, data.data.progress)
          // 可以通知 Realtime Store 或更新 UI 進度條
        }
        break
        
      case 'analysis_started':
        console.log('分析已開始')
        isProcessing.value = true
        break
        
      case 'analysis_completed':
        console.log('分析已完成')
        isProcessing.value = false
        break
        
      case 'analysis_error':
        console.error('分析錯誤:', data.data?.message)
        isProcessing.value = false
        // 可以添加錯誤訊息到聊天
        if (data.data?.message) {
          const errorMessage: Message = {
            id: `error-${Date.now()}`,
            content: `錯誤: ${data.data.message}`,
            sender: 'system',
            timestamp: new Date().toISOString(),
            type: MessageType.SYSTEM
          }
          messages.value.push(errorMessage)
        }
        break
        
      default:
        console.log('收到未知類型的消息:', data.type)
    }
  }

  // 通知 Realtime Store 狀態更新
  const notifyRealtimeStore = (backendState: BackendState): void => {
    try {
      console.log('📡 Chat Store 通知 Realtime Store 狀態更新:', {
        sender: backendState.sender,
        needs_decision: backendState.needs_decision,
        message_count: backendState.messages?.length || 0
      })
      
      // 發送通用狀態更新事件
      document.dispatchEvent(new CustomEvent('realtime-state-update', {
        detail: {
          type: 'chat_state',
          data: backendState,
          timestamp: Date.now(),
          source: 'chat_store'
        }
      }))
      
      // 如果有代理狀態更新，發送代理狀態事件
      if (backendState.sender) {
        document.dispatchEvent(new CustomEvent('realtime-agent-status', {
          detail: {
            agentId: backendState.sender,
            name: backendState.sender,
            status: backendState.needs_decision ? 'completed' : 'processing',
            progress: 100,
            lastActivity: new Date().toISOString(),
            currentTask: backendState.needs_decision ? '等待用戶決策' : '處理中'
          }
        }))
      }
      
    } catch (error) {
      console.error('通知 Realtime Store 失敗:', error)
    }
  }

  // 智能狀態同步函數 - 專門配合後端統一中斷檢測邏輯
  const syncWithUnifiedInterruptDetection = (backendState: BackendState): boolean => {
    const backendNeedsDecision = Boolean(backendState.needs_decision)
    const isHumanChoiceEvent = backendState.sender === 'human_choice'
    const isDecisionStateChange = backendNeedsDecision !== needsDecision.value
    
    console.log('🤖 智能狀態同步 - 統一中斷檢測協調:', {
      backendSender: backendState.sender,
      backendNeedsDecision,
      frontendNeedsDecision: needsDecision.value,
      frontendIsProcessing: isProcessingDecision.value,
      isHumanChoiceEvent,
      isDecisionStateChange,
      stateVersion: stateVersion.value
    })
    
    // 場景1: 後端統一檢測觸發新的決策需求
    if (backendNeedsDecision && !needsDecision.value) {
      console.log('📢 後端統一檢測觸發新決策需求')
      needsDecision.value = true
      isProcessing.value = false
      return true
    }
    
    // 場景2: 後端原子性操作完成決策處理
    if (!backendNeedsDecision && needsDecision.value && isProcessingDecision.value) {
      console.log('✅ 後端原子性操作完成，解除決策狀態')
      needsDecision.value = false
      isProcessingDecision.value = false
      return true
    }
    
    // 場景3: 人工選擇事件的特殊處理
    if (isHumanChoiceEvent) {
      console.log('👤 處理人工選擇事件')
      if (backendNeedsDecision && !isProcessingDecision.value) {
        needsDecision.value = true
        isProcessing.value = false
        return true
      }
    }
    
    // 場景4: 狀態已經同步，無需處理
    if (backendNeedsDecision === needsDecision.value && !isDecisionStateChange) {
      console.log('🔄 狀態已同步，無需更新')
      return false
    }
    
    // 默認同步邏輯
    if (isDecisionStateChange) {
      console.log('🔧 執行默認狀態同步')
      needsDecision.value = backendNeedsDecision
      return true
    }
    
    return false
  }

  // 狀態更新 - 增強版本，配合後端統一中斷檢測邏輯
  const updateFromBackendState = (backendState: BackendState) => {
    const currentTime = Date.now()
    const newStateVersion = stateVersion.value + 1
    
    // 增強的狀態競爭防護，配合後端原子性操作
    const timeSinceLastUpdate = currentTime - lastStateUpdateTime.value
    if (timeSinceLastUpdate < 50 && lastStateUpdateTime.value > 0) {
      // 縮短防護時間窗口，提高與後端原子性操作的同步響應性
      console.log('狀態更新過於頻繁，跳過此次更新 (原子性操作防護)', {
        timeSinceLastUpdate,
        currentVersion: stateVersion.value,
        backendSender: backendState.sender,
        backendNeedsDecision: backendState.needs_decision
      })
      return
    }
    
    // 檢測是否為來自後端統一中斷檢測的重要狀態更新
    const isUnifiedInterruptUpdate = backendState.sender === 'human_choice' ||
                                   (backendState.needs_decision !== undefined &&
                                    backendState.needs_decision !== needsDecision.value)
    
    if (isUnifiedInterruptUpdate) {
      console.log('🔄 檢測到後端統一中斷檢測狀態更新:', {
        sender: backendState.sender,
        needs_decision: backendState.needs_decision,
        current_frontend_state: {
          needsDecision: needsDecision.value,
          isProcessingDecision: isProcessingDecision.value
        }
      })
    }
    
    console.log('🔄 處理後端狀態更新 (配合統一中斷邏輯):', backendState)
    console.log('當前前端狀態:', {
      版本號: stateVersion.value,
      消息數量: messages.value.length,
      處理中: isProcessing.value,
      需要決策: needsDecision.value,
      決策處理中: isProcessingDecision.value,
      當前代理: currentTypingAgent.value,
      上次更新時間: new Date(lastStateUpdateTime.value).toISOString(),
      統一中斷更新: isUnifiedInterruptUpdate
    })
    
    // 更新狀態版本和時間戳
    stateVersion.value = newStateVersion
    lastStateUpdateTime.value = currentTime
    
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

    // 使用智能狀態同步函數處理決策狀態更新
    const oldNeedsDecision = needsDecision.value
    const stateChanged = syncWithUnifiedInterruptDetection(backendState)
    
    // 決策狀態變更的詳細日誌
    if (stateChanged) {
      console.log(`=== 智能決策狀態同步完成 ===`)
      console.log(`狀態變更: ${oldNeedsDecision} → ${needsDecision.value}`)
      console.log(`觸發代理: ${backendState.sender}`)
      console.log(`決策鎖定狀態: ${isProcessingDecision.value}`)
      console.log(`狀態版本: ${stateVersion.value}`)
      console.log(`同步時間: ${new Date(lastStateUpdateTime.value).toISOString()}`)
      console.log(`原子性操作協調: ✅`)
      console.log(`==================================`)
    } else {
      console.log('智能狀態同步: 狀態已同步，無需更新')
    }
    
    // 更新處理狀態 - 修復狀態處理邏輯
    if (backendState.sender) {
      console.log(`後端發送者: ${backendState.sender}`)
      
      // 更新當前代理
      const oldAgent = currentTypingAgent.value
      currentTypingAgent.value = backendState.sender
      if (oldAgent !== currentTypingAgent.value) {
        console.log(`當前代理變更: ${oldAgent || 'None'} -> ${currentTypingAgent.value}`)
      }
      
      // 優先檢查 needs_decision 狀態 - 這是最重要的條件
      if (needsDecision.value) {
        console.log('需要用戶決策，停止處理並等待決策')
        console.log(`決策觸發代理: ${backendState.sender}`)
        isProcessing.value = false
      } else if (backendState.sender === 'human_choice' || backendState.sender === 'human_review') {
        console.log('檢測到人工決策發送者，停止處理')
        isProcessing.value = false
      } else {
        // 檢查是否為需要停止處理的代理
        console.log('代理狀態更新，檢查是否完成處理')
        
        // 真正的完成代理（工作流程結束）
        const finalCompletionAgents = ['report_agent', 'quality_review_agent']
        // 可能觸發中斷的代理（但不一定結束工作流程）
        const interruptionAgents = ['hypothesis_agent']
        
        if (finalCompletionAgents.includes(backendState.sender) && !needsDecision.value) {
          // 這些代理完成意味著整個工作流程結束
          isProcessing.value = false
          console.log(`檢測到最終完成狀態，停止處理 (代理: ${backendState.sender})`)
        } else if (interruptionAgents.includes(backendState.sender)) {
          // 對於 hypothesis_agent，只有在需要決策時才停止處理
          console.log(`檢測到中斷代理 ${backendState.sender}`)
          if (needsDecision.value) {
            // 需要決策的情況已經在上面處理了
            console.log('中斷代理需要決策，處理狀態已在上面設置')
          } else {
            console.log('中斷代理完成但不需要決策，繼續處理後續步驟')
            // 保持處理狀態，讓工作流程繼續
          }
        } else {
          console.log(`代理 ${backendState.sender} 仍在處理中，保持處理狀態`)
        }
      }
    }
    
    // 在updateFromBackendState結尾檢查所有狀態
    console.log('=== updateFromBackendState 完成狀態檢查 ===')
    console.log('後端發送者:', backendState.sender)
    console.log('後端needs_decision:', backendState.needs_decision)
    console.log('前端狀態:', {
      版本號: stateVersion.value,
      更新時間: lastStateUpdateTime.value,
      isConnected: isConnected.value,
      isProcessing: isProcessing.value,
      needsDecision: needsDecision.value,
      canSendMessage: canSendMessage.value,
      currentTypingAgent: currentTypingAgent.value,
      isProcessingDecision: isProcessingDecision.value
    })
    console.log('==========================================')
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
      const apiUrl = `${getApiBaseUrl()}/api/send_message`
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
    // 增強的決策處理前置檢查，配合後端原子性操作
    if (!needsDecision.value || isProcessingDecision.value) {
      console.log('決策請求被拒絕 - 狀態檢查失敗', {
        needsDecision: needsDecision.value,
        isProcessingDecision: isProcessingDecision.value,
        stateVersion: stateVersion.value,
        canSendMessage: canSendMessage.value,
        timestamp: new Date().toISOString()
      })
      return
    }

    // 記錄決策開始時的狀態版本，用於衝突檢測
    const decisionStartVersion = stateVersion.value
    const decisionStartTime = Date.now()

    // 優化的決策處理鎖定邏輯
    isProcessingDecision.value = true
    needsDecision.value = false
    isProcessing.value = true

    console.log('開始處理決策', {
      decision,
      startVersion: decisionStartVersion,
      startTime: decisionStartTime,
      currentState: {
        isProcessing: isProcessing.value,
        needsDecision: needsDecision.value,
        isProcessingDecision: isProcessingDecision.value
      }
    })

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
      const response = await fetch(`${getApiBaseUrl()}/api/send_message`, {
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
      console.log('決策發送成功，等待後端原子性狀態更新', {
        result,
        decisionCode,
        startVersion: decisionStartVersion,
        currentVersion: stateVersion.value,
        processingTime: Date.now() - decisionStartTime
      })
      
      // 暫時保持決策鎖定，等待後端 SSE 確認狀態更新
      // isProcessingDecision.value 將在 updateFromBackendState 中根據後端狀態解除
      console.log('決策發送完成，等待後端 SSE 狀態確認')
      
    } catch (error) {
      console.error('發送決策失敗，恢復決策狀態', {
        error: error instanceof Error ? error.message : '未知錯誤',
        startVersion: decisionStartVersion,
        currentVersion: stateVersion.value,
        processingTime: Date.now() - decisionStartTime
      })
      
      // 添加錯誤消息並恢復決策狀態
      const errorMessage: Message = {
        id: generateMessageId(),
        content: `錯誤: 發送決策失敗 (${error instanceof Error ? error.message : '未知錯誤'})`,
        sender: 'System',
        timestamp: new Date().toISOString(),
        type: MessageType.SYSTEM
      }
      
      messages.value.push(errorMessage)
      
      // 錯誤時恢復到決策前狀態
      needsDecision.value = true
      isProcessing.value = false
      isProcessingDecision.value = false
      
      // 更新狀態版本，標記此次錯誤
      stateVersion.value++
      lastStateUpdateTime.value = Date.now()
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
      const baseUrl = getApiBaseUrl()
      console.log('正在連接後端 API:', baseUrl)
      const response = await fetch(`${baseUrl}/api/state`, {
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
        
        // 後端可用，建立 WebSocket 連接
        connectWebSocket()
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
    disconnectWebSocket()
    clearMessages()
    isProcessing.value = false
    needsDecision.value = false
    currentTypingAgent.value = undefined
    isProcessingDecision.value = false
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
            console.log('嘗試重新建立 WebSocket 連接...')
            connectWebSocket()
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
      console.log('網路已恢復，重新建立 WebSocket 連接')
      if (!isConnected.value) {
        connectWebSocket()
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
      console.log('收到網路重連事件，檢查 WebSocket 連接狀態')
      if (!isConnected.value) {
        connectWebSocket()
      }
    }

    // 移除對來自 realtime store 的聊天狀態更新監聽，防止循環更新
    // 現在統一由 chat store 的 SSE 監聽器直接處理 state_update 事件
    // const handleChatStateUpdate = (event: CustomEvent) => {
    //   console.log('收到聊天狀態更新事件:', event.detail)
    //   try {
    //     updateFromBackendState(event.detail)
    //   } catch (error) {
    //     console.error('處理聊天狀態更新失敗:', error)
    //   }
    // }

    document.addEventListener('network-reconnected', handleNetworkReconnect)
    // 移除自定義事件監聽器，防止重複處理
    // document.addEventListener('chat-state-update', handleChatStateUpdate as EventListener)

    // 儲存事件監聽器引用以便清理
    ;(window as any).chatEventListeners = {
      handleOnline,
      handleOffline,
      handleNetworkReconnect,
      // 移除 handleChatStateUpdate 引用
      // handleChatStateUpdate
    }
  }

  const stopConnectionMonitoring = (): void => {
    const listeners = (window as any).chatEventListeners
    if (listeners) {
      window.removeEventListener('online', listeners.handleOnline)
      window.removeEventListener('offline', listeners.handleOffline)
      document.removeEventListener('network-reconnected', listeners.handleNetworkReconnect)
      // 移除對已刪除的自定義事件監聽器的清理
      // document.removeEventListener('chat-state-update', listeners.handleChatStateUpdate)
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
    isProcessingDecision: readonly(isProcessingDecision),
    
    // 計算屬性
    chatState,
    canSendMessage,
    
    // 基礎方法
    sendMessage,
    sendDecision,
    clearMessages,
    initializeChat,
    destroyChat,
    connectWebSocket,
    disconnectWebSocket,
    
    // 增強方法
    updateFromBackendState,
    syncWithUnifiedInterruptDetection,
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