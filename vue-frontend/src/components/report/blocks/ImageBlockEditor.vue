<template>
  <div class="image-block-editor" :class="{ selected: isSelected }">
    <!-- 工具欄 -->
    <div v-if="isSelected" class="editor-toolbar">
      <el-upload
        :show-file-list="false"
        :before-upload="handleImageUpload"
        accept="image/*"
      >
        <el-button size="small" :icon="Picture">
          {{ block.src ? '更換圖片' : '上傳圖片' }}
        </el-button>
      </el-upload>
      
      <el-input
        v-if="block.src"
        v-model="imageAlt"
        size="small"
        placeholder="圖片描述"
        style="width: 150px; margin-left: 8px"
        @change="updateAlt"
      />
    </div>

    <!-- 圖片顯示 -->
    <div v-if="block.src" class="image-container">
      <img
        :src="block.src"
        :alt="block.alt"
        class="block-image"
        @load="handleImageLoad"
        @error="handleImageError"
      />
      <div v-if="block.caption" class="image-caption">
        {{ block.caption }}
      </div>
    </div>

    <!-- 佔位符 -->
    <div v-else class="image-placeholder">
      <el-icon class="placeholder-icon"><Picture /></el-icon>
      <p>點擊上傳圖片</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { Picture } from '@element-plus/icons-vue';
import type { ImageBlock } from '@/types/report';

// Props
interface Props {
  block: ImageBlock;
  isSelected: boolean;
}

const props = defineProps<Props>();

// Emits
interface Emits {
  (event: 'update', blockId: string, updates: Partial<ImageBlock>): void;
}

const emit = defineEmits<Emits>();

// 響應式狀態
const imageAlt = ref(props.block.alt || '');

// 方法
const handleImageUpload = (file: File) => {
  // 這裡應該實現實際的圖片上傳邏輯
  // 目前使用 FileReader 來創建本地預覽
  const reader = new FileReader();
  reader.onload = (e) => {
    const src = e.target?.result as string;
    emit('update', props.block.id, {
      src,
      alt: imageAlt.value || file.name,
      updatedAt: new Date().toISOString(),
    });
  };
  reader.readAsDataURL(file);
  
  return false; // 阻止自動上傳
};

const updateAlt = (alt: string) => {
  emit('update', props.block.id, {
    alt,
    updatedAt: new Date().toISOString(),
  });
};

const handleImageLoad = () => {
  // 圖片載入成功
};

const handleImageError = () => {
  ElMessage.error('圖片載入失敗');
};

// 監聽塊屬性變化
watch(
  () => props.block.alt,
  (newAlt) => {
    imageAlt.value = newAlt || '';
  }
);
</script>

<style scoped>
.image-block-editor {
  position: relative;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.image-block-editor.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.image-block-editor:hover {
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

.image-container {
  padding: 12px;
  text-align: center;
}

.block-image {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-caption {
  margin-top: 8px;
  font-size: 14px;
  color: var(--el-text-color-regular);
  font-style: italic;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--el-text-color-placeholder);
  background-color: var(--el-fill-color-lighter);
  border-radius: 0 0 6px 6px;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.image-placeholder p {
  margin: 0;
  font-size: 14px;
}

/* 深色主題適配 */
.dark .image-block-editor.selected {
  background-color: rgba(64, 158, 255, 0.1);
}

.dark .editor-toolbar {
  background-color: rgba(255, 255, 255, 0.05);
}

.dark .image-placeholder {
  background-color: rgba(255, 255, 255, 0.05);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .image-placeholder {
    padding: 24px;
  }
  
  .placeholder-icon {
    font-size: 36px;
  }
}

/* 打印樣式 */
@media print {
  .editor-toolbar {
    display: none;
  }
  
  .image-block-editor {
    border: none;
    background: none !important;
  }
  
  .image-container {
    padding: 0;
  }
}
</style>