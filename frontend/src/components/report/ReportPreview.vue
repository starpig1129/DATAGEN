<template>
  <div class="report-preview">
    <div class="preview-header">
      <h3>預覽</h3>
      <div class="preview-controls">
        <el-button-group>
          <el-button
            size="small"
            :type="previewMode === 'desktop' ? 'primary' : 'default'"
            :icon="Monitor"
            @click="previewMode = 'desktop'"
          />
          <el-button
            size="small"
            :type="previewMode === 'tablet' ? 'primary' : 'default'"
            :icon="Monitor"
            @click="previewMode = 'tablet'"
          />
          <el-button
            size="small"
            :type="previewMode === 'mobile' ? 'primary' : 'default'"
            :icon="Cellphone"
            @click="previewMode = 'mobile'"
          />
        </el-button-group>
        
        <el-button
          size="small"
          :icon="FullScreen"
          @click="toggleFullscreen"
        >
          全屏預覽
        </el-button>
      </div>
    </div>

    <div class="preview-container" :class="previewModeClass">
      <div class="preview-content" ref="previewContentRef">
        <!-- 報告標題頁 -->
        <div class="report-title-page">
          <h1 class="report-title">{{ report.metadata.title }}</h1>
          <div class="report-meta">
            <p class="report-author">作者：{{ report.metadata.author }}</p>
            <p class="report-date">{{ formatDateTime(report.metadata.updatedAt, { dateStyle: 'long' }) }}</p>
            <p v-if="report.metadata.description" class="report-description">
              {{ report.metadata.description }}
            </p>
          </div>
        </div>

        <!-- 目錄 (如果啟用) -->
        <div v-if="report.tableOfContents && headings.length > 0" class="table-of-contents">
          <h2>目錄</h2>
          <ul class="toc-list">
            <li
              v-for="heading in headings"
              :key="heading.id"
              :class="`toc-level-${heading.level}`"
            >
              <a :href="`#${heading.id}`" class="toc-link">
                {{ heading.content }}
              </a>
            </li>
          </ul>
        </div>

        <!-- 報告內容 -->
        <div class="report-content">
          <div
            v-for="(block, index) in sortedBlocks"
            :key="block.id"
            class="preview-block"
            :class="`block-${block.type}`"
          >
            <!-- 渲染不同類型的內容塊 -->
            <component
              :is="getPreviewComponent(block.type)"
              :block="block as any"
              :index="index"
            />
          </div>
        </div>

        <!-- 頁腳 (如果啟用頁碼) -->
        <div v-if="report.pageNumbers" class="report-footer">
          <div class="page-number">- 1 -</div>
        </div>
      </div>
    </div>

    <!-- 全屏預覽對話框 -->
    <el-dialog
      v-model="fullscreenVisible"
      title="報告預覽"
      fullscreen
      :show-close="true"
      class="fullscreen-preview-dialog"
    >
      <div class="fullscreen-preview">
        <div class="preview-content">
          <!-- 相同的內容，但在全屏模式下 -->
          <div class="report-title-page">
            <h1 class="report-title">{{ report.metadata.title }}</h1>
            <div class="report-meta">
              <p class="report-author">作者：{{ report.metadata.author }}</p>
              <p class="report-date">{{ formatDateTime(report.metadata.updatedAt, { dateStyle: 'long' }) }}</p>
              <p v-if="report.metadata.description" class="report-description">
                {{ report.metadata.description }}
              </p>
            </div>
          </div>

          <div v-if="report.tableOfContents && headings.length > 0" class="table-of-contents">
            <h2>目錄</h2>
            <ul class="toc-list">
              <li
                v-for="heading in headings"
                :key="heading.id"
                :class="`toc-level-${heading.level}`"
              >
                <a :href="`#${heading.id}`" class="toc-link">
                  {{ heading.content }}
                </a>
              </li>
            </ul>
          </div>

          <div class="report-content">
            <div
              v-for="(block, index) in sortedBlocks"
              :key="block.id"
              class="preview-block"
              :class="`block-${block.type}`"
            >
              <component
                :is="getPreviewComponent(block.type)"
                :block="block as any"
                :index="index"
              />
            </div>
          </div>

          <div v-if="report.pageNumbers" class="report-footer">
            <div class="page-number">- 1 -</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue';
import {
  Monitor,
  Cellphone,
  FullScreen,
} from '@element-plus/icons-vue';
import type { Report, ReportBlock, HeadingBlock } from '@/types/report';
import { formatDateTime } from '@/utils/date';

// 預覽組件 - 懶加載
const TextPreview = defineAsyncComponent(() => import('./preview/TextPreview.vue'));
const HeadingPreview = defineAsyncComponent(() => import('./preview/HeadingPreview.vue'));
const ImagePreview = defineAsyncComponent(() => import('./preview/ImagePreview.vue'));
const ChartPreview = defineAsyncComponent(() => import('./preview/ChartPreview.vue'));
const TablePreview = defineAsyncComponent(() => import('./preview/TablePreview.vue'));
const DividerPreview = defineAsyncComponent(() => import('./preview/DividerPreview.vue'));
const CodePreview = defineAsyncComponent(() => import('./preview/CodePreview.vue'));
const QuotePreview = defineAsyncComponent(() => import('./preview/QuotePreview.vue'));

// Props
interface Props {
  report: Report;
}

const props = defineProps<Props>();

// 響應式狀態
const previewMode = ref<'desktop' | 'tablet' | 'mobile'>('desktop');
const fullscreenVisible = ref(false);

// 計算屬性
const sortedBlocks = computed(() => {
  return [...props.report.blocks].sort((a, b) => a.order - b.order);
});

const headings = computed(() => {
  return sortedBlocks.value
    .filter((block): block is HeadingBlock => block.type === 'heading')
    .map((block, index) => ({
      id: `heading-${index}`,
      level: block.level,
      content: block.content,
    }));
});

const previewModeClass = computed(() => ({
  'preview-desktop': previewMode.value === 'desktop',
  'preview-tablet': previewMode.value === 'tablet',
  'preview-mobile': previewMode.value === 'mobile',
}));

// 方法
const getPreviewComponent = (blockType: ReportBlock['type']) => {
  switch (blockType) {
    case 'text': return TextPreview;
    case 'heading': return HeadingPreview;
    case 'image': return ImagePreview;
    case 'chart': return ChartPreview;
    case 'table': return TablePreview;
    case 'divider': return DividerPreview;
    case 'code': return CodePreview;
    case 'quote': return QuotePreview;
    default: return TextPreview;
  }
};

const toggleFullscreen = () => {
  fullscreenVisible.value = !fullscreenVisible.value;
};
</script>

<style scoped>
.report-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-extra-light);
}

.preview-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.preview-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-container {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-tertiary);
  padding: 20px;
  transition: all 0.3s ease;
}

.preview-container.preview-desktop {
  padding: 20px;
}

.preview-container.preview-tablet {
  padding: 16px;
}

.preview-container.preview-mobile {
  padding: 8px;
}

.preview-content {
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg-primary);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.preview-tablet .preview-content {
  max-width: 600px;
}

.preview-mobile .preview-content {
  max-width: 400px;
}

.report-title-page {
  padding: 60px 40px;
  text-align: center;
  border-bottom: 2px solid var(--el-border-color-light);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.report-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 24px 0;
  line-height: 1.2;
}

.report-meta {
  font-size: 16px;
  opacity: 0.9;
}

.report-author,
.report-date,
.report-description {
  margin: 8px 0;
}

.report-description {
  font-style: italic;
  max-width: 600px;
  margin: 16px auto 0;
}

.table-of-contents {
  padding: 40px;
  background: var(--el-fill-color-extra-light);
  border-bottom: 1px solid var(--el-border-color-light);
}

.table-of-contents h2 {
  margin: 0 0 24px 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-list li {
  margin: 8px 0;
}

.toc-level-1 { margin-left: 0; }
.toc-level-2 { margin-left: 20px; }
.toc-level-3 { margin-left: 40px; }
.toc-level-4 { margin-left: 60px; }
.toc-level-5 { margin-left: 80px; }
.toc-level-6 { margin-left: 100px; }

.toc-link {
  color: var(--el-color-primary);
  text-decoration: none;
  font-weight: 500;
}

.toc-link:hover {
  text-decoration: underline;
}

.report-content {
  padding: 40px;
}

.preview-block {
  margin-bottom: 24px;
}

.preview-block:last-child {
  margin-bottom: 0;
}

.report-footer {
  padding: 20px;
  text-align: center;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-fill-color-extra-light);
}

.page-number {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

/* 全屏預覽樣式 */
.fullscreen-preview {
  height: 100%;
  overflow-y: auto;
  background: var(--bg-tertiary);
  padding: 40px;
}

.fullscreen-preview .preview-content {
  max-width: 900px;
}

/* 深色主題適配 */
.dark .preview-container {
  background: var(--el-bg-color-page);
}

.dark .preview-content {
  background: var(--el-bg-color);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

.dark .report-title-page {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

.dark .fullscreen-preview {
  background: var(--el-bg-color-page);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .preview-header {
    flex-direction: column;
    gap: 8px;
    padding: 8px 12px;
  }
  
  .preview-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .preview-container {
    padding: 8px;
  }
  
  .preview-content {
    border-radius: 4px;
  }
  
  .report-title-page {
    padding: 30px 20px;
  }
  
  .report-title {
    font-size: 24px;
  }
  
  .table-of-contents,
  .report-content {
    padding: 20px;
  }
}

/* 滾動條樣式 */
.preview-container::-webkit-scrollbar,
.fullscreen-preview::-webkit-scrollbar {
  width: 8px;
}

.preview-container::-webkit-scrollbar-track,
.fullscreen-preview::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

.preview-container::-webkit-scrollbar-thumb,
.fullscreen-preview::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.preview-container::-webkit-scrollbar-thumb:hover,
.fullscreen-preview::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

/* 打印樣式 */
@media print {
  .preview-header {
    display: none;
  }
  
  .preview-container {
    padding: 0;
    background: white;
    overflow: visible;
  }
  
  .preview-content {
    box-shadow: none;
    border-radius: 0;
    max-width: none;
  }
}
</style>