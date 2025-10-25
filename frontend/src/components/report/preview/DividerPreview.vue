<template>
  <div class="divider-preview">
    <hr class="preview-divider" :class="dividerClasses" :style="dividerStyle" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { DividerBlock } from '@/types/report';

interface Props {
  block: DividerBlock;
  index?: number;
}

const props = defineProps<Props>();

const dividerClasses = computed(() => ({
  [`style-${props.block.style || 'solid'}`]: true,
}));

const dividerStyle = computed(() => ({
  borderTopWidth: `${props.block.thickness || 1}px`,
}));
</script>

<style scoped>
.divider-preview {
  margin: 2rem 0;
  width: 100%;
}

.preview-divider {
  width: 100%;
  border: none;
  border-top: 1px solid var(--el-border-color);
  margin: 0;
  padding: 0;
}

.preview-divider.style-solid {
  border-top-style: solid;
}

.preview-divider.style-dashed {
  border-top-style: dashed;
}

.preview-divider.style-dotted {
  border-top-style: dotted;
}

/* 深色主題適配 */
.dark .preview-divider {
  border-top-color: var(--el-border-color-dark);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .divider-preview {
    margin: 1.5rem 0;
  }
}
</style>