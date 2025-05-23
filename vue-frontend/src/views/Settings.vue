<template>
  <div class="settings">
    <div class="page-header">
      <h1 class="page-title">系統設置</h1>
      <p class="page-description">配置系統參數和個人偏好</p>
    </div>

    <div class="settings-container">
      <el-card class="settings-card" shadow="never">
        <div class="coming-soon">
          <el-icon :size="80" color="#909399">
            <Setting />
          </el-icon>
          <h2>系統設置功能開發中</h2>
          <p>個性化設置和系統配置界面即將上線</p>
          <div class="features">
            <el-tag v-for="feature in features" :key="feature" type="info" class="feature-tag">
              {{ feature }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Setting } from '@element-plus/icons-vue'

const features = [
  '主題設置',
  '語言切換',
  '通知配置',
  '用戶偏好',
  '系統參數'
]
</script>

<style scoped>
.settings {
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

.settings-container {
  height: calc(100vh - 200px);
}

.settings-card {
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