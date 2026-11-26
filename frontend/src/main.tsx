import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './phong-cach-pixel.css'
import './nen'
import App from './App.tsx'
import { moDanKhiDongHop } from './moDanHop'

moDanKhiDongHop()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
