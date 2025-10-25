<template>
  <div class="agent-monitor">
    <div class="page-header">
      <h1 class="page-title">代理監控</h1>
      <p class="page-description">實時監控代理狀態和性能</p>
    </div>

    <div class="monitor-container">
      <el-card class="monitor-card" shadow="never">
        <div class="coming-soon">
          <el-icon :size="80" color="#67c23a">
            <Monitor />
          </el-icon>
          <h2>代理監控系統開發中</h2>
          <p>全面的代理監控和管理界面即將推出</p>
          <div class="features">
            <el-tag v-for="feature in features" :key="feature" type="success" class="feature-tag">
              {{ feature }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Monitor } from '@element-plus/icons-vue'

const features = [
  '實時狀態監控',
  '性能指標追蹤',
  '工作流可視化',
  '異常警報',
  '負載均衡'
]
</script>

<style scoped>
.agent-monitor {
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

.monitor-container {
  height: calc(100vh - 200px);
}

.monitor-card {
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