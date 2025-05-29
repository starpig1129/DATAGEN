# 報告組件目錄

這個目錄包含所有與報告生成和編輯相關的組件。

## 組件結構

### 主要組件
- `ReportPreview.vue` - 報告預覽組件
- `NewReportDialog.vue` - 新建報告對話框
- `ExportDialog.vue` - 報告導出對話框

### 內容塊編輯器 (blocks/)
- `TextBlockEditor.vue` - 文本塊編輯器
- `HeadingBlockEditor.vue` - 標題塊編輯器
- `ImageBlockEditor.vue` - 圖片塊編輯器
- `ChartBlockEditor.vue` - 圖表塊編輯器
- `TableBlockEditor.vue` - 表格塊編輯器
- `DividerBlockEditor.vue` - 分隔線塊編輯器
- `CodeBlockEditor.vue` - 代碼塊編輯器
- `QuoteBlockEditor.vue` - 引用塊編輯器

## 設計原則

1. **模塊化**: 每個內容塊類型都有獨立的編輯器組件
2. **響應式**: 所有組件都支援響應式設計
3. **可訪問性**: 遵循 WCAG 2.1 可訪問性標準
4. **性能優化**: 使用懶加載和虛擬滾動等技術
5. **類型安全**: 完整的 TypeScript 類型定義

## 使用指南

### 添加新的內容塊類型

1. 在 `types/report.ts` 中定義新的塊類型
2. 在 `blocks/` 目錄下創建對應的編輯器組件
3. 在 `ReportGenerator.vue` 中註冊新組件
4. 更新 `stores/report.ts` 中的塊創建邏輯

### 自定義主題

報告組件支援多種主題，可以通過修改 CSS 變量來自定義外觀。

### 國際化

所有文本都通過 vue-i18n 進行國際化處理，支援多語言切換。