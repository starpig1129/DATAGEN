<template>
  <div class="heading-block-editor" :class="{ focused: isFocused }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-select
        v-model="headingLevel"
        size="small"
        style="width: 120px"
        @change="updateLevel"
      >
        <el-option label="標題 1" :value="1" />
        <el-option label="標題 2" :value="2" />
        <el-option label="標題 3" :value="3" />
        <el-option label="標題 4" :value="4" />
        <el-option label="標題 5" :value="5" />
        <el-option label="標題 6" :value="6" />
      </el-select>
      
      <el-checkbox
        v-model="enableNumbering"
        style="margin-left: 12px"
        @change="updateNumbering"
      >
        自動編號
      </el-checkbox>
    </div>

    <!-- 標題編輯區域 -->
    <component
      :is="headingTag"
      ref="editorRef"
      class="heading-editor"
      :class="headingClass"
      :contenteditable="true"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
      @keydown="handleKeydown"
    >
      {{ block.content }}
    </component>

    <!-- 佔位符 -->
    <div v-if="!block.content && !isFocused" class="placeholder">
      輸入標題內容...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import type { HeadingBlock } from '@/types/report';

// Props
interface Props {
  block: HeadingBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<HeadingBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const editorRef = ref<HTMLElement>();
const isFocused = ref(false);
const headingLevel = ref(props.block.level);
const enableNumbering = ref(props.block.numbering || false);

// 計算屬性
const headingTag = computed(() => `h${headingLevel.value}`);

const headingClass = computed(() => [
  `heading-level-${headingLevel.value}`,
  {
    'with-numbering': enableNumbering.value,
  },
]);

// 方法
const handleInput = (event: Event) => {
  const target = event.target as HTMLElement;
  const content = target.innerText || target.textContent || '';
  
  emit('update', props.block.id, {
    content,
    updatedAt: new Date().toISOString(),
  });
};

const handleFocus = () => {
  isFocused.value = true;
};

const handleBlur = () => {
  isFocused.value = false;
};

const handleKeydown = (event: KeyboardEvent) => {
  // 處理 Enter 鍵 - 創建新段落
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    // 在這裡可以觸發創建新文本塊的邏輯
  }
  
  // 處理 Backspace - 如果內容為空，可能需要刪除當前塊
  if (event.key === 'Backspace' && !props.block.content) {
    event.preventDefault();
    // 可以在這裡觸發刪除當前塊的邏輯
  }
};

const updateLevel = (level: number) => {
  emit('update', props.block.id, {
    level: level as 1 | 2 | 3 | 4 | 5 | 6,
    updatedAt: new Date().toISOString(),
  });
};

const updateNumbering = (enabled: boolean | string | number) => {
  const isEnabled = Boolean(enabled);
  emit('update', props.block.id, {
    numbering: isEnabled,
    updatedAt: new Date().toISOString(),
  });
};

// 監聽塊內容變化，同步到編輯器
watch(
  () => props.block.content,
  (newContent) => {
    if (editorRef.value && editorRef.value.innerText !== newContent) {
      editorRef.value.innerText = newContent;
    }
  }
);

// 監聽標題級別變化
watch(
  () => props.block.level,
  (newLevel) => {
    headingLevel.value = newLevel;
  }
);

// 監聽編號設置變化
watch(
  () => props.block.numbering,
  (newNumbering) => {
    enableNumbering.value = newNumbering || false;
  }
);

// 監聽選中狀態，自動聚焦
watch(
  () => props.isSelected,
  (selected) => {
    if (selected && editorRef.value) {
      nextTick(() => {
        editorRef.value?.focus();
      });
    }
  }
);
</script>

<style scoped>
.heading-block-editor {
  position: relative;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.heading-block-editor.focused {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--el-fill-color-extra-light);
  border-bottom: 1px solid var(--el-border-color-lighter);
  border-radius: 6px 6px 0 0;
}

.heading-editor {
  margin: 0;
  padding: 12px;
  outline: none;
  background-color: var(--el-bg-color);
  border-radius: 0 0 6px 6px;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* 不同級別標題的樣式 */
.heading-level-1 {
  font-size: 32px;
  line-height: 1.2;
  border-bottom: 2px solid var(--el-border-color-light);
  padding-bottom: 8px;
}

.heading-level-2 {
  font-size: 28px;
  line-height: 1.3;
}

.heading-level-3 {
  font-size: 24px;
  line-height: 1.4;
}

.heading-level-4 {
  font-size: 20px;
  line-height: 1.4;
}

.heading-level-5 {
  font-size: 18px;
  line-height: 1.5;
}

.heading-level-6 {
  font-size: 16px;
  line-height: 1.5;
  font-weight: 500;
}

/* 帶編號的標題 */
.with-numbering::before {
  content: counter(heading-counter) '. ';
  color: var(--el-color-primary);
  font-weight: 700;
}

.placeholder {
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  color: var(--el-text-color-placeholder);
  pointer-events: none;
  font-style: italic;
  font-weight: normal;
}

/* 選中狀態樣式 */
.heading-block-editor:hover {
  border-color: var(--el-border-color);
}

/* 深色主題適配 */
.dark .heading-block-editor.focused {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .heading-editor {
  background-color: var(--el-bg-color);
}

.dark .heading-level-1 {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .heading-level-1 {
    font-size: 28px;
  }
  
  .heading-level-2 {
    font-size: 24px;
  }
  
  .heading-level-3 {
    font-size: 20px;
  }
  
  .heading-level-4 {
    font-size: 18px;
  }
  
  .heading-level-5 {
    font-size: 16px;
  }
  
  .heading-level-6 {
    font-size: 14px;
  }
}

/* 無障礙支援 */
.heading-editor:focus {
  box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
}

/* 打印樣式 */
@media print {
  .editor-toolbar {
    display: none;
  }
  
  .heading-block-editor {
    border: none;
    background: none !important;
  }
}
</style>