import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Proxy /api sang FastAPI để dev cùng origin như bản demo (cookie SameSite=Strict, kien-truc.md KT-02)
export default defineConfig({
  plugins: [react()],
  // host 127.0.0.1: mặc định Vite nghe "localhost", có máy chỉ ra ::1 nên http://127.0.0.1:5173 không mở được
  server: { host: '127.0.0.1', proxy: { '/api': 'http://127.0.0.1:8000' } },
})
