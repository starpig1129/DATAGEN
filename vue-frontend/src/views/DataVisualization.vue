<template>
  <div class="data-visualization">
    <div class="page-header">
      <h1 class="page-title">數據視覺化</h1>
      <p class="page-description">交互式數據分析和圖表展示</p>
    </div>

    <div class="visualization-container">
      <el-card class="visualization-card" shadow="never">
        <div class="coming-soon">
          <el-icon :size="80" color="#e6a23c">
            <DataAnalysis />
          </el-icon>
          <h2>數據視覺化功能開發中</h2>
          <p>基於 Plotly.js 的強大圖表分析工具即將發布</p>
          <div class="features">
            <el-tag v-for="feature in features" :key="feature" type="warning" class="feature-tag">
              {{ feature }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DataAnalysis } from '@element-plus/icons-vue'

const features = [
  '交互式圖表',
  '實時數據更新',
  '多圖表聯動',
  '數據導出',
  '自定義儀表板'
]
</script>

<style scoped>
.data-visualization {
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

.visualization-container {
  height: calc(100vh - 200px);
}

.visualization-card {
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