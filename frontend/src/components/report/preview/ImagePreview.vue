<template>
  <figure class="image-preview" :class="alignmentClass">
    <div class="image-container" :style="containerStyle">
      <img
        :src="block.src"
        :alt="block.alt"
        :style="imageStyle"
        class="preview-image"
        @load="onImageLoad"
        @error="onImageError"
      />
      <div v-if="isLoading" class="image-placeholder">
        <el-icon class="loading-icon">
          <Loading />
        </el-icon>
        <span>載入中...</span>
      </div>
      <div v-if="hasError" class="image-error">
        <el-icon class="error-icon">
          <Picture />
        </el-icon>
        <span>圖片載入失敗</span>
      </div>
    </div>
    <figcaption v-if="block.caption" class="image-caption">
      {{ block.caption }}
    </figcaption>
  </figure>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Loading, Picture } from '@element-plus/icons-vue';
import type { ImageBlock } from '@/types/report';

interface Props {
  block: ImageBlock;
  index?: number;
}

const props = defineProps<Props>();

const isLoading = ref(true);
const hasError = ref(false);

const alignmentClass = computed(() => ({
  [`align-${props.block.align || 'center'}`]: true,
}));

const containerStyle = computed(() => {
  const style: Record<string, string> = {};
  
  if (props.block.width) {
    style.maxWidth = `${props.block.width}px`;
  }
  
  return style;
});

const imageStyle = computed(() => {
  const style: Record<string, string> = {
    width: '100%',
    height: 'auto',
  };
  
  if (props.block.width) {
    style.maxWidth = `${props.block.width}px`;
  }
  
  if (props.block.height) {
    style.maxHeight = `${props.block.height}px`;
    style.objectFit = 'contain';
  }
  
  return style;
});

const onImageLoad = () => {
  isLoading.value = false;
  hasError.value = false;
};

const onImageError = () => {
  isLoading.value = false;
  hasError.value = true;
};
</script>

<style scoped>
.image-preview {
  margin: 1.5rem 0;
  text-align: center;
}

.image-preview.align-left {
  text-align: left;
}

.image-preview.align-right {
  text-align: right;
}

.image-preview.align-center {
  text-align: center;
}

.image-container {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.preview-image {
  display: block;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.preview-image:hover {
  transform: scale(1.02);
}

.image-placeholder,
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  background: var(--el-fill-color-light);
  border: 2px dashed var(--el-border-color);
  border-radius: 8px;
  color: var(--el-text-color-regular);
}

.loading-icon,
.error-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

.error-icon {
  color: var(--el-color-warning);
}

.image-caption {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: var(--el-text-color-regular);
  font-style: italic;
  line-height: 1.4;
}

/* 深色主題適配 */
.dark .preview-image {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark .image-placeholder,
.dark .image-error {
  background: var(--el-fill-color-darker);
  border-color: var(--el-border-color);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .image-preview {
    margin: 1rem 0;
  }
  
  .image-container {
    max-width: 100%;
  }
  
  .preview-image {
    border-radius: 4px;
  }
  
  .image-placeholder,
  .image-error {
    min-height: 150px;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>