<template>
  <blockquote class="quote-preview">
    <div class="quote-content">
      <p class="quote-text">{{ block.content }}</p>
    </div>
    
    <footer v-if="block.author || block.source" class="quote-footer">
      <cite class="quote-citation">
        <span v-if="block.author" class="quote-author">— {{ block.author }}</span>
        <span v-if="block.source" class="quote-source">
          {{ block.author ? ', ' : '— ' }}{{ block.source }}
        </span>
      </cite>
    </footer>
  </blockquote>
</template>

<script setup lang="ts">
import type { QuoteBlock } from '@/types/report';

interface Props {
  block: QuoteBlock;
  index?: number;
}

defineProps<Props>();
</script>

<style scoped>
.quote-preview {
  margin: 2rem 0;
  padding: 1.5rem 2rem;
  background: var(--el-fill-color-extra-light);
  border-left: 4px solid var(--el-color-primary);
  border-radius: 0 8px 8px 0;
  position: relative;
  font-style: italic;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.quote-preview::before {
  content: '"';
  position: absolute;
  top: -0.5rem;
  left: 1rem;
  font-size: 4rem;
  font-weight: bold;
  color: var(--el-color-primary);
  opacity: 0.3;
  line-height: 1;
  font-family: Georgia, serif;
}

.quote-content {
  position: relative;
  z-index: 1;
}

.quote-text {
  margin: 0;
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  text-align: justify;
}

.quote-footer {
  margin-top: 1rem;
  text-align: right;
}

.quote-citation {
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  font-style: normal;
  font-weight: 500;
}

.quote-author {
  color: var(--el-text-color-primary);
}

.quote-source {
  color: var(--el-text-color-secondary);
}

/* 深色主題適配 */
.dark .quote-preview {
  background: var(--el-fill-color-darker);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.dark .quote-preview::before {
  color: var(--el-color-primary-light-3);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .quote-preview {
    margin: 1.5rem 0;
    padding: 1rem 1.5rem;
    border-radius: 0 4px 4px 0;
  }
  
  .quote-preview::before {
    font-size: 3rem;
    top: -0.25rem;
    left: 0.75rem;
  }
  
  .quote-text {
    font-size: 1rem;
  }
  
  .quote-citation {
    font-size: 0.8rem;
  }
}

/* 替代引用樣式變體 */
.quote-preview.style-minimal {
  background: transparent;
  border-left: 2px solid var(--el-border-color);
  box-shadow: none;
  padding: 1rem 1.5rem;
}

.quote-preview.style-minimal::before {
  display: none;
}

.quote-preview.style-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-left: 4px solid var(--el-color-primary);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quote-preview.style-highlight {
  background: linear-gradient(135deg, var(--el-color-primary-light-9) 0%, var(--el-color-success-light-9) 100%);
  border-left-color: var(--el-color-success);
}

/* 引用標記動畫 */
.quote-preview:hover::before {
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

/* 焦點樣式 */
.quote-preview:focus-within {
  border-left-color: var(--el-color-primary-light-3);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.dark .quote-preview:focus-within {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
}

/* 長引用樣式 */
.quote-preview .quote-text:first-letter {
  font-size: 1.3em;
  font-weight: bold;
  color: var(--el-color-primary);
}
</style>