/**
 * 主題樣式注入器 - 確保深色模式樣式具有最高優先級
 */

export function injectDarkModeStyles() {
  // 移除舊的注入樣式
  const existingStyle = document.getElementById('dark-mode-override')
  if (existingStyle) {
    existingStyle.remove()
  }

  // 創建新的樣式元素
  const style = document.createElement('style')
  style.id = 'dark-mode-override'
  style.setAttribute('data-priority', '9999')
  
  // 使用更強力的CSS覆蓋策略
  style.textContent = `
    /* 深色模式強制覆蓋樣式 - 絕對最高優先級 */
    html.dark,
    html[data-theme="dark"],
    body.dark,
    .dark {
      color-scheme: dark !important;
      background-color: #111827 !important;
      color: #f9fafb !important;
    }

    /* 強制覆蓋所有 Element Plus 組件 */
    html.dark *[class*="el-"],
    html[data-theme="dark"] *[class*="el-"],
    body.dark *[class*="el-"],
    .dark *[class*="el-"] {
      color: #f9fafb !important;
    }

    /* Element Plus 表單標籤 - 絕對覆蓋 */
    html.dark .el-form-item__label,
    html[data-theme="dark"] .el-form-item__label,
    body.dark .el-form-item__label,
    .dark .el-form-item__label,
    html.dark label,
    html[data-theme="dark"] label,
    body.dark label,
    .dark label {
      color: #f1f5f9 !important;
    }

    /* Element Plus 輸入框 - 絕對覆蓋 */
    html.dark .el-input__wrapper,
    html[data-theme="dark"] .el-input__wrapper,
    body.dark .el-input__wrapper,
    .dark .el-input__wrapper {
      background-color: #374151 !important;
      border-color: #4b5563 !important;
      box-shadow: 0 0 0 1px #4b5563 inset !important;
    }

    html.dark .el-input__inner,
    html[data-theme="dark"] .el-input__inner,
    body.dark .el-input__inner,
    .dark .el-input__inner,
    html.dark input,
    html[data-theme="dark"] input,
    body.dark input,
    .dark input {
      color: #f9fafb !important;
      background-color: transparent !important;
    }

    html.dark .el-input__inner::placeholder,
    html[data-theme="dark"] .el-input__inner::placeholder,
    body.dark .el-input__inner::placeholder,
    .dark .el-input__inner::placeholder,
    html.dark input::placeholder,
    html[data-theme="dark"] input::placeholder,
    body.dark input::placeholder,
    .dark input::placeholder {
      color: #9ca3af !important;
    }

    /* Element Plus 選擇器 - 絕對覆蓋 */
    html.dark .el-select .el-input__wrapper,
    html[data-theme="dark"] .el-select .el-input__wrapper,
    body.dark .el-select .el-input__wrapper,
    .dark .el-select .el-input__wrapper {
      background-color: #374151 !important;
      border-color: #4b5563 !important;
    }

    html.dark .el-select-dropdown,
    html[data-theme="dark"] .el-select-dropdown,
    body.dark .el-select-dropdown,
    .dark .el-select-dropdown {
      background-color: #374151 !important;
      border-color: #4b5563 !important;
    }

    html.dark .el-select-dropdown__item,
    html[data-theme="dark"] .el-select-dropdown__item,
    body.dark .el-select-dropdown__item,
    .dark .el-select-dropdown__item {
      color: #f9fafb !important;
      background-color: transparent !important;
    }

    html.dark .el-select-dropdown__item:hover,
    html[data-theme="dark"] .el-select-dropdown__item:hover,
    body.dark .el-select-dropdown__item:hover,
    .dark .el-select-dropdown__item:hover {
      background-color: #4b5563 !important;
      color: #ffffff !important;
    }

    /* Element Plus 按鈕 - 絕對覆蓋 */
    html.dark .el-button,
    html[data-theme="dark"] .el-button,
    body.dark .el-button,
    .dark .el-button {
      border-color: #4b5563 !important;
      color: #f9fafb !important;
    }

    html.dark .el-button--default,
    html[data-theme="dark"] .el-button--default,
    body.dark .el-button--default,
    .dark .el-button--default {
      background-color: #374151 !important;
      color: #f9fafb !important;
      border-color: #4b5563 !important;
    }

    /* Element Plus 卡片 - 絕對覆蓋 */
    html.dark .el-card,
    html[data-theme="dark"] .el-card,
    body.dark .el-card,
    .dark .el-card {
      background-color: #1f2937 !important;
      border-color: #374151 !important;
      color: #f9fafb !important;
    }

    html.dark .el-card__body,
    html[data-theme="dark"] .el-card__body,
    body.dark .el-card__body,
    .dark .el-card__body {
      color: #f9fafb !important;
    }

    /* Element Plus 單選框 - 絕對覆蓋 */
    html.dark .el-radio__label,
    html[data-theme="dark"] .el-radio__label,
    body.dark .el-radio__label,
    .dark .el-radio__label {
      color: #f9fafb !important;
    }

    /* Element Plus 文字 - 絕對覆蓋 */
    html.dark .el-text,
    html[data-theme="dark"] .el-text,
    body.dark .el-text,
    .dark .el-text {
      color: #f9fafb !important;
    }

    /* 幫助文字 - 絕對覆蓋 */
    html.dark .help-text,
    html[data-theme="dark"] .help-text,
    body.dark .help-text,
    .dark .help-text {
      color: #94a3b8 !important;
    }

    /* 通用文字顏色 - 絕對覆蓋 */
    html.dark *,
    html[data-theme="dark"] *,
    body.dark *,
    .dark * {
      color: #f9fafb !important;
    }

    /* 邊框顏色 - 絕對覆蓋 */
    html.dark *,
    html[data-theme="dark"] *,
    body.dark *,
    .dark * {
      border-color: #4b5563 !important;
    }

    /* 強制覆蓋任何可能的白色文字 */
    html.dark *[style*="color"],
    html[data-theme="dark"] *[style*="color"],
    body.dark *[style*="color"],
    .dark *[style*="color"] {
      color: #f9fafb !important;
    }
  `

  // 插入到head的最後，確保最高優先級
  document.head.appendChild(style)
  
  console.log('🎨 深色模式樣式已強制注入')
}

export function removeDarkModeStyles() {
  const existingStyle = document.getElementById('dark-mode-override')
  if (existingStyle) {
    existingStyle.remove()
    console.log('🎨 深色模式樣式已移除')
  }
}