<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-illustration">
        <el-icon :size="120" color="#dcdfe6">
          <Warning />
        </el-icon>
      </div>
      
      <h1 class="error-title">404</h1>
      <h2 class="error-subtitle">頁面未找到</h2>
      <p class="error-message">
        抱歉，您訪問的頁面不存在或已被移動。
      </p>
      
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <el-icon><House /></el-icon>
          返回首頁
        </el-button>
        <el-button @click="goBack">
          <el-icon><Back /></el-icon>
          返回上頁
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Warning, House, Back } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.not-found {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.not-found-content {
  text-align: center;
  padding: 48px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin: 0 16px;
}

.error-illustration {
  margin-bottom: 24px;
}

.error-title {
  font-size: 72px;
  font-weight: 700;
  color: #dcdfe6;
  margin: 0 0 16px 0;
  line-height: 1;
}

.error-subtitle {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 16px 0;
}

.error-message {
  font-size: 16px;
  color: var(--el-text-color-regular);
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 480px) {
  .not-found-content {
    padding: 32px 24px;
  }
  
  .error-title {
    font-size: 48px;
  }
  
  .error-subtitle {
    font-size: 20px;
  }
  
  .error-actions {
    flex-direction: column;
  }
}
</style>