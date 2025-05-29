<template>
  <div class="table-block-editor" :class="{ selected: isSelected }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-button size="small" @click="addRow">
        添加行
      </el-button>
      <el-button size="small" @click="addColumn">
        添加列
      </el-button>
      <el-button size="small" @click="removeRow" :disabled="block.rows.length <= 1">
        刪除行
      </el-button>
      <el-button size="small" @click="removeColumn" :disabled="block.headers.length <= 1">
        刪除列
      </el-button>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table
        :data="tableData"
        border
        style="width: 100%"
        :header-cell-style="headerStyle"
      >
        <el-table-column
          v-for="(header, index) in block.headers"
          :key="index"
          :label="header"
          :prop="`col${index}`"
        >
          <template #header>
            <el-input
              v-model="headers[index]"
              size="small"
              @change="updateHeaders"
            />
          </template>
          <template #default="{ row, $index }">
            <el-input
              v-model="row[`col${index}`]"
              size="small"
              @change="updateCellData($index, index, row[`col${index}`])"
            />
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="block.caption" class="table-caption">
        {{ block.caption }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { TableBlock } from '@/types/report';

// Props
interface Props {
  block: TableBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<TableBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const headers = ref([...props.block.headers]);

// 計算屬性
const tableData = computed(() => {
  return props.block.rows.map((row, rowIndex) => {
    const rowData: Record<string, string> = {};
    row.forEach((cell, colIndex) => {
      rowData[`col${colIndex}`] = cell;
    });
    return rowData;
  });
});

const headerStyle = computed(() => ({
  backgroundColor: '#f5f7fa',
  color: '#606266',
  ...props.block.styling?.headerStyle,
}));

// 方法
const addRow = () => {
  const newRow = new Array(props.block.headers.length).fill('');
  const newRows = [...props.block.rows, newRow];
  
  emit('update', props.block.id, {
    rows: newRows,
    updatedAt: new Date().toISOString(),
  });
};

const addColumn = () => {
  const newHeaders = [...props.block.headers, `欄位${props.block.headers.length + 1}`];
  const newRows = props.block.rows.map(row => [...row, '']);
  
  emit('update', props.block.id, {
    headers: newHeaders,
    rows: newRows,
    updatedAt: new Date().toISOString(),
  });
};

const removeRow = () => {
  if (props.block.rows.length > 1) {
    const newRows = props.block.rows.slice(0, -1);
    
    emit('update', props.block.id, {
      rows: newRows,
      updatedAt: new Date().toISOString(),
    });
  }
};

const removeColumn = () => {
  if (props.block.headers.length > 1) {
    const newHeaders = props.block.headers.slice(0, -1);
    const newRows = props.block.rows.map(row => row.slice(0, -1));
    
    emit('update', props.block.id, {
      headers: newHeaders,
      rows: newRows,
      updatedAt: new Date().toISOString(),
    });
  }
};

const updateHeaders = () => {
  emit('update', props.block.id, {
    headers: [...headers.value],
    updatedAt: new Date().toISOString(),
  });
};

const updateCellData = (rowIndex: number, colIndex: number, value: string) => {
  const newRows = [...props.block.rows];
  newRows[rowIndex] = [...newRows[rowIndex]];
  newRows[rowIndex][colIndex] = value;
  
  emit('update', props.block.id, {
    rows: newRows,
    updatedAt: new Date().toISOString(),
  });
};

// 監聽塊屬性變化
watch(
  () => props.block.headers,
  (newHeaders) => {
    headers.value = [...newHeaders];
  },
  { deep: true }
);
</script>

<style scoped>
.table-block-editor {
  position: relative;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.table-block-editor.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.table-block-editor:hover {
  border-color: var(--el-border-color);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: var(--el-fill-color-extra-light);
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.table-container {
  padding: 12px;
}

.table-caption {
  margin-top: 8px;
  text-align: center;
  font-size: 14px;
  color: var(--el-text-color-regular);
  font-style: italic;
}

/* 深色主題適配 */
.dark .table-block-editor.selected {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
  }
  
  .table-container {
    overflow-x: auto;
  }
}

/* 打印樣式 */
@media print {
  .editor-toolbar {
    display: none;
  }
  
  .table-block-editor {
    border: none;
    background: none !important;
  }
  
  .table-container {
    padding: 0;
  }
}
</style>