import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

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
      resolvers: [ElementPlusResolver()],
      dts: true,
      eslintrc: {
        enabled: true
      }
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: true
    })
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
      '@assets': resolve(__dirname, 'src/assets')
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
          apollo: ['@apollo/client', {
          '@vue/apollo-composable': [
            'useQuery',
            'useMutation',
            'useSubscription',
            'useApolloClient',
            'useResult',
            'useLoading'
          ]
        }, 'graphql'],
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
    __VUE_PROD_DEVTOOLS__: false
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
    environment: 'jsdom'
  }
})