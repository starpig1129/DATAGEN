<template>
  <div class="settings-section">
    <div class="section-header">
      <div class="section-icon" v-if="icon">
        <el-icon :size="20">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="section-info">
        <h3 class="section-title">{{ title }}</h3>
        <p class="section-description" v-if="description">{{ description }}</p>
      </div>
      <div class="section-actions" v-if="$slots.actions">
        <slot name="actions" />
      </div>
    </div>
    
    <div class="section-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

interface Props {
  title: string
  description?: string
  icon?: Component
}

defineProps<Props>()
</script>

<style scoped>
.settings-section {
  @apply rounded-lg border overflow-hidden;
  background-color: var(--bg-secondary);
  border-color: var(--border-color-light);
}

.section-header {
  @apply flex items-start gap-4 p-6 border-b;
  border-color: var(--border-color-light);
}

.section-icon {
  @apply flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center;
  background-color: var(--bg-tertiary);
}

.section-icon .el-icon {
  @apply text-blue-600 dark:text-blue-400;
}

.section-info {
  @apply flex-1 min-w-0;
}

.section-title {
  @apply text-lg font-semibold text-gray-900 dark:text-white mb-1;
}

.section-description {
  @apply text-sm text-gray-600 dark:text-gray-400 m-0;
}

.section-actions {
  @apply flex-shrink-0;
}

.section-content {
  @apply p-6;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .section-header {
    @apply flex-col gap-3;
  }
  
  .section-icon {
    @apply self-start;
  }
  
  .section-actions {
    @apply self-stretch;
  }
}
</style>