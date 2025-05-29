<template>
  <div class="code-preview">
    <div class="code-header" v-if="block.language">
      <span class="language-label">{{ languageDisplay }}</span>
      <div class="code-actions">
        <el-button
          size="small"
          text
          :icon="CopyDocument"
          @click="copyCode"
          class="copy-button"
        >
          複製
        </el-button>
      </div>
    </div>
    
    <div class="code-container">
      <pre class="code-block" :class="codeClasses"><code ref="codeRef">{{ block.content }}</code></pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue';
import { CopyDocument } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import type { CodeBlock } from '@/types/report';

interface Props {
  block: CodeBlock;
  index?: number;
}

const props = defineProps<Props>();

const codeRef = ref<HTMLElement>();

const languageDisplay = computed(() => {
  const lang = props.block.language;
  if (!lang) return '';
  
  // 語言名稱映射
  const languageMap: Record<string, string> = {
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    python: 'Python',
    java: 'Java',
    cpp: 'C++',
    csharp: 'C#',
    php: 'PHP',
    go: 'Go',
    rust: 'Rust',
    sql: 'SQL',
    html: 'HTML',
    css: 'CSS',
    scss: 'SCSS',
    json: 'JSON',
    yaml: 'YAML',
    xml: 'XML',
    bash: 'Bash',
    shell: 'Shell',
    powershell: 'PowerShell',
    markdown: 'Markdown',
  };
  
  return languageMap[lang.toLowerCase()] || lang.toUpperCase();
});

const codeClasses = computed(() => ({
  'show-line-numbers': props.block.showLineNumbers ?? false,
  [`language-${props.block.language || 'text'}`]: true,
}));

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.block.content);
    ElMessage.success('代碼已複製到剪貼板');
  } catch (error) {
    console.error('複製失敗:', error);
    ElMessage.error('複製失敗');
  }
};

const highlightCode = () => {
  // 這裡可以整合語法高亮庫，如 Prism.js 或 highlight.js
  // 暫時使用簡單的實現
  if (codeRef.value && props.block.language) {
    // TODO: 整合語法高亮
  }
};

onMounted(async () => {
  await nextTick();
  highlightCode();
});
</script>

<style scoped>
.code-preview {
  margin: 1.5rem 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-fill-color-extra-light);
  border: 1px solid var(--el-border-color-lighter);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.language-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--el-text-color-regular);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.code-actions {
  display: flex;
  gap: 8px;
}

.copy-button {
  font-size: 0.75rem;
  padding: 4px 8px;
  height: auto;
}

.code-container {
  position: relative;
  overflow-x: auto;
}

.code-block {
  margin: 0;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  background: transparent;
  overflow-x: auto;
  white-space: pre;
  counter-reset: line-number;
}

.code-block.show-line-numbers {
  padding-left: 3.5rem;
  counter-reset: line-number;
}

.code-block.show-line-numbers::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3rem;
  background: var(--el-fill-color-darker);
  border-right: 1px solid var(--el-border-color-light);
}

/* 行號樣式 */
.show-line-numbers code {
  display: block;
  position: relative;
}

.show-line-numbers code::before {
  content: counter(line-number);
  counter-increment: line-number;
  position: absolute;
  left: -3rem;
  width: 2.5rem;
  text-align: right;
  color: var(--el-text-color-placeholder);
  font-size: 0.75rem;
  line-height: inherit;
  padding-right: 0.5rem;
}

/* 語法高亮基礎樣式 */
.language-javascript code,
.language-typescript code {
  color: #2d3748;
}

.language-python code {
  color: #3776ab;
}

.language-json code {
  color: #005cc5;
}

.language-css code,
.language-scss code {
  color: #1572b6;
}

.language-html code,
.language-xml code {
  color: #e34c26;
}

.language-sql code {
  color: #336791;
}

.language-bash code,
.language-shell code {
  color: #4eaa25;
}

/* 深色主題適配 */
.dark .code-preview {
  background: var(--el-fill-color-darker);
  border-color: var(--el-border-color);
}

.dark .code-header {
  background: var(--el-fill-color-dark);
  border-bottom-color: var(--el-border-color);
}

.dark .code-block {
  color: var(--el-text-color-primary);
}

.dark .show-line-numbers::before {
  background: var(--el-fill-color-extra-dark);
  border-right-color: var(--el-border-color);
}

.dark .show-line-numbers code::before {
  color: var(--el-text-color-disabled);
}

/* 深色主題語法高亮 */
.dark .language-javascript code,
.dark .language-typescript code {
  color: #f7df1e;
}

.dark .language-python code {
  color: #ffd43b;
}

.dark .language-json code {
  color: #79b8ff;
}

.dark .language-css code,
.dark .language-scss code {
  color: #264de4;
}

.dark .language-html code,
.dark .language-xml code {
  color: #ff6347;
}

.dark .language-sql code {
  color: #87ceeb;
}

.dark .language-bash code,
.dark .language-shell code {
  color: #98fb98;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .code-preview {
    margin: 1rem 0;
    border-radius: 4px;
  }
  
  .code-header {
    padding: 6px 12px;
  }
  
  .code-block {
    padding: 12px;
    font-size: 0.8rem;
  }
  
  .code-block.show-line-numbers {
    padding-left: 2.5rem;
  }
  
  .show-line-numbers::before {
    width: 2rem;
  }
  
  .show-line-numbers code::before {
    left: -2rem;
    width: 1.5rem;
  }
}

/* 滾動條樣式 */
.code-container::-webkit-scrollbar {
  height: 8px;
}

.code-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

.code-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.code-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}
</style>