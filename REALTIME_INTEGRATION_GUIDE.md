# 實時更新與 API 整合指南

## 概述

本系統實現了一個完整的實時更新和 API 整合解決方案，包含以下主要組件：

- **前端 Pinia Stores**: 管理應用狀態和實時數據
- **WebSocket 服務器**: 提供實時雙向通信
- **Flask API**: 提供 RESTful API 和 SSE 支持
- **集成管理器**: 協調各個組件的工作

## 架構圖

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue Frontend  │    │   Flask API      │    │  WebSocket      │
│                 │    │                  │    │  Server         │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Pinia       │◄┼────┼─│ REST API     │ │    │ │ Real-time   │ │
│ │ Stores      │ │    │ │              │ │    │ │ Updates     │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Components  │ │    │ │ SSE Stream   │ │    │ │ Message     │ │
│ │             │ │    │ │              │ │    │ │ Broadcasting│ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 快速開始

### 1. 安裝依賴

```bash
# Python 後端依賴
pip install flask flask-cors websockets gunicorn gevent

# 前端依賴 (在 vue-frontend 目錄下)
cd vue-frontend
npm install
```

### 2. 啟動系統

#### 方法一：使用集成啟動腳本 (推薦)

```bash
# 啟動完整系統 (API + WebSocket)
python run_server.py

# 同時啟動前端開發服務器
python run_server.py --with-frontend

# 僅啟動 API 服務器
python run_server.py --api-only

# 自定義端口
python run_server.py --flask-port 5001 --ws-port 8765 --frontend-port 3000
```

#### 方法二：分別啟動

```bash
# 啟動 Flask API (終端 1)
python app.py

# 啟動 WebSocket 服務器 (終端 2)
python websocket_server.py

# 啟動前端開發服務器 (終端 3)
cd vue-frontend
npm run dev
```

### 3. 驗證服務

- **API 服務器**: http://localhost:5001
- **WebSocket 服務器**: ws://localhost:8765
- **前端應用**: http://localhost:3000

## 核心組件詳解

### 1. Pinia Stores

#### App Store (`src/stores/app.ts`)
- 應用全局狀態管理
- API 請求重試機制
- 網路狀態監控
- 通知系統

```typescript
// 使用示例
const appStore = useAppStore()

// API 請求 (自動重試)
const data = await appStore.apiRequest('/api/files')

// 添加通知
appStore.addNotification({
  type: 'success',
  title: '操作成功',
  message: '文件上傳完成'
})
```

#### Real-time Store (`src/stores/realtime.ts`)
- WebSocket 連接管理
- 實時數據接收和處理
- 系統指標監控

```typescript
// 使用示例
const realtimeStore = useRealTimeStore()

// 初始化實時連接
await realtimeStore.initialize()

// 獲取系統指標
const metrics = realtimeStore.getSystemMetrics()

// 發送消息
realtimeStore.sendMessage({
  type: 'subscribe',
  subscription: 'agent_status'
})
```

#### Chat Store (`src/stores/chat.ts`)
- 聊天功能管理
- SSE 連接
- 消息處理和重試

```typescript
// 使用示例
const chatStore = useChatStore()

// 初始化聊天 (增強版)
await chatStore.initializeChatEnhanced()

// 發送消息 (自動重試)
await chatStore.sendMessageWithRetry('分析這個數據集')

// 批量處理消息
const results = await chatStore.processBatchMessages([
  '上傳文件',
  '開始分析',
  '生成報告'
])
```

#### File Store (`src/stores/file.ts`)
- 文件管理
- 上傳進度追蹤
- 實時文件狀態同步

```typescript
// 使用示例
const fileStore = useFileStore()

// 啟用自動同步
fileStore.enableAutoSync()

// 批量文件操作
await fileStore.batchFileOperation(['file1', 'file2'], 'delete')

// 高級搜索
const results = await fileStore.advancedSearch({
  query: 'data',
  fileType: 'text',
  sizeRange: { min: 0, max: 1024 * 1024 }
})
```

#### Data Store (`src/stores/data.ts`)
- 數據源管理
- 數據集緩存
- 自動同步

```typescript
// 使用示例
const dataStore = useDataStore()

// 添加數據源
const sourceId = dataStore.addDataSource({
  name: 'API 數據',
  type: 'api',
  url: '/api/dashboard/metrics'
})

// 從 API 加載數據
const datasetId = await dataStore.loadDataFromAPI(sourceId)

// 啟用實時更新
dataStore.enableRealtimeUpdates(sourceId)
```

#### Integration Store (`src/stores/integration.ts`)
- 系統集成管理
- 健康監控
- 事件協調

```typescript
// 使用示例
const integrationStore = useIntegrationStore()

// 初始化系統
await integrationStore.initialize()

// 手動同步所有系統
await integrationStore.syncAllSystems()

// 獲取系統信息
const info = integrationStore.getSystemInfo()
```

### 2. WebSocket 服務器 (`websocket_server.py`)

#### 功能特性
- 自動連接管理
- 消息廣播
- 心跳檢測
- 系統指標推送

#### 消息類型

```python
# 代理狀態更新
broadcast_agent_update(
  agent_id="search_agent",
  status="processing", 
  progress=75,
  task="搜尋相關文獻"
)

# 數據更新通知
broadcast_data_update(
  data_type="dashboard_metrics",
  data={"totalFiles": 23, "activeAgents": 2}
)

# 文件狀態更新
broadcast_file_update({
  "type": "file_uploaded",
  "file": file_info,
  "timestamp": datetime.now().isoformat()
})
```

### 3. Flask API 集成 (`app.py`)

#### 增強功能
- WebSocket 事件觸發
- 實時狀態廣播
- 檔案操作通知

```python
# 在 API 端點中觸發實時更新
@app.route('/api/files/upload', methods=['POST'])
def upload_files():
    # ... 文件上傳邏輯 ...
    
    # 廣播文件狀態更新
    broadcast_file_update({
        "type": "file_uploaded",
        "file": file_info,
        "timestamp": datetime.now().isoformat()
    })
    
    return jsonify({"status": "success"})
```

## 實時組件使用

### RealtimeStatus 組件

```vue
<template>
  <div>
    <!-- 實時狀態顯示 -->
    <RealtimeStatus />
  </div>
</template>

<script setup>
import RealtimeStatus from '@/components/realtime/RealtimeStatus.vue'
</script>
```

### 自定義實時更新

```vue
<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRealTimeStore } from '@/stores/realtime'

const realtimeStore = useRealTimeStore()

// 監聽特定類型的實時數據
const handleChartUpdate = (event) => {
  const { detail } = event
  if (detail.chartId === 'my-chart') {
    // 更新圖表數據
    updateChart(detail.data)
  }
}

onMounted(() => {
  // 註冊事件監聽器
  document.addEventListener('chart-data-update', handleChartUpdate)
})

onUnmounted(() => {
  // 清理事件監聽器
  document.removeEventListener('chart-data-update', handleChartUpdate)
})
</script>
```

## 最佳實踐

### 1. 錯誤處理

```typescript
// 在 store 中處理錯誤
try {
  await someAsyncOperation()
} catch (error) {
  // 記錄錯誤
  console.error('操作失敗:', error)
  
  // 通知用戶
  appStore.addNotification({
    type: 'error',
    title: '操作失敗',
    message: error.message
  })
  
  // 觸發錯誤事件
  document.dispatchEvent(new CustomEvent('store-error', {
    detail: { store: 'data', error: error.message }
  }))
}
```

### 2. 性能優化

```typescript
// 使用緩存減少 API 調用
const cachedData = await fileStore.fetchFiles(true) // 使用緩存

// 批量操作減少網路請求
await fileStore.batchFileOperation(selectedIds, 'delete')

// 智能預加載
await fileStore.preloadFiles(visibleFileIds)
```

### 3. 記憶體管理

```typescript
// 在組件銷毀時清理資源
onUnmounted(() => {
  // 停止自動同步
  fileStore.disableAutoSync()
  
  // 清理實時連接
  realtimeStore.destroy()
  
  // 清理集成管理器
  integrationStore.destroy()
})
```

## 故障排除

### 常見問題

#### 1. WebSocket 連接失敗
```bash
# 檢查 WebSocket 服務器是否運行
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:8765
```

#### 2. API 請求失敗
```bash
# 檢查 API 服務器狀態
curl http://localhost:5001/api/system/status
```

#### 3. 前端無法連接後端
```javascript
// 檢查 CORS 設置
// 在 app.py 中確保 CORS 正確配置
CORS(app, origins=["http://localhost:3000"])
```

### 調試模式

```bash
# 啟用調試模式
python run_server.py --debug

# 查看詳細日誌
FLASK_ENV=development python app.py
```

## 擴展指南

### 添加新的實時事件類型

1. **定義事件類型**
```typescript
// 在 stores/realtime.ts 中添加
export type CustomEventType = 'custom_event'
```

2. **後端發送事件**
```python
# 在 websocket_server.py 中添加
async def send_custom_event(self, data: Dict[str, Any]):
    custom_msg = WebSocketMessage(
        id=str(uuid.uuid4()),
        type="custom_event",
        data=data,
        timestamp=int(time.time() * 1000)
    )
    await self.broadcast(custom_msg)
```

3. **前端處理事件**
```typescript
// 在組件中監聽
document.addEventListener('custom-event', (event) => {
  const { detail } = event as CustomEvent
  // 處理自定義事件
})
```

### 添加新的 Store

```typescript
// stores/custom.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAppStore } from './app'

export const useCustomStore = defineStore('custom', () => {
  const appStore = useAppStore()
  
  // 狀態
  const customData = ref([])
  
  // 方法
  const fetchCustomData = async () => {
    try {
      const data = await appStore.apiRequest('/api/custom')
      customData.value = data
    } catch (error) {
      console.error('獲取自定義數據失敗:', error)
    }
  }
  
  return {
    customData,
    fetchCustomData
  }
})
```

## API 參考

### WebSocket 消息格式

```typescript
interface WebSocketMessage {
  id: string
  type: 'agent_status' | 'system_metrics' | 'data_update' | 'chart_data' | 'file_status'
  data: any
  timestamp: number
  source: string
}
```

### REST API 端點

- `GET /api/system/status` - 獲取系統狀態
- `GET /api/files` - 獲取文件列表
- `POST /api/files/upload` - 上傳文件
- `GET /api/state` - 獲取聊天狀態
- `POST /api/send_message` - 發送聊天消息
- `GET /stream` - SSE 事件流

## 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/new-feature`)
3. 提交變更 (`git commit -am 'Add new feature'`)
4. 推送分支 (`git push origin feature/new-feature`)
5. 創建 Pull Request

## 許可證

MIT License - 詳見 LICENSE 文件

---

更多問題請查看 [Issues](https://github.com/your-repo/issues) 或聯繫開發團隊。