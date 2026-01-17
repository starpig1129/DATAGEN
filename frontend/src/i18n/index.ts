import { createI18n } from 'vue-i18n'
import type { LanguageCode } from '@/types/settings'

// Async language loaders (kept for future lazy loading support)
// const zhTW = () => import('./locales/zh-TW.json')
// const zhCN = () => import('./locales/zh-CN.json')
// const enUS = () => import('./locales/en-US.json')

// 同步載入語言包
import zhTWMessages from './locales/zh-TW.json'
import zhCNMessages from './locales/zh-CN.json'
import enUSMessages from './locales/en-US.json'

// 語言配置
export const LANGUAGES: Record<LanguageCode, { name: string; nativeName: string; flag: string }> = {
  'zh-TW': {
    name: 'Traditional Chinese',
    nativeName: '繁體中文',
    flag: '🇹🇼'
  },
  'zh-CN': {
    name: 'Simplified Chinese',
    nativeName: '简体中文',
    flag: '🇨🇳'
  },
  'en-US': {
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸'
  }
}

// 創建i18n實例
export const i18n = createI18n({
  legacy: false,
  locale: 'zh-TW',
  fallbackLocale: 'en-US',
  messages: {
    'zh-TW': zhTWMessages as any,
    'zh-CN': zhCNMessages as any,
    'en-US': enUSMessages as any
  },
  numberFormats: {
    'zh-TW': {
      currency: {
        style: 'currency',
        currency: 'TWD',
        notation: 'standard'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      },
      percent: {
        style: 'percent',
        useGrouping: false
      }
    },
    'zh-CN': {
      currency: {
        style: 'currency',
        currency: 'CNY',
        notation: 'standard'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      },
      percent: {
        style: 'percent',
        useGrouping: false
      }
    },
    'en-US': {
      currency: {
        style: 'currency',
        currency: 'USD',
        notation: 'standard'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      },
      percent: {
        style: 'percent',
        useGrouping: false
      }
    }
  },
  datetimeFormats: {
    'zh-TW': {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      },
      long: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        weekday: 'short',
        hour: 'numeric',
        minute: 'numeric'
      }
    },
    'zh-CN': {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      },
      long: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        weekday: 'short',
        hour: 'numeric',
        minute: 'numeric'
      }
    },
    'en-US': {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      },
      long: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        weekday: 'short',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      }
    }
  }
})

// 切換語言
export async function setLocale(locale: LanguageCode) {
  i18n.global.locale.value = locale
  
  // 更新HTML語言屬性
  document.querySelector('html')?.setAttribute('lang', locale)
  
  // 可以在這裡添加動態載入語言包的邏輯
  console.log(`語言已切換為: ${LANGUAGES[locale].nativeName}`)
}

// 獲取當前語言
export function getCurrentLocale(): LanguageCode {
  return i18n.global.locale.value
}

// 檢查語言是否支援
export function isSupportedLocale(locale: string): locale is LanguageCode {
  return Object.keys(LANGUAGES).includes(locale)
}

export default i18n