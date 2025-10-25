<template>
  <div class="divider-block-editor" :class="{ selected: isSelected }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-select
        v-model="dividerStyle"
        size="small"
        style="width: 120px"
        @change="updateStyle"
      >
        <el-option label="實線" value="solid" />
        <el-option label="虛線" value="dashed" />
        <el-option label="點線" value="dotted" />
      </el-select>
      
      <el-slider
        v-model="dividerThickness"
        :min="1"
        :max="10"
        style="width: 120px; margin-left: 12px"
        @change="updateThickness"
      />
      
      <span class="thickness-label">{{ dividerThickness }}px</span>
    </div>

    <!-- 分隔線 -->
    <div
      class="divider-line"
      :style="dividerStyles"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { DividerBlock } from '@/types/report';

// Props
interface Props {
  block: DividerBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<DividerBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const dividerStyle = ref(props.block.style || 'solid');
const dividerThickness = ref(props.block.thickness || 2);

// 計算屬性
const dividerStyles = computed(() => ({
  borderTop: `${dividerThickness.value}px ${dividerStyle.value} var(--el-border-color)`,
  width: '100%',
  margin: '16px 0',
}));

// 方法
const updateStyle = (style: string) => {
  emit('update', props.block.id, {
    style: style as 'solid' | 'dashed' | 'dotted',
    updatedAt: new Date().toISOString(),
  });
};

const updateThickness = (thickness: number | number[]) => {
  const value = Array.isArray(thickness) ? thickness[0] : thickness;
  emit('update', props.block.id, {
    thickness: value,
    updatedAt: new Date().toISOString(),
  });
};

// 監聽塊屬性變化
watch(
  () => props.block.style,
  (newStyle) => {
    if (newStyle) {
      dividerStyle.value = newStyle;
    }
  }
);

watch(
  () => props.block.thickness,
  (newThickness) => {
    if (newThickness) {
      dividerThickness.value = newThickness;
    }
  }
);
</script>

<style scoped>
.divider-block-editor {
  position: relative;
  padding: 8px;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.divider-block-editor.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.divider-block-editor:hover {
  border-color: var(--el-border-color);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--el-fill-color-extra-light);
  border-radius: 6px;
  margin-bottom: 12px;
}

.thickness-label {
  margin-left: 8px;
  font-size: 12px;
  color: var(--el-text-color-regular);
  min-width: 30px;
}

.divider-line {
  transition: all 0.3s ease;
}

/* 深色主題適配 */
.dark .divider-block-editor.selected {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .divider-line {
  border-top-color: var(--el-border-color) !important;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
}

/* 打印樣式 */
@media print {
  .editor-toolbar {
    display: none;
  }
  
  .divider-block-editor {
    border: none;
    background: none !important;
    padding: 0;
  }
}
</style>