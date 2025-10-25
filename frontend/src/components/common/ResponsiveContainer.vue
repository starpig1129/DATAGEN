<template>
  <div
    ref="containerRef"
    class="responsive-container"
    :class="containerClasses"
    :style="containerStyle"
    :role="role"
    :aria-label="ariaLabel"
    :aria-labelledby="ariaLabelledby"
    :aria-describedby="ariaDescribedby"
    :tabindex="focusable ? 0 : undefined"
    @focus="handleFocus"
    @blur="handleBlur"
    @keydown="handleKeydown"
  >
    <!-- 焦點環境指示器 -->
    <div v-if="showFocusRing && isFocused" class="focus-ring"></div>
    
    <!-- 跳轉到內容的鏈接（無障礙） -->
    <a
      v-if="showSkipLink"
      href="#main-content"
      class="skip-link"
      @click="skipToContent"
    >
      跳轉到主要內容
    </a>
    
    <!-- 響應式內容區域 -->
    <div class="content-area" :class="contentClasses">
      <!-- 標題區域 -->
      <header v-if="$slots.header || title" class="container-header">
        <slot name="header" :breakpoint="currentBreakpoint" :is-mobile="isMobile">
          <h2 v-if="title" :id="titleId" class="container-title">{{ title }}</h2>
        </slot>
      </header>

      <!-- 主要內容 -->
      <main
        id="main-content"
        class="main-content"
        :class="mainContentClasses"
        role="main"
      >
        <slot
          :breakpoint="currentBreakpoint"
          :is-mobile="isMobile"
          :is-tablet="isTablet"
          :is-desktop="isDesktop"
          :container-width="containerWidth"
          :container-height="containerHeight"
          :aspect-ratio="aspectRatio"
        ></slot>
      </main>

      <!-- 側邊欄 -->
      <aside
        v-if="$slots.sidebar"
        class="sidebar"
        :class="sidebarClasses"
        role="complementary"
        :aria-label="sidebarLabel"
      >
        <slot
          name="sidebar"
          :breakpoint="currentBreakpoint"
          :is-collapsed="isSidebarCollapsed"
          :toggle-sidebar="toggleSidebar"
        ></slot>
      </aside>

      <!-- 頁腳 -->
      <footer v-if="$slots.footer" class="container-footer">
        <slot name="footer" :breakpoint="currentBreakpoint"></slot>
      </footer>
    </div>

    <!-- 載入覆蓋層 -->
    <div v-if="loading" class="loading-overlay" role="status" aria-live="polite">
      <div class="loading-content">
        <div class="loading-spinner" aria-hidden="true"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>
    </div>

    <!-- 錯誤覆蓋層 -->
    <div v-if="error" class="error-overlay" role="alert" aria-live="assertive">
      <div class="error-content">
        <div class="error-icon" aria-hidden="true">⚠️</div>
        <p class="error-message">{{ error }}</p>
        <button v-if="showRetry" @click="$emit('retry')" class="retry-button">
          重試
        </button>
      </div>
    </div>

    <!-- 觸控手勢指示器 -->
    <div
      v-if="showGestureHints && isTouchDevice"
      class="gesture-hints"
      :class="{ 'visible': showHints }"
    >
      <div v-for="hint in gestureHints" :key="hint.type" class="gesture-hint">
        <div class="gesture-icon">{{ hint.icon }}</div>
        <span class="gesture-text">{{ hint.text }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  ref, 
  computed, 
  onMounted, 
  onUnmounted, 
  watch, 
  nextTick 
} from 'vue'

interface GestureHint {
  type: string
  icon: string
  text: string
}

interface Props {
  title?: string
  layout?: 'default' | 'sidebar' | 'centered' | 'full-width' | 'grid'
  breakpoints?: Record<string, number>
  minHeight?: string | number
  maxHeight?: string | number
  minWidth?: string | number
  maxWidth?: string | number
  aspectRatio?: string
  padding?: string | number
  margin?: string | number
  role?: string
  ariaLabel?: string
  ariaLabelledby?: string
  ariaDescribedby?: string
  focusable?: boolean
  showFocusRing?: boolean
  showSkipLink?: boolean
  sidebarLabel?: string
  loading?: boolean
  loadingText?: string
  error?: string | null
  showRetry?: boolean
  responsive?: boolean
  mobileFirst?: boolean
  showGestureHints?: boolean
  gestureHints?: GestureHint[]
  autoFocus?: boolean
  trapFocus?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'default',
  breakpoints: () => ({
    xs: 0,
    sm: 576,
    md: 768,
    lg: 992,
    xl: 1200,
    xxl: 1400
  }),
  role: 'region',
  showFocusRing: true,
  showSkipLink: false,
  sidebarLabel: '側邊欄',
  loadingText: '載入中...',
  showRetry: true,
  responsive: true,
  mobileFirst: true,
  showGestureHints: false,
  gestureHints: () => [
    { type: 'swipe', icon: '👆', text: '滑動導航' },
    { type: 'pinch', icon: '🤏', text: '縮放檢視' },
    { type: 'tap', icon: '👇', text: '點擊選擇' }
  ],
  autoFocus: false,
  trapFocus: false
})

const emit = defineEmits<{
  resize: [width: number, height: number]
  breakpointChange: [breakpoint: string]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
  retry: []
}>()

// 響應式狀態
const containerRef = ref<HTMLElement>()
const containerWidth = ref(0)
const containerHeight = ref(0)
const currentBreakpoint = ref('xs')
const isSidebarCollapsed = ref(false)
const isFocused = ref(false)
const showHints = ref(false)
const resizeObserver = ref<ResizeObserver>()
const titleId = ref(`container-title-${Math.random().toString(36).substr(2, 9)}`)

// 設備檢測
const isTouchDevice = ref(false)

// 計算屬性
const isMobile = computed(() => 
  currentBreakpoint.value === 'xs' || currentBreakpoint.value === 'sm'
)

const isTablet = computed(() => 
  currentBreakpoint.value === 'md'
)

const isDesktop = computed(() => 
  currentBreakpoint.value === 'lg' || 
  currentBreakpoint.value === 'xl' || 
  currentBreakpoint.value === 'xxl'
)

const aspectRatio = computed(() => {
  if (!containerWidth.value || !containerHeight.value) return '16:9'
  const ratio = containerWidth.value / containerHeight.value
  return `${Math.round(ratio * 100) / 100}:1`
})

const containerClasses = computed(() => ({
  [`layout-${props.layout}`]: true,
  [`breakpoint-${currentBreakpoint.value}`]: true,
  'is-mobile': isMobile.value,
  'is-tablet': isTablet.value,
  'is-desktop': isDesktop.value,
  'is-touch-device': isTouchDevice.value,
  'is-loading': props.loading,
  'has-error': !!props.error,
  'has-sidebar': props.layout === 'sidebar',
  'sidebar-collapsed': isSidebarCollapsed.value,
  'is-focused': isFocused.value,
  'mobile-first': props.mobileFirst
}))

const containerStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.minHeight) style.minHeight = typeof props.minHeight === 'number' ? `${props.minHeight}px` : props.minHeight
  if (props.maxHeight) style.maxHeight = typeof props.maxHeight === 'number' ? `${props.maxHeight}px` : props.maxHeight
  if (props.minWidth) style.minWidth = typeof props.minWidth === 'number' ? `${props.minWidth}px` : props.minWidth
  if (props.maxWidth) style.maxWidth = typeof props.maxWidth === 'number' ? `${props.maxWidth}px` : props.maxWidth
  if (props.padding) style.padding = typeof props.padding === 'number' ? `${props.padding}px` : props.padding
  if (props.margin) style.margin = typeof props.margin === 'number' ? `${props.margin}px` : props.margin
  
  if (props.aspectRatio) {
    style.aspectRatio = props.aspectRatio
  }
  
  return style
})

const contentClasses = computed(() => ({
  'content-grid': props.layout === 'grid',
  'content-centered': props.layout === 'centered',
  'content-full-width': props.layout === 'full-width'
}))

const mainContentClasses = computed(() => ({
  'main-full': props.layout === 'full-width',
  'main-centered': props.layout === 'centered',
  'main-with-sidebar': props.layout === 'sidebar'
}))

const sidebarClasses = computed(() => ({
  'sidebar-collapsed': isSidebarCollapsed.value,
  'sidebar-mobile': isMobile.value
}))

// 方法
const updateBreakpoint = (width: number) => {
  const breakpointEntries = Object.entries(props.breakpoints)
    .sort(([, a], [, b]) => b - a) // 從大到小排序
  
  for (const [name, minWidth] of breakpointEntries) {
    if (width >= minWidth) {
      if (currentBreakpoint.value !== name) {
        currentBreakpoint.value = name
        emit('breakpointChange', name)
      }
      break
    }
  }
}

const updateDimensions = () => {
  if (!containerRef.value) return
  
  const rect = containerRef.value.getBoundingClientRect()
  containerWidth.value = rect.width
  containerHeight.value = rect.height
  
  if (props.responsive) {
    updateBreakpoint(rect.width)
  }
  
  emit('resize', rect.width, rect.height)
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleKeydown = (event: KeyboardEvent) => {
  // ESC 鍵關閉側邊欄
  if (event.key === 'Escape' && props.layout === 'sidebar' && !isSidebarCollapsed.value) {
    toggleSidebar()
    event.preventDefault()
  }
  
  // 空格鍵或 Enter 鍵切換側邊欄
  if ((event.key === ' ' || event.key === 'Enter') && event.target === containerRef.value) {
    if (props.layout === 'sidebar') {
      toggleSidebar()
      event.preventDefault()
    }
  }
}

const skipToContent = (event: Event) => {
  event.preventDefault()
  const mainContent = containerRef.value?.querySelector('#main-content') as HTMLElement
  if (mainContent) {
    mainContent.focus()
    mainContent.scrollIntoView({ behavior: 'smooth' })
  }
}

const showGestureHintsTemporarily = () => {
  if (!props.showGestureHints || !isTouchDevice.value) return
  
  showHints.value = true
  setTimeout(() => {
    showHints.value = false
  }, 3000)
}

const setupResizeObserver = () => {
  if (!containerRef.value) return
  
  resizeObserver.value = new ResizeObserver(() => {
    updateDimensions()
  })
  
  resizeObserver.value.observe(containerRef.value)
}

const setupTouchDetection = () => {
  isTouchDevice.value = 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

const setupFocusTrap = () => {
  if (!props.trapFocus || !containerRef.value) return
  
  const focusableElements = containerRef.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  
  if (focusableElements.length === 0) return
  
  const firstElement = focusableElements[0] as HTMLElement
  const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement
  
  const handleTabKey = (event: KeyboardEvent) => {
    if (event.key !== 'Tab') return
    
    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        lastElement.focus()
        event.preventDefault()
      }
    } else {
      if (document.activeElement === lastElement) {
        firstElement.focus()
        event.preventDefault()
      }
    }
  }
  
  containerRef.value.addEventListener('keydown', handleTabKey)
  
  return () => {
    containerRef.value?.removeEventListener('keydown', handleTabKey)
  }
}

// 監聽器
watch(() => props.layout, (newLayout) => {
  if (newLayout === 'sidebar' && isMobile.value) {
    isSidebarCollapsed.value = true
  }
})

watch(isMobile, (newIsMobile) => {
  if (newIsMobile && props.layout === 'sidebar') {
    isSidebarCollapsed.value = true
  }
})

// 生命週期
onMounted(() => {
  setupTouchDetection()
  setupResizeObserver()
  updateDimensions()
  
  if (props.autoFocus) {
    nextTick(() => {
      containerRef.value?.focus()
    })
  }
  
  if (props.trapFocus) {
    const cleanup = setupFocusTrap()
    onUnmounted(cleanup || (() => {}))
  }
  
  if (props.showGestureHints && isTouchDevice.value) {
    setTimeout(showGestureHintsTemporarily, 1000)
  }
})

onUnmounted(() => {
  if (resizeObserver.value) {
    resizeObserver.value.disconnect()
  }
})
</script>

<style scoped>
.responsive-container {
  position: relative;
  width: 100%;
  box-sizing: border-box;
  outline: none;
  background: var(--el-bg-color);
  border-radius: var(--el-border-radius-base);
  transition: all 0.3s ease;
}

.responsive-container:focus-visible {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
}

/* 焦點環 */
.focus-ring {
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border: 2px solid var(--el-color-primary);
  border-radius: inherit;
  pointer-events: none;
  z-index: 10;
}

/* 跳轉鏈接 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--el-color-primary);
  color: white;
  padding: 8px;
  border-radius: 4px;
  text-decoration: none;
  z-index: 1000;
  transition: top 0.3s ease;
}

.skip-link:focus {
  top: 6px;
}

/* 內容區域 */
.content-area {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-grid {
  display: grid;
  grid-template-areas: 
    "header header"
    "main sidebar"
    "footer footer";
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 1fr auto;
  gap: 16px;
}

.content-centered {
  align-items: center;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

/* 標題 */
.container-header {
  grid-area: header;
  padding: 16px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.container-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* 主要內容 */
.main-content {
  grid-area: main;
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.main-full {
  width: 100vw;
  margin: 0 calc(-50vw + 50%);
}

.main-centered {
  max-width: 800px;
  margin: 0 auto;
}

.main-with-sidebar {
  margin-right: 16px;
}

/* 側邊欄 */
.sidebar {
  grid-area: sidebar;
  width: 300px;
  background: var(--el-bg-color-page);
  border-radius: var(--el-border-radius-base);
  border: 1px solid var(--el-border-color-light);
  transition: all 0.3s ease;
  overflow: hidden;
}

.sidebar-collapsed {
  width: 0;
  border: none;
  opacity: 0;
}

.sidebar-mobile {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  z-index: 1000;
  transform: translateX(100%);
}

.sidebar-mobile:not(.sidebar-collapsed) {
  transform: translateX(0);
}

/* 頁腳 */
.container-footer {
  grid-area: footer;
  padding: 16px 0;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* 載入覆蓋層 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: inherit;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--el-border-color-light);
  border-top: 3px solid var(--el-color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

/* 錯誤覆蓋層 */
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: inherit;
}

.error-content {
  text-align: center;
  max-width: 400px;
  padding: 24px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-message {
  color: var(--el-text-color-regular);
  margin-bottom: 16px;
  line-height: 1.5;
}

.retry-button {
  background: var(--el-color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background: var(--el-color-primary-dark-2);
}

/* 手勢提示 */
.gesture-hints {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  padding: 12px;
  box-shadow: var(--el-box-shadow-light);
  transform: translateY(100px);
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 50;
}

.gesture-hints.visible {
  transform: translateY(0);
  opacity: 1;
}

.gesture-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.gesture-hint:last-child {
  margin-bottom: 0;
}

.gesture-icon {
  font-size: 16px;
}

/* 佈局特定樣式 */
.layout-sidebar .content-area {
  grid-template-areas: 
    "header header"
    "main sidebar"
    "footer footer";
  grid-template-columns: 1fr 300px;
}

.layout-centered .main-content {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.layout-full-width .main-content {
  width: 100%;
  max-width: none;
}

/* 響應式斷點 */
@media (max-width: 768px) {
  .responsive-container.layout-sidebar .content-area {
    grid-template-areas: 
      "header"
      "main"
      "footer";
    grid-template-columns: 1fr;
  }
  
  .main-with-sidebar {
    margin-right: 0;
  }
  
  .container-title {
    font-size: 20px;
  }
  
  .content-centered {
    padding: 0 12px;
  }
}

@media (max-width: 576px) {
  .container-header,
  .container-footer {
    padding: 12px 0;
  }
  
  .container-title {
    font-size: 18px;
  }
  
  .gesture-hints {
    bottom: 12px;
    right: 12px;
    padding: 8px;
  }
}

/* 深色主題支援 */
.dark .loading-overlay {
  background: rgba(0, 0, 0, 0.9);
}

.dark .error-overlay {
  background: rgba(0, 0, 0, 0.95);
}

/* 高對比度模式 */
@media (prefers-contrast: high) {
  .responsive-container {
    border: 2px solid var(--el-border-color-base);
  }
  
  .focus-ring {
    border-width: 3px;
  }
}

/* 減少動畫模式 */
@media (prefers-reduced-motion: reduce) {
  .responsive-container,
  .sidebar,
  .loading-spinner,
  .gesture-hints {
    transition: none;
    animation: none;
  }
}

/* 列印樣式 */
@media print {
  .gesture-hints,
  .loading-overlay,
  .error-overlay,
  .skip-link {
    display: none !important;
  }
  
  .sidebar {
    position: static;
    width: auto;
    border: 1px solid #000;
  }
}
</style>