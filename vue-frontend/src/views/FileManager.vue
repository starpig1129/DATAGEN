<template>
  <div class="file-manager">
    <div class="page-header">
      <h1 class="page-title">文件管理</h1>
      <p class="page-description">管理和組織系統文件</p>
    </div>

    <div class="file-container">
      <el-card class="file-card" shadow="never">
        <div class="coming-soon">
          <el-icon :size="80" color="#f56c6c">
            <Folder />
          </el-icon>
          <h2>文件管理系統開發中</h2>
          <p>完整的文件上傳、管理和預覽功能即將推出</p>
          <div class="features">
            <el-tag v-for="feature in features" :key="feature" type="danger" class="feature-tag">
              {{ feature }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Folder } from '@element-plus/icons-vue'

const features = [
  '文件上傳',
  '目錄管理',
  '文件預覽',
  '權限控制',
  '版本管理'
]
</script>

<style scoped>
.file-manager {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 8px 0;
}

.page-description {
  color: var(--el-text-color-regular);
  margin: 0;
}

.file-container {
  height: calc(100vh - 200px);
}

.file-card {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.coming-soon {
  text-align: center;
  padding: 48px;
}

.coming-soon h2 {
  margin: 24px 0 16px 0;
  color: var(--el-text-color-primary);
}

.coming-soon p {
  color: var(--el-text-color-regular);
  margin-bottom: 32px;
}

.features {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-tag {
  margin: 4px;
}
</style>