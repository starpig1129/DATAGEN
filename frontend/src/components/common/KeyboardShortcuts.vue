<template>
  <teleport to="body">
    <!-- 快捷鍵幫助面板 -->
    <transition name="help-panel">
      <div
        v-if="showHelp"
        class="shortcuts-help-panel"
        @click="closeHelp"
        role="dialog"
        aria-labelledby="shortcuts-title"
        aria-modal="true"
      >
        <div class="help-content" @click.stop>
          <header class="help-header">
            <h2 id="shortcuts-title">鍵盤快捷鍵</h2>
            <button
              class="close-button"
              @click="closeHelp"
              aria-label="關閉快捷鍵幫助"
            >
              ✕
            </button>
          </header>
          
          <div class="help-body">
            <div
              v-for="category in shortcutCategories"
              :key="category.name"
              class="shortcut-category"
            >
              <h3 class="category-title">{{ category.title }}</h3>
              <div class="shortcuts-list">
                <div
                  v-for="shortcut in category.shortcuts"
                  :key="shortcut.keys"
                  class="shortcut-item"
                >
                  <div class="shortcut-keys">
                    <kbd
                      v-for="key in parseKeys(shortcut.keys)"
                      :key="key"
                      class="key"
                    >
                      {{ formatKey(key) }}
                    </kbd>
                  </div>
                  <div class="shortcut-description">
                    {{ shortcut.description }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <footer class="help-footer">
            <p class="help-tip">
              按 <kbd class="key">?</kbd> 或 <kbd class="key">F1</kbd> 重新打開此幫助
            </p>
          </footer>
        </div>
      </div>
    </transition>

    <!-- 命令面板 -->
    <transition name="command-panel">
      <div
        v-if="showCommandPalette"
        class="command-palette-overlay"
        @click="closeCommandPalette"
        role="dialog"
        aria-labelledby="command-title"
        aria-modal="true"
      >
        <div class="command-palette" @click.stop>
          <header class="command-header">
            <h2 id="command-title" class="sr-only">命令面板</h2>
            <div class="search-container">
              <input
                ref="commandInput"
                v-model="commandQuery"
                type="text"
                placeholder="輸入命令或搜索..."
                class="command-input"
                @keydown="handleCommandKeydown"
                aria-label="命令搜索"
              />
              <div class="search-icon">🔍</div>
            </div>
          </header>
          
          <div class="command-body">
            <div v-if="filteredCommands.length === 0" class="no-commands">
              <p>找不到匹配的命令</p>
            </div>
            <div v-else class="commands-list" role="listbox">
              <div
                v-for="(command, index) in filteredCommands"
                :key="command.id"
                class="command-item"
                :class="{ 'selected': selectedCommandIndex === index }"
                role="option"
                :aria-selected="selectedCommandIndex === index"
                @click="executeCommand(command)"
                @mouseenter="selectedCommandIndex = index"
              >
                <div class="command-icon" v-if="command.icon">
                  {{ command.icon }}
                </div>
                <div class="command-info">
                  <div class="command-title">{{ command.title }}</div>
                  <div class="command-subtitle" v-if="command.subtitle">
                    {{ command.subtitle }}
                  </div>
                </div>
                <div class="command-shortcut" v-if="command.shortcut">
                  <kbd
                    v-for="key in parseKeys(command.shortcut)"
                    :key="key"
                    class="key small"
                  >
                    {{ formatKey(key) }}
                  </kbd>
                </div>
              </div>
            </div>
          </div>
          
          <footer class="command-footer">
            <div class="command-tips">
              <span class="tip">
                <kbd class="key small">↑↓</kbd> 導航
              </span>
              <span class="tip">
                <kbd class="key small">Enter</kbd> 執行
              </span>
              <span class="tip">
                <kbd class="key small">Esc</kbd> 關閉
              </span>
            </div>
          </footer>
        </div>
      </div>
    </transition>

    <!-- 快速搜索 -->
    <transition name="search-panel">
      <div
        v-if="showQuickSearch"
        class="quick-search-overlay"
        @click="closeQuickSearch"
      >
        <div class="quick-search" @click.stop>
          <div class="search-input-container">
            <input
              ref="searchInput"
              v-model="searchQuery"
              type="text"
              placeholder="快速搜索..."
              class="search-input"
              @keydown="handleSearchKeydown"
              @input="handleSearchInput"
            />
            <div class="search-spinner" v-if="searching">⟳</div>
          </div>
          
          <div class="search-results" v-if="searchResults.length > 0">
            <div
              v-for="(result, index) in searchResults"
              :key="result.id"
              class="search-result"
              :class="{ 'selected': selectedSearchIndex === index }"
              @click="selectSearchResult(result)"
              @mouseenter="selectedSearchIndex = index"
            >
              <div class="result-type">{{ result.type }}</div>
              <div class="result-title">{{ result.title }}</div>
              <div class="result-path" v-if="result.path">{{ result.path }}</div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 狀態提示 -->
    <div v-if="statusMessage" class="status-toast" :class="statusType">
      {{ statusMessage }}
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

interface Shortcut {
  keys: string
  description: string
  action?: () => void
  disabled?: boolean
}

interface ShortcutCategory {
  name: string
  title: string
  shortcuts: Shortcut[]
}

interface Command {
  id: string
  title: string
  subtitle?: string
  icon?: string
  shortcut?: string
  action: () => void | Promise<void>
  category?: string
  keywords?: string[]
}

interface SearchResult {
  id: string
  title: string
  type: string
  path?: string
  action: () => void
}

interface Props {
  shortcuts?: Record<string, Shortcut>
  commands?: Command[]
  enableCommandPalette?: boolean
  enableQuickSearch?: boolean
  enableGlobalShortcuts?: boolean
  customCategories?: ShortcutCategory[]
}

const props = withDefaults(defineProps<Props>(), {
  shortcuts: () => ({}),
  commands: () => [],
  enableCommandPalette: true,
  enableQuickSearch: true,
  enableGlobalShortcuts: true,
  customCategories: () => []
})

const emit = defineEmits<{
  shortcut: [keys: string, event: KeyboardEvent]
  command: [command: Command]
  search: [query: string, results: SearchResult[]]
}>()

const router = useRouter()

// 狀態
const showHelp = ref(false)
const showCommandPalette = ref(false)
const showQuickSearch = ref(false)
const commandQuery = ref('')
const searchQuery = ref('')
const selectedCommandIndex = ref(0)
const selectedSearchIndex = ref(0)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | 'info'>('info')
const searching = ref(false)
const searchResults = ref<SearchResult[]>([])
const commandInput = ref<HTMLInputElement>()
const searchInput = ref<HTMLInputElement>()

// 預設快捷鍵
const defaultShortcuts: Record<string, Shortcut> = {
  'ctrl+k': {
    keys: 'ctrl+k',
    description: '打開命令面板',
    action: () => openCommandPalette()
  },
  'ctrl+shift+p': {
    keys: 'ctrl+shift+p',
    description: '打開命令面板',
    action: () => openCommandPalette()
  },
  'ctrl+f': {
    keys: 'ctrl+f',
    description: '快速搜索',
    action: () => openQuickSearch()
  },
  'f1': {
    keys: 'f1',
    description: '顯示快捷鍵幫助',
    action: () => toggleHelp()
  },
  '?': {
    keys: '?',
    description: '顯示快捷鍵幫助',
    action: () => toggleHelp()
  },
  'esc': {
    keys: 'esc',
    description: '關閉面板',
    action: () => closeAllPanels()
  },
  'ctrl+r': {
    keys: 'ctrl+r',
    description: '刷新頁面',
    action: () => window.location.reload()
  },
  'ctrl+shift+d': {
    keys: 'ctrl+shift+d',
    description: '切換深色模式',
    action: () => toggleDarkMode()
  },
  'ctrl+1': {
    keys: 'ctrl+1',
    description: '跳轉到儀表板',
    action: () => router.push('/')
  },
  'ctrl+2': {
    keys: 'ctrl+2',
    description: '跳轉到聊天界面',
    action: () => router.push('/chat')
  },
  'ctrl+3': {
    keys: 'ctrl+3',
    description: '跳轉到數據視覺化',
    action: () => router.push('/visualization')
  },
  'ctrl+4': {
    keys: 'ctrl+4',
    description: '跳轉到文件管理',
    action: () => router.push('/files')
  },
  'ctrl+5': {
    keys: 'ctrl+5',
    description: '跳轉到代理監控',
    action: () => router.push('/agents')
  },
  'ctrl+,': {
    keys: 'ctrl+,',
    description: '打開設定',
    action: () => router.push('/settings')
  }
}

// 預設命令
const defaultCommands: Command[] = [
  {
    id: 'goto-dashboard',
    title: '跳轉到儀表板',
    subtitle: '系統總覽和統計',
    icon: '📊',
    shortcut: 'ctrl+1',
    action: () => router.push('/'),
    category: '導航',
    keywords: ['dashboard', 'home', '儀表板', '首頁']
  },
  {
    id: 'goto-chat',
    title: '跳轉到聊天界面',
    subtitle: '與 AI 代理對話',
    icon: '💬',
    shortcut: 'ctrl+2',
    action: () => router.push('/chat'),
    category: '導航',
    keywords: ['chat', 'conversation', '聊天', '對話']
  },
  {
    id: 'goto-visualization',
    title: '跳轉到數據視覺化',
    subtitle: '圖表和分析',
    icon: '📈',
    shortcut: 'ctrl+3',
    action: () => router.push('/visualization'),
    category: '導航',
    keywords: ['visualization', 'charts', '視覺化', '圖表']
  },
  {
    id: 'goto-files',
    title: '跳轉到文件管理',
    subtitle: '檔案管理和上傳',
    icon: '📁',
    shortcut: 'ctrl+4',
    action: () => router.push('/files'),
    category: '導航',
    keywords: ['files', 'upload', '文件', '檔案']
  },
  {
    id: 'goto-agents',
    title: '跳轉到代理監控',
    subtitle: '代理狀態和性能',
    icon: '🤖',
    shortcut: 'ctrl+5',
    action: () => router.push('/agents'),
    category: '導航',
    keywords: ['agents', 'monitor', '代理', '監控']
  },
  {
    id: 'goto-settings',
    title: '打開設定',
    subtitle: '系統配置和偏好',
    icon: '⚙️',
    shortcut: 'ctrl+,',
    action: () => router.push('/settings'),
    category: '系統',
    keywords: ['settings', 'config', '設定', '配置']
  },
  {
    id: 'toggle-theme',
    title: '切換深色模式',
    subtitle: '在淺色和深色主題間切換',
    icon: '🌙',
    shortcut: 'ctrl+shift+d',
    action: () => toggleDarkMode(),
    category: '系統',
    keywords: ['theme', 'dark', 'light', '主題', '深色', '淺色']
  },
  {
    id: 'refresh-page',
    title: '刷新頁面',
    subtitle: '重新載入當前頁面',
    icon: '🔄',
    shortcut: 'ctrl+r',
    action: () => window.location.reload(),
    category: '系統',
    keywords: ['refresh', 'reload', '刷新', '重新載入']
  }
]

// 計算屬性
const allShortcuts = computed(() => ({
  ...defaultShortcuts,
  ...props.shortcuts
}))

const allCommands = computed(() => [
  ...defaultCommands,
  ...props.commands
])

const shortcutCategories = computed((): ShortcutCategory[] => {
  if (props.customCategories.length > 0) {
    return props.customCategories
  }

  const categories: ShortcutCategory[] = [
    {
      name: 'navigation',
      title: '導航',
      shortcuts: [
        allShortcuts.value['ctrl+1'],
        allShortcuts.value['ctrl+2'],
        allShortcuts.value['ctrl+3'],
        allShortcuts.value['ctrl+4'],
        allShortcuts.value['ctrl+5']
      ].filter(Boolean)
    },
    {
      name: 'tools',
      title: '工具',
      shortcuts: [
        allShortcuts.value['ctrl+k'],
        allShortcuts.value['ctrl+f'],
        allShortcuts.value['f1']
      ].filter(Boolean)
    },
    {
      name: 'system',
      title: '系統',
      shortcuts: [
        allShortcuts.value['ctrl+,'],
        allShortcuts.value['ctrl+shift+d'],
        allShortcuts.value['ctrl+r'],
        allShortcuts.value['esc']
      ].filter(Boolean)
    }
  ]

  return categories.filter(category => category.shortcuts.length > 0)
})

const filteredCommands = computed(() => {
  if (!commandQuery.value) return allCommands.value

  const query = commandQuery.value.toLowerCase()
  return allCommands.value.filter(command => {
    const titleMatch = command.title.toLowerCase().includes(query)
    const subtitleMatch = command.subtitle?.toLowerCase().includes(query)
    const keywordsMatch = command.keywords?.some(keyword => 
      keyword.toLowerCase().includes(query)
    )
    
    return titleMatch || subtitleMatch || keywordsMatch
  })
})

// 方法
const parseKeys = (keys: string): string[] => {
  return keys.split('+').map(key => key.trim())
}

const formatKey = (key: string): string => {
  const keyMap: Record<string, string> = {
    'ctrl': 'Ctrl',
    'shift': 'Shift',
    'alt': 'Alt',
    'cmd': 'Cmd',
    'meta': 'Cmd',
    'esc': 'Esc',
    'enter': 'Enter',
    'space': 'Space',
    'tab': 'Tab',
    'up': '↑',
    'down': '↓',
    'left': '←',
    'right': '→',
    'f1': 'F1',
    'f2': 'F2',
    'f3': 'F3',
    'f4': 'F4',
    'f5': 'F5',
    'f6': 'F6',
    'f7': 'F7',
    'f8': 'F8',
    'f9': 'F9',
    'f10': 'F10',
    'f11': 'F11',
    'f12': 'F12'
  }
  
  return keyMap[key.toLowerCase()] || key.toUpperCase()
}

const normalizeKey = (event: KeyboardEvent): string => {
  const parts: string[] = []
  
  if (event.ctrlKey || event.metaKey) parts.push('ctrl')
  if (event.shiftKey) parts.push('shift')
  if (event.altKey) parts.push('alt')
  
  let key = event.key.toLowerCase()
  if (key === ' ') key = 'space'
  if (key === 'escape') key = 'esc'
  
  parts.push(key)
  
  return parts.join('+')
}

const handleKeydown = (event: KeyboardEvent) => {
  if (!props.enableGlobalShortcuts) return
  
  const keys = normalizeKey(event)
  const shortcut = allShortcuts.value[keys]
  
  if (shortcut && !shortcut.disabled) {
    event.preventDefault()
    shortcut.action?.()
    emit('shortcut', keys, event)
    showStatus(`執行快捷鍵: ${shortcut.description}`, 'info')
  }
}

const openCommandPalette = () => {
  if (!props.enableCommandPalette) return
  
  showCommandPalette.value = true
  commandQuery.value = ''
  selectedCommandIndex.value = 0
  
  nextTick(() => {
    commandInput.value?.focus()
  })
}

const closeCommandPalette = () => {
  showCommandPalette.value = false
  commandQuery.value = ''
  selectedCommandIndex.value = 0
}

const openQuickSearch = () => {
  if (!props.enableQuickSearch) return
  
  showQuickSearch.value = true
  searchQuery.value = ''
  selectedSearchIndex.value = 0
  
  nextTick(() => {
    searchInput.value?.focus()
  })
}

const closeQuickSearch = () => {
  showQuickSearch.value = false
  searchQuery.value = ''
  searchResults.value = []
  selectedSearchIndex.value = 0
}

const toggleHelp = () => {
  showHelp.value = !showHelp.value
}

const closeHelp = () => {
  showHelp.value = false
}

const closeAllPanels = () => {
  showHelp.value = false
  showCommandPalette.value = false
  showQuickSearch.value = false
}

const executeCommand = async (command: Command) => {
  try {
    await command.action()
    emit('command', command)
    closeCommandPalette()
    showStatus(`執行命令: ${command.title}`, 'success')
  } catch (error) {
    console.error('執行命令失敗:', error)
    showStatus(`執行命令失敗: ${command.title}`, 'error')
  }
}

const selectSearchResult = (result: SearchResult) => {
  try {
    result.action()
    closeQuickSearch()
    showStatus(`跳轉到: ${result.title}`, 'success')
  } catch (error) {
    console.error('跳轉失敗:', error)
    showStatus(`跳轉失敗: ${result.title}`, 'error')
  }
}

const handleCommandKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'ArrowUp':
      event.preventDefault()
      selectedCommandIndex.value = Math.max(0, selectedCommandIndex.value - 1)
      break
    case 'ArrowDown':
      event.preventDefault()
      selectedCommandIndex.value = Math.min(
        filteredCommands.value.length - 1,
        selectedCommandIndex.value + 1
      )
      break
    case 'Enter':
      event.preventDefault()
      if (filteredCommands.value[selectedCommandIndex.value]) {
        executeCommand(filteredCommands.value[selectedCommandIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      closeCommandPalette()
      break
  }
}

const handleSearchKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'ArrowUp':
      event.preventDefault()
      selectedSearchIndex.value = Math.max(0, selectedSearchIndex.value - 1)
      break
    case 'ArrowDown':
      event.preventDefault()
      selectedSearchIndex.value = Math.min(
        searchResults.value.length - 1,
        selectedSearchIndex.value + 1
      )
      break
    case 'Enter':
      event.preventDefault()
      if (searchResults.value[selectedSearchIndex.value]) {
        selectSearchResult(searchResults.value[selectedSearchIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      closeQuickSearch()
      break
  }
}

const handleSearchInput = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  
  searching.value = true
  
  try {
    // 模擬搜索延遲
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // 這裡應該是實際的搜索邏輯
    const mockResults: SearchResult[] = [
      {
        id: '1',
        title: '儀表板',
        type: '頁面',
        path: '/',
        action: () => router.push('/')
      },
      {
        id: '2',
        title: '聊天界面',
        type: '頁面',
        path: '/chat',
        action: () => router.push('/chat')
      }
    ].filter(result => 
      result.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    
    searchResults.value = mockResults
    selectedSearchIndex.value = 0
    
    emit('search', searchQuery.value, mockResults)
  } finally {
    searching.value = false
  }
}

const toggleDarkMode = () => {
  // 這裡應該調用實際的主題切換邏輯
  const isDark = document.documentElement.classList.contains('dark')
  if (isDark) {
    document.documentElement.classList.remove('dark')
  } else {
    document.documentElement.classList.add('dark')
  }
}

const showStatus = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  statusMessage.value = message
  statusType.value = type
  
  setTimeout(() => {
    statusMessage.value = ''
  }, 2000)
}

// 監聽器
watch(commandQuery, () => {
  selectedCommandIndex.value = 0
})

watch(searchQuery, () => {
  selectedSearchIndex.value = 0
})

// 生命週期
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* 幫助面板 */
.shortcuts-help-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.help-content {
  background: var(--el-bg-color);
  border-radius: 12px;
  box-shadow: var(--el-box-shadow-dark);
  max-width: 800px;
  max-height: 80vh;
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.help-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.close-button {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  color: var(--el-text-color-regular);
  transition: all 0.2s ease;
}

.close-button:hover {
  background: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
}

.help-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.shortcut-category {
  margin-bottom: 32px;
}

.shortcut-category:last-child {
  margin-bottom: 0;
}

.category-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 16px 0;
}

.shortcuts-list {
  display: grid;
  gap: 12px;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

.shortcut-keys {
  display: flex;
  gap: 4px;
}

.key {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-base);
  border-radius: 4px;
  padding: 4px 8px;
  font-family: monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.key.small {
  padding: 2px 6px;
  font-size: 11px;
}

.shortcut-description {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.help-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color-page);
}

.help-tip {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: center;
}

/* 命令面板 */
.command-palette-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 2000;
  padding-top: 10vh;
}

.command-palette {
  background: var(--el-bg-color);
  border-radius: 12px;
  box-shadow: var(--el-box-shadow-dark);
  width: 600px;
  max-width: 90vw;
  max-height: 70vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.command-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.search-container {
  position: relative;
}

.command-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  font-size: 16px;
  background: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
  outline: none;
  transition: border-color 0.2s ease;
}

.command-input:focus {
  border-color: var(--el-color-primary);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--el-text-color-secondary);
}

.command-body {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}

.no-commands {
  padding: 40px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.commands-list {
  padding: 8px;
}

.command-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.command-item:hover,
.command-item.selected {
  background: var(--el-bg-color-page);
}

.command-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.command-info {
  flex: 1;
}

.command-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.command-subtitle {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.command-shortcut {
  display: flex;
  gap: 2px;
}

.command-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color-page);
}

.command-tips {
  display: flex;
  gap: 16px;
  justify-content: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.tip {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 快速搜索 */
.quick-search-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 2000;
  padding-top: 15vh;
}

.quick-search {
  background: var(--el-bg-color);
  border-radius: 12px;
  box-shadow: var(--el-box-shadow-dark);
  width: 500px;
  max-width: 90vw;
  overflow: hidden;
}

.search-input-container {
  position: relative;
  padding: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  font-size: 16px;
  background: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
  outline: none;
}

.search-spinner {
  position: absolute;
  right: 28px;
  top: 50%;
  transform: translateY(-50%);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: translateY(-50%) rotate(0deg); }
  100% { transform: translateY(-50%) rotate(360deg); }
}

.search-results {
  border-top: 1px solid var(--el-border-color-light);
  max-height: 300px;
  overflow-y: auto;
}

.search-result {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.search-result:hover,
.search-result.selected {
  background: var(--el-bg-color-page);
}

.search-result:last-child {
  border-bottom: none;
}

.result-type {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 2px;
}

.result-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.result-path {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-family: monospace;
}

/* 狀態提示 */
.status-toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 3000;
  box-shadow: var(--el-box-shadow-light);
  transition: all 0.3s ease;
}

.status-toast.success {
  background: var(--el-color-success);
  color: white;
}

.status-toast.error {
  background: var(--el-color-danger);
  color: white;
}

.status-toast.info {
  background: var(--el-color-info);
  color: white;
}

/* 過渡動畫 */
.help-panel-enter-active,
.help-panel-leave-active,
.command-panel-enter-active,
.command-panel-leave-active,
.search-panel-enter-active,
.search-panel-leave-active {
  transition: all 0.3s ease;
}

.help-panel-enter-from,
.help-panel-leave-to,
.command-panel-enter-from,
.command-panel-leave-to,
.search-panel-enter-from,
.search-panel-leave-to {
  opacity: 0;
}

.help-panel-enter-from .help-content,
.help-panel-leave-to .help-content,
.command-panel-enter-from .command-palette,
.command-panel-leave-to .command-palette,
.search-panel-enter-from .quick-search,
.search-panel-leave-to .quick-search {
  transform: scale(0.9) translateY(-20px);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .shortcuts-help-panel {
    padding: 10px;
  }
  
  .help-content {
    max-height: 90vh;
  }
  
  .help-header,
  .help-body {
    padding: 16px;
  }
  
  .command-palette,
  .quick-search {
    width: 95vw;
  }
  
  .shortcut-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .command-tips {
    flex-wrap: wrap;
    gap: 8px;
  }
}

/* 無障礙支援 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 減少動畫 */
@media (prefers-reduced-motion: reduce) {
  .help-panel-enter-active,
  .help-panel-leave-active,
  .command-panel-enter-active,
  .command-panel-leave-active,
  .search-panel-enter-active,
  .search-panel-leave-active,
  .search-spinner {
    transition: none;
    animation: none;
  }
}
</style>