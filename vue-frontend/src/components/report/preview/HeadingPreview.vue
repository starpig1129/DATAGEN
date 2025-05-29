<template>
  <component
    :is="headingTag"
    :id="headingId"
    class="heading-preview"
    :class="headingClass"
  >
    <span v-if="block.numbering && headingNumber" class="heading-number">
      {{ headingNumber }}
    </span>
    {{ block.content }}
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { HeadingBlock } from '@/types/report';

interface Props {
  block: HeadingBlock;
  index?: number;
}

const props = defineProps<Props>();

const headingTag = computed(() => `h${props.block.level}`);

const headingId = computed(() => `heading-${props.index}`);

const headingClass = computed(() => ({
  [`level-${props.block.level}`]: true,
  'numbered': props.block.numbering,
}));

const headingNumber = computed(() => {
  if (!props.block.numbering || props.index === undefined) return '';
  
  // 簡單的編號邏輯，實際應用中可能需要更複雜的邏輯
  return `${props.index + 1}.`;
});
</script>

<style scoped>
.heading-preview {
  margin: 1.5em 0 1em 0;
  font-weight: 600;
  line-height: 1.3;
  color: var(--el-text-color-primary);
}

.heading-preview.level-1 {
  font-size: 2.25rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid var(--el-border-color-light);
  padding-bottom: 0.5rem;
}

.heading-preview.level-2 {
  font-size: 1.875rem;
  margin-top: 2rem;
}

.heading-preview.level-3 {
  font-size: 1.5rem;
  margin-top: 1.75rem;
}

.heading-preview.level-4 {
  font-size: 1.25rem;
  margin-top: 1.5rem;
}

.heading-preview.level-5 {
  font-size: 1.125rem;
  margin-top: 1.25rem;
}

.heading-preview.level-6 {
  font-size: 1rem;
  margin-top: 1rem;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.heading-number {
  margin-right: 0.5rem;
  color: var(--el-color-primary);
}

/* 深色主題適配 */
.dark .heading-preview {
  color: var(--el-text-color-primary);
}

.dark .heading-preview.level-1 {
  border-bottom-color: var(--el-border-color);
}

.dark .heading-preview.level-6 {
  color: var(--el-text-color-regular);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .heading-preview.level-1 {
    font-size: 1.875rem;
  }
  
  .heading-preview.level-2 {
    font-size: 1.5rem;
  }
  
  .heading-preview.level-3 {
    font-size: 1.25rem;
  }
}
</style>