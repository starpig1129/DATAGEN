# 用戶體驗 (UX) 組件庫

這個目錄包含了一系列增強用戶體驗的通用組件，旨在提供一致、流暢且無障礙的用戶界面。

## 組件概覽

### 1. SkeletonLoader - 骨架屏載入組件
用於在內容載入過程中顯示佔位符，提供更好的視覺反饋。

```vue
<template>
  <!-- 卡片骨架屏 -->
  <SkeletonLoader type="card" :lines="3" />
  
  <!-- 圖表骨架屏 -->
  <SkeletonLoader type="chart" />
  
  <!-- 表格骨架屏 -->
  <SkeletonLoader type="table" :rows="5" :columns="4" />
  
  <!-- 列表骨架屏 -->
  <SkeletonLoader type="list" :items="5" />
  
  <!-- 自定義骨架屏 -->
  <SkeletonLoader type="custom">
    <div class="custom-skeleton-content">
      <!-- 自定義內容 -->
    </div>
  </SkeletonLoader>
</template>

<script setup>
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
</script>
```

**屬性：**
- `type`: 骨架屏類型 ('card' | 'chart' | 'table' | 'list' | 'text' | 'custom')
- `lines`: 文字行數 (預設: 3)
- `rows`: 表格行數 (預設: 5)
- `columns`: 表格列數 (預設: 4)
- `items`: 列表項目數 (預設: 5)
- `animated`: 是否顯示動畫 (預設: true)

### 2. ProgressiveLoader - 漸進式載入組件
支援多階段載入過程，提供詳細的進度反饋和狀態管理。

```vue
<template>
  <ProgressiveLoader
    :loading="isLoading"
    :progress="loadingProgress"
    :stages="loadingStages"
    :current-stage-index="currentStage"
    :error="loadingError"
    :success="loadingSuccess"
    auto-progress
    show-animation
    spinner-type="pulse"
    @retry="handleRetry"
    @complete="handleComplete"
  />
</template>

<script setup>
import ProgressiveLoader from '@/components/common/ProgressiveLoader.vue'

const loadingStages = ref([
  { title: '初始化', description: '準備系統', duration: 1000 },
  { title: '載入數據', description: '獲取最新信息', duration: 1500 },
  { title: '完成', description: '準備就緒', duration: 500 }
])

const currentStage = ref(0)
const isLoading = ref(false)
const loadingProgress = ref(0)
const loadingError = ref(null)
const loadingSuccess = ref(false)
</script>
```

**屬性：**
- `loading`: 是否正在載入
- `progress`: 載入進度 (0-100)
- `stages`: 載入階段配置
- `currentStageIndex`: 當前階段索引
- `spinnerType`: 載入器類型 ('circle' | 'dots' | 'wave' | 'pulse')
- `autoProgress`: 自動進度模式
- `error`: 錯誤信息
- `success`: 是否成功完成

### 3. ErrorBoundary - 錯誤邊界組件
用於捕獲和優雅處理組件錯誤，提供友好的錯誤界面。

```vue
<template>
  <ErrorBoundary
    :show-details="true"
    :show-retry="true"
    :show-report="true"
    @retry="handleRetry"
    @report="handleReport"
  >
    <!-- 可能出錯的組件 -->
    <SomeComponent />
  </ErrorBoundary>
</template>

<script setup>
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'

const handleRetry = () => {
  // 重試邏輯
}

const handleReport = (error, info) => {
  // 錯誤報告邏輯
}
</script>
```

**屬性：**
- `error`: 錯誤對象
- `errorInfo`: 錯誤詳細信息
- `showDetails`: 是否顯示錯誤詳情
- `showRetry`: 是否顯示重試按鈕
- `showReport`: 是否顯示報告按鈕
- `customTitle`: 自定義錯誤標題
- `customMessage`: 自定義錯誤信息

### 4. InteractiveElement - 互動元素組件
為任何元素添加豐富的互動效果和動畫。

```vue
<template>
  <!-- 基本互動效果 -->
  <InteractiveElement effect="scale" enable-ripple>
    <el-button type="primary">點擊我</el-button>
  </InteractiveElement>
  
  <!-- 複合效果 -->
  <InteractiveElement
    effect="bounce"
    enable-ripple
    enable-glow
    enable-particles
    intensity="strong"
    :tooltip="'這是一個互動按鈕'"
    @click="handleClick"
  >
    <div class="custom-element">
      自定義元素
    </div>
  </InteractiveElement>
  
  <!-- 狀態指示器 -->
  <InteractiveElement
    show-status-indicator
    :status="elementStatus"
    tooltip="狀態指示"
  >
    <el-card>帶狀態的卡片</el-card>
  </InteractiveElement>
</template>

<script setup>
import InteractiveElement from '@/components/common/InteractiveElement.vue'

const elementStatus = ref('success') // 'success' | 'warning' | 'error' | 'info'
</script>
```

**效果類型：**
- `scale`: 縮放效果
- `bounce`: 彈跳效果
- `glow`: 發光效果
- `particles`: 粒子效果
- `ripple`: 漣漪效果
- `float`: 浮動效果

### 5. ResponsiveContainer - 響應式容器組件
提供響應式佈局和無障礙支援的容器組件。

```vue
<template>
  <ResponsiveContainer
    title="頁面標題"
    layout="sidebar"
    :loading="isLoading"
    :error="errorMessage"
    show-skip-link
    auto-focus
    @retry="handleRetry"
    @resize="handleResize"
  >
    <template #header="{ isMobile }">
      <div class="page-header">
        <h1>{{ isMobile ? '手機標題' : '桌面標題' }}</h1>
      </div>
    </template>
    
    <template #default="{ breakpoint, isMobile, isTablet, isDesktop }">
      <div class="main-content">
        <p>當前斷點: {{ breakpoint }}</p>
        <p v-if="isMobile">手機版內容</p>
        <p v-else-if="isTablet">平板版內容</p>
        <p v-else>桌面版內容</p>
      </div>
    </template>
    
    <template #sidebar="{ isCollapsed, toggleSidebar }">
      <div class="sidebar-content">
        <button @click="toggleSidebar">
          {{ isCollapsed ? '展開' : '收起' }}
        </button>
      </div>
    </template>
  </ResponsiveContainer>
</template>

<script setup>
import ResponsiveContainer from '@/components/common/ResponsiveContainer.vue'
</script>
```

**佈局類型：**
- `default`: 預設佈局
- `sidebar`: 側邊欄佈局
- `centered`: 居中佈局
- `full-width`: 全寬度佈局
- `grid`: 網格佈局

### 6. KeyboardShortcuts - 鍵盤快捷鍵組件
提供全域鍵盤快捷鍵支援、命令面板和快速搜索功能。

```vue
<template>
  <div class="app-container">
    <!-- 你的應用內容 -->
    
    <!-- 鍵盤快捷鍵組件 -->
    <KeyboardShortcuts
      :shortcuts="customShortcuts"
      :commands="customCommands"
      enable-command-palette
      enable-quick-search
      @shortcut="handleShortcut"
      @command="handleCommand"
    />
  </div>
</template>

<script setup>
import KeyboardShortcuts from '@/components/common/KeyboardShortcuts.vue'

const customShortcuts = ref({
  'ctrl+s': {
    keys: 'ctrl+s',
    description: '保存文件',
    action: () => saveFile()
  },
  'ctrl+n': {
    keys: 'ctrl+n',
    description: '新建文件',
    action: () => createFile()
  }
})

const customCommands = ref([
  {
    id: 'save-file',
    title: '保存文件',
    subtitle: '保存當前編輯的文件',
    icon: '💾',
    shortcut: 'ctrl+s',
    action: () => saveFile(),
    keywords: ['save', 'file', '保存', '文件']
  }
])
</script>
```

**功能特性：**
- 全域快捷鍵支援
- 命令面板 (Ctrl+K)
- 快速搜索 (Ctrl+F)
- 幫助面板 (F1 或 ?)
- 自動完成和模糊搜索

## 最佳實踐

### 1. 性能優化
```vue
<!-- 使用 v-memo 避免不必要的重新渲染 -->
<SkeletonLoader v-memo="[isLoading]" :loading="isLoading" />

<!-- 懶載入重型組件 -->
<InteractiveElement v-if="shouldShowInteractive" />
```

### 2. 無障礙支援
```vue
<!-- 提供適當的 ARIA 標籤 -->
<ResponsiveContainer
  role="main"
  aria-label="主要內容區域"
  aria-labelledby="page-title"
/>

<!-- 鍵盤導航支援 -->
<InteractiveElement
  focusable
  @keydown.enter="handleActivate"
  @keydown.space="handleActivate"
/>
```

### 3. 響應式設計
```vue
<!-- 根據斷點調整內容 -->
<ResponsiveContainer>
  <template #default="{ isMobile, isTablet }">
    <SkeletonLoader 
      :type="isMobile ? 'list' : 'card'"
      :items="isMobile ? 3 : 6"
    />
  </template>
</ResponsiveContainer>
```

### 4. 錯誤處理
```vue
<!-- 分層錯誤處理 -->
<ErrorBoundary :show-details="isDev">
  <Suspense>
    <template #default>
      <AsyncComponent />
    </template>
    <template #fallback>
      <SkeletonLoader type="card" />
    </template>
  </Suspense>
</ErrorBoundary>
```

### 5. 狀態管理
```vue
<script setup>
// 使用組合式 API 管理複雜狀態
const { 
  loading, 
  error, 
  data, 
  retry 
} = useAsyncData(fetchData)

// 組合多個載入狀態
const isAnyLoading = computed(() => 
  loading.value || fileStore.loading || chatStore.loading
)
</script>
```

## 主題化和自定義

### CSS 變數
所有組件都支援通過 CSS 變數進行主題化：

```css
:root {
  /* 載入動畫 */
  --skeleton-color: #f2f2f2;
  --skeleton-highlight: #ffffff;
  --skeleton-duration: 1.5s;
  
  /* 互動效果 */
  --ripple-color: rgba(255, 255, 255, 0.6);
  --glow-color: var(--el-color-primary);
  --particle-color: var(--el-color-primary);
  
  /* 響應式斷點 */
  --breakpoint-xs: 0px;
  --breakpoint-sm: 576px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 992px;
  --breakpoint-xl: 1200px;
}
```

### 深色模式
```vue
<template>
  <SkeletonLoader :class="{ 'dark-mode': isDark }" />
</template>

<script setup>
const isDark = computed(() => 
  document.documentElement.classList.contains('dark')
)
</script>
```

## 組件開發指南

### 創建新的 UX 組件

1. **遵循命名約定**
   - 文件名：PascalCase (如 `NewComponent.vue`)
   - 組件名：與文件名一致
   - 屬性名：camelCase

2. **必要的功能**
   - 響應式支援
   - 無障礙標籤
   - 載入狀態
   - 錯誤處理
   - 動畫支援

3. **性能考量**
   - 使用 `v-memo` 優化重渲染
   - 懶載入非關鍵功能
   - 避免深層嵌套的響應式對象

4. **測試要求**
   - 單元測試
   - 無障礙測試
   - 響應式測試
   - 性能測試

### 組件模板
```vue
<template>
  <div 
    class="ux-component"
    :class="componentClasses"
    :style="componentStyle"
    :role="role"
    :aria-label="ariaLabel"
    v-bind="$attrs"
  >
    <slot 
      :loading="loading"
      :error="error"
      :data="data"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  // 定義屬性
}

const props = withDefaults(defineProps<Props>(), {
  // 預設值
})

const emit = defineEmits<{
  // 定義事件
}>()

// 響應式狀態
const loading = ref(false)
const error = ref<string | null>(null)

// 計算屬性
const componentClasses = computed(() => ({}))
const componentStyle = computed(() => ({}))

// 方法
const handleAction = () => {
  // 實現邏輯
}

// 暴露 API
defineExpose({
  handleAction
})
</script>

<style scoped>
.ux-component {
  /* 基礎樣式 */
}

/* 響應式樣式 */
@media (max-width: 768px) {
  .ux-component {
    /* 移動端樣式 */
  }
}

/* 無障礙樣式 */
@media (prefers-reduced-motion: reduce) {
  .ux-component {
    /* 減少動畫 */
  }
}
</style>
```

這些組件旨在提供一致、高品質的用戶體驗，同時保持靈活性和可定制性。使用時請參考各組件的具體文檔和示例。