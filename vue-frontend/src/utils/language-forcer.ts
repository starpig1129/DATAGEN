/**
 * 語言強制更新器 - 確保語言變更傳播到所有組件
 */

export function setupLanguageForcer() {
  // 監聽語言變更事件
  window.addEventListener('language-changed', (event: any) => {
    const { language } = event.detail
    console.log('🌐 收到語言變更事件:', language)
    
    // 強制更新所有可能的語言相關屬性
    document.documentElement.setAttribute('lang', language)
    document.body.setAttribute('lang', language)
    
    // 觸發 Vue 重新渲染
    setTimeout(() => {
      // 強制觸發 window resize 事件來刷新組件
      window.dispatchEvent(new Event('resize'))
      
      // 強制觸發 DOM 變更
      const event = new CustomEvent('vue-force-update')
      document.dispatchEvent(event)
      
    }, 100)
  })
  
  console.log('🌐 語言強制更新器已啟動')
}

export function forceLanguageUpdate(language: string) {
  // 直接強制更新語言
  document.documentElement.setAttribute('lang', language)
  document.body.setAttribute('lang', language)
  
  // 更新 HTML meta 標籤
  const metaLang = document.querySelector('meta[http-equiv="Content-Language"]')
  if (metaLang) {
    metaLang.setAttribute('content', language)
  } else {
    const meta = document.createElement('meta')
    meta.setAttribute('http-equiv', 'Content-Language')
    meta.setAttribute('content', language)
    document.head.appendChild(meta)
  }
  
  // 強制刷新頁面語言環境
  if (language === 'zh-TW') {
    document.documentElement.style.setProperty('--language', '"zh-TW"')
  } else if (language === 'en-US') {
    document.documentElement.style.setProperty('--language', '"en-US"')
  }
  
  console.log('🌐 語言已強制更新為:', language)
}