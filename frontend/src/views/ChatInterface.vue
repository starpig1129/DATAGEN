<template>
  <div class="chat-interface h-full flex flex-col">
    <!-- 頁面標題 -->
    <div class="page-header flex-shrink-0 mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">聊天界面</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-1">與多代理系統進行互動對話</p>
    </div>

    <!-- 聊天容器 -->
    <div class="chat-container flex-1 flex flex-col rounded-lg shadow-sm border overflow-hidden">
      
      <!-- 連接狀態指示器 -->
      <div v-if="!chatStore.isConnected" class="connection-status border-b px-4 py-2 text-sm flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span v-if="chatStore.reconnectAttempts < 5">
            正在嘗試連接後端服務... ({{ chatStore.reconnectAttempts }}/5)
          </span>
          <span v-else>
            後端服務不可用 - 離線模式
          </span>
        </div>
        <button
          @click="reconnectToBackend"
          class="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition-colors duration-200"
        >
          重新連接
        </button>
      </div>

      <!-- 消息顯示區域 -->
      <div 
        ref="messagesContainer"
        class="messages-container flex-1 overflow-y-auto p-4 space-y-4"
        @scroll="handleScroll"
      >
        <!-- 歡迎消息 -->
        <div v-if="chatStore.messages.length === 0" class="welcome-message text-center py-12">
          <div class="text-6xl mb-4">🤖</div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">歡迎使用多代理數據分析系統</h3>
          <p class="text-gray-600 dark:text-gray-400 mb-6">8個專業代理準備為您提供深度數據分析服務</p>
          <div class="flex flex-wrap justify-center gap-2">
            <span v-for="agent in agentTypes" :key="agent" class="agent-badge px-3 py-1 text-sm rounded-full">
              {{ agent }}
            </span>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-for="message in chatStore.messages" :key="message.id" class="message-item">
          <ChatMessage 
            :message="message"
            :is-latest="message.id === chatStore.lastMessageId"
          />
        </div>

        <!-- 加載指示器 -->
        <div v-if="chatStore.isProcessing && chatStore.currentTypingAgent" class="typing-indicator">
          <ChatMessage 
            :message="typingMessage"
            :is-typing="true"
          />
        </div>
      </div>

      <!-- 決策按鈕區域 -->
      <div v-if="chatStore.needsDecision" class="decision-buttons-container border-t p-4">
        <div class="text-sm text-yellow-700 dark:text-yellow-300 mb-3 flex items-center gap-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          系統需要您做出決策
        </div>
        <div class="flex gap-3">
          <button 
            @click="handleDecision(DecisionType.REGENERATE_HYPOTHESIS)"
            :disabled="chatStore.isProcessing"
            class="decision-button regenerate flex-1 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white py-3 px-4 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            重新生成假設
          </button>
          <button 
            @click="handleDecision(DecisionType.CONTINUE_RESEARCH)"
            :disabled="chatStore.isProcessing"
            class="decision-button continue flex-1 bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white py-3 px-4 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
            繼續研究
          </button>
        </div>
      </div>

      <!-- 消息輸入區域 -->
      <div class="input-container border-t p-4">
        <div class="flex gap-3 items-end">
          <div class="flex-1">
            <textarea
              ref="messageInput"
              v-model="inputMessage"
              @keydown="handleKeyDown"
              @input="handleInput"
              :disabled="!canSendMessage"
              :placeholder="inputPlaceholder"
              class="message-input w-full resize-none rounded-lg border px-3 py-2 placeholder-gray-500 transition-colors duration-200"
              rows="1"
              :maxlength="maxMessageLength"
            ></textarea>
            <div v-if="inputMessage.length > 0" class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
              {{ inputMessage.length }}/{{ maxMessageLength }}
            </div>
          </div>
          <button
            @click="sendMessage"
            :disabled="!canSendMessage || !inputMessage.trim()"
            class="send-button bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white p-3 rounded-lg transition-colors duration-200 flex items-center justify-center min-w-[48px]"
          >
            <svg v-if="!chatStore.isProcessing" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            <div v-else class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </button>
        </div>
        
        <!-- 輸入提示 -->
        <div v-if="!canSendMessage" class="mt-2 text-xs text-yellow-600 dark:text-yellow-400">
          <span v-if="chatStore.needsDecision">請先做出決策後再發送消息</span>
          <span v-else-if="chatStore.isProcessing">系統正在處理中，請稍候...</span>
          <span v-else-if="!chatStore.isConnected">正在連接後端服務...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import type { Message } from '@/types/chat'
import { MessageType, DecisionType } from '@/types/chat'
import ChatMessage from '@/components/chat/ChatMessage.vue'

// Store
const chatStore = useChatStore()

// 響應式數據
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLTextAreaElement>()
const inputMessage = ref('')
const isScrolledToBottom = ref(true)
const maxMessageLength = 2000

// 代理類型列表
const agentTypes = [
  '搜索代理', '假設代理', '過程代理', '代碼代理',
  '可視化代理', '筆記代理', '報告代理', '質量審查代理'
]

// 計算屬性
const canSendMessage = computed(() => chatStore.canSendMessage)

const inputPlaceholder = computed(() => {
  if (chatStore.needsDecision) return '請先做出決策...'
  if (chatStore.isProcessing) return '系統處理中...'
  if (!chatStore.isConnected) return '連接中...'
  return '請輸入您的問題或數據分析需求...'
})

// 模擬正在輸入的消息
const typingMessage = computed((): Message => ({
  id: 'typing',
  content: '正在思考中...',
  sender: chatStore.currentTypingAgent || 'Assistant',
  timestamp: new Date().toISOString(),
  type: MessageType.AGENT
}))

// 方法
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (canSendMessage.value) {
      sendMessage()
    }
  }
}

const handleInput = () => {
  // 自動調整文本框高度
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.style.height = 'auto'
      const scrollHeight = messageInput.value.scrollHeight
      messageInput.value.style.height = Math.min(scrollHeight, 120) + 'px'
    }
  })
}

const sendMessage = async () => {
  if (!canSendMessage.value) return
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  
  // 重置文本框高度
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
  }
  
  try {
    await chatStore.sendMessage(message)
  } catch (error) {
    console.error('發送消息失敗:', error)
  }
}

const handleDecision = async (decision: DecisionType) => {
  try {
    await chatStore.sendDecision(decision)
  } catch (error) {
    console.error('發送決策失敗:', error)
  }
}

const reconnectToBackend = async () => {
  console.log('手動重新連接後端...')
  try {
    await chatStore.initializeChat()
  } catch (error) {
    console.error('重新連接失敗:', error)
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    nextTick(() => {
      messagesContainer.value!.scrollTop = messagesContainer.value!.scrollHeight
      isScrolledToBottom.value = true
    })
  }
}

const handleScroll = () => {
  if (messagesContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
    isScrolledToBottom.value = scrollTop + clientHeight >= scrollHeight - 10
  }
}

// 監聽消息變化，自動滾動到底部
watch(() => chatStore.messages.length, () => {
  if (isScrolledToBottom.value) {
    scrollToBottom()
  }
}, { immediate: true })

// 監聽決策狀態變化
watch(() => chatStore.needsDecision, (newValue, oldValue) => {
  console.log(`決策狀態變化: ${oldValue} -> ${newValue}`)
  if (newValue) {
    console.log('需要決策，應該顯示決策按鈕')
  } else {
    console.log('不需要決策，隱藏決策按鈕')
  }
}, { immediate: true })

// 生命周期
onMounted(async () => {
  console.log('ChatInterface組件已掛載')
  
  // 初始化聊天
  await chatStore.initializeChat()
  
  // 聚焦輸入框
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.focus()
    }
  })
})

onUnmounted(() => {
  console.log('ChatInterface組件即將卸載')
  chatStore.destroyChat()
})
</script>

<style scoped>
.chat-interface {
  height: 100%;
  max-height: 100vh;
}

.chat-container {
  background-color: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.messages-container {
  scroll-behavior: smooth;
  background-color: var(--bg-primary);
}

.agent-badge {
  background-color: var(--bg-tertiary);
  color: var(--el-color-primary);
  border: 1px solid var(--border-color-light);
}

.connection-status {
  background-color: rgba(245, 108, 108, 0.1);
  border-color: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
}

.decision-buttons-container {
  background-color: rgba(230, 162, 60, 0.05);
  border-color: var(--border-color-light);
}

.input-container {
  background-color: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.message-input {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--border-color-light);
}

.message-input:focus {
  outline: none;
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.message-input:disabled {
  background-color: var(--bg-tertiary);
  cursor: not-allowed;
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: rgb(243 244 246);
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgb(209 213 219);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgb(156 163 175);
}

.dark .messages-container::-webkit-scrollbar-track {
  background: rgb(55 65 81);
}

.dark .messages-container::-webkit-scrollbar-thumb {
  background: rgb(75 85 99);
}

.dark .messages-container::-webkit-scrollbar-thumb:hover {
  background: rgb(107 114 128);
}

.message-input {
  min-height: 40px;
  max-height: 120px;
  line-height: 1.5;
}

.decision-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.typing-indicator {
  opacity: 0.8;
}

.connection-status {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.welcome-message {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item {
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>