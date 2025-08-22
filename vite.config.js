import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@services': resolve(__dirname, 'src/services')
    }
  },
  
  build: {
    outDir: 'static/dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    target: 'es2015', // Целевая версия ES для совместимости
    cssCodeSplit: false, // Не разделяем CSS на чанки
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug']
      },
      mangle: {
        toplevel: true
      }
    },
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.js')
      },
      output: {
        format: 'iife', // Создаем IIFE для совместимости с браузером
        globals: {
          vue: 'Vue',
          'vue-router': 'VueRouter',
          pinia: 'Pinia',
          axios: 'axios'
        },
        // Убираем manualChunks для IIFE формата
      }
    },
    chunkSizeWarningLimit: 1000,
    reportCompressedSize: false
  },
  
  server: {
    port: 3002,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    },
    // Добавляем fallback для SPA маршрутизации
    historyApiFallback: true
  },
  
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  },
  
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios',
      'bootstrap',
      '@fortawesome/fontawesome-free',
      'vue-demi'
    ]
  },
  
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false
  },
  
  esbuild: {
    pure: ['console.log', 'console.info', 'console.debug']
  }
})
