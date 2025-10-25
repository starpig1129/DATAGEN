import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type {
  MessageSelectionState,
  
  SelectionConfig
} from '@/types/chat'
import { BulkActionType } from '@/types/chat'

export const useSelectionStore = defineStore('selection', () => {
  // 選擇狀態
  const selectedIds = ref<Set<string>>(new Set())
  const isInSelectionMode = ref(false)
  const lastSelectedId = ref<string | undefined>()

  // 選擇配置
  const config = ref<SelectionConfig>({
    maxSelections: undefined,
    allowMultiSelect: true,
    showSelectAll: true,
    enableBulkActions: true,
    availableActions: [
      BulkActionType.COPY,
      BulkActionType.EXPORT,
      BulkActionType.DELETE,
      BulkActionType.ARCHIVE
    ]
  })

  // 計算屬性
  const selectionState = computed<MessageSelectionState>(() => ({
    selectedIds: selectedIds.value,
    isInSelectionMode: isInSelectionMode.value,
    lastSelectedId: lastSelectedId.value
  }))

  const selectedCount = computed(() => selectedIds.value.size)
  const hasSelections = computed(() => selectedCount.value > 0)
  const isAtMaxSelections = computed(() => {
    if (!config.value.maxSelections) return false
    return selectedCount.value >= config.value.maxSelections
  })

  const canSelectMore = computed(() => {
    if (!config.value.maxSelections) return true
    return selectedCount.value < config.value.maxSelections
  })

  // 方法
  const enterSelectionMode = (): void => {
    isInSelectionMode.value = true
    selectedIds.value.clear()
    lastSelectedId.value = undefined
  }

  const exitSelectionMode = (): void => {
    isInSelectionMode.value = false
    selectedIds.value.clear()
    lastSelectedId.value = undefined
  }

  const toggleSelection = (messageId: string): void => {
    if (!isInSelectionMode.value) {
      enterSelectionMode()
    }

    if (selectedIds.value.has(messageId)) {
      selectedIds.value.delete(messageId)
      if (lastSelectedId.value === messageId) {
        lastSelectedId.value = undefined
      }
    } else {
      if (!canSelectMore.value) {
        console.warn('已達到最大選擇數量限制')
        return
      }
      selectedIds.value.add(messageId)
      lastSelectedId.value = messageId
    }
  }

  const selectMessage = (messageId: string): void => {
    if (!isInSelectionMode.value) {
      enterSelectionMode()
    }

    if (!canSelectMore.value) {
      console.warn('已達到最大選擇數量限制')
      return
    }

    selectedIds.value.add(messageId)
    lastSelectedId.value = messageId
  }

  const deselectMessage = (messageId: string): void => {
    selectedIds.value.delete(messageId)
    if (lastSelectedId.value === messageId) {
      lastSelectedId.value = undefined
    }
  }

  const selectAll = (messageIds: string[]): void => {
    if (!config.value.showSelectAll) return

    selectedIds.value.clear()

    const maxToSelect = config.value.maxSelections || messageIds.length
    const idsToSelect = messageIds.slice(0, maxToSelect)

    idsToSelect.forEach(id => selectedIds.value.add(id))
    lastSelectedId.value = idsToSelect[idsToSelect.length - 1]
  }

  const clearSelection = (): void => {
    selectedIds.value.clear()
    lastSelectedId.value = undefined
  }

  const isSelected = (messageId: string): boolean => {
    return selectedIds.value.has(messageId)
  }

  const performBulkAction = async (action: BulkActionType): Promise<boolean> => {
    if (!hasSelections.value) {
      console.warn('沒有選中的消息')
      return false
    }

    try {
      switch (action) {
        case BulkActionType.COPY:
          return await copySelectedMessages()
        case BulkActionType.DELETE:
          return await deleteSelectedMessages()
        case BulkActionType.EXPORT:
          return await exportSelectedMessages()
        case BulkActionType.ARCHIVE:
          return await archiveSelectedMessages()
        default:
          console.warn('未知的批量操作類型:', action)
          return false
      }
    } catch (error) {
      console.error('執行批量操作失敗:', error)
      return false
    }
  }

  // 私有方法
  const copySelectedMessages = async (): Promise<boolean> => {
    const selectedMessages = Array.from(selectedIds.value)
    const textToCopy = selectedMessages.join(', ')

    try {
      await navigator.clipboard.writeText(textToCopy)
      console.log('已複製選中的消息ID:', selectedMessages)
      return true
    } catch (error) {
      console.error('複製失敗:', error)
      return false
    }
  }

  const deleteSelectedMessages = async (): Promise<boolean> => {
    // 這裡應該調用實際的刪除API
    console.log('刪除選中的消息:', Array.from(selectedIds.value))
    selectedIds.value.clear()
    lastSelectedId.value = undefined
    return true
  }

  const exportSelectedMessages = async (): Promise<boolean> => {
    // 這裡應該實現導出功能
    console.log('導出選中的消息:', Array.from(selectedIds.value))
    return true
  }

  const archiveSelectedMessages = async (): Promise<boolean> => {
    // 這裡應該實現歸檔功能
    console.log('歸檔選中的消息:', Array.from(selectedIds.value))
    return true
  }

  const updateConfig = (newConfig: Partial<SelectionConfig>): void => {
    config.value = { ...config.value, ...newConfig }
  }

  return {
    // 狀態
    selectedIds: readonly(selectedIds),
    isInSelectionMode: readonly(isInSelectionMode),
    lastSelectedId: readonly(lastSelectedId),

    // 計算屬性
    selectionState,
    selectedCount,
    hasSelections,
    isAtMaxSelections,
    canSelectMore,

    // 配置
    config: readonly(config),

    // 方法
    enterSelectionMode,
    exitSelectionMode,
    toggleSelection,
    selectMessage,
    deselectMessage,
    selectAll,
    clearSelection,
    isSelected,
    performBulkAction,
    updateConfig
  }
})