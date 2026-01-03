import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  FileInfo,
  FileUploadInput,
  FileUploadProgress,
  FileSearchParams,
  FileOperationResult
} from '@/types/file'
import { useAppStore } from './app'

export const useFileStore = defineStore('file', () => {
  // 狀態
  const files = ref<FileInfo[]>([])
  const uploadProgress = ref<Map<string, FileUploadProgress>>(new Map())
  const isLoading = ref(false)
  const selectedFiles = ref<Set<string>>(new Set())
  const searchParams = ref<FileSearchParams>({})
  const viewMode = ref<'grid' | 'list'>('grid')
  const sortBy = ref<'name' | 'size' | 'date'>('name')
  const sortOrder = ref<'asc' | 'desc'>('asc')

  // 計算屬性
  const filteredFiles = computed(() => {
    let filtered = [...files.value]

    // 搜索過濾
    if (searchParams.value.query) {
      const query = searchParams.value.query.toLowerCase()
      filtered = filtered.filter(file => 
        file.name.toLowerCase().includes(query) ||
        file.extension.toLowerCase().includes(query)
      )
    }

    // 文件類型過濾
    if (searchParams.value.type) {
      filtered = filtered.filter(file => file.type === searchParams.value.type)
    }

    // 副檔名過濾
    if (searchParams.value.extension) {
      filtered = filtered.filter(file => file.extension === searchParams.value.extension)
    }

    // 大小範圍過濾
    if (searchParams.value.sizeRange) {
      const { min, max } = searchParams.value.sizeRange
      filtered = filtered.filter(file => file.size >= min && file.size <= max)
    }

    // 日期範圍過濾
    if (searchParams.value.dateRange) {
      const { start, end } = searchParams.value.dateRange
      filtered = filtered.filter(file => {
        const fileDate = new Date(file.updatedAt)
        return fileDate >= new Date(start) && fileDate <= new Date(end)
      })
    }

    // 排序
    filtered.sort((a, b) => {
      let comparison = 0
      
      switch (sortBy.value) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'size':
          comparison = a.size - b.size
          break
        case 'date':
          comparison = new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
          break
      }

      return sortOrder.value === 'asc' ? comparison : -comparison
    })

    return filtered
  })

  const uploadingFiles = computed(() => {
    return Array.from(uploadProgress.value.values()).filter(
      progress => progress.status === 'uploading'
    )
  })

  const totalSize = computed(() => {
    return files.value.reduce((total, file) => total + file.size, 0)
  })

  const fileTypes = computed(() => {
    const types = new Set(files.value.map(file => file.type))
    return Array.from(types)
  })

  // Actions
  const fetchFiles = async (useCache: boolean = false): Promise<void> => {
    // 如果使用緩存且文件列表不為空，則跳過
    if (useCache && files.value.length > 0) {
      return
    }
    
    isLoading.value = true
    try {
      const appStore = useAppStore()
      const response = await appStore.apiRequest<{ files: FileInfo[] }>('/api/files')
      
      // 直接使用後端返回的文件列表
      // 後端已經提供了完整的文件信息
      files.value = response.files
      
      console.log(`成功獲取 ${response.files.length} 個文件`)
      
    } catch (error) {
      console.error('獲取文件列表失敗:', error)
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '錯誤',
        message: '獲取文件列表失敗'
      })
    } finally {
      isLoading.value = false
    }
  }

  const uploadFiles = async (inputs: FileUploadInput[]): Promise<void> => {
    const appStore = useAppStore()
    
    for (const input of inputs) {
      const fileId = `upload_${Date.now()}_${Math.random()}`
      const progress: FileUploadProgress = {
        fileId,
        fileName: input.file.name,
        progress: 0,
        status: 'pending'
      }
      
      uploadProgress.value.set(fileId, progress)
      
      try {
        progress.status = 'uploading'
        
        const formData = new FormData()
        formData.append('file', input.file)
        if (input.path) formData.append('path', input.path)
        if (input.tags) formData.append('tags', JSON.stringify(input.tags))
        if (input.metadata) formData.append('metadata', JSON.stringify(input.metadata))

        const response = await fetch('/api/files/upload', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error(`上傳失敗: ${response.statusText}`)
        }

        progress.progress = 100
        progress.status = 'completed'
        
        appStore.addNotification({
          type: 'success',
          title: '上傳成功',
          message: `文件 ${input.file.name} 上傳完成`
        })

        // 重新獲取文件列表
        await fetchFiles()
        
      } catch (error) {
        progress.status = 'error'
        progress.error = error instanceof Error ? error.message : '上傳失敗'
        
        appStore.addNotification({
          type: 'error',
          title: '上傳失敗',
          message: `文件 ${input.file.name} 上傳失敗: ${progress.error}`
        })
      }
    }
  }

  const downloadFile = async (fileId: string): Promise<void> => {
    const file = files.value.find(f => f.id === fileId)
    if (!file) return

    try {
      const response = await fetch(`/api/files/download/${encodeURIComponent(file.name)}`)
      if (!response.ok) {
        throw new Error(`下載失敗: ${response.statusText}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      const appStore = useAppStore()
      appStore.addNotification({
        type: 'success',
        title: '下載成功',
        message: `文件 ${file.name} 已下載`
      })

    } catch (error) {
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '下載失敗',
        message: error instanceof Error ? error.message : '下載失敗'
      })
    }
  }

  const deleteFiles = async (fileIds: string[]): Promise<FileOperationResult> => {
    const appStore = useAppStore()
    const result: FileOperationResult = {
      success: true,
      affectedFiles: [],
      errors: []
    }

    for (const fileId of fileIds) {
      const file = files.value.find(f => f.id === fileId)
      if (!file) continue

      try {
        const response = await fetch(`/api/files/${encodeURIComponent(file.name)}`, {
          method: 'DELETE'
        })

        if (!response.ok) {
          throw new Error(`刪除失敗: ${response.statusText}`)
        }

        result.affectedFiles.push(fileId)
        
      } catch (error) {
        result.success = false
        result.errors?.push({
          fileId,
          error: error instanceof Error ? error.message : '刪除失敗'
        })
      }
    }

    if (result.success) {
      appStore.addNotification({
        type: 'success',
        title: '刪除成功',
        message: `已刪除 ${result.affectedFiles.length} 個文件`
      })
      await fetchFiles()
    } else {
      appStore.addNotification({
        type: 'error',
        title: '刪除失敗',
        message: `部分文件刪除失敗`
      })
    }

    return result
  }

  const renameFile = async (fileId: string, newName: string): Promise<boolean> => {
    const file = files.value.find(f => f.id === fileId)
    if (!file) return false

    const appStore = useAppStore()

    try {
      const response = await fetch(`/api/files/${encodeURIComponent(file.name)}/rename`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ newName })
      })

      if (!response.ok) {
        throw new Error(`重命名失敗: ${response.statusText}`)
      }

      appStore.addNotification({
        type: 'success',
        title: '重命名成功',
        message: `文件已重命名為 ${newName}`
      })

      await fetchFiles()
      return true

    } catch (error) {
      appStore.addNotification({
        type: 'error',
        title: '重命名失敗',
        message: error instanceof Error ? error.message : '重命名失敗'
      })
      return false
    }
  }

  const selectFile = (fileId: string): void => {
    selectedFiles.value.add(fileId)
  }

  const deselectFile = (fileId: string): void => {
    selectedFiles.value.delete(fileId)
  }

  const toggleFileSelection = (fileId: string): void => {
    if (selectedFiles.value.has(fileId)) {
      deselectFile(fileId)
    } else {
      selectFile(fileId)
    }
  }

  const selectAllFiles = (): void => {
    filteredFiles.value.forEach(file => selectedFiles.value.add(file.id))
  }

  const deselectAllFiles = (): void => {
    selectedFiles.value.clear()
  }

  const updateSearchParams = (params: Partial<FileSearchParams>): void => {
    searchParams.value = { ...searchParams.value, ...params }
  }

  const clearSearch = (): void => {
    searchParams.value = {}
  }

  const setSortBy = (field: 'name' | 'size' | 'date'): void => {
    if (sortBy.value === field) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortBy.value = field
      sortOrder.value = 'asc'
    }
  }

  const setViewMode = (mode: 'grid' | 'list'): void => {
    viewMode.value = mode
  }

  // 工具函數
  // 工具函數已簡化


  // 工具函數已簡化


  // MimeType 獲取函數已簡化


  const formatFileSize = (bytes: number): string => {
    if (!bytes || isNaN(bytes) || bytes === 0) return '0 B'
    
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 實時文件狀態更新
  const syncFileStatus = (fileData: any): void => {
    try {
      if (fileData.type === 'file_update') {
        console.log('文件狀態更新:', fileData)
        
        // 刷新文件列表
        fetchFiles(false) // 強制刷新，不使用緩存
      } else if (fileData.type === 'file_upload_progress') {
        // 更新上傳進度
        const { fileId, progress, status } = fileData.data
        const currentProgress = uploadProgress.value.get(fileId)
        if (currentProgress) {
          uploadProgress.value.set(fileId, {
            ...currentProgress,
            progress,
            status
          })
        }
      }
    } catch (error) {
      console.error('同步文件狀態失敗:', error)
    }
  }

  // 批量文件操作
  const batchFileOperation = async (
    fileIds: string[],
    operation: 'delete' | 'download',
    _options?: any
  ): Promise<void> => {
    const appStore = useAppStore()
    
    try {
      isLoading.value = true
      
      const results = await Promise.allSettled(
        fileIds.map(async (fileId) => {
          switch (operation) {
            case 'delete':
              return await deleteFiles([fileId])
            case 'download':
              return await downloadFile(fileId)
            default:
              throw new Error(`不支援的操作: ${operation}`)
          }
        })
      )
      
      const successful = results.filter(r => r.status === 'fulfilled').length
      const failed = results.filter(r => r.status === 'rejected').length
      
      if (successful > 0) {
        appStore.addNotification({
          type: 'success',
          title: '批量操作完成',
          message: `成功處理 ${successful} 個文件${failed > 0 ? `，失敗 ${failed} 個` : ''}`
        })
      }
      
      if (failed > 0) {
        appStore.addNotification({
          type: 'warning',
          title: '部分操作失敗',
          message: `${failed} 個文件操作失敗`
        })
      }
      
    } catch (error) {
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '批量操作失敗',
        message: error instanceof Error ? error.message : '未知錯誤'
      })
    } finally {
      isLoading.value = false
    }
  }

  // 智能文件預加載
  const preloadFiles = async (fileIds: string[]): Promise<void> => {
    try {
      // 預加載文件內容到緩存
      const preloadPromises = fileIds.map(async (fileId) => {
        const file = files.value.find(f => f.id === fileId)
        if (file && file.type === 'text' && file.size < 1024 * 1024) { // 只預加載小於1MB的文本文件
          try {
            const response = await fetch(`/api/files/content/${encodeURIComponent(file.name)}`)
            if (response.ok) {
              const content = await response.text()
              // 緩存到 sessionStorage
              sessionStorage.setItem(`file_content_${fileId}`, content)
              console.log(`預加載文件成功: ${file.name}`)
            }
          } catch (error) {
            console.warn(`預加載文件失敗: ${file.name}`, error)
          }
        }
      })
      
      await Promise.allSettled(preloadPromises)
    } catch (error) {
      console.error('文件預加載失敗:', error)
    }
  }

  // 文件搜索增強
  const advancedSearch = async (searchCriteria: {
    query?: string
    fileType?: string
    dateRange?: { start: string; end: string }
    sizeRange?: { min: number; max: number }
    tags?: string[]
  }): Promise<FileInfo[]> => {
    try {
      // 構建搜索參數
      const params = new URLSearchParams()
      
      if (searchCriteria.query) params.append('q', searchCriteria.query)
      if (searchCriteria.fileType) params.append('type', searchCriteria.fileType)
      if (searchCriteria.dateRange) {
        params.append('dateStart', searchCriteria.dateRange.start)
        params.append('dateEnd', searchCriteria.dateRange.end)
      }
      if (searchCriteria.sizeRange) {
        params.append('sizeMin', searchCriteria.sizeRange.min.toString())
        params.append('sizeMax', searchCriteria.sizeRange.max.toString())
      }
      if (searchCriteria.tags) {
        params.append('tags', searchCriteria.tags.join(','))
      }
      
      const appStore = useAppStore()
      const response = await appStore.apiRequest<{ files: FileInfo[] }>(
        `/api/files/search?${params.toString()}`
      )
      
      return response.files || []
      
    } catch (error) {
      console.error('高級搜索失敗:', error)
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '搜索失敗',
        message: error instanceof Error ? error.message : '搜索請求失敗'
      })
      return []
    }
  }

  // 文件自動同步
  const enableAutoSync = (interval: number = 30000): void => {
    // 定期自動刷新文件列表
    const autoSyncInterval = setInterval(async () => {
      try {
        const currentCount = files.value.length
        await fetchFiles(false)
        const newCount = files.value.length
        
        if (newCount !== currentCount) {
          const appStore = useAppStore()
          appStore.addNotification({
            type: 'info',
            title: '文件已同步',
            message: `檢測到文件變更，列表已更新`,
            duration: 3000
          })
        }
      } catch (error) {
        console.error('自動同步失敗:', error)
      }
    }, interval)
    
    // 儲存間隔 ID 以便清理
    ;(window as any).fileAutoSyncInterval = autoSyncInterval
  }

  const disableAutoSync = (): void => {
    const intervalId = (window as any).fileAutoSyncInterval
    if (intervalId) {
      clearInterval(intervalId)
      ;(window as any).fileAutoSyncInterval = null
    }
  }

  // 增強的文件統計
  const getFileStatistics = () => {
    const stats = {
      totalFiles: files.value.length,
      totalSize: totalSize.value,
      typeDistribution: {} as Record<string, number>,
      sizeDistribution: {
        small: 0,  // < 1MB
        medium: 0, // 1MB - 10MB
        large: 0   // > 10MB
      },
      recentFiles: files.value
        .filter(f => {
          const fileDate = new Date(f.updatedAt)
          const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
          return fileDate > dayAgo
        }).length
    }
    
    files.value.forEach(file => {
      // 類型分佈
      stats.typeDistribution[file.type] = (stats.typeDistribution[file.type] || 0) + 1
      
      // 大小分佈
      if (file.size < 1024 * 1024) {
        stats.sizeDistribution.small++
      } else if (file.size < 10 * 1024 * 1024) {
        stats.sizeDistribution.medium++
      } else {
        stats.sizeDistribution.large++
      }
    })
    
    return stats
  }

  return {
    // 狀態
    files,
    uploadProgress,
    isLoading,
    selectedFiles,
    searchParams,
    viewMode,
    sortBy,
    sortOrder,
    
    // 計算屬性
    filteredFiles,
    uploadingFiles,
    totalSize,
    fileTypes,
    
    // 基礎 Actions
    fetchFiles,
    uploadFiles,
    downloadFile,
    deleteFiles,
    renameFile,
    selectFile,
    deselectFile,
    toggleFileSelection,
    selectAllFiles,
    deselectAllFiles,
    updateSearchParams,
    clearSearch,
    setSortBy,
    setViewMode,
    
    // 增強功能
    syncFileStatus,
    batchFileOperation,
    preloadFiles,
    advancedSearch,
    enableAutoSync,
    disableAutoSync,
    getFileStatistics,
    
    // 工具函數
    formatFileSize
  }
})