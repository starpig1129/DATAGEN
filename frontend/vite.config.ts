import { webcrypto } from 'crypto'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

// 同步應用 crypto polyfill - 必須在 Vite 配置解析之前完成
if (typeof globalThis.crypto === 'undefined') {
  // @ts-ignore
  globalThis.crypto = webcrypto
  console.log('Vite config: Applied crypto polyfill (full webcrypto object)')
} else if (typeof globalThis.crypto.getRandomValues !== 'function') {
  // @ts-ignore
  globalThis.crypto.getRandomValues = webcrypto.getRandomValues.bind(webcrypto)
  console.log('Vite config: Applied crypto.getRandomValues polyfill')
} else {
  console.log('Vite config: crypto.getRandomValues already available')
}

// https://vitejs.dev/config/
export default defineConfig({
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
        'pinia',
        {
          '@vue/apollo-composable': [
            'useQuery',
            'useMutation',
            'useSubscription',
            'useApolloClient',
            'useResult',
            'useLoading'
          ]
        }
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
      '@graphql': resolve(__dirname, 'src/graphql'),
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
    proxy: {
      '/graphql': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true
      },
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      },
      '/stream': {
        target: 'http://localhost:5001',
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
          apollo: ['@apollo/client', '@vue/apollo-composable', 'graphql'],
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
  }
})