import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5379,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8150',
        changeOrigin: true,
      },
    },
  },
})
