<template>
  <div 
    :class="[
      'chat-message flex gap-3 group',
      {
        'user-message': isUserMessage,
        'agent-message': !isUserMessage,
        'latest-message': isLatest,
        'typing': isTyping
      }
    ]"
  >
    <!-- 頭像區域 -->
    <div class="avatar-container flex-shrink-0">
      <div 
        :class="[
          'avatar w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
          avatarClass
        ]"
      >
        <span v-if="!isUserMessage">{{ avatarText }}</span>
        <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- 消息內容區域 -->
    <div class="message-content flex-1 min-w-0">
      <!-- 消息頭部信息 -->
      <div class="message-header flex items-center gap-2 mb-1">
        <span class="sender-name text-sm font-medium text-gray-900 dark:text-white">
          {{ translatedSender }}
        </span>
        <span class="timestamp text-xs text-gray-500 dark:text-gray-400">
          {{ formattedTime }}
        </span>
        <span v-if="message.type === MessageType.SYSTEM" class="system-badge text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded">
          系統
        </span>
      </div>

      <!-- 消息氣泡 -->
      <div 
        :class="[
          'message-bubble rounded-lg px-4 py-3 max-w-4xl',
          bubbleClass
        ]"
      >
        <!-- 正在輸入指示器 -->
        <div v-if="isTyping" class="typing-dots flex items-center gap-1">
          <div class="dot w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0ms"></div>
          <div class="dot w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 150ms"></div>
          <div class="dot w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          <span class="ml-2 text-sm opacity-70">{{ translatedSender }}正在思考...</span>
        </div>

        <!-- 消息內容 -->
        <div v-else class="message-text">
          <!-- Markdown 渲染的內容 -->
          <div 
            v-if="renderedContent"
            v-html="renderedContent"
            class="prose prose-sm max-w-none dark:prose-invert prose-headings:mt-4 prose-headings:mb-2 prose-p:my-2 prose-pre:bg-gray-800 prose-pre:text-gray-100 prose-code:bg-gray-100 dark:prose-code:bg-gray-700 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm"
          ></div>
          
          <!-- 純文本後備 -->
          <div v-else class="whitespace-pre-wrap break-words">
            {{ message.content }}
          </div>
        </div>

        <!-- 消息元數據 -->
        <div v-if="message.metadata && hasMetadata" class="message-metadata mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
          <div class="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span v-if="message.metadata.agentType" class="flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd" />
              </svg>
              {{ message.metadata.agentType }}
            </span>
            <span v-if="message.metadata.confidence" class="flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
              </svg>
              信心度: {{ Math.round(message.metadata.confidence * 100) }}%
            </span>
            <span v-if="message.metadata.processingTime" class="flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
              </svg>
              {{ message.metadata.processingTime }}ms
            </span>
          </div>
          
          <!-- 來源鏈接 -->
          <div v-if="message.metadata.sources && message.metadata.sources.length > 0" class="sources mt-2">
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">參考來源:</div>
            <div class="flex flex-wrap gap-1">
              <a
                v-for="(source, index) in message.metadata.sources"
                :key="index"
                :href="source"
                target="_blank"
                rel="noopener noreferrer"
                class="source-link text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
              >
                來源 {{ index + 1 }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按鈕 (僅在hover時顯示) -->
    <div class="message-actions opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex-shrink-0 flex items-start gap-1 mt-8">
      <button
        @click="copyMessage"
        class="action-button p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
        title="複製消息"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import type { Message } from '@/types/chat'
import { MessageType } from '@/types/chat'

interface Props {
  message: Message
  isLatest?: boolean
  isTyping?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLatest: false,
  isTyping: false
})

// 響應式數據
const copySuccess = ref(false)

// 代理名稱翻譯映射
const agentNameMap: Record<string, string> = {
  'hypothesis_agent': '假設代理',
  'code_agent': '代碼代理',
  'process_agent': '處理代理',
  'visualization_agent': '視覺化代理',
  'report_agent': '報告代理',
  'quality_review_agent': '品質檢查代理',
  'human_choice': '等待決策',
  'human_review': '等待審核',
  'System': '系統',
  'Assistant': '助手',
  'User': '用戶'
}

// 計算屬性
const isUserMessage = computed(() => props.message.type === MessageType.USER)

// 翻譯代理名稱
const translatedSender = computed(() => {
  const sender = props.message.sender
  return agentNameMap[sender] || sender
})

const formattedTime = computed(() => {
  const date = new Date(props.message.timestamp)
  return date.toLocaleTimeString('zh-TW', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false
  })
})

const avatarText = computed(() => {
  if (props.message.type === MessageType.SYSTEM) return 'S'
  if (props.message.sender === 'Assistant') return 'AI'
  
  // 使用翻譯後的代理名稱來生成頭像文字
  const translated = translatedSender.value
  if (translated.includes('代理')) {
    const agentType = translated.replace(/代理/g, '')
    return agentType.charAt(0) || 'A'
  }
  
  return translated.charAt(0) || 'A'
})

const avatarClass = computed(() => {
  if (isUserMessage.value) {
    return 'bg-blue-500 text-white'
  }
  
  if (props.message.type === MessageType.SYSTEM) {
    return 'bg-gray-500 text-white'
  }
  
  // 根據發送者類型設置不同顏色
  const colors = [
    'bg-green-500 text-white',
    'bg-purple-500 text-white', 
    'bg-orange-500 text-white',
    'bg-teal-500 text-white',
    'bg-pink-500 text-white',
    'bg-indigo-500 text-white',
    'bg-red-500 text-white',
    'bg-yellow-500 text-white'
  ]
  
  const senderHash = props.message.sender.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0)
  
  return colors[Math.abs(senderHash) % colors.length]
})

const bubbleClass = computed(() => {
  if (isUserMessage.value) {
    return 'bg-blue-500 text-white ml-auto'
  }
  
  if (props.message.type === MessageType.SYSTEM) {
    return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600'
  }
  
  return 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 shadow-sm'
})

const renderedContent = computed(() => {
  if (props.isTyping) return null
  
  try {
    // 配置 marked 選項
    marked.setOptions({
      breaks: true,
      gfm: true,
    })
    
    // 解析 Markdown
    const rawHtml = marked.parse(props.message.content)
    
    // 使用 DOMPurify 清理 HTML
    const cleanHtml = DOMPurify.sanitize(rawHtml, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'code', 'pre', 
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'a', 'img',
        'table', 'thead', 'tbody', 'tr', 'th', 'td'
      ],
      ALLOWED_ATTR: ['href', 'target', 'rel', 'src', 'alt', 'title', 'class']
    })
    
    return cleanHtml
  } catch (error) {
    console.error('Markdown 渲染失敗:', error)
    return null
  }
})

const hasMetadata = computed(() => {
  const meta = props.message.metadata
  return meta && (
    meta.agentType || 
    meta.confidence !== undefined || 
    meta.processingTime !== undefined ||
    (meta.sources && meta.sources.length > 0)
  )
})

// 方法
const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('複製失敗:', error)
  }
}
</script>

<style scoped>
.chat-message {
  transition: all 0.2s ease;
}

.latest-message {
  animation: highlight 0.5s ease-out;
}

@keyframes highlight {
  0% {
    background-color: rgba(59, 130, 246, 0.1);
  }
  100% {
    background-color: transparent;
  }
}

.typing-dots .dot:nth-child(1) {
  animation-delay: 0ms;
}

.typing-dots .dot:nth-child(2) {
  animation-delay: 150ms;
}

.typing-dots .dot:nth-child(3) {
  animation-delay: 300ms;
}

.message-bubble {
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.action-button {
  transition: all 0.2s ease;
}

.action-button:hover {
  transform: scale(1.05);
}

/* Markdown 內容樣式優化 */
.message-text :deep(pre) {
  background: rgb(30, 41, 59) !important;
  color: rgb(226, 232, 240) !important;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.5;
}

.message-text :deep(code) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.message-text :deep(pre code) {
  background: none !important;
  padding: 0 !important;
  border-radius: 0 !important;
}

.message-text :deep(blockquote) {
  border-left: 4px solid rgb(229, 231, 235);
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
}

.dark .message-text :deep(blockquote) {
  border-left-color: rgb(75, 85, 99);
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}

.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid rgb(229, 231, 235);
  padding: 0.5rem;
  text-align: left;
}

.dark .message-text :deep(th),
.dark .message-text :deep(td) {
  border-color: rgb(75, 85, 99);
}

.message-text :deep(th) {
  background-color: rgb(249, 250, 251);
  font-weight: 600;
}

.dark .message-text :deep(th) {
  background-color: rgb(55, 65, 81);
}
</style>