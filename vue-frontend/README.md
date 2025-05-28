# Vue 3 多代理數據分析系統前端

## 項目簡介

這是一個基於 Vue 3 + TypeScript + GraphQL 的現代化前端應用，用於多代理數據分析系統的用戶界面。

## 技術棧

### 核心框架
- **Vue 3** - 漸進式 JavaScript 框架
- **TypeScript** - JavaScript 的超集，提供類型安全
- **Vite** - 下一代前端構建工具

### 狀態管理與路由
- **Pinia** - Vue 的官方狀態管理庫
- **Vue Router 4** - Vue.js 的官方路由器

### UI 組件庫
- **Element Plus** - 基於 Vue 3 的組件庫
- **TailwindCSS** - 實用優先的 CSS 框架

### GraphQL 與 API
- **Apollo Client** - 全功能的 GraphQL 客戶端
- **GraphQL** - 數據查詢和操作語言
- **GraphQL WebSocket** - GraphQL 訂閱支持

### 數據視覺化
- **Plotly.js** - 交互式圖表庫
- **D3.js** - 數據驅動的文檔操作庫

### 開發工具
- **ESLint** - 代碼質量工具
- **Prettier** - 代碼格式化工具
- **Husky** - Git hooks 工具
- **Vitest** - 單元測試框架

## 項目結構

```
vue-frontend/
├── public/                          # 靜態資源
├── src/
│   ├── components/                  # 可復用組件
│   │   ├── base/                   # 基礎UI組件
│   │   ├── chat/                   # 聊天相關組件
│   │   ├── visualization/          # 視覺化組件
│   │   ├── agent/                  # 代理相關組件
│   │   ├── file/                   # 文件管理組件
│   │   ├── layout/                 # 佈局組件
│   │   └── common/                 # 通用組件
│   ├── views/                      # 頁面組件
│   ├── stores/                     # Pinia stores
│   ├── graphql/                    # GraphQL 查詢和訂閱
│   ├── composables/                # Vue 3 Composition 函數
│   ├── types/                      # TypeScript 類型定義
│   ├── utils/                      # 工具函數
│   ├── router/                     # Vue Router 配置
│   └── assets/                     # 資源文件
├── tests/                          # 測試文件
├── docs/                           # 文檔
└── 配置文件
```

## 開發環境設置

### 前置要求
- Node.js >= 18.0.0
- npm >= 9.0.0

### 安裝依賴
```bash
cd vue-frontend
npm install
```

### 開發模式
```bash
npm run dev
```
訪問 http://localhost:3000

### 構建生產版本
```bash
npm run build
```

### 類型檢查
```bash
npm run type-check
```

### 代碼檢查
```bash
npm run lint
npm run lint:fix
```

### 測試
```bash
npm run test           # 運行測試
npm run test:ui        # 測試 UI
npm run test:coverage  # 測試覆蓋率
```

## 環境配置

### 開發環境 (.env.development)
```env
VITE_APP_TITLE=多代理數據分析系統 - 開發環境
VITE_API_BASE_URL=http://localhost:5001
VITE_GRAPHQL_HTTP_URL=http://localhost:8000/graphql
VITE_GRAPHQL_WS_URL=ws://localhost:8000/graphql/ws
VITE_ENABLE_DEVTOOLS=true
```

### 生產環境 (.env.production)
```env
VITE_APP_TITLE=多代理數據分析系統
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_GRAPHQL_HTTP_URL=https://api.yourdomain.com/graphql
VITE_GRAPHQL_WS_URL=wss://api.yourdomain.com/graphql/ws
VITE_ENABLE_DEVTOOLS=false
```

## 功能特性

### 🎯 核心功能
- [x] 響應式佈局系統
- [x] 多主題支持（明亮/暗黑）
- [x] 國際化支持
- [ ] 實時聊天界面
- [ ] 代理狀態監控
- [ ] 數據視覺化
- [ ] 文件管理系統

### 🔧 技術特性
- [x] TypeScript 類型安全
- [x] GraphQL 客戶端
- [x] 組件懶加載
- [x] PWA 支持
- [ ] 離線模式
- [ ] 實時數據同步

### 📱 用戶體驗
- [x] 移動端適配
- [x] 無障礙輔助
- [x] 性能優化
- [ ] 手勢操作
- [ ] 快捷鍵支持

## 代碼規範

### 命名規範
- **組件名稱**: PascalCase (例: `ChatContainer.vue`)
- **文件名稱**: kebab-case (例: `chat-container.vue`)
- **函數/變數**: camelCase (例: `handleMessage`)
- **常數**: UPPER_SNAKE_CASE (例: `API_BASE_URL`)

### 文件組織
- 按功能模組組織，避免深層嵌套
- 每個組件目錄包含 `.vue`、`.ts`、`.scss` 文件
- 共享邏輯抽取到 `composables` 目錄

### Git 提交規範
```
feat: 新功能
fix: Bug 修復
docs: 文檔更新
style: 代碼格式調整
refactor: 代碼重構
test: 測試相關
chore: 構建/工具相關
```

## 性能優化

### 構建優化
- 代碼分割和懶加載
- Tree-shaking 移除未使用代碼
- 圖片壓縮和 WebP 格式
- CSS 清理和壓縮

### 運行時優化
- 組件緩存 (keep-alive)
- 虛擬列表處理大數據
- 防抖和節流處理
- 內存洩漏檢測

## 部署

### Docker 部署
```bash
# 構建 Docker 鏡像
docker build -t vue-frontend .

# 運行容器
docker run -p 3000:80 vue-frontend
```

### Nginx 配置
```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 貢獻指南

1. Fork 項目
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 創建 Pull Request

## 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 聯繫方式

如有問題或建議，請聯繫開發團隊或創建 Issue。

---

**多代理數據分析系統** © 2025

---

# English Documentation - Recent Settings Page Completion

## Settings Page Enhancement Summary

The settings page has been significantly enhanced with comprehensive form validation, improved error handling, and complete internationalization. This work was completed to provide a robust and user-friendly configuration interface for the multi-agent data analysis system.

### ✅ Completed Enhancements

#### 1. **Comprehensive Form Validation**
- **Real-time validation**: Implemented Element Plus form validation with immediate feedback
- **Cross-field validation**: Added validation for dependent settings and configuration conflicts
- **Async validation**: Token and connection validation with backend verification
- **Custom validation rules**: Specific rules for API keys, URLs, timeouts, and other settings

#### 2. **Enhanced Error Handling**
- **Network error detection**: Distinguishes between timeout, network, and server errors
- **Retry logic**: Exponential backoff for failed API requests
- **User-friendly messages**: Clear, actionable error messages in all supported languages
- **Graceful degradation**: Fallback behavior for failed operations

#### 3. **Complete Internationalization**
- **Full language coverage**: English, Simplified Chinese, and Traditional Chinese
- **No hard-coded text**: All user-facing text properly internationalized
- **Consistent terminology**: Unified translation approach across all components
- **Dynamic language switching**: Real-time language changes without page reload

#### 4. **API Integration Improvements**
- **Enhanced connection testing**: Detailed feedback with test history
- **Token validation**: Real-time API key verification
- **Improved error reporting**: Specific error codes and messages for different failure types
- **Settings synchronization**: Robust sync with backend with conflict resolution

#### 5. **Settings Store Enhancements**
- **Retry mechanism**: `makeApiRequest` method with configurable retry logic
- **Better state management**: Improved loading states and error tracking
- **Validation integration**: Form validation tied to store validation methods
- **Performance optimization**: Efficient caching and state updates

### 🔧 Technical Implementation Details

#### Enhanced Components

**SettingsSimple.vue**
- Added comprehensive form validation rules
- Implemented real-time validation feedback
- Enhanced save functionality with pre-validation checks
- Improved error handling with specific error types

**ConnectionTest.vue**
- Completely internationalized all text
- Enhanced error reporting with detailed feedback
- Added test history tracking
- Improved visual feedback for different states

**TokenInput.vue**
- Real-time token format validation
- Async token verification with backend
- Enhanced visual feedback for validation states
- Proper error handling and user guidance

**Settings Store (stores/settings.ts)**
- Added `makeApiRequest` method with retry logic
- Enhanced error handling with specific error types
- Improved connection testing with detailed feedback
- Better validation state management

#### Translation Coverage

**English (en-US.json)**
- Complete validation message translations
- Error handling message translations
- Settings interface text coverage
- Consistent terminology throughout

**Simplified Chinese (zh-CN.json)**
- Full translation parity with English
- Proper technical terminology
- Cultural adaptation where appropriate
- Consistent interface language

**Traditional Chinese (zh-TW.json)**
- Complete translation coverage
- Proper traditional character usage
- Consistent with simplified Chinese where applicable
- Culturally appropriate expressions

### 🚀 Key Features Implemented

1. **Form Validation System**
   - Required field validation
   - Format validation for URLs, API keys, emails
   - Range validation for numeric inputs
   - Custom validation rules for specific use cases

2. **Error Handling Framework**
   - Network timeout detection
   - Connection failure handling
   - Server error interpretation
   - User-friendly error presentation

3. **Internationalization Framework**
   - Dynamic language switching
   - Persistent language preferences
   - Complete text coverage
   - Cultural adaptation

4. **API Integration Layer**
   - Retry logic with exponential backoff
   - Request timeout handling
   - Error classification and reporting
   - Connection status monitoring

### 📈 Quality Improvements

- **Type Safety**: Full TypeScript coverage with strict typing
- **Performance**: Optimized API calls and state management
- **Accessibility**: Proper form labels and error announcements
- **User Experience**: Clear feedback and intuitive interactions
- **Maintainability**: Well-structured code with proper separation of concerns

### 🔍 Testing Recommendations

To verify the implementation:

1. **Form Validation**: Test all validation rules with various input combinations
2. **Error Handling**: Simulate network failures and server errors
3. **Internationalization**: Switch between all three languages and verify text coverage
4. **API Integration**: Test connection scenarios and token validation
5. **User Experience**: Verify smooth interactions and clear feedback

This enhancement significantly improves the robustness and usability of the settings interface, providing a solid foundation for user configuration management in the multi-agent data analysis system.