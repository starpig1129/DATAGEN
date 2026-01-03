<template>
  <el-dialog
    v-model="dialogVisible"
    title="新建報告"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="new-report-dialog">
      <!-- 基本信息 -->
      <el-form :model="reportForm" label-width="80px" class="report-form">
        <el-form-item label="報告標題" required>
          <el-input
            v-model="reportForm.title"
            placeholder="請輸入報告標題"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="作者">
          <el-input
            v-model="reportForm.author"
            placeholder="請輸入作者姓名"
          />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="reportForm.description"
            type="textarea"
            :rows="3"
            placeholder="請輸入報告描述（可選）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <!-- 模板選擇 -->
      <div class="template-section">
        <h3>選擇模板</h3>
        <div class="template-grid">
          <!-- 空白模板 -->
          <div
            class="template-card"
            :class="{ selected: selectedTemplate === null }"
            @click="selectTemplate(null)"
          >
            <div class="template-preview blank-template">
              <el-icon class="template-icon"><Document /></el-icon>
            </div>
            <div class="template-info">
              <h4>空白報告</h4>
              <p>從頭開始創建報告</p>
            </div>
          </div>

          <!-- 預設模板 -->
          <div
            v-for="template in templates"
            :key="template.id"
            class="template-card"
            :class="{ selected: selectedTemplate?.id === template.id }"
            @click="selectTemplate(template)"
          >
            <div class="template-preview">
              <img
                v-if="template.preview"
                :src="template.preview"
                :alt="template.name"
                class="template-image"
                @error="handleImageError"
              />
              <div v-else class="template-placeholder">
                <el-icon class="template-icon"><Document /></el-icon>
              </div>
            </div>
            <div class="template-info">
              <h4>{{ template.name }}</h4>
              <p>{{ template.description }}</p>
              <el-tag :type="getTemplateTagType(template.category)" size="small">
                {{ getCategoryLabel(template.category) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 模板詳情 -->
      <div v-if="selectedTemplate" class="template-details">
        <h4>模板詳情</h4>
        <div class="detail-content">
          <p><strong>名稱：</strong>{{ selectedTemplate.name }}</p>
          <p><strong>描述：</strong>{{ selectedTemplate.description }}</p>
          <p><strong>類別：</strong>{{ getCategoryLabel(selectedTemplate.category) }}</p>
          <p><strong>包含內容：</strong></p>
          <ul>
            <li v-for="block in selectedTemplate.defaultBlocks" :key="block.type">
              {{ getBlockTypeLabel(block.type || 'text') }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button
          type="primary"
          :disabled="!reportForm.title.trim()"
          @click="handleCreate"
        >
          創建報告
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Document } from '@element-plus/icons-vue';
import type { ReportTemplate } from '@/types/report';

// Props
interface Props {
  modelValue: boolean;
  templates: ReportTemplate[];
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update:modelValue', value: boolean): void;
  (event: 'create', template?: ReportTemplate): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const reportForm = ref({
  title: '',
  author: '系統用戶',
  description: '',
});

const selectedTemplate = ref<ReportTemplate | null>(null);

// 計算屬性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

// 方法
const selectTemplate = (template: ReportTemplate | null) => {
  selectedTemplate.value = template;
  
  // 如果選擇了模板，可以預填一些信息
  if (template) {
    if (!reportForm.value.title.trim()) {
      reportForm.value.title = `基於 ${template.name} 的報告`;
    }
  }
};

const getTemplateTagType = (category: string) => {
  const typeMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    academic: 'primary',
    business: 'success',
    technical: 'warning',
    custom: 'info',
  };
  return typeMap[category] || 'info';
};

const getCategoryLabel = (category: string) => {
  const labelMap: Record<string, string> = {
    academic: '學術',
    business: '商業',
    technical: '技術',
    custom: '自定義',
  };
  return labelMap[category] || category;
};

const getBlockTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    text: '文本段落',
    heading: '標題',
    image: '圖片',
    chart: '圖表',
    table: '表格',
    divider: '分隔線',
    code: '代碼塊',
    quote: '引用',
  };
  return labelMap[type] || type;
};

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';
  // 可以顯示一個佔位符
};

const handleCreate = () => {
  if (!reportForm.value.title.trim()) {
    return;
  }

  // 創建報告時傳遞基本信息和選中的模板
  const templateWithMetadata = selectedTemplate.value ? {
    ...selectedTemplate.value,
    metadata: {
      title: reportForm.value.title,
      author: reportForm.value.author,
      description: reportForm.value.description,
    },
  } : undefined;

  emit('create', templateWithMetadata);
  handleClose();
};

const handleCancel = () => {
  handleClose();
};

const handleClose = () => {
  // 重置表單
  reportForm.value = {
    title: '',
    author: '系統用戶',
    description: '',
  };
  selectedTemplate.value = null;
  emit('update:modelValue', false);
};

// 監聽對話框打開，重置狀態
watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      // 對話框打開時可以做一些初始化
    }
  }
);
</script>

<style scoped>
.new-report-dialog {
  max-height: 70vh;
  overflow-y: auto;
}

.report-form {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.template-section h3 {
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.template-card {
  border: 2px solid var(--el-border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--el-bg-color);
}

.template-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.template-card.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.template-preview {
  height: 120px;
  background-color: var(--el-fill-color-lighter);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.blank-template {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--border-color-light) 100%);
}

.template-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.template-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.template-icon {
  font-size: 36px;
  color: var(--el-text-color-placeholder);
}

.template-info {
  padding: 12px;
}

.template-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.template-info p {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: var(--el-text-color-regular);
  line-height: 1.4;
}

.template-details {
  padding: 16px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 6px;
  margin-top: 16px;
}

.template-details h4 {
  margin: 0 0 12px 0;
  color: var(--el-text-color-primary);
  font-size: 14px;
  font-weight: 600;
}

.detail-content p {
  margin: 8px 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.detail-content ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.detail-content li {
  margin: 4px 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 深色主題適配 */
.dark .template-card {
  background-color: var(--el-bg-color);
}

.dark .template-card.selected {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .template-details {
  background-color: rgba(255, 255, 255, 0.05);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .new-report-dialog {
    max-height: 80vh;
  }
}

/* 滾動條樣式 */
.new-report-dialog::-webkit-scrollbar {
  width: 6px;
}

.new-report-dialog::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.new-report-dialog::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

.new-report-dialog::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-dark);
}
</style>