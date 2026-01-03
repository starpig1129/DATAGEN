<template>
  <div class="file-manager">
    <!-- 頁面標題 -->
    <div class="page-header">
      <h1 class="page-title">文件管理</h1>
      <p class="page-description">管理和組織系統文件，支援多種格式的上傳、下載和預覽</p>
    </div>

    <!-- 文件上傳區域 -->
    <div class="upload-section">
      <div class="upload-zone" @click="triggerFileInput" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
        <input
          ref="fileInput"
          type="file"
          multiple
          :accept="acceptedFileTypes.join(',')"
          class="upload-input"
          @change="handleFileSelect"
        />
        
        <div class="upload-content">
          <div class="upload-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7,10 12,15 17,10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </div>
          
          <div class="upload-text">
            <h3 class="upload-title">拖拽文件到此處或點擊選擇</h3>
            <p class="upload-description">支援的格式：{{ acceptedFileTypes.join(', ') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件操作工具欄 -->
    <div class="file-actions">
      <div class="primary-actions">
        <button
          class="action-btn action-btn--primary"
          :disabled="selectedFiles.size === 0"
          @click="handleBulkDownload"
        >
          下載 ({{ selectedFiles.size }})
        </button>
        
        <button
          class="action-btn action-btn--danger"
          :disabled="selectedFiles.size === 0"
          @click="handleBulkDelete"
        >
          刪除 ({{ selectedFiles.size }})
        </button>
      </div>

      <div class="view-toggle">
        <button
          class="toggle-btn"
          :class="{ 'toggle-btn--active': viewMode === 'grid' }"
          @click="setViewMode('grid')"
        >
          網格
        </button>
        
        <button
          class="toggle-btn"
          :class="{ 'toggle-btn--active': viewMode === 'list' }"
          @click="setViewMode('list')"
        >
          列表
        </button>
      </div>

      <div class="search-section">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索文件..."
          class="search-input"
          @input="handleSearch"
        />
        
        <select v-model="sortBy" class="sort-select" @change="handleSortChange">
          <option value="name">按名稱排序</option>
          <option value="size">按大小排序</option>
          <option value="date">按時間排序</option>
        </select>
      </div>
    </div>

    <!-- 文件列表區域 -->
    <div class="file-list-container">
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在載入文件列表...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <h3>載入失敗</h3>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="refreshFiles">重新載入</button>
      </div>

      <div v-else-if="filteredFiles.length === 0" class="empty-state">
        <h3>{{ hasSearchOrFilter ? '沒有找到匹配的文件' : '沒有文件' }}</h3>
        <p>
          {{ hasSearchOrFilter 
            ? '請嘗試調整搜索條件' 
            : '上傳一些文件開始使用文件管理功能' 
          }}
        </p>
      </div>

      <div v-else class="file-list">
        <!-- 網格視圖 -->
        <div v-if="viewMode === 'grid'" class="file-grid">
          <div
            v-for="file in filteredFiles"
            :key="file.id"
            class="file-item group"
            :class="{ 'file-item--selected': selectedFiles.has(file.id) }"
            @click="toggleFileSelection(file.id)"
          >
            <div class="file-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2Z"/>
                <polyline points="14,2 14,8 20,8"/>
              </svg>
            </div>
            
            <div class="file-info">
              <span class="file-name" :title="file.name">{{ file.name }}</span>
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
            </div>
            
            <div class="file-actions-overlay">
              <button class="file-action-btn" @click.stop="openPreview(file.id)" title="預覽" v-if="canPreview(file)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
              <button class="file-action-btn" @click.stop="downloadFile(file.id)" title="下載">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7,10 12,15 17,10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
              </button>
              <button class="file-action-btn" @click.stop="deleteFile(file.id)" title="刪除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="3,6 5,6 21,6"/>
                  <path d="M19,6V20A2,2 0 0,1 17,22H7A2,2 0 0,1 5,20V6"/>
                  <line x1="10" y1="11" x2="10" y2="17"/>
                  <line x1="14" y1="11" x2="14" y2="17"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 列表視圖 -->
        <div v-else class="file-list-view">
          <div class="list-header">
            <div class="header-cell header-cell--name">名稱</div>
            <div class="header-cell header-cell--size">大小</div>
            <div class="header-cell header-cell--date">修改時間</div>
            <div class="header-cell header-cell--actions">操作</div>
          </div>
          
          <div class="list-body">
            <div
              v-for="file in filteredFiles"
              :key="file.id"
              class="list-item"
              :class="{ 'list-item--selected': selectedFiles.has(file.id) }"
              @click="toggleFileSelection(file.id)"
            >
              <div class="list-cell list-cell--name">
                <div class="file-icon-small">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2Z"/>
                    <polyline points="14,2 14,8 20,8"/>
                  </svg>
                </div>
                <span class="file-name">{{ file.name }}</span>
              </div>
              <div class="list-cell list-cell--size">{{ formatFileSize(file.size) }}</div>
              <div class="list-cell list-cell--date">{{ formatDate(file.updatedAt) }}</div>
              <div class="list-cell list-cell--actions">
                <button class="list-action-btn" @click.stop="openPreview(file.id)" title="預覽" v-if="canPreview(file)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
                <button class="list-action-btn" @click.stop="downloadFile(file.id)" title="下載">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7,10 12,15 17,10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                </button>
                <button class="list-action-btn" @click.stop="deleteFile(file.id)" title="刪除">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3,6 5,6 21,6"/>
                    <path d="M19,6V20A2,2 0 0,1 17,22H7A2,2 0 0,1 5,20V6"/>
                    <line x1="10" y1="11" x2="10" y2="17"/>
                    <line x1="14" y1="11" x2="14" y2="17"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件統計 -->
    <div class="file-stats">
      <span>總計 {{ filteredFiles.length }} 個文件</span>
      <span v-if="selectedFiles.size > 0">已選擇 {{ selectedFiles.size }} 個</span>
    </div>
    
    <!-- 文件預覽對話框 -->
    <div v-if="previewVisible" class="file-preview-overlay" @click="closePreview">
      <div class="file-preview-container" @click.stop>
        <div class="preview-header">
          <h3 class="preview-title">{{ previewFile?.name }}</h3>
          <button class="preview-close-btn" @click="closePreview">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <div class="preview-content">
          <!-- 圖片預覽 -->
          <img v-if="previewType === 'image'" :src="previewUrl" class="preview-image" alt="圖片預覽" />
          
          <!-- 文本預覽 -->
          <div v-else-if="previewType === 'text'" class="preview-text">
            <pre>{{ previewContent }}</pre>
          </div>
          
          <!-- 不支持預覽 -->
          <div v-else class="preview-unsupported">
            <p>無法預覽此類型的文件</p>
            <button class="action-btn action-btn--primary" @click="downloadPreviewFile">下載文件</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFileStore } from '@/stores/file'
import { useAppStore } from '@/stores/app'
import type { FileInfo } from '@/types/file'

const fileStore = useFileStore()
const appStore = useAppStore()

// 配置
const acceptedFileTypes = ['.txt', '.csv', '.json', '.pdf', '.xlsx', '.xls', '.png', '.jpg', '.jpeg']

// 狀態
const fileInput = ref<HTMLInputElement>()
const searchQuery = ref('')
const sortBy = ref('name')
const error = ref<string | null>(null)
const previewVisible = ref(false)
const previewFile = ref<FileInfo | null>(null)
const previewType = ref<'image' | 'text' | 'other'>('other')
const previewUrl = ref('')
const previewContent = ref('')

// 計算屬性
const isLoading = computed(() => fileStore.isLoading)
const filteredFiles = computed(() => fileStore.filteredFiles)
const selectedFiles = computed(() => fileStore.selectedFiles)
const viewMode = computed(() => fileStore.viewMode)

const hasSearchOrFilter = computed(() => {
  return searchQuery.value !== ''
})

// 方法
const refreshFiles = async () => {
  error.value = null
  try {
    await fileStore.fetchFiles()
    // 刷新文件列表後清空選中的文件
    fileStore.deselectAllFiles()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '載入文件失敗'
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    await uploadFiles(Array.from(target.files))
    target.value = ''
  }
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  const files = event.dataTransfer?.files
  if (files) {
    await uploadFiles(Array.from(files))
  }
}

const uploadFiles = async (files: File[]) => {
  // 使用store的uploadFiles方法，它提供了更完整的功能
  const fileInputs = files.map(file => ({
    file,
    path: '/data_storage'
  }))
  
  await fileStore.uploadFiles(fileInputs)
  await refreshFiles()
}

const downloadFile = async (fileId: string) => {
  try {
    await fileStore.downloadFile(fileId)
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '下載失敗',
      message: error instanceof Error ? error.message : '下載文件時發生錯誤'
    })
  }
}

const deleteFile = async (fileId: string) => {
  const file = filteredFiles.value.find(f => f.id === fileId)
  if (file && confirm(`確定要刪除文件 "${file.name}" 嗎？`)) {
    const result = await fileStore.deleteFiles([fileId])
    if (result.success) {
      // 刪除成功後刷新文件列表
      await refreshFiles()
    }
  }
}

const toggleFileSelection = (fileId: string) => {
  fileStore.toggleFileSelection(fileId)
}

const setViewMode = (mode: 'grid' | 'list') => {
  fileStore.setViewMode(mode)
}

const handleSearch = () => {
  fileStore.updateSearchParams({ query: searchQuery.value })
}

const handleSortChange = () => {
  fileStore.setSortBy(sortBy.value as 'name' | 'size' | 'date')
}

const handleBulkDownload = () => {
  const fileIds = Array.from(selectedFiles.value)
  if (fileIds.length === 0) {
    appStore.addNotification({
      type: 'warning',
      title: '無法下載',
      message: '請先選擇要下載的文件'
    })
    return
  }
  
  // 批量下載文件
  fileIds.forEach(id => downloadFile(id))
  
  appStore.addNotification({
    type: 'info',
    title: '批量下載',
    message: `正在下載 ${fileIds.length} 個文件`
  })
}

const handleBulkDelete = async () => {
  const fileIds = Array.from(selectedFiles.value)
  if (fileIds.length === 0) {
    appStore.addNotification({
      type: 'warning',
      title: '無法刪除',
      message: '請先選擇要刪除的文件'
    })
    return
  }
  
  if (confirm(`確定要刪除選中的 ${fileIds.length} 個文件嗎？`)) {
    const result = await fileStore.deleteFiles(fileIds)
    if (result.success) {
      // 刪除成功後刷新文件列表
      await refreshFiles()
    }
  }
}

const formatFileSize = (bytes: number): string => {
  return fileStore.formatFileSize(bytes)
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW')
}

// 文件預覽相關方法
const canPreview = (file: FileInfo): boolean => {
  return file.type === 'image' || file.type === 'text'
}

const openPreview = async (fileId: string) => {
  const file = filteredFiles.value.find(f => f.id === fileId)
  if (!file) return
  
  previewFile.value = file
  previewVisible.value = true
  
  try {
    if (file.type === 'image') {
      previewType.value = 'image'
      previewUrl.value = `/api/files/preview/${encodeURIComponent(file.name)}`
      previewContent.value = ''
    } else if (file.type === 'text') {
      previewType.value = 'text'
      previewUrl.value = ''
      
      const response = await fetch(`/api/files/content/${encodeURIComponent(file.name)}`)
      if (!response.ok) {
        throw new Error(`獲取文件內容失敗: ${response.statusText}`)
      }
      
      previewContent.value = await response.text()
    } else {
      previewType.value = 'other'
      previewUrl.value = ''
      previewContent.value = ''
    }
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '預覽失敗',
      message: error instanceof Error ? error.message : '預覽文件時發生錯誤'
    })
    closePreview()
  }
}

const closePreview = () => {
  previewVisible.value = false
  previewFile.value = null
  previewUrl.value = ''
  previewContent.value = ''
}

const downloadPreviewFile = () => {
  if (previewFile.value) {
    downloadFile(previewFile.value.id)
  }
}

// 生命週期
onMounted(async () => {
  // 清空選中的文件
  fileStore.deselectAllFiles()
  await refreshFiles()
})
</script>

<style scoped>
.file-manager {
  @apply flex flex-col h-full p-6;
  background-color: var(--bg-primary);
}

.page-header {
  @apply mb-6;
}

.page-title {
  @apply text-2xl font-bold text-gray-900 mb-2;
}

.page-description {
  color: var(--text-secondary);
}

.upload-section {
  @apply mb-6;
}

.upload-zone {
  @apply border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200;
  border-color: var(--border-color-light);
}

.upload-zone:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.upload-input {
  @apply hidden;
}

.upload-content {
  @apply flex flex-col items-center space-y-4;
}

.upload-icon {
  color: var(--text-placeholder);
}

.upload-title {
  @apply text-lg font-medium;
  color: var(--text-primary);
}

.upload-description {
  @apply text-sm;
  color: var(--text-secondary);
}

.file-actions {
  @apply flex flex-wrap items-center gap-4 p-4 border rounded-lg mb-4;
  background-color: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.primary-actions {
  @apply flex items-center space-x-2;
}

.action-btn {
  @apply px-4 py-2 rounded-lg border transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.action-btn--primary {
  @apply bg-blue-600 text-white border-blue-600 hover:bg-blue-700;
}

.action-btn--danger {
  @apply bg-red-600 text-white border-red-600 hover:bg-red-700;
}

.view-toggle {
  @apply flex items-center space-x-1 rounded-lg p-1;
  background-color: var(--bg-tertiary);
}

.toggle-btn {
  @apply px-3 py-1 rounded text-sm transition-colors;
  color: var(--text-secondary);
}

.toggle-btn:hover {
  color: var(--text-primary);
}

.toggle-btn--active {
  @apply shadow-sm;
  background-color: var(--bg-primary);
  color: var(--el-color-primary);
}

.search-section {
  @apply flex items-center space-x-4 flex-1;
}

.search-input {
  @apply flex-1 max-w-sm px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--border-color-light);
}

.sort-select {
  @apply px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--border-color-light);
}

.file-list-container {
  @apply flex-1 rounded-lg shadow-sm border overflow-hidden;
  background-color: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.loading-state, .error-state, .empty-state {
  @apply flex flex-col items-center justify-center py-16 text-center;
}

.loading-spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4;
}

.retry-btn {
  @apply mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors;
}

.file-grid {
  @apply grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 p-4;
}

.file-item {
  @apply relative border rounded-lg p-4 cursor-pointer transition-all duration-200 hover:shadow-md;
  background-color: var(--bg-primary);
  border-color: var(--border-color-light);
}

.file-item--selected {
  @apply border-blue-500 bg-blue-50;
}

.file-icon {
  @apply w-12 h-12 transition-colors mx-auto mb-3;
  color: var(--text-placeholder);
}

.file-item:hover .file-icon {
  color: var(--el-color-primary);
}

.file-info {
  @apply text-center space-y-1;
}

.file-name {
  @apply block text-sm font-medium truncate;
  color: var(--text-primary);
}

.file-size {
  @apply block text-xs;
  color: var(--text-secondary);
}

.file-actions-overlay {
  @apply absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity;
}

.file-action-btn {
  @apply w-6 h-6 flex items-center justify-center rounded-full shadow-sm text-gray-400 hover:text-gray-600 transition-colors;
  background-color: var(--bg-secondary);
}

.file-list-view {
  @apply flex flex-col h-full;
}

.list-header {
  @apply flex items-center border-b px-4 py-3 text-sm font-medium;
  background-color: var(--bg-secondary);
  color: var(--text-regular);
  border-color: var(--border-color-light);
}

.header-cell--name {
  @apply flex-1;
}

.header-cell--size {
  @apply w-24;
}

.header-cell--date {
  @apply w-32;
}

.header-cell--actions {
  @apply w-20;
}

.list-body {
  @apply flex-1 overflow-auto;
}

.list-item {
  @apply flex items-center px-4 py-3 border-b cursor-pointer;
  border-color: var(--border-color-extra-light);
}

.list-item:hover {
  background-color: var(--bg-secondary);
}

.list-item--selected {
  @apply bg-blue-50;
}

.list-cell--name {
  @apply flex items-center space-x-3 flex-1 min-w-0;
}

.file-icon-small {
  @apply w-6 h-6 text-gray-400 flex-shrink-0;
}

.list-cell--size {
  @apply w-24 text-sm;
  color: var(--text-secondary);
}

.list-cell--date {
  @apply w-32 text-sm;
  color: var(--text-secondary);
}

.list-cell--actions {
  @apply w-20 flex items-center space-x-2;
}

.list-action-btn {
  @apply w-6 h-6 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors;
}

.file-stats {
  @apply mt-4 flex items-center justify-between text-sm p-4 rounded-lg border;
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border-color: var(--border-color-light);
}

/* 文件預覽對話框樣式 */
.file-preview-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.file-preview-container {
  @apply bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden;
  background-color: var(--bg-primary);
}

.preview-header {
  @apply flex items-center justify-between p-4 border-b;
  border-color: var(--border-color-light);
}

.preview-title {
  @apply text-lg font-medium truncate;
  color: var(--text-primary);
}

.preview-close-btn {
  @apply w-8 h-8 flex items-center justify-center transition-colors;
  color: var(--text-secondary);
}

.preview-close-btn:hover {
  color: var(--text-primary);
}

.preview-content {
  @apply flex-1 overflow-auto p-4 flex items-center justify-center;
}

.preview-image {
  @apply max-w-full max-h-[70vh] object-contain;
}

.preview-text {
  @apply w-full h-full overflow-auto p-4 rounded;
  background-color: var(--bg-tertiary);
}

.preview-text pre {
  @apply font-mono text-sm whitespace-pre-wrap;
}

.preview-unsupported {
  @apply text-center p-8;
}

.preview-unsupported p {
  @apply mb-4 text-gray-600;
}
</style>