<template>
  <div class="chat-interface">
    <div class="page-header">
      <h1 class="page-title">聊天界面</h1>
      <p class="page-description">與多代理系統進行互動對話</p>
    </div>

    <div class="chat-container">
      <el-card class="chat-card" shadow="never">
        <div class="coming-soon">
          <el-icon :size="80" color="#409eff">
            <ChatDotRound />
          </el-icon>
          <h2>聊天功能開發中</h2>
          <p>強大的多代理對話界面即將上線</p>
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
import { ChatDotRound } from '@element-plus/icons-vue'

const features = [
  '實時對話',
  '代理協作',
  '決策支持',
  '智能建議',
  '多媒體支持'
]
</script>

<style scoped>
.chat-interface {
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

.chat-container {
  height: calc(100vh - 200px);
}

.chat-card {
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