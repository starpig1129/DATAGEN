<template>
  <figure class="table-preview">
    <div v-if="block.caption" class="table-caption">
      {{ block.caption }}
    </div>
    
    <div class="table-container">
      <table class="preview-table" :class="tableClasses">
        <thead v-if="block.headers.length > 0">
          <tr>
            <th
              v-for="(header, index) in block.headers"
              :key="`header-${index}`"
              :style="headerCellStyle"
            >
              {{ header }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, rowIndex) in block.rows"
            :key="`row-${rowIndex}`"
            :class="{ 'striped-row': isStripedRow(rowIndex) }"
          >
            <td
              v-for="(cell, cellIndex) in row"
              :key="`cell-${rowIndex}-${cellIndex}`"
              :style="cellStyle"
            >
              {{ cell }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </figure>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { TableBlock } from '@/types/report';

interface Props {
  block: TableBlock;
  index?: number;
}

const props = defineProps<Props>();

const tableClasses = computed(() => ({
  'bordered-table': props.block.styling?.bordered ?? true,
  'striped-table': props.block.styling?.striped ?? false,
}));

const headerCellStyle = computed(() => ({
  ...props.block.styling?.headerStyle,
}));

const cellStyle = computed(() => ({
  ...props.block.styling?.cellStyle,
}));

const isStripedRow = (rowIndex: number): boolean => {
  return props.block.styling?.striped === true && rowIndex % 2 === 1;
};
</script>

<style scoped>
.table-preview {
  margin: 1.5rem 0;
  overflow-x: auto;
}

.table-caption {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  font-style: italic;
  text-align: center;
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  line-height: 1.5;
  background: var(--el-bg-color);
}

.preview-table th {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-primary);
  font-weight: 600;
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid var(--el-border-color);
}

.preview-table td {
  padding: 10px 16px;
  color: var(--el-text-color-regular);
  border-bottom: 1px solid var(--el-border-color-lighter);
  vertical-align: top;
}

.preview-table tr:last-child td {
  border-bottom: none;
}

/* 邊框樣式 */
.bordered-table {
  border: 1px solid var(--el-border-color);
}

.bordered-table th,
.bordered-table td {
  border-right: 1px solid var(--el-border-color-lighter);
}

.bordered-table th:last-child,
.bordered-table td:last-child {
  border-right: none;
}

/* 條紋樣式 */
.striped-table .striped-row {
  background: var(--el-fill-color-extra-light);
}

/* 懸停效果 */
.preview-table tbody tr:hover {
  background: var(--el-fill-color-light);
  transition: background-color 0.2s ease;
}

/* 深色主題適配 */
.dark .table-container {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.dark .preview-table {
  background: var(--el-bg-color-page);
}

.dark .preview-table th {
  background: var(--el-fill-color-darker);
  border-bottom-color: var(--el-border-color);
}

.dark .preview-table td {
  border-bottom-color: var(--el-border-color-light);
}

.dark .bordered-table {
  border-color: var(--el-border-color);
}

.dark .bordered-table th,
.dark .bordered-table td {
  border-right-color: var(--el-border-color-light);
}

.dark .striped-table .striped-row {
  background: var(--el-fill-color-darker);
}

.dark .preview-table tbody tr:hover {
  background: var(--el-fill-color-dark);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .table-preview {
    margin: 1rem 0;
  }
  
  .preview-table {
    font-size: 0.8rem;
  }
  
  .preview-table th,
  .preview-table td {
    padding: 8px 12px;
  }
  
  .table-container {
    border-radius: 4px;
  }
}

/* 可滾動表格指示器 */
.table-container::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 20px;
  background: linear-gradient(to left, var(--el-bg-color), transparent);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.table-container:hover::after {
  opacity: 1;
}

@media (max-width: 768px) {
  .table-container::after {
    opacity: 1;
  }
}
</style>