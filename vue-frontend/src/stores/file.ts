import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  FileInfo,
  FileUploadInput,
  FileUploadProgress,
  FileSearchParams,
  FileOperation,
  FileOperationResult,
  DirectoryTree
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
  const fetchFiles = async (): Promise<void> => {
    isLoading.value = true
    try {
      const response = await fetch('/api/files')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      // 直接使用後端返回的文件列表
      // 後端已經提供了完整的文件信息
      files.value = data.files
      
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
  const getFileType = (fileName: string): string => {
    const ext = getFileExtension(fileName).toLowerCase()
    
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return 'image'
    if (['pdf'].includes(ext)) return 'document'
    if (['txt', 'md', 'json', 'csv'].includes(ext)) return 'text'
    if (['mp4', 'avi', 'mov', 'webm'].includes(ext)) return 'video'
    if (['mp3', 'wav', 'ogg'].includes(ext)) return 'audio'
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return 'archive'
    
    return 'other'
  }

  const getFileExtension = (fileName: string): string => {
    const lastDot = fileName.lastIndexOf('.')
    return lastDot !== -1 ? fileName.substring(lastDot + 1) : ''
  }

  const getMimeType = (fileName: string): string => {
    const ext = getFileExtension(fileName).toLowerCase()
    const mimeTypes: Record<string, string> = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'pdf': 'application/pdf',
      'txt': 'text/plain',
      'json': 'application/json',
      'csv': 'text/csv'
    }
    return mimeTypes[ext] || 'application/octet-stream'
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
    
    // Actions
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
    
    // 工具函數
    formatFileSize
  }
})