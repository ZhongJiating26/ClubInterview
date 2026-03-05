import path from 'node:path'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss(), tsconfigPaths()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // 允许其他电脑访问
    proxy: {
      // 所有 API 接口统一加 /api 前缀，直接代理到后端，保留 /api 前缀
      '^/api/': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
