import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { useAppStore } from './app'
// import type { ChartConfig, ChartData } from '@/types/visualization'

// 數據源類型
export interface DataSource {
  id: string
  name: string
  type: 'api' | 'file' | 'realtime' | 'computed'
  url?: string
  filePath?: string
  updateInterval?: number
  lastUpdate: string
  status: 'active' | 'inactive' | 'error'
  error?: string
  metadata?: Record<string, any>
}

// 數據集類型
export interface Dataset {
  id: string
  name: string
  sourceId: string
  data: any[]
  schema: Record<string, string>
  size: number
  lastUpdate: string
  version: number
  cached: boolean
}

// 數據更新事件
export interface DataUpdateEvent {
  id: string
  datasetId: string
  type: 'create' | 'update' | 'delete' | 'refresh'
  timestamp: number
  changes?: any
}

interface DataState {
  // 數據源管理
  dataSources: Map<string, DataSource>
  datasets: Map<string, Dataset>
  
  // 實時更新
  updateEvents: DataUpdateEvent[]
  isUpdating: boolean
  updateError: string | null
  
  // 緩存管理
  cacheEnabled: boolean
  cacheSize: number
  maxCacheSize: number
  
  // 同步狀態
  lastSyncTime: string | null
  syncInProgress: boolean
  autoSyncEnabled: boolean
  syncInterval: number
}

export const useDataStore = defineStore('data', () => {
  const appStore = useAppStore()
  
  // 響應式狀態
  const state = ref<DataState>({
    dataSources: new Map(),
    datasets: new Map(),
    updateEvents: [],
    isUpdating: false,
    updateError: null,
    cacheEnabled: true,
    cacheSize: 0,
    maxCacheSize: 100 * 1024 * 1024, // 100MB
    lastSyncTime: null,
    syncInProgress: false,
    autoSyncEnabled: true,
    syncInterval: 30000 // 30秒
  })
  
  // 定時器
  const syncTimer = ref<number | null>(null)
  const updateTimer = ref<number | null>(null)
  
  // 計算屬性
  const activeSources = computed(() => 
    Array.from(state.value.dataSources.values()).filter(
      source => source.status === 'active'
    )
  )
  
  const totalDatasets = computed(() => state.value.datasets.size)
  
  const cacheUsagePercent = computed(() => 
    (state.value.cacheSize / state.value.maxCacheSize) * 100
  )
  
  const recentEvents = computed(() => 
    state.value.updateEvents.slice(-10).reverse()
  )
  
  // 數據源管理
  const addDataSource = (source: Omit<DataSource, 'id' | 'lastUpdate' | 'status'>): string => {
    const id = generateId('source')
    const newSource: DataSource = {
      ...source,
      id,
      lastUpdate: new Date().toISOString(),
      status: 'inactive'
    }
    
    state.value.dataSources.set(id, newSource)
    console.log(`新增數據源: ${newSource.name} (${id})`)
    
    return id
  }
  
  const removeDataSource = (sourceId: string): boolean => {
    const source = state.value.dataSources.get(sourceId)
    if (!source) return false
    
    // 移除相關數據集
    const relatedDatasets = Array.from(state.value.datasets.values())
      .filter(dataset => dataset.sourceId === sourceId)
    
    relatedDatasets.forEach(dataset => {
      state.value.datasets.delete(dataset.id)
    })
    
    state.value.dataSources.delete(sourceId)
    
    console.log(`移除數據源: ${source.name} 及其 ${relatedDatasets.length} 個數據集`)
    return true
  }
  
  const updateDataSource = (sourceId: string, updates: Partial<DataSource>): boolean => {
    const source = state.value.dataSources.get(sourceId)
    if (!source) return false
    
    const updatedSource = {
      ...source,
      ...updates,
      lastUpdate: new Date().toISOString()
    }
    
    state.value.dataSources.set(sourceId, updatedSource)
    return true
  }
  
  // 數據集管理
  const createDataset = (
    name: string, 
    sourceId: string, 
    data: any[], 
    schema?: Record<string, string>
  ): string => {
    const id = generateId('dataset')
    const dataset: Dataset = {
      id,
      name,
      sourceId,
      data: [...data], // 深拷貝數據
      schema: schema || inferSchema(data),
      size: calculateDataSize(data),
      lastUpdate: new Date().toISOString(),
      version: 1,
      cached: true
    }
    
    state.value.datasets.set(id, dataset)
    updateCacheSize()
    
    // 記錄事件
    addUpdateEvent({
      id: generateId('event'),
      datasetId: id,
      type: 'create',
      timestamp: Date.now()
    })
    
    console.log(`創建數據集: ${name} (${id}), 大小: ${formatBytes(dataset.size)}`)
    return id
  }
  
  const updateDataset = (datasetId: string, newData: any[], changes?: any): boolean => {
    const dataset = state.value.datasets.get(datasetId)
    if (!dataset) return false
    
    const updatedDataset: Dataset = {
      ...dataset,
      data: [...newData],
      size: calculateDataSize(newData),
      lastUpdate: new Date().toISOString(),
      version: dataset.version + 1
    }
    
    state.value.datasets.set(datasetId, updatedDataset)
    updateCacheSize()
    
    // 記錄事件
    addUpdateEvent({
      id: generateId('event'),
      datasetId,
      type: 'update',
      timestamp: Date.now(),
      changes
    })
    
    // 通知組件數據已更新
    notifyDataUpdate(datasetId, newData)
    
    console.log(`更新數據集: ${dataset.name}, 新版本: ${updatedDataset.version}`)
    return true
  }
  
  const deleteDataset = (datasetId: string): boolean => {
    const dataset = state.value.datasets.get(datasetId)
    if (!dataset) return false
    
    state.value.datasets.delete(datasetId)
    updateCacheSize()
    
    // 記錄事件
    addUpdateEvent({
      id: generateId('event'),
      datasetId,
      type: 'delete',
      timestamp: Date.now()
    })
    
    console.log(`刪除數據集: ${dataset.name}`)
    return true
  }
  
  // 數據加載
  const loadDataFromAPI = async (sourceId: string): Promise<string | null> => {
    const source = state.value.dataSources.get(sourceId)
    if (!source || !source.url) return null
    
    try {
      state.value.isUpdating = true
      updateDataSource(sourceId, { status: 'active' })
      
      const response = await appStore.apiRequest(source.url)
      
      // 處理不同的響應格式
      let data: any[] = []
      if (Array.isArray(response)) {
        data = response
      } else if (response.data && Array.isArray(response.data)) {
        data = response.data
      } else if (response.results && Array.isArray(response.results)) {
        data = response.results
      } else {
        data = [response] // 單個對象包裝成數組
      }
      
      const datasetId = createDataset(`${source.name}_data`, sourceId, data)
      
      updateDataSource(sourceId, { 
        status: 'active',
        error: undefined,
        lastUpdate: new Date().toISOString()
      })
      
      console.log(`從 API 加載數據成功: ${source.url}, 數據量: ${data.length}`)
      return datasetId
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知錯誤'
      
      updateDataSource(sourceId, { 
        status: 'error',
        error: errorMessage
      })
      
      state.value.updateError = errorMessage
      
      appStore.addNotification({
        type: 'error',
        title: 'API 數據加載失敗',
        message: `數據源 ${source.name}: ${errorMessage}`
      })
      
      console.error('API 數據加載失敗:', error)
      return null
      
    } finally {
      state.value.isUpdating = false
    }
  }
  
  const loadDataFromFile = async (sourceId: string, filePath: string): Promise<string | null> => {
    const source = state.value.dataSources.get(sourceId)
    if (!source) return null
    
    try {
      state.value.isUpdating = true
      updateDataSource(sourceId, { status: 'active' })
      
      const response = await fetch(`/api/files/content/${encodeURIComponent(filePath)}`)
      if (!response.ok) {
        throw new Error(`文件加載失敗: ${response.statusText}`)
      }
      
      const content = await response.text()
      let data: any[] = []
      
      // 根據文件類型解析數據
      if (filePath.endsWith('.json')) {
        const parsed = JSON.parse(content)
        data = Array.isArray(parsed) ? parsed : [parsed]
      } else if (filePath.endsWith('.csv')) {
        data = parseCSV(content)
      } else {
        throw new Error('不支援的文件格式')
      }
      
      const datasetId = createDataset(`${source.name}_file`, sourceId, data)
      
      updateDataSource(sourceId, { 
        status: 'active',
        error: undefined,
        lastUpdate: new Date().toISOString()
      })
      
      console.log(`從文件加載數據成功: ${filePath}, 數據量: ${data.length}`)
      return datasetId
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知錯誤'
      
      updateDataSource(sourceId, { 
        status: 'error',
        error: errorMessage
      })
      
      state.value.updateError = errorMessage
      
      appStore.addNotification({
        type: 'error',
        title: '文件數據加載失敗',
        message: `數據源 ${source.name}: ${errorMessage}`
      })
      
      console.error('文件數據加載失敗:', error)
      return null
      
    } finally {
      state.value.isUpdating = false
    }
  }
  
  // 實時數據更新
  const enableRealtimeUpdates = (sourceId: string): void => {
    const source = state.value.dataSources.get(sourceId)
    if (!source || source.type !== 'realtime') return
    
    // 監聽實時數據事件
    const handleRealtimeData = (event: Event) => {
      const customEvent = event as CustomEvent
      const { datasetId, data, changes } = customEvent.detail
      
      const dataset = state.value.datasets.get(datasetId)
      if (dataset && dataset.sourceId === sourceId) {
        updateDataset(datasetId, data, changes)
      }
    }
    
    document.addEventListener('realtime-data-update', handleRealtimeData)
    
    // 儲存事件監聽器引用
    ;(source as any).realtimeListener = handleRealtimeData
    
    console.log(`啟用實時更新: ${source.name}`)
  }
  
  const disableRealtimeUpdates = (sourceId: string): void => {
    const source = state.value.dataSources.get(sourceId)
    if (!source) return
    
    const listener = (source as any).realtimeListener
    if (listener) {
      document.removeEventListener('realtime-data-update', listener)
      delete (source as any).realtimeListener
    }
    
    console.log(`禁用實時更新: ${source.name}`)
  }
  
  // 數據同步
  const syncAllData = async (): Promise<void> => {
    if (state.value.syncInProgress) return
    
    state.value.syncInProgress = true
    state.value.updateError = null
    
    try {
      const activeSources = Array.from(state.value.dataSources.values())
        .filter(source => source.status === 'active')
      
      const syncPromises = activeSources.map(async (source) => {
        try {
          if (source.type === 'api' && source.url) {
            await loadDataFromAPI(source.id)
          } else if (source.type === 'file' && source.filePath) {
            await loadDataFromFile(source.id, source.filePath)
          }
        } catch (error) {
          console.error(`同步數據源失敗: ${source.name}`, error)
        }
      })
      
      await Promise.allSettled(syncPromises)
      
      state.value.lastSyncTime = new Date().toISOString()
      
      console.log(`數據同步完成，處理了 ${activeSources.length} 個數據源`)
      
    } catch (error) {
      console.error('數據同步失敗:', error)
      state.value.updateError = error instanceof Error ? error.message : '同步失敗'
    } finally {
      state.value.syncInProgress = false
    }
  }
  
  const startAutoSync = (): void => {
    if (syncTimer.value) return
    
    syncTimer.value = setInterval(async () => {
      if (state.value.autoSyncEnabled && !state.value.syncInProgress) {
        await syncAllData()
      }
    }, state.value.syncInterval)
    
    console.log(`啟動自動同步，間隔: ${state.value.syncInterval}ms`)
  }
  
  const stopAutoSync = (): void => {
    if (syncTimer.value) {
      clearInterval(syncTimer.value)
      syncTimer.value = null
      console.log('停止自動同步')
    }
  }
  
  // 緩存管理
  const updateCacheSize = (): void => {
    let totalSize = 0
    state.value.datasets.forEach(dataset => {
      if (dataset.cached) {
        totalSize += dataset.size
      }
    })
    state.value.cacheSize = totalSize
  }
  
  const clearCache = (): void => {
    state.value.datasets.forEach((dataset, id) => {
      if (dataset.cached) {
        state.value.datasets.delete(id)
      }
    })
    
    state.value.cacheSize = 0
    
    appStore.addNotification({
      type: 'success',
      title: '緩存已清理',
      message: '所有緩存數據已清除'
    })
    
    console.log('數據緩存已清理')
  }
  
  const optimizeCache = (): void => {
    if (state.value.cacheSize <= state.value.maxCacheSize) return
    
    // 按最後更新時間排序，移除最舊的數據
    const datasets = Array.from(state.value.datasets.entries())
      .sort(([, a], [, b]) => new Date(a.lastUpdate).getTime() - new Date(b.lastUpdate).getTime())
    
    let freedSize = 0
    for (const [id, dataset] of datasets) {
      if (state.value.cacheSize - freedSize <= state.value.maxCacheSize * 0.8) break
      
      state.value.datasets.delete(id)
      freedSize += dataset.size
      console.log(`移除過期數據集: ${dataset.name}`)
    }
    
    updateCacheSize()
    console.log(`緩存優化完成，釋放空間: ${formatBytes(freedSize)}`)
  }
  
  // 工具函數
  const generateId = (prefix: string): string => {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  const calculateDataSize = (data: any[]): number => {
    return JSON.stringify(data).length * 2 // 估算字節大小
  }
  
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  
  const inferSchema = (data: any[]): Record<string, string> => {
    if (data.length === 0) return {}
    
    const sample = data[0]
    const schema: Record<string, string> = {}
    
    Object.keys(sample).forEach(key => {
      const value = sample[key]
      if (typeof value === 'number') {
        schema[key] = 'number'
      } else if (typeof value === 'boolean') {
        schema[key] = 'boolean'
      } else if (value instanceof Date) {
        schema[key] = 'date'
      } else {
        schema[key] = 'string'
      }
    })
    
    return schema
  }
  
  const parseCSV = (content: string): any[] => {
    const lines = content.trim().split('\n')
    if (lines.length < 2) return []
    
    const headers = lines[0].split(',').map(h => h.trim())
    const data = []
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      const row: any = {}
      
      headers.forEach((header, index) => {
        const value = values[index] || ''
        // 嘗試轉換數字
        if (!isNaN(Number(value)) && value !== '') {
          row[header] = Number(value)
        } else {
          row[header] = value
        }
      })
      
      data.push(row)
    }
    
    return data
  }
  
  const addUpdateEvent = (event: DataUpdateEvent): void => {
    state.value.updateEvents.push(event)
    
    // 限制事件歷史長度
    if (state.value.updateEvents.length > 100) {
      state.value.updateEvents = state.value.updateEvents.slice(-100)
    }
  }
  
  const notifyDataUpdate = (datasetId: string, data: any[]): void => {
    // 通知相關組件數據已更新
    const event = new CustomEvent('dataset-updated', {
      detail: { datasetId, data, timestamp: Date.now() }
    })
    document.dispatchEvent(event)
  }
  
  // 初始化和清理
  const initialize = (): void => {
    console.log('初始化數據管理系統')
    
    // 啟動自動同步
    if (state.value.autoSyncEnabled) {
      startAutoSync()
    }
    
    // 定期清理緩存
    updateTimer.value = setInterval(() => {
      optimizeCache()
    }, 300000) // 每5分鐘檢查一次
  }
  
  const destroy = (): void => {
    console.log('銷毀數據管理系統')
    
    stopAutoSync()
    
    if (updateTimer.value) {
      clearInterval(updateTimer.value)
      updateTimer.value = null
    }
    
    // 清理所有實時監聽器
    state.value.dataSources.forEach((source) => {
      disableRealtimeUpdates(source.id)
    })
    
    state.value.dataSources.clear()
    state.value.datasets.clear()
    state.value.updateEvents = []
  }
  
  return {
    // 狀態
    state: readonly(state),
    
    // 計算屬性
    activeSources,
    totalDatasets,
    cacheUsagePercent,
    recentEvents,
    
    // 數據源管理
    addDataSource,
    removeDataSource,
    updateDataSource,
    
    // 數據集管理
    createDataset,
    updateDataset,
    deleteDataset,
    
    // 數據加載
    loadDataFromAPI,
    loadDataFromFile,
    
    // 實時更新
    enableRealtimeUpdates,
    disableRealtimeUpdates,
    
    // 數據同步
    syncAllData,
    startAutoSync,
    stopAutoSync,
    
    // 緩存管理
    clearCache,
    optimizeCache,
    
    // 系統管理
    initialize,
    destroy,
    
    // 數據訪問
    getDataSource: (id: string) => state.value.dataSources.get(id),
    getDataset: (id: string) => state.value.datasets.get(id),
    getAllDataSources: () => Array.from(state.value.dataSources.values()),
    getAllDatasets: () => Array.from(state.value.datasets.values()),
    
    // 配置
    setAutoSync: (enabled: boolean) => { state.value.autoSyncEnabled = enabled },
    setSyncInterval: (interval: number) => { state.value.syncInterval = interval },
    setCacheEnabled: (enabled: boolean) => { state.value.cacheEnabled = enabled }
  }
})