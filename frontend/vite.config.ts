import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Proxy /api sang FastAPI để dev cùng origin như bản demo (cookie SameSite=Strict, kien-truc.md KT-02)
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
