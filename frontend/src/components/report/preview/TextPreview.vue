<template>
  <div class="text-preview" :style="textStyle">
    <p v-html="formattedContent" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { TextBlock } from '@/types/report';

interface Props {
  block: TextBlock;
  index?: number;
}

const props = defineProps<Props>();

const formattedContent = computed(() => {
  let content = props.block.content;
  
  if (props.block.formatting?.bold) {
    content = `<strong>${content}</strong>`;
  }
  
  if (props.block.formatting?.italic) {
    content = `<em>${content}</em>`;
  }
  
  if (props.block.formatting?.underline) {
    content = `<u>${content}</u>`;
  }
  
  return content;
});

const textStyle = computed(() => {
  const formatting = props.block.formatting;
  if (!formatting) return {};
  
  return {
    fontSize: formatting.fontSize ? `${formatting.fontSize}px` : undefined,
    color: formatting.color || undefined,
    textAlign: formatting.align || 'left',
  };
});
</script>

<style scoped>
.text-preview {
  line-height: 1.6;
  margin: 0;
}

.text-preview p {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 深色主題適配 */
.dark .text-preview {
  color: var(--el-text-color-primary);
}
</style>