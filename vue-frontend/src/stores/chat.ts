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
  
  // 添加決策處理鎖定機制，防止狀態競爭
  const isProcessingDecision = ref(false)
  
  // 添加狀態版本號，防止舊狀態覆蓋新狀態
  const stateVersion = ref(0)
  const lastStateUpdateTime = ref(0)

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
          console.log('🔥 收到關鍵的 state_update SSE事件:', event.type)
          // 確保連接狀態為true
          if (!isConnected.value) {
            console.log('通過state_update事件確認SSE連接已建立')
            isConnected.value = true
            reconnectAttempts.value = 0
            reconnectDelay.value = 1000
          }
          
          const backendState: BackendState = JSON.parse(event.data)
          console.log('=== 🚨 重要 SSE state_update 調試 ===')
          console.log('原始事件數據:', event.data)
          console.log('解析後的數據:', backendState)
          console.log('sender:', backendState.sender)
          console.log('needs_decision:', backendState.needs_decision)
          console.log('解析SSE數據成功，代理狀態:', backendState.sender)
          console.log('======================================')
          
          // 更新本地狀態
          updateFromBackendState(backendState)
          
          // 通知 Realtime Store 狀態更新
          notifyRealtimeStore(backendState)
        } catch (error) {
          console.error('🚨 解析SSE數據失敗:', error)
        }
      })

      eventSource.onerror = (error) => {
        console.error('SSE連接錯誤 - 增強錯誤處理:', {
          error,
          readyState: eventSource.readyState,
          url: sseUrl,
          currentState: {
            isConnected: isConnected.value,
            isProcessingDecision: isProcessingDecision.value,
            needsDecision: needsDecision.value,
            stateVersion: stateVersion.value
          }
        })
        
        // 立即設置斷線狀態
        isConnected.value = false
        
        // 保存當前關鍵狀態，用於重連後恢復
        const criticalState = {
          isProcessingDecision: isProcessingDecision.value,
          needsDecision: needsDecision.value,
          messagesCount: messages.value.length,
          stateVersion: stateVersion.value
        }
        
        // 延遲重連，避免立即重試，但考慮決策狀態
        const reconnectDelay = isProcessingDecision.value ? 500 : 1000
        setTimeout(() => {
          if (eventSource.readyState === EventSource.CLOSED ||
              eventSource.readyState === EventSource.CONNECTING) {
            console.log('啟動SSE重連，保留關鍵狀態:', criticalState)
            handleSSEReconnect()
          }
        }, reconnectDelay)
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
      console.log(`嘗試重新連接SSE (${reconnectAttempts.value}/${maxReconnectAttempts})`, {
        currentDelay: reconnectDelay.value,
        stateVersion: stateVersion.value,
        lastUpdateTime: lastStateUpdateTime.value,
        isProcessingDecision: isProcessingDecision.value
      })
      
      // 在重連前檢查決策狀態，防止重連時丟失決策鎖定
      const preserveDecisionState = isProcessingDecision.value
      const preserveNeedsDecision = needsDecision.value
      
      setTimeout(() => {
        console.log('執行SSE重連，保持決策狀態', {
          preserveDecisionState,
          preserveNeedsDecision,
          attempt: reconnectAttempts.value
        })
        
        // 重連前保存狀態
        const preReconnectState = {
          isProcessingDecision: preserveDecisionState,
          needsDecision: preserveNeedsDecision,
          stateVersion: stateVersion.value
        }
        
        connectSSE()
        
        // 重連後恢復關鍵決策狀態（如果需要）
        if (preserveDecisionState) {
          isProcessingDecision.value = true
          console.log('SSE重連後恢復決策處理狀態')
        }
        if (preserveNeedsDecision && !isProcessingDecision.value) {
          needsDecision.value = true
          console.log('SSE重連後恢復決策需求狀態')
        }
        
        console.log('SSE重連完成，狀態恢復檢查', {
          preReconnectState,
          currentState: {
            isProcessingDecision: isProcessingDecision.value,
            needsDecision: needsDecision.value,
            isConnected: isConnected.value
          }
        })
      }, reconnectDelay.value)
      
      // 指數退避，但針對決策處理中的情況加快重連
      if (preserveDecisionState) {
        // 決策處理中時使用較短的重連間隔
        reconnectDelay.value = Math.min(reconnectDelay.value * 1.5, 10000)
      } else {
        // 正常情況下的指數退避
        reconnectDelay.value = Math.min(reconnectDelay.value * 2, 30000)
      }
    } else {
      console.error('SSE重連次數已達上限，進入離線模式', {
        finalAttempts: reconnectAttempts.value,
        maxAttempts: maxReconnectAttempts,
        isProcessingDecision: isProcessingDecision.value,
        stateVersion: stateVersion.value
      })
      
      // 重連失敗時的狀態處理
      if (isProcessingDecision.value) {
        console.warn('SSE重連失敗時仍在處理決策，保持決策狀態等待手動重連')
        // 保持決策狀態，等待用戶手動刷新或重連
      }
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
    connectSSE,
    disconnectSSE,
    
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