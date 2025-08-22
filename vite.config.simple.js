import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  
  build: {
    outDir: 'static/dist',
    assetsDir: 'assets'
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
      '/media': 'http://localhost:8000'
    }
  }
})
