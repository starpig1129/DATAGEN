import { webcrypto } from 'crypto'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

// 同步應用 crypto polyfill - 必須在 Vite 配置解析之前完成
// 強制應用 crypto polyfill for Node 16
if (!globalThis.crypto) {
  // @ts-ignore
  globalThis.crypto = webcrypto
}

if (!globalThis.crypto.getRandomValues) {
  // @ts-ignore
  globalThis.crypto.getRandomValues = (array) => webcrypto.getRandomValues(array)
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 載入環境變數
  const env = loadEnv(mode, process.cwd() + '/frontend', '')

  return {
  plugins: [
    vue({
      script: {
        defineModel: true,
        propsDestructure: true
      }
    }),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia'
      ],
      // 移除 ElementPlusResolver 避免自動導入衝突
      dts: true,
      eslintrc: {
        enabled: true
      }
    }),
    Components({
      // 移除 ElementPlusResolver 避免自動導入衝突
      dts: true
    }),
    // 添加 Node.js polyfills 插件來解決瀏覽器端的 Node.js 模組相容性
    nodePolyfills()
  ],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@types': resolve(__dirname, 'src/types'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@composables': resolve(__dirname, 'src/composables'),
      '@assets': resolve(__dirname, 'src/assets'),
      // 添加 buffer polyfill alias
      'buffer': 'buffer',
      // 直接重定向 crypto 模組到 Node.js crypto
      'crypto': 'crypto',
    },
  },

  server: {
    port: 3000,
    host: true,
    open: false,
    proxy: {
      '/api': {
        target: env.VITE_API_BASE_URL || 'http://localhost:5001',
        changeOrigin: true
      },
      '/stream': {
        target: env.VITE_SSE_URL || 'http://localhost:5001',
        changeOrigin: true
      }
    }
  },

  build: {
    target: 'es2015',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router'],
          pinia: ['pinia'],
          ui: ['element-plus', '@element-plus/icons-vue'],
          visualization: ['plotly.js', 'd3'],
          utils: ['marked', 'dompurify', 'dayjs', 'lodash-es']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    sourcemap: true
  },

  define: {
    __VUE_OPTIONS_API__: false,
    __VUE_PROD_DEVTOOLS__: false,
  },

  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/assets/styles/variables.scss" as *;`
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
  }
 }
})