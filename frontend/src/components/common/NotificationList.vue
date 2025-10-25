<template>
  <div class="notification-list">
    <div v-if="notifications.length === 0" class="empty-state">
      <el-icon><Bell /></el-icon>
      <p>暫無通知</p>
    </div>
    
    <div v-else class="notifications">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.read }"
      >
        <div class="notification-icon">
          <el-icon :color="getNotificationColor(notification.type)">
            <component :is="getNotificationIcon(notification.type)" />
          </el-icon>
        </div>
        
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-message">{{ notification.message }}</div>
          <div class="notification-time">{{ formatTime(notification.createdAt) }}</div>
        </div>
        
        <div class="notification-actions">
          <el-button
            v-if="!notification.read"
            size="small"
            type="primary"
            text
            @click="markAsRead(notification.id)"
          >
            標記為已讀
          </el-button>
          
          <el-button
            size="small"
            type="danger"
            text
            @click="removeNotification(notification.id)"
          >
            刪除
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-if="notifications.length > 0" class="notification-footer">
      <el-button type="primary" text @click="markAllAsRead">
        全部標記為已讀
      </el-button>
      <el-button type="danger" text @click="clearAll">
        清空通知
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Bell,
  InfoFilled,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  read: boolean
  createdAt: Date
}

// 模擬通知數據
const notifications = ref<Notification[]>([
  {
    id: '1',
    type: 'success',
    title: '代理任務完成',
    message: '假設生成代理已成功完成數據分析任務',
    read: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 5)
  },
  {
    id: '2',
    type: 'warning',
    title: '系統性能警告',
    message: 'CPU 使用率超過 80%，建議檢查系統負載',
    read: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 15)
  },
  {
    id: '3',
    type: 'info',
    title: '新版本可用',
    message: '系統有新版本 v1.1.0 可供更新',
    read: true,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2)
  }
])

const getNotificationIcon = (type: string) => {
  const iconMap = {
    info: InfoFilled,
    success: SuccessFilled,
    warning: WarningFilled,
    error: CircleCloseFilled
  }
  return iconMap[type as keyof typeof iconMap] || InfoFilled
}

const getNotificationColor = (type: string) => {
  const colorMap = {
    info: '#409eff',
    success: '#67c23a',
    warning: '#e6a23c',
    error: '#f56c6c'
  }
  return colorMap[type as keyof typeof colorMap] || '#409eff'
}

const formatTime = (date: Date) => {
  return formatDistanceToNow(date, {
    addSuffix: true,
    locale: zhTW
  })
}

const markAsRead = (id: string) => {
  const notification = notifications.value.find(n => n.id === id)
  if (notification) {
    notification.read = true
  }
}

const removeNotification = (id: string) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
}

const clearAll = () => {
  notifications.value = []
}
</script>

<style scoped>
.notification-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--el-text-color-placeholder);
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.notifications {
  flex: 1;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: var(--el-bg-color-page);
}

.notification-item.unread {
  background-color: var(--el-color-primary-light-9);
}

.notification-icon {
  margin-right: 12px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.notification-message {
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.4;
  margin-bottom: 8px;
  word-break: break-word;
}

.notification-time {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.notification-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 8px;
  flex-shrink: 0;
}

.notification-footer {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: space-between;
  background-color: var(--el-bg-color-page);
}

/* 深色主題 */
.dark .notification-item:hover {
  background-color: var(--el-bg-color-page);
}

.dark .notification-item.unread {
  background-color: var(--el-color-primary-dark-2);
}

.dark .notification-footer {
  background-color: var(--el-bg-color-page);
  border-top-color: var(--el-border-color-dark);
}
</style>