<template>
  <div class="report-generator">
    <!-- 頁面標題和工具欄 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">報告生成器</h1>
          <p class="page-description">
            專業的報告編輯和生成工具，支援富文本、圖表和多種導出格式
          </p>
        </div>
        <div class="header-actions">
          <el-button
            v-if="currentReport"
            :loading="isSaving"
            type="primary"
            :icon="Document"
            @click="handleSaveReport"
          >
            {{ isSaving ? '保存中...' : '保存報告' }}
          </el-button>
          <el-button
            v-if="canExport"
            :loading="isExporting"
            :icon="Download"
            @click="showExportDialog = true"
          >
            {{ isExporting ? '導出中...' : '導出報告' }}
          </el-button>
          <el-button
            :icon="Plus"
            @click="showNewReportDialog = true"
          >
            新建報告
          </el-button>
        </div>
      </div>
      
      <!-- 自動保存指示器 -->
      <div v-if="currentReport" class="auto-save-indicator">
        <el-icon v-if="hasUnsavedChanges" class="unsaved-icon">
          <Warning />
        </el-icon>
        <span class="save-status">
          {{ hasUnsavedChanges ? '有未保存的變更' : '已保存' }}
        </span>
        <span v-if="lastSaved" class="last-saved">
          最後保存: {{ formatDateTime(lastSaved) }}
        </span>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="main-content">
      <!-- 側邊欄 - 報告列表和工具 -->
      <div class="sidebar">
        <!-- 報告列表 -->
        <div class="sidebar-section">
          <div class="section-header">
            <h3>我的報告</h3>
            <el-button
              size="small"
              type="text"
              :icon="Refresh"
              @click="loadReportList"
            >
              刷新
            </el-button>
          </div>
          <div class="report-list">
            <div
              v-for="report in reportList"
              :key="report.id"
              class="report-item"
              :class="{ active: currentReport?.id === report.id }"
              @click="loadSelectedReport(report.id)"
            >
              <div class="report-info">
                <h4 class="report-title">{{ report.title }}</h4>
                <p class="report-meta">
                  {{ formatDateTime(report.updatedAt) }}
                </p>
                <div class="report-tags">
                  <el-tag
                    v-for="tag in report.tags"
                    :key="tag"
                    size="small"
                    type="info"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
              <div class="report-actions">
                <el-button
                  size="small"
                  type="text"
                  :icon="Delete"
                  @click.stop="handleDeleteReport(report.id)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 塊工具箱 -->
        <div class="sidebar-section">
          <div class="section-header">
            <h3>內容塊</h3>
          </div>
          <div class="block-tools">
            <el-button
              v-for="blockType in blockTypes"
              :key="blockType.type"
              class="block-tool"
              :icon="blockType.icon"
              @click="handleAddBlock(blockType.type)"
            >
              {{ blockType.label }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 報告編輯區域 -->
      <div class="editor-area">
        <div v-if="!currentReport" class="no-report">
          <el-empty description="請選擇或創建一個報告開始編輯">
            <el-button type="primary" @click="showNewReportDialog = true">
              創建新報告
            </el-button>
          </el-empty>
        </div>

        <div v-else class="report-editor">
          <!-- 報告元數據編輯 -->
          <div class="metadata-section">
            <el-form :model="reportMetadata" label-width="80px">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="標題">
                    <el-input
                      v-model="reportMetadata.title"
                      placeholder="輸入報告標題"
                      @change="updateReportMetadata"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="作者">
                    <el-input
                      v-model="reportMetadata.author"
                      placeholder="輸入作者姓名"
                      @change="updateReportMetadata"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="描述">
                <el-input
                  v-model="reportMetadata.description"
                  type="textarea"
                  :rows="2"
                  placeholder="輸入報告描述"
                  @change="updateReportMetadata"
                />
              </el-form-item>
              <el-form-item label="標籤">
                <el-tag
                  v-for="tag in reportMetadata.tags"
                  :key="tag"
                  closable
                  @close="removeTag(tag)"
                >
                  {{ tag }}
                </el-tag>
                <el-input
                  v-if="showTagInput"
                  ref="tagInputRef"
                  v-model="newTag"
                  size="small"
                  style="width: 100px"
                  @keyup.enter="addTag"
                  @blur="addTag"
                />
                <el-button
                  v-else
                  size="small"
                  @click="showAddTag"
                >
                  + 新標籤
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 報告內容編輯 -->
          <div class="content-section">
            <div
              v-for="(block, index) in sortedBlocks"
              :key="block.id"
              class="block-container"
              :class="{ active: selectedBlockId === block.id }"
              @click="selectBlock(block.id)"
            >
              <!-- 塊工具欄 -->
              <div class="block-toolbar">
                <div class="block-info">
                  <span class="block-type">{{ getBlockTypeLabel(block.type) }}</span>
                  <span class="block-order">#{{ index + 1 }}</span>
                </div>
                <div class="block-actions">
                  <el-button
                    size="small"
                    type="text"
                    :icon="ArrowUp"
                    :disabled="index === 0"
                    @click.stop="moveBlockUp(block.id)"
                  />
                  <el-button
                    size="small"
                    type="text"
                    :icon="ArrowDown"
                    :disabled="index === sortedBlocks.length - 1"
                    @click.stop="moveBlockDown(block.id)"
                  />
                  <el-button
                    size="small"
                    type="text"
                    :icon="Delete"
                    @click.stop="handleDeleteBlock(block.id)"
                  />
                </div>
              </div>

              <!-- Block content editor -->
              <div class="block-content">
                <component
                  :is="getBlockComponent(block.type)"
                  v-bind="{ block, isSelected: selectedBlockId === block.id } as any"
                  @update="updateBlockContent"
                />
              </div>
            </div>

            <!-- 添加新塊按鈕 -->
            <div class="add-block-section">
              <el-button
                type="default"
                :icon="Plus"
                @click="showBlockSelector = !showBlockSelector"
              >
                添加內容塊
              </el-button>
              
              <div v-if="showBlockSelector" class="block-selector">
                <el-button
                  v-for="blockType in blockTypes"
                  :key="blockType.type"
                  size="small"
                  :icon="blockType.icon"
                  @click="handleAddBlock(blockType.type)"
                >
                  {{ blockType.label }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 預覽面板 -->
      <div class="preview-panel" :class="{ collapsed: !showPreview }">
        <div class="panel-header">
          <h3>預覽</h3>
          <el-button
            size="small"
            type="text"
            :icon="showPreview ? Fold : Expand"
            @click="showPreview = !showPreview"
          />
        </div>
        <div v-if="showPreview" class="preview-content">
          <ReportPreview
            v-if="currentReport"
            :report="currentReport"
          />
        </div>
      </div>
    </div>

    <!-- 新建報告對話框 -->
    <NewReportDialog
      v-model="showNewReportDialog"
      :templates="templates"
      @create="handleCreateReport"
    />

    <!-- 導出對話框 -->
    <ExportDialog
      v-model="showExportDialog"
      :report="currentReport"
      @export="handleExportReport"
    />

    <!-- 錯誤提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      :closable="true"
      @close="clearError"
      class="error-alert"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Document,
  Download,
  Plus,
  Warning,
  Refresh,
  Delete,
  ArrowUp,
  ArrowDown,
  Fold,
  Expand,
  Edit,
  Picture,
  DataLine,
  Grid,
  Minus,
  CopyDocument,
  ChatDotSquare,
} from '@element-plus/icons-vue';
import { useReportStore } from '@/stores/report';
import type { ReportBlock, ReportTemplate } from '@/types/report';
import { defineAsyncComponent } from 'vue';
import { formatDateTime } from '@/utils/date';

// 組件導入 - 懶加載以提升性能
const ReportPreview = defineAsyncComponent(() => import('@/components/report/ReportPreview.vue'));
const NewReportDialog = defineAsyncComponent(() => import('@/components/report/NewReportDialog.vue'));
const ExportDialog = defineAsyncComponent(() => import('@/components/report/ExportDialog.vue'));

// 塊編輯器組件
const TextBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/TextBlockEditor.vue'));
const HeadingBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/HeadingBlockEditor.vue'));
const ImageBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/ImageBlockEditor.vue'));
const ChartBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/ChartBlockEditor.vue'));
const TableBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/TableBlockEditor.vue'));
const DividerBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/DividerBlockEditor.vue'));
const CodeBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/CodeBlockEditor.vue'));
const QuoteBlockEditor = defineAsyncComponent(() => import('@/components/report/blocks/QuoteBlockEditor.vue'));

// Store
const reportStore = useReportStore();

// 響應式狀態
const showNewReportDialog = ref(false);
const showExportDialog = ref(false);
const showPreview = ref(true);
const showBlockSelector = ref(false);
const showTagInput = ref(false);
const newTag = ref('');
const selectedBlockId = ref<string | null>(null);
const tagInputRef = ref<HTMLInputElement>();

// 計算屬性 - 從 store 獲取
const currentReport = computed(() => reportStore.currentReport);
const reportList = computed(() => reportStore.reportList);
const templates = computed(() => reportStore.templates);
// const _isLoading = computed(() => reportStore.isLoading);  // Reserved for loading indicator
const isSaving = computed(() => reportStore.isSaving);
const isExporting = computed(() => reportStore.isExporting);
const error = computed(() => reportStore.error);
const lastSaved = computed(() => reportStore.lastSaved);
const hasUnsavedChanges = computed(() => reportStore.hasUnsavedChanges);
const canExport = computed(() => reportStore.canExport);

// 報告元數據的響應式副本
const reportMetadata = ref({
  title: '',
  author: '',
  description: '',
  tags: [] as string[],
  createdAt: '',
  updatedAt: '',
  version: 1,
  language: 'zh-TW',
  template: '',
});

// 監聽當前報告變化，同步元數據
watch(currentReport, (newReport) => {
  if (newReport?.metadata) {
    reportMetadata.value = {
      title: newReport.metadata.title,
      author: newReport.metadata.author,
      description: newReport.metadata.description || '',
      tags: [...newReport.metadata.tags],
      createdAt: newReport.metadata.createdAt,
      updatedAt: newReport.metadata.updatedAt,
      version: newReport.metadata.version,
      language: newReport.metadata.language,
      template: newReport.metadata.template || '',
    };
  }
}, { immediate: true, deep: true });

// 排序後的塊列表
const sortedBlocks = computed(() => {
  if (!currentReport.value) return [];
  return [...currentReport.value.blocks].sort((a, b) => a.order - b.order);
});

// 塊類型配置
const blockTypes = [
  { type: 'text', label: '文本', icon: Edit },
  { type: 'heading', label: '標題', icon: 'H' },
  { type: 'image', label: '圖片', icon: Picture },
  { type: 'chart', label: '圖表', icon: DataLine },
  { type: 'table', label: '表格', icon: Grid },
  { type: 'divider', label: '分隔線', icon: Minus },
  { type: 'code', label: '代碼', icon: CopyDocument },
  { type: 'quote', label: '引用', icon: ChatDotSquare },
] as const;

// 方法
const loadReportList = async () => {
  // 這裡可以添加載入報告列表的邏輯
  // 目前 store 已經處理了模擬數據
};

const loadSelectedReport = async (reportId: string) => {
  try {
    await reportStore.loadReport(reportId);
    selectedBlockId.value = null;
  } catch (error) {
    ElMessage.error('載入報告失敗');
  }
};

const handleCreateReport = async (template?: ReportTemplate) => {
  try {
    reportStore.createNewReport(template);
    showNewReportDialog.value = false;
    ElMessage.success('報告創建成功');
  } catch (error) {
    ElMessage.error('創建報告失敗');
  }
};

const handleSaveReport = async () => {
  const success = await reportStore.saveReport();
  if (success) {
    ElMessage.success('報告保存成功');
  } else {
    ElMessage.error('保存報告失敗');
  }
};

const handleDeleteReport = async (reportId: string) => {
  try {
    await ElMessageBox.confirm(
      '確定要刪除這個報告嗎？此操作無法撤銷。',
      '確認刪除',
      {
        type: 'warning',
        confirmButtonText: '確定刪除',
        cancelButtonText: '取消',
      }
    );

    const success = await reportStore.deleteReport(reportId);
    if (success) {
      ElMessage.success('報告刪除成功');
    } else {
      ElMessage.error('刪除報告失敗');
    }
  } catch {
    // 用戶取消操作
  }
};

const handleAddBlock = (blockType: ReportBlock['type']) => {
  try {
    const blockId = reportStore.addBlock(blockType);
    selectedBlockId.value = blockId;
    showBlockSelector.value = false;
    ElMessage.success(`${getBlockTypeLabel(blockType)} 塊已添加`);
  } catch (error) {
    ElMessage.error('添加內容塊失敗');
  }
};

const handleDeleteBlock = async (blockId: string) => {
  try {
    await ElMessageBox.confirm(
      '確定要刪除這個內容塊嗎？',
      '確認刪除',
      {
        type: 'warning',
        confirmButtonText: '確定刪除',
        cancelButtonText: '取消',
      }
    );

    reportStore.deleteBlock(blockId);
    if (selectedBlockId.value === blockId) {
      selectedBlockId.value = null;
    }
    ElMessage.success('內容塊已刪除');
  } catch {
    // 用戶取消操作
  }
};

const selectBlock = (blockId: string) => {
  selectedBlockId.value = blockId;
};

const moveBlockUp = (blockId: string) => {
  const block = sortedBlocks.value.find(b => b.id === blockId);
  if (block && block.order > 0) {
    reportStore.moveBlock(blockId, block.order - 1);
  }
};

const moveBlockDown = (blockId: string) => {
  const block = sortedBlocks.value.find(b => b.id === blockId);
  if (block && block.order < sortedBlocks.value.length - 1) {
    reportStore.moveBlock(blockId, block.order + 1);
  }
};

const updateBlockContent = (blockId: string, updates: Partial<ReportBlock>) => {
  reportStore.updateBlock(blockId, updates);
};

const updateReportMetadata = () => {
  if (currentReport.value) {
    // 直接調用 store 方法來更新報告元數據
    // 這裡需要添加一個專門更新報告元數據的方法
    // Build updated report object for future store update implementation
    // const _updatedReport = {
    //   ...currentReport.value,
    //   metadata: {
    //     ...reportMetadata.value,
    //     updatedAt: new Date().toISOString(),
    //   },
    // };
    // TODO: Implement update report metadata in store
  }
};

const addTag = () => {
  if (newTag.value && !reportMetadata.value.tags.includes(newTag.value)) {
    reportMetadata.value.tags.push(newTag.value);
    updateReportMetadata();
  }
  newTag.value = '';
  showTagInput.value = false;
};

const removeTag = (tag: string) => {
  const index = reportMetadata.value.tags.indexOf(tag);
  if (index > -1) {
    reportMetadata.value.tags.splice(index, 1);
    updateReportMetadata();
  }
};

const showAddTag = () => {
  showTagInput.value = true;
  nextTick(() => {
    tagInputRef.value?.focus();
  });
};

const handleExportReport = async (options: any) => {
  try {
    const blob = await reportStore.exportReport(options);
    if (blob) {
      // 下載檔案
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportMetadata.value.title}.${options.format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      showExportDialog.value = false;
      ElMessage.success('報告導出成功');
    }
  } catch (error) {
    ElMessage.error('導出報告失敗');
  }
};

const getBlockTypeLabel = (type: ReportBlock['type']): string => {
  const blockType = blockTypes.find(bt => bt.type === type);
  return blockType?.label || type;
};

const getBlockComponent = (type: ReportBlock['type']) => {
  switch (type) {
    case 'text': return TextBlockEditor;
    case 'heading': return HeadingBlockEditor;
    case 'image': return ImageBlockEditor;
    case 'chart': return ChartBlockEditor;
    case 'table': return TableBlockEditor;
    case 'divider': return DividerBlockEditor;
    case 'code': return CodeBlockEditor;
    case 'quote': return QuoteBlockEditor;
    default: return TextBlockEditor;
  }
};

const clearError = () => {
  reportStore.clearError();
};

// 生命週期
onMounted(async () => {
  await reportStore.loadTemplates();
  await loadReportList();
});

// 監聽路由變化以自動保存
watch(
  hasUnsavedChanges,
  (hasChanges) => {
    if (hasChanges && reportStore.autoSaveEnabled) {
      // 自動保存邏輯（可選）
      // setTimeout(() => handleSaveReport(), 5000);
    }
  }
);
</script>

<style scoped>
.report-generator {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color-page);
}

.page-header {
  padding: 16px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title-section {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 4px 0;
}

.page-description {
  color: var(--el-text-color-regular);
  margin: 0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.auto-save-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.unsaved-icon {
  color: var(--el-color-warning);
}

.save-status {
  font-weight: 500;
}

.last-saved {
  opacity: 0.7;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  overflow-y: auto;
}

.sidebar-section {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.report-list {
  max-height: 400px;
  overflow-y: auto;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.report-item:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.report-item.active {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-8);
}

.report-info {
  flex: 1;
}

.report-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.report-meta {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.report-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.report-actions {
  margin-left: 8px;
}

.block-tools {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.block-tool {
  justify-content: flex-start;
  padding: 8px 12px;
  border: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
}

.block-tool:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.editor-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.no-report {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.report-editor {
  max-width: 800px;
  margin: 0 auto;
}

.metadata-section {
  background: var(--el-bg-color);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  margin-bottom: 24px;
}

.content-section {
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
}

.block-container {
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s ease;
}

.block-container:last-child {
  border-bottom: none;
}

.block-container:hover {
  background-color: var(--el-fill-color-lighter);
}

.block-container.active {
  background-color: var(--el-color-primary-light-9);
  border-left: 3px solid var(--el-color-primary);
}

.block-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: var(--el-fill-color-extra-light);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.block-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.block-type {
  font-weight: 500;
}

.block-order {
  color: var(--el-text-color-placeholder);
}

.block-actions {
  display: flex;
  gap: 4px;
}

.block-content {
  padding: 16px;
}

.add-block-section {
  padding: 20px;
  text-align: center;
  border-top: 1px solid var(--el-border-color-lighter);
}

.block-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
}

.preview-panel {
  width: 350px;
  background: var(--el-bg-color);
  border-left: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.preview-panel.collapsed {
  width: 50px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.error-alert {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 3000;
  max-width: 400px;
}

/* 響應式設計 */
@media (max-width: 1200px) {
  .preview-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    order: 2;
    max-height: 300px;
  }
  
  .editor-area {
    order: 1;
    padding: 16px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .page-title {
    font-size: 20px;
  }
}

/* 深色主題適配 */
.dark .report-generator {
  background-color: var(--el-bg-color-page);
}

.dark .block-container:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .block-container.active {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .block-toolbar {
  background-color: rgba(255, 255, 255, 0.03);
}
</style>