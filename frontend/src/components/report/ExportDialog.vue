<template>
  <el-dialog
    v-model="dialogVisible"
    title="導出報告"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="export-dialog">
      <!-- 導出格式選擇 -->
      <div class="export-section">
        <h3>導出格式</h3>
        <el-radio-group v-model="exportOptions.format" class="format-group">
          <el-radio value="pdf" class="format-option">
            <div class="format-card">
              <el-icon class="format-icon"><Document /></el-icon>
              <div class="format-info">
                <h4>PDF</h4>
                <p>適合打印和分享</p>
              </div>
            </div>
          </el-radio>
          
          <el-radio value="docx" class="format-option">
            <div class="format-card">
              <el-icon class="format-icon"><Edit /></el-icon>
              <div class="format-info">
                <h4>Word 文檔</h4>
                <p>可進一步編輯</p>
              </div>
            </div>
          </el-radio>
          
          <el-radio value="html" class="format-option">
            <div class="format-card">
              <el-icon class="format-icon"><ChromeFilled /></el-icon>
              <div class="format-info">
                <h4>HTML</h4>
                <p>網頁格式</p>
              </div>
            </div>
          </el-radio>
          
          <el-radio value="markdown" class="format-option">
            <div class="format-card">
              <el-icon class="format-icon"><DocumentCopy /></el-icon>
              <div class="format-info">
                <h4>Markdown</h4>
                <p>純文本格式</p>
              </div>
            </div>
          </el-radio>
        </el-radio-group>
      </div>

      <!-- 導出選項 -->
      <div class="export-section">
        <h3>導出選項</h3>
        
        <el-form :model="exportOptions" label-width="120px" class="export-form">
          <el-form-item label="導出質量">
            <el-select v-model="exportOptions.quality" style="width: 200px">
              <el-option label="草稿 (快速)" value="draft" />
              <el-option label="標準" value="standard" />
              <el-option label="高質量 (較慢)" value="high" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="包含內容">
            <div class="content-options">
              <el-checkbox v-model="exportOptions.includeImages">
                包含圖片
              </el-checkbox>
              <el-checkbox v-model="exportOptions.includeCharts">
                包含圖表
              </el-checkbox>
            </div>
          </el-form-item>
          
          <el-form-item label="水印文字" v-if="exportOptions.format === 'pdf'">
            <el-input
              v-model="exportOptions.watermark"
              placeholder="可選，留空則無水印"
              maxlength="50"
            />
          </el-form-item>
          
          <el-form-item label="文件密碼" v-if="exportOptions.format === 'pdf'">
            <el-input
              v-model="exportOptions.password"
              type="password"
              placeholder="可選，留空則無密碼保護"
              maxlength="20"
              show-password
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 報告信息預覽 -->
      <div v-if="report" class="export-section">
        <h3>報告信息</h3>
        <div class="report-info">
          <div class="info-item">
            <span class="label">標題：</span>
            <span class="value">{{ report.metadata.title }}</span>
          </div>
          <div class="info-item">
            <span class="label">作者：</span>
            <span class="value">{{ report.metadata.author }}</span>
          </div>
          <div class="info-item">
            <span class="label">內容塊數：</span>
            <span class="value">{{ report.blocks.length }} 個</span>
          </div>
          <div class="info-item">
            <span class="label">最後更新：</span>
            <span class="value">{{ formatDateTime(report.metadata.updatedAt) }}</span>
          </div>
        </div>
      </div>

      <!-- 文件大小估算 -->
      <div class="export-section">
        <el-alert
          :title="sizeEstimate"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button
          type="primary"
          :loading="isExporting"
          @click="handleExport"
        >
          {{ isExporting ? '導出中...' : '開始導出' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  Document,
  Edit,
  ChromeFilled,
  DocumentCopy,
} from '@element-plus/icons-vue';
import type { Report, ExportOptions } from '@/types/report';
import { formatDateTime } from '@/utils/date';

// Props
interface Props {
  modelValue: boolean;
  report: Report | null;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update:modelValue', value: boolean): void;
  (event: 'export', options: ExportOptions): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const isExporting = ref(false);
const exportOptions = ref<ExportOptions>({
  format: 'pdf',
  quality: 'standard',
  includeImages: true,
  includeCharts: true,
  watermark: '',
  password: '',
  metadata: {},
});

// 計算屬性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

const sizeEstimate = computed(() => {
  if (!props.report) return '無法估算文件大小';
  
  const blockCount = props.report.blocks.length;
  const hasImages = exportOptions.value.includeImages && 
    props.report.blocks.some(block => block.type === 'image');
  const hasCharts = exportOptions.value.includeCharts && 
    props.report.blocks.some(block => block.type === 'chart');
  
  let estimatedSize = blockCount * 10; // 基礎大小 (KB)
  
  if (hasImages) {
    estimatedSize += 500; // 圖片增加大小
  }
  
  if (hasCharts) {
    estimatedSize += 200; // 圖表增加大小
  }
  
  // 根據質量調整大小
  switch (exportOptions.value.quality) {
    case 'draft':
      estimatedSize *= 0.5;
      break;
    case 'high':
      estimatedSize *= 2;
      break;
    default:
      // standard quality, no change
      break;
  }
  
  // 根據格式調整大小
  switch (exportOptions.value.format) {
    case 'pdf':
      estimatedSize *= 1.2;
      break;
    case 'docx':
      estimatedSize *= 0.8;
      break;
    case 'html':
      estimatedSize *= 0.3;
      break;
    case 'markdown':
      estimatedSize *= 0.1;
      break;
  }
  
  if (estimatedSize < 100) {
    return `預估文件大小：${Math.round(estimatedSize)} KB`;
  } else {
    return `預估文件大小：${(estimatedSize / 1024).toFixed(1)} MB`;
  }
});

// 方法
const handleExport = async () => {
  if (!props.report) return;
  
  isExporting.value = true;
  
  try {
    // 添加報告元數據到導出選項
    const optionsWithMetadata = {
      ...exportOptions.value,
      metadata: {
        title: props.report.metadata.title,
        author: props.report.metadata.author,
        createdAt: props.report.metadata.createdAt,
        exportedAt: new Date().toISOString(),
      },
    };
    
    emit('export', optionsWithMetadata);
  } finally {
    isExporting.value = false;
  }
};

const handleCancel = () => {
  handleClose();
};

const handleClose = () => {
  // 重置導出選項
  exportOptions.value = {
    format: 'pdf',
    quality: 'standard',
    includeImages: true,
    includeCharts: true,
    watermark: '',
    password: '',
    metadata: {},
  };
  isExporting.value = false;
  emit('update:modelValue', false);
};

// 監聽對話框打開，可以做一些初始化
watch(
  () => props.modelValue,
  (visible) => {
    if (visible && props.report) {
      // 可以根據報告內容自動設置一些選項
      const hasImages = props.report.blocks.some(block => block.type === 'image');
      const hasCharts = props.report.blocks.some(block => block.type === 'chart');
      
      exportOptions.value.includeImages = hasImages;
      exportOptions.value.includeCharts = hasCharts;
    }
  }
);
</script>

<style scoped>
.export-dialog {
  max-height: 70vh;
  overflow-y: auto;
}

.export-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.export-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.export-section h3 {
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

.format-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.format-option {
  margin: 0 !important;
}

.format-card {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 2px solid var(--el-border-color-lighter);
  border-radius: 6px;
  background: var(--el-bg-color);
  transition: all 0.3s ease;
  cursor: pointer;
}

.format-card:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.format-option.is-checked .format-card {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-8);
}

.format-icon {
  font-size: 24px;
  color: var(--el-color-primary);
  margin-right: 8px;
}

.format-info h4 {
  margin: 0 0 2px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.format-info p {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.export-form {
  margin: 0;
}

.content-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-info {
  background-color: var(--el-fill-color-lighter);
  padding: 16px;
  border-radius: 6px;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: var(--el-text-color-regular);
  min-width: 80px;
}

.value {
  color: var(--el-text-color-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 深色主題適配 */
.dark .format-card {
  background-color: var(--el-bg-color);
}

.dark .format-card:hover {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .format-option.is-checked .format-card {
  background-color: rgba(64, 158, 255, 0.15);
}

.dark .report-info {
  background-color: rgba(255, 255, 255, 0.05);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .format-group {
    grid-template-columns: 1fr;
  }
  
  .export-dialog {
    max-height: 80vh;
  }
}

/* 滾動條樣式 */
.export-dialog::-webkit-scrollbar {
  width: 6px;
}

.export-dialog::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.export-dialog::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

.export-dialog::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-dark);
}
</style>