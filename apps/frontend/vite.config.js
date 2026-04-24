import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Prevent full-page reload on file changes outside src/
    watch: {
      ignored: ['**/node_modules/**', '**/dist/**'],
    },
  },
})
