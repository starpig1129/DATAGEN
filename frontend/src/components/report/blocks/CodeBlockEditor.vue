<template>
  <div class="code-block-editor" :class="{ selected: isSelected }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-select
        v-model="codeLanguage"
        size="small"
        style="width: 150px"
        placeholder="選擇語言"
        @change="updateLanguage"
      >
        <el-option label="JavaScript" value="javascript" />
        <el-option label="Python" value="python" />
        <el-option label="Java" value="java" />
        <el-option label="C++" value="cpp" />
        <el-option label="HTML" value="html" />
        <el-option label="CSS" value="css" />
        <el-option label="SQL" value="sql" />
        <el-option label="純文本" value="text" />
      </el-select>
      
      <el-checkbox
        v-model="showLineNumbers"
        style="margin-left: 12px"
        @change="updateLineNumbers"
      >
        顯示行號
      </el-checkbox>
    </div>

    <!-- 代碼編輯區域 -->
    <div class="code-container">
      <pre
        v-if="showLineNumbers"
        class="line-numbers"
      ><span
        v-for="n in lineCount"
        :key="n"
        class="line-number"
      >{{ n }}</span></pre>
      
      <textarea
        ref="codeEditorRef"
        v-model="codeContent"
        class="code-editor"
        :class="{ 'with-line-numbers': showLineNumbers }"
        :placeholder="placeholder"
        @input="handleInput"
        @scroll="handleScroll"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import type { CodeBlock } from '@/types/report';

// Props
interface Props {
  block: CodeBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<CodeBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const codeEditorRef = ref<HTMLTextAreaElement>();
const codeContent = ref(props.block.content || '');
const codeLanguage = ref(props.block.language || 'javascript');
const showLineNumbers = ref(props.block.showLineNumbers || false);

// 計算屬性
const lineCount = computed(() => {
  return codeContent.value.split('\n').length;
});

const placeholder = computed(() => {
  const langMap: Record<string, string> = {
    javascript: '// 在此輸入 JavaScript 代碼',
    python: '# 在此輸入 Python 代碼',
    java: '// 在此輸入 Java 代碼',
    cpp: '// 在此輸入 C++ 代碼',
    html: '<!-- 在此輸入 HTML 代碼 -->',
    css: '/* 在此輸入 CSS 代碼 */',
    sql: '-- 在此輸入 SQL 代碼',
    text: '在此輸入文本內容',
  };
  return langMap[codeLanguage.value] || '在此輸入代碼';
});

// 方法
const handleInput = () => {
  emit('update', props.block.id, {
    content: codeContent.value,
    updatedAt: new Date().toISOString(),
  });
};

const handleScroll = (event: Event) => {
  // 同步行號滾動
  const target = event.target as HTMLTextAreaElement;
  const lineNumbers = target.parentElement?.querySelector('.line-numbers') as HTMLElement;
  if (lineNumbers) {
    lineNumbers.scrollTop = target.scrollTop;
  }
};

const updateLanguage = (language: string) => {
  emit('update', props.block.id, {
    language,
    updatedAt: new Date().toISOString(),
  });
};

const updateLineNumbers = (show: boolean | string | number) => {
  const showNumbers = Boolean(show);
  emit('update', props.block.id, {
    showLineNumbers: showNumbers,
    updatedAt: new Date().toISOString(),
  });
};

// 監聽塊屬性變化
watch(
  () => props.block.content,
  (newContent) => {
    if (newContent !== codeContent.value) {
      codeContent.value = newContent || '';
    }
  }
);

watch(
  () => props.block.language,
  (newLanguage) => {
    if (newLanguage) {
      codeLanguage.value = newLanguage;
    }
  }
);

watch(
  () => props.block.showLineNumbers,
  (newShowLineNumbers) => {
    showLineNumbers.value = newShowLineNumbers || false;
  }
);

// 監聽選中狀態，自動聚焦
watch(
  () => props.isSelected,
  (selected) => {
    if (selected && codeEditorRef.value) {
      nextTick(() => {
        codeEditorRef.value?.focus();
      });
    }
  }
);
</script>

<style scoped>
.code-block-editor {
  position: relative;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-family: 'Courier New', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
}

.code-block-editor.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.code-block-editor:hover {
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

.code-container {
  position: relative;
  display: flex;
  background-color: var(--bg-tertiary);
  border-radius: 0 0 6px 6px;
  overflow: hidden;
}

.line-numbers {
  margin: 0;
  padding: 12px 8px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color-light);
  color: #6c757d;
  font-size: 14px;
  line-height: 1.5;
  text-align: right;
  user-select: none;
  overflow: hidden;
  min-width: 40px;
}

.line-number {
  display: block;
  height: 21px; /* 匹配 textarea 行高 */
}

.code-editor {
  flex: 1;
  margin: 0;
  padding: 12px;
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  resize: vertical;
  min-height: 120px;
  tab-size: 2;
}

.code-editor.with-line-numbers {
  padding-left: 8px;
}

.code-editor::placeholder {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

/* 深色主題適配 */
.dark .code-block-editor.selected {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .code-container {
  background-color: var(--bg-primary);
}

.dark .line-numbers {
  background-color: var(--bg-tertiary);
  color: var(--text-placeholder);
}

.dark .code-editor {
  color: #d4d4d4;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .code-editor {
    font-size: 13px;
  }
  
  .line-numbers {
    font-size: 13px;
    min-width: 35px;
  }
}

/* 打印樣式 */
@media print {
  .editor-toolbar {
    display: none;
  }
  
  .code-block-editor {
    border: 1px solid #ccc;
    background: white !important;
  }
  
  .code-container {
    background-color: #f8f9fa;
  }
  
  .code-editor {
    background: white;
    color: black;
  }
}

/* 語法高亮提示樣式 */
.code-editor:focus {
  background-color: rgba(64, 158, 255, 0.05);
}
</style>