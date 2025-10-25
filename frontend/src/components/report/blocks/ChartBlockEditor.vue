<template>
  <div class="chart-block-editor" :class="{ selected: isSelected }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-select
        v-model="chartType"
        size="small"
        style="width: 150px"
        placeholder="選擇圖表類型"
        @change="updateChartType"
      >
        <el-option label="線性圖" value="line" />
        <el-option label="柱狀圖" value="bar" />
        <el-option label="餅圖" value="pie" />
        <el-option label="散點圖" value="scatter" />
      </el-select>
      
      <el-button
        size="small"
        style="margin-left: 8px"
        @click="selectChart"
      >
        選擇圖表
      </el-button>
    </div>

    <!-- 圖表顯示 -->
    <div v-if="block.chartId" class="chart-container">
      <div class="chart-placeholder">
        <el-icon class="chart-icon"><DataLine /></el-icon>
        <h4>{{ block.title || '圖表' }}</h4>
        <p>圖表 ID: {{ block.chartId }}</p>
        <p>類型: {{ block.chartType }}</p>
      </div>
      <div v-if="block.caption" class="chart-caption">
        {{ block.caption }}
      </div>
    </div>

    <!-- 佔位符 -->
    <div v-else class="chart-placeholder-empty">
      <el-icon class="placeholder-icon"><DataLine /></el-icon>
      <p>選擇一個圖表來插入</p>
      <el-button type="primary" @click="selectChart">
        選擇圖表
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { DataLine } from '@element-plus/icons-vue';
import type { ChartBlock } from '@/types/report';

// Props
interface Props {
  block: ChartBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<ChartBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const chartType = ref(props.block.chartType || 'line');

// 方法
const updateChartType = (type: string) => {
  emit('update', props.block.id, {
    chartType: type,
    updatedAt: new Date().toISOString(),
  });
};

const selectChart = () => {
  // 這裡應該打開圖表選擇對話框
  ElMessage.info('圖表選擇功能將在後續版本中實現');
  
  // 模擬選擇圖表
  emit('update', props.block.id, {
    chartId: `chart_${Date.now()}`,
    chartType: chartType.value,
    title: '示例圖表',
    updatedAt: new Date().toISOString(),
  });
};

// 監聽塊屬性變化
watch(
  () => props.block.chartType,
  (newType) => {
    if (newType) {
      chartType.value = newType;
    }
  }
);
</script>

<style scoped>
.chart-block-editor {
  position: relative;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.chart-block-editor.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.chart-block-editor:hover {
  border-color: var(--el-border-color);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--el-fill-color-extra-light);
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.chart-container {
  padding: 12px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 6px;
  border: 2px dashed var(--el-border-color);
}

.chart-icon {
  font-size: 48px;
  color: var(--el-color-primary);
  margin-bottom: 12px;
}

.chart-placeholder h4 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.chart-placeholder p {
  margin: 4px 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.chart-caption {
  margin-top: 8px;
  text-align: center;
  font-size: 14px;
  color: var(--el-text-color-regular);
  font-style: italic;
}

.chart-placeholder-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--el-text-color-placeholder);
  background-color: var(--el-fill-color-lighter);
  border-radius: 0 0 6px 6px;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.chart-placeholder-empty p {
  margin: 0 0 16px 0;
  font-size: 14px;
}

/* 深色主題適配 */
.dark .chart-block-editor.selected {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .chart-placeholder,
.dark .chart-placeholder-empty {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .chart-placeholder,
  .chart-placeholder-empty {
    padding: 24px 16px;
  }
  
  .chart-icon,
  .placeholder-icon {
    font-size: 36px;
  }
}

/* 打印樣式 */
@media print {
  .editor-toolbar {
    display: none;
  }
  
  .chart-block-editor {
    border: none;
    background: none !important;
  }
  
  .chart-container {
    padding: 0;
  }
}
</style>