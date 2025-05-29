<template>
  <div class="quote-block-editor" :class="{ selected: isSelected }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-input
        v-model="quoteAuthor"
        size="small"
        placeholder="作者"
        style="width: 120px"
        @change="updateAuthor"
      />
      
      <el-input
        v-model="quoteSource"
        size="small"
        placeholder="來源"
        style="width: 120px; margin-left: 8px"
        @change="updateSource"
      />
    </div>

    <!-- 引用內容 -->
    <div class="quote-container">
      <div class="quote-mark">"</div>
      <div
        ref="quoteEditorRef"
        class="quote-content"
        :contenteditable="true"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
      >
        {{ block.content }}
      </div>
      
      <!-- 作者和來源信息 -->
      <div v-if="block.author || block.source" class="quote-attribution">
        <span v-if="block.author" class="quote-author">— {{ block.author }}</span>
        <span v-if="block.source" class="quote-source">《{{ block.source }}》</span>
      </div>
    </div>

    <!-- 佔位符 -->
    <div v-if="!block.content && !isFocused" class="placeholder">
      輸入引用內容...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import type { QuoteBlock } from '@/types/report';

// Props
interface Props {
  block: QuoteBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<QuoteBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const quoteEditorRef = ref<HTMLDivElement>();
const isFocused = ref(false);
const quoteAuthor = ref(props.block.author || '');
const quoteSource = ref(props.block.source || '');

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

const updateAuthor = (author: string) => {
  emit('update', props.block.id, {
    author,
    updatedAt: new Date().toISOString(),
  });
};

const updateSource = (source: string) => {
  emit('update', props.block.id, {
    source,
    updatedAt: new Date().toISOString(),
  });
};

// 監聽塊屬性變化
watch(
  () => props.block.content,
  (newContent) => {
    if (quoteEditorRef.value && quoteEditorRef.value.innerText !== newContent) {
      quoteEditorRef.value.innerText = newContent;
    }
  }
);

watch(
  () => props.block.author,
  (newAuthor) => {
    quoteAuthor.value = newAuthor || '';
  }
);

watch(
  () => props.block.source,
  (newSource) => {
    quoteSource.value = newSource || '';
  }
);

// 監聽選中狀態，自動聚焦
watch(
  () => props.isSelected,
  (selected) => {
    if (selected && quoteEditorRef.value) {
      nextTick(() => {
        quoteEditorRef.value?.focus();
      });
    }
  }
);
</script>

<style scoped>
.quote-block-editor {
  position: relative;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.quote-block-editor.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.quote-block-editor:hover {
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

.quote-container {
  position: relative;
  padding: 20px 24px;
  background-color: var(--el-fill-color-lighter);
  border-left: 4px solid var(--el-color-primary);
  border-radius: 0 0 6px 6px;
}

.quote-mark {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 48px;
  font-weight: bold;
  color: var(--el-color-primary);
  opacity: 0.3;
  line-height: 1;
  pointer-events: none;
}

.quote-content {
  position: relative;
  z-index: 1;
  margin: 0;
  padding: 0;
  outline: none;
  font-size: 16px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  font-style: italic;
  background: transparent;
  word-wrap: break-word;
  white-space: pre-wrap;
  min-height: 60px;
}

.quote-attribution {
  margin-top: 16px;
  text-align: right;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.quote-author {
  font-weight: 500;
}

.quote-source {
  margin-left: 8px;
  font-style: italic;
}

.placeholder {
  position: absolute;
  top: 50%;
  left: 24px;
  transform: translateY(-50%);
  color: var(--el-text-color-placeholder);
  pointer-events: none;
  font-style: italic;
  z-index: 2;
}

/* 深色主題適配 */
.dark .quote-block-editor.selected {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .quote-container {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .quote-mark {
  color: var(--el-color-primary);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .quote-container {
    padding: 16px 20px;
  }
  
  .quote-mark {
    font-size: 36px;
    top: 4px;
    left: 4px;
  }
  
  .quote-content {
    font-size: 15px;
  }
  
  .quote-attribution {
    font-size: 13px;
  }
}

/* 打印樣式 */
@media print {
  .editor-toolbar {
    display: none;
  }
  
  .quote-block-editor {
    border: none;
    background: none !important;
  }
  
  .quote-container {
    background-color: #f8f9fa;
    border-left-color: #333;
  }
  
  .quote-content {
    color: #333;
  }
  
  .quote-mark {
    color: #666;
  }
}

/* 無障礙支援 */
.quote-content:focus {
  box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
  border-radius: 4px;
}

/* 打字機效果（可選） */
.quote-content {
  transition: all 0.3s ease;
}

.quote-content:focus {
  background-color: rgba(64, 158, 255, 0.05);
}
</style>