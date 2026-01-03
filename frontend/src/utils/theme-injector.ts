/**
 * 主題樣式注入器 - 已簡化為僅處理基礎深色模式設定
 * 具體樣式由 main.css 中的 CSS 變數主導
 */

export function injectDarkModeStyles() {
  // 移除舊的注入樣式
  const existingStyle = document.getElementById('dark-mode-override')
  if (existingStyle) {
    existingStyle.remove()
  }

  // 創建新的樣式元素 (僅作為保險，主要靠 html.dark 類名)
  const style = document.createElement('style')
  style.id = 'dark-mode-override'
  
  style.textContent = `
    /* 深色模式基礎設定 - 由 main.css 變數接管 */
    html.dark {
      color-scheme: dark;
    }
  `

  document.head.appendChild(style)
  console.log('🎨 深色模式樣式已更新 (基於 CSS 變數)')
}

export function removeDarkModeStyles() {
  const existingStyle = document.getElementById('dark-mode-override')
  if (existingStyle) {
    existingStyle.remove()
  }
  console.log('🎨 深色模式樣式已移除')
}