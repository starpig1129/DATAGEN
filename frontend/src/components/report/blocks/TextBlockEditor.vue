<template>
  <div class="text-block-editor" :class="{ focused: isFocused }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-button-group>
        <el-button
          size="small"
          :type="block.formatting?.bold ? 'primary' : 'default'"
          @click="toggleFormat('bold')"
        >
          <strong>B</strong>
        </el-button>
        <el-button
          size="small"
          :type="block.formatting?.italic ? 'primary' : 'default'"
          @click="toggleFormat('italic')"
        >
          <em>I</em>
        </el-button>
        <el-button
          size="small"
          :type="block.formatting?.underline ? 'primary' : 'default'"
          @click="toggleFormat('underline')"
        >
          <u>U</u>
        </el-button>
      </el-button-group>
      
      <el-select
        v-model="textAlign"
        size="small"
        style="width: 100px; margin-left: 8px"
        @change="updateAlignment"
      >
        <el-option label="左對齊" value="left" />
        <el-option label="居中" value="center" />
        <el-option label="右對齊" value="right" />
        <el-option label="兩端對齊" value="justify" />
      </el-select>
      
      <el-color-picker
        v-model="textColor"
        size="small"
        style="margin-left: 8px"
        @change="updateColor"
      />
    </div>

    <!-- 文本編輯區域 -->
    <div
      ref="editorRef"
      class="text-editor"
      :contenteditable="true"
      :style="editorStyle"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
      @keydown="handleKeydown"
    >
      {{ block.content }}
    </div>

    <!-- 佔位符 -->
    <div v-if="!block.content && !isFocused" class="placeholder">
      點擊這裡輸入文本...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import type { TextBlock } from '@/types/report';

// Props
interface Props {
  block: TextBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<TextBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const editorRef = ref<HTMLDivElement>();
const isFocused = ref(false);

// 計算屬性
const textAlign = ref(props.block.formatting?.align || 'left');
const textColor = ref(props.block.formatting?.color || '#000000');

const editorStyle = computed(() => ({
  textAlign: textAlign.value,
  color: textColor.value,
  fontWeight: props.block.formatting?.bold ? 'bold' : 'normal',
  fontStyle: props.block.formatting?.italic ? 'italic' : 'normal',
  textDecoration: props.block.formatting?.underline ? 'underline' : 'none',
  fontSize: props.block.formatting?.fontSize ? `${props.block.formatting.fontSize}px` : '14px',
}));

// 方法
const handleInput = (event: Event) => {
  const target = event.target as HTMLDivElement;
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
  // 處理快捷鍵
  if (event.ctrlKey || event.metaKey) {
    switch (event.key) {
      case 'b':
        event.preventDefault();
        toggleFormat('bold');
        break;
      case 'i':
        event.preventDefault();
        toggleFormat('italic');
        break;
      case 'u':
        event.preventDefault();
        toggleFormat('underline');
        break;
    }
  }
  
  // 處理 Enter 鍵
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    // 可以在這裡添加邏輯來創建新的文本塊
  }
};

const toggleFormat = (format: 'bold' | 'italic' | 'underline') => {
  const currentFormatting = props.block.formatting || {};
  const newFormatting = {
    ...currentFormatting,
    [format]: !currentFormatting[format],
  };
  
  emit('update', props.block.id, {
    formatting: newFormatting,
    updatedAt: new Date().toISOString(),
  });
};

const updateAlignment = (align: string) => {
  const currentFormatting = props.block.formatting || {};
  const newFormatting = {
    ...currentFormatting,
    align: align as 'left' | 'center' | 'right' | 'justify',
  };
  
  emit('update', props.block.id, {
    formatting: newFormatting,
    updatedAt: new Date().toISOString(),
  });
};

const updateColor = (color: string | null) => {
  if (!color) return;
  
  const currentFormatting = props.block.formatting || {};
  const newFormatting = {
    ...currentFormatting,
    color,
  };
  
  emit('update', props.block.id, {
    formatting: newFormatting,
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
.text-block-editor {
  position: relative;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.text-block-editor.focused {
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

.text-editor {
  min-height: 60px;
  padding: 12px;
  outline: none;
  line-height: 1.6;
  background-color: var(--el-bg-color);
  border-radius: 0 0 6px 6px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.text-editor:empty::before {
  content: '';
}

.placeholder {
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  color: var(--el-text-color-placeholder);
  pointer-events: none;
  font-style: italic;
}

/* 選中狀態樣式 */
.text-block-editor:hover {
  border-color: var(--el-border-color);
}

/* 工具欄按鈕樣式 */
.editor-toolbar .el-button-group .el-button {
  padding: 4px 8px;
  min-width: 32px;
}

.editor-toolbar .el-button-group .el-button strong,
.editor-toolbar .el-button-group .el-button em,
.editor-toolbar .el-button-group .el-button u {
  font-size: 12px;
}

/* 深色主題適配 */
.dark .text-block-editor.focused {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .text-editor {
  background-color: var(--el-bg-color);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .text-editor {
    padding: 8px;
    min-height: 50px;
  }
}
</style>