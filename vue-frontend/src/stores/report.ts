/**
 * 報告管理 Store
 * 基於 Pinia 和 Vue 3 Composition API
 */

import { defineStore } from 'pinia';
import { ref, computed, readonly } from 'vue';
import type {
  Report,
  ReportBlock,
  ReportTemplate,
  ReportListItem,
  ExportOptions,
  ReportStyle,
  ReportMetadata,
  ReportApiResponse,
} from '@/types/report';

/** Store 狀態介面 */
interface ReportState {
  currentReport: Report | null;
  reportList: ReportListItem[];
  templates: ReportTemplate[];
  isLoading: boolean;
  isSaving: boolean;
  isExporting: boolean;
  error: string | null;
  lastSaved: string | null;
  autoSaveEnabled: boolean;
}

/** 預設報告樣式 */
const defaultStyle: ReportStyle = {
  theme: 'default',
  fontFamily: 'Arial, sans-serif',
  fontSize: 14,
  lineHeight: 1.6,
  margins: {
    top: 2.54,
    right: 2.54,
    bottom: 2.54,
    left: 2.54,
  },
  colors: {
    primary: '#409eff',
    secondary: '#67c23a',
    text: '#303133',
    background: '#ffffff',
    border: '#dcdfe6',
  },
  pageSize: 'A4',
  orientation: 'portrait',
};

/** 預設報告元數據 */
const createDefaultMetadata = (): ReportMetadata => ({
  title: '未命名報告',
  author: '系統用戶',
  description: '',
  tags: [],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  version: 1,
  language: 'zh-TW',
  template: 'default',
});

export const useReportStore = defineStore('report', () => {
  // ===== 響應式狀態 =====
  const state = ref<ReportState>({
    currentReport: null,
    reportList: [],
    templates: [],
    isLoading: false,
    isSaving: false,
    isExporting: false,
    error: null,
    lastSaved: null,
    autoSaveEnabled: true,
  });

  // ===== 計算屬性 =====
  const hasUnsavedChanges = computed(() => {
    if (!state.value.currentReport || !state.value.lastSaved) {
      return false;
    }
    return state.value.currentReport.metadata.updatedAt > state.value.lastSaved;
  });

  const canExport = computed(() => {
    return state.value.currentReport && state.value.currentReport.blocks.length > 0;
  });

  const reportCount = computed(() => state.value.reportList.length);

  // ===== 報告操作方法 =====

  /**
   * 創建新報告
   */
  const createNewReport = (template?: ReportTemplate): Report => {
    const id = `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const newReport: Report = {
      id,
      metadata: createDefaultMetadata(),
      style: template?.style || { ...defaultStyle },
      blocks: template?.defaultBlocks.map((block, index) => ({
        ...block,
        id: `block_${Date.now()}_${index}`,
        order: index,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      })) as ReportBlock[] || [],
      tableOfContents: false,
      pageNumbers: true,
    };

    if (template) {
      newReport.metadata.template = template.id;
      newReport.metadata.title = `基於 ${template.name} 的報告`;
    }

    state.value.currentReport = newReport;
    state.value.error = null;
    
    return newReport;
  };

  /**
   * 載入報告
   */
  const loadReport = async (reportId: string): Promise<void> => {
    state.value.isLoading = true;
    state.value.error = null;

    try {
      // 這裡應該調用 API 載入報告
      // const response = await api.getReport(reportId);
      
      // 模擬 API 響應
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 暫時使用模擬數據
      const mockReport: Report = {
        id: reportId,
        metadata: {
          ...createDefaultMetadata(),
          title: '示例報告',
          description: '這是一個示例報告',
        },
        style: { ...defaultStyle },
        blocks: [],
        tableOfContents: true,
        pageNumbers: true,
      };

      state.value.currentReport = mockReport;
      state.value.lastSaved = new Date().toISOString();
    } catch (error) {
      state.value.error = error instanceof Error ? error.message : '載入報告失敗';
      console.error('載入報告失敗:', error);
    } finally {
      state.value.isLoading = false;
    }
  };

  /**
   * 保存報告
   */
  const saveReport = async (): Promise<boolean> => {
    if (!state.value.currentReport) {
      state.value.error = '沒有要保存的報告';
      return false;
    }

    state.value.isSaving = true;
    state.value.error = null;

    try {
      // 更新元數據
      state.value.currentReport.metadata.updatedAt = new Date().toISOString();
      state.value.currentReport.metadata.version += 1;

      // 這裡應該調用 API 保存報告
      // const response = await api.saveReport(state.value.currentReport);
      
      // 模擬 API 響應
      await new Promise(resolve => setTimeout(resolve, 1000));

      state.value.lastSaved = new Date().toISOString();
      
      // 更新報告列表
      const existingIndex = state.value.reportList.findIndex(
        item => item.id === state.value.currentReport!.id
      );
      
      const listItem: ReportListItem = {
        id: state.value.currentReport.id,
        title: state.value.currentReport.metadata.title,
        author: state.value.currentReport.metadata.author,
        description: state.value.currentReport.metadata.description,
        createdAt: state.value.currentReport.metadata.createdAt,
        updatedAt: state.value.currentReport.metadata.updatedAt,
        status: 'draft',
        tags: state.value.currentReport.metadata.tags,
      };

      if (existingIndex >= 0) {
        state.value.reportList[existingIndex] = listItem;
      } else {
        state.value.reportList.unshift(listItem);
      }

      return true;
    } catch (error) {
      state.value.error = error instanceof Error ? error.message : '保存報告失敗';
      console.error('保存報告失敗:', error);
      return false;
    } finally {
      state.value.isSaving = false;
    }
  };

  /**
   * 刪除報告
   */
  const deleteReport = async (reportId: string): Promise<boolean> => {
    try {
      // 這裡應該調用 API 刪除報告
      // await api.deleteReport(reportId);
      
      // 模擬 API 響應
      await new Promise(resolve => setTimeout(resolve, 300));

      // 從列表中移除
      state.value.reportList = state.value.reportList.filter(
        item => item.id !== reportId
      );

      // 如果刪除的是當前報告，清空當前報告
      if (state.value.currentReport?.id === reportId) {
        state.value.currentReport = null;
        state.value.lastSaved = null;
      }

      return true;
    } catch (error) {
      state.value.error = error instanceof Error ? error.message : '刪除報告失敗';
      console.error('刪除報告失敗:', error);
      return false;
    }
  };

  // ===== 報告塊操作方法 =====

  /**
   * 添加報告塊
   */
  const addBlock = (blockType: ReportBlock['type'], insertAfter?: string): string => {
    if (!state.value.currentReport) {
      throw new Error('沒有活動的報告');
    }

    const blockId = `block_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const now = new Date().toISOString();
    
    let order = 0;
    if (insertAfter) {
      const afterBlock = state.value.currentReport.blocks.find(b => b.id === insertAfter);
      if (afterBlock) {
        order = afterBlock.order + 1;
        // 更新後續塊的順序
        state.value.currentReport.blocks
          .filter(b => b.order > afterBlock.order)
          .forEach(b => b.order += 1);
      }
    } else {
      order = state.value.currentReport.blocks.length;
    }

    // 創建基礎塊結構
    const baseBlock = {
      id: blockId,
      type: blockType,
      order,
      createdAt: now,
      updatedAt: now,
    };

    // 根據類型創建具體的塊
    let newBlock: ReportBlock;
    switch (blockType) {
      case 'text':
        newBlock = { ...baseBlock, type: 'text', content: '' };
        break;
      case 'heading':
        newBlock = { ...baseBlock, type: 'heading', content: '', level: 2 };
        break;
      case 'image':
        newBlock = { ...baseBlock, type: 'image', src: '', alt: '' };
        break;
      case 'chart':
        newBlock = { ...baseBlock, type: 'chart', chartId: '', chartType: '' };
        break;
      case 'table':
        newBlock = { ...baseBlock, type: 'table', headers: ['欄位1'], rows: [['資料1']] };
        break;
      case 'divider':
        newBlock = { ...baseBlock, type: 'divider' };
        break;
      case 'code':
        newBlock = { ...baseBlock, type: 'code', content: '' };
        break;
      case 'quote':
        newBlock = { ...baseBlock, type: 'quote', content: '' };
        break;
      default:
        throw new Error(`不支援的塊類型: ${blockType}`);
    }

    state.value.currentReport.blocks.push(newBlock);
    state.value.currentReport.blocks.sort((a, b) => a.order - b.order);
    state.value.currentReport.metadata.updatedAt = now;

    return blockId;
  };

  /**
   * 更新報告塊
   */
  const updateBlock = (blockId: string, updates: Partial<ReportBlock>): void => {
    if (!state.value.currentReport) {
      throw new Error('沒有活動的報告');
    }

    const blockIndex = state.value.currentReport.blocks.findIndex(b => b.id === blockId);
    if (blockIndex === -1) {
      throw new Error(`找不到塊: ${blockId}`);
    }

    const updatedBlock = {
      ...state.value.currentReport.blocks[blockIndex],
      ...updates,
      id: blockId, // 確保 ID 不被覆蓋
      updatedAt: new Date().toISOString(),
    };

    state.value.currentReport.blocks[blockIndex] = updatedBlock as ReportBlock;
    state.value.currentReport.metadata.updatedAt = new Date().toISOString();
  };

  /**
   * 刪除報告塊
   */
  const deleteBlock = (blockId: string): void => {
    if (!state.value.currentReport) {
      throw new Error('沒有活動的報告');
    }

    const blockIndex = state.value.currentReport.blocks.findIndex(b => b.id === blockId);
    if (blockIndex === -1) {
      throw new Error(`找不到塊: ${blockId}`);
    }

    const deletedBlock = state.value.currentReport.blocks[blockIndex];
    state.value.currentReport.blocks.splice(blockIndex, 1);

    // 更新後續塊的順序
    state.value.currentReport.blocks
      .filter(b => b.order > deletedBlock.order)
      .forEach(b => b.order -= 1);

    state.value.currentReport.metadata.updatedAt = new Date().toISOString();
  };

  /**
   * 移動報告塊
   */
  const moveBlock = (blockId: string, newOrder: number): void => {
    if (!state.value.currentReport) {
      throw new Error('沒有活動的報告');
    }

    const block = state.value.currentReport.blocks.find(b => b.id === blockId);
    if (!block) {
      throw new Error(`找不到塊: ${blockId}`);
    }

    const oldOrder = block.order;
    const maxOrder = state.value.currentReport.blocks.length - 1;
    const targetOrder = Math.max(0, Math.min(newOrder, maxOrder));

    if (oldOrder === targetOrder) {
      return;
    }

    // 更新其他塊的順序
    if (oldOrder < targetOrder) {
      // 向下移動
      state.value.currentReport.blocks
        .filter(b => b.order > oldOrder && b.order <= targetOrder)
        .forEach(b => b.order -= 1);
    } else {
      // 向上移動
      state.value.currentReport.blocks
        .filter(b => b.order >= targetOrder && b.order < oldOrder)
        .forEach(b => b.order += 1);
    }

    block.order = targetOrder;
    block.updatedAt = new Date().toISOString();

    // 重新排序塊
    state.value.currentReport.blocks.sort((a, b) => a.order - b.order);
    state.value.currentReport.metadata.updatedAt = new Date().toISOString();
  };

  // ===== 導出功能 =====

  /**
   * 導出報告
   */
  const exportReport = async (options: ExportOptions): Promise<Blob | null> => {
    if (!state.value.currentReport) {
      state.value.error = '沒有要導出的報告';
      return null;
    }

    state.value.isExporting = true;
    state.value.error = null;

    try {
      // 這裡應該調用 API 或執行實際的導出邏輯
      // const blob = await exportService.exportReport(state.value.currentReport, options);
      
      // 模擬導出過程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 創建模擬的 blob
      const content = `模擬導出的 ${options.format.toUpperCase()} 檔案內容`;
      const blob = new Blob([content], { 
        type: options.format === 'pdf' ? 'application/pdf' : 'text/plain' 
      });

      return blob;
    } catch (error) {
      state.value.error = error instanceof Error ? error.message : '導出報告失敗';
      console.error('導出報告失敗:', error);
      return null;
    } finally {
      state.value.isExporting = false;
    }
  };

  // ===== 模板管理 =====

  /**
   * 載入報告模板
   */
  const loadTemplates = async (): Promise<void> => {
    state.value.isLoading = true;
    
    try {
      // 這裡應該從 API 載入模板
      // const templates = await api.getReportTemplates();
      
      // 模擬模板數據
      const mockTemplates: ReportTemplate[] = [
        {
          id: 'academic',
          name: '學術報告',
          description: '適用於學術論文和研究報告',
          category: 'academic',
          preview: '/templates/academic-preview.png',
          style: { ...defaultStyle, theme: 'academic' },
          defaultBlocks: [
            { type: 'heading', content: '摘要', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '引言', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '方法', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '結果', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '討論', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '結論', level: 1 },
            { type: 'text', content: '' },
          ],
        },
        {
          id: 'business',
          name: '商業報告',
          description: '適用於商業分析和項目報告',
          category: 'business',
          preview: '/templates/business-preview.png',
          style: { ...defaultStyle, theme: 'business' },
          defaultBlocks: [
            { type: 'heading', content: '執行摘要', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '市場分析', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '財務預測', level: 1 },
            { type: 'chart', chartId: '', chartType: 'line' },
            { type: 'heading', content: '建議', level: 1 },
            { type: 'text', content: '' },
          ],
        },
        {
          id: 'technical',
          name: '技術報告',
          description: '適用於技術文檔和系統分析',
          category: 'technical',
          preview: '/templates/technical-preview.png',
          style: { ...defaultStyle, theme: 'minimal' },
          defaultBlocks: [
            { type: 'heading', content: '概述', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '系統架構', level: 1 },
            { type: 'text', content: '' },
            { type: 'heading', content: '實現細節', level: 1 },
            { type: 'code', content: '', language: 'javascript' },
            { type: 'heading', content: '測試結果', level: 1 },
            { type: 'table', headers: ['測試項目', '結果', '備註'], rows: [['', '', '']] },
          ],
        },
      ];

      state.value.templates = mockTemplates;
    } catch (error) {
      state.value.error = error instanceof Error ? error.message : '載入模板失敗';
      console.error('載入模板失敗:', error);
    } finally {
      state.value.isLoading = false;
    }
  };

  // ===== 工具方法 =====

  /**
   * 清除錯誤
   */
  const clearError = (): void => {
    state.value.error = null;
  };

  /**
   * 重置 store
   */
  const resetStore = (): void => {
    state.value.currentReport = null;
    state.value.reportList = [];
    state.value.templates = [];
    state.value.isLoading = false;
    state.value.isSaving = false;
    state.value.isExporting = false;
    state.value.error = null;
    state.value.lastSaved = null;
    state.value.autoSaveEnabled = true;
  };

  // ===== 返回公共 API =====
  return {
    // 唯讀狀態
    currentReport: readonly(computed(() => state.value.currentReport)),
    reportList: readonly(computed(() => state.value.reportList)),
    templates: readonly(computed(() => state.value.templates)),
    isLoading: readonly(computed(() => state.value.isLoading)),
    isSaving: readonly(computed(() => state.value.isSaving)),
    isExporting: readonly(computed(() => state.value.isExporting)),
    error: readonly(computed(() => state.value.error)),
    lastSaved: readonly(computed(() => state.value.lastSaved)),
    autoSaveEnabled: readonly(computed(() => state.value.autoSaveEnabled)),
    
    // 計算屬性
    hasUnsavedChanges,
    canExport,
    reportCount,
    
    // 方法
    createNewReport,
    loadReport,
    saveReport,
    deleteReport,
    addBlock,
    updateBlock,
    deleteBlock,
    moveBlock,
    exportReport,
    loadTemplates,
    clearError,
    resetStore,
  };
});