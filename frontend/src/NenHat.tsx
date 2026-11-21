import { useEffect, useRef } from 'react'
import { dangHieuUng } from './nen'

type Hat = {
  bx: number
  by: number
  vx: number
  vy: number
  ox: number
  oy: number
  ovx: number
  ovy: number
  len: number
  day: number
  goc: number
  vGoc: number
  mau: string
  alpha: number
}

const BAN_KINH_CHUOT = 120

// Nền hạt (v4): canvas phủ vùng ảnh màn đăng nhập (pointer-events: none), ~60–90 hạt (màn ≤ 600 px: ≤ 35 hạt)
// dạng vệt ngắn màu --chay, --cam, --nhan-sang và trắng; trôi chậm, dạt khỏi chuột trong bán kính ~120 px rồi trôi về.
export default function NenHat() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const cv = canvasRef.current
    if (!cv || !dangHieuUng()) return
    const ctx = cv.getContext('2d')
    if (!ctx) return

    let w = 0
    let h = 0
    let dpr = 1
    let raf = 0
    let dangChay = false
    const chuot = { x: -9999, y: -9999 }
    let dsHat: Hat[] = []

    const layBangMau = () => {
      const cs = getComputedStyle(document.documentElement)
      const chay = cs.getPropertyValue('--chay').trim() || '#1f6f8b'
      const cam = cs.getPropertyValue('--cam').trim() || '#c2410c'
      const nhanSang = cs.getPropertyValue('--nhan-sang').trim() || '#86d4b6'
      return [chay, cam, nhanSang, '#ffffff']
    }

    const soHatMucTieu = () => (window.innerWidth <= 600 ? 30 : 76)

    const taoHat = (mau: string[]): Hat => {
      const tocDo = 0.16 + Math.random() * 0.28
      const huong = Math.random() * Math.PI * 2
      return {
        bx: Math.random() * Math.max(w, 1),
        by: Math.random() * Math.max(h, 1),
        vx: Math.cos(huong) * tocDo,
        vy: Math.sin(huong) * tocDo,
        ox: 0,
        oy: 0,
        ovx: 0,
        ovy: 0,
        len: 5 + Math.random() * 6,
        day: 1.6 + Math.random() * 1.1,
        goc: huong,
        vGoc: (Math.random() - 0.5) * 0.012,
        mau: mau[Math.floor(Math.random() * mau.length)],
        alpha: 0.45 + Math.random() * 0.4,
      }
    }

    const capNhatCo = () => {
      const r = cv.getBoundingClientRect()
      const nw = Math.max(1, Math.round(r.width))
      const nh = Math.max(1, Math.round(r.height))
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      cv.width = Math.round(nw * dpr)
      cv.height = Math.round(nh * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      const mau = layBangMau()
      const mucTieu = soHatMucTieu()
      if (dsHat.length === 0) {
        w = nw
        h = nh
        dsHat = Array.from({ length: mucTieu }, () => taoHat(mau))
      } else {
        const tlX = nw / Math.max(w, 1)
        const tlY = nh / Math.max(h, 1)
        w = nw
        h = nh
        for (const p of dsHat) {
          p.bx *= tlX
          p.by *= tlY
        }
        while (dsHat.length < mucTieu) dsHat.push(taoHat(mau))
        if (dsHat.length > mucTieu) dsHat.length = mucTieu
      }
    }

    const ve = () => {
      if (!dangChay) return
      if (!dangHieuUng() || document.hidden) {
        dung()
        return
      }
      ctx.clearRect(0, 0, w, h)
      ctx.lineCap = 'round'

      for (const p of dsHat) {
        p.bx += p.vx
        p.by += p.vy
        if (p.bx < -12) p.bx = w + 12
        else if (p.bx > w + 12) p.bx = -12
        if (p.by < -12) p.by = h + 12
        else if (p.by > h + 12) p.by = -12

        const xHienTai = p.bx + p.ox
        const yHienTai = p.by + p.oy
        const dx = xHienTai - chuot.x
        const dy = yHienTai - chuot.y
        const kc = Math.hypot(dx, dy)
        if (kc < BAN_KINH_CHUOT && kc > 0.01) {
          const luc = ((BAN_KINH_CHUOT - kc) / BAN_KINH_CHUOT) * 1.35
          p.ovx += (dx / kc) * luc
          p.ovy += (dy / kc) * luc
        }

        // Lực kéo đàn hồi đưa hạt trôi về quỹ đạo gốc sau khi dạt ra
        p.ovx += -p.ox * 0.042
        p.ovy += -p.oy * 0.042
        p.ovx *= 0.88
        p.ovy *= 0.88
        p.ox += p.ovx
        p.oy += p.ovy

        const tvx = p.vx + p.ovx
        const tvy = p.vy + p.ovy
        if (Math.hypot(p.ovx, p.ovy) > 0.25) {
          p.goc = Math.atan2(tvy, tvx)
        } else {
          p.goc += p.vGoc
        }

        const x = p.bx + p.ox
        const y = p.by + p.oy
        const nx = Math.cos(p.goc) * (p.len * 0.5)
        const ny = Math.sin(p.goc) * (p.len * 0.5)

        ctx.beginPath()
        ctx.strokeStyle = p.mau
        ctx.globalAlpha = p.alpha
        ctx.lineWidth = p.day
        ctx.moveTo(x - nx, y - ny)
        ctx.lineTo(x + nx, y + ny)
        ctx.stroke()
      }
      ctx.globalAlpha = 1
      raf = requestAnimationFrame(ve)
    }

    const batDau = () => {
      if (dangChay || document.hidden || !dangHieuUng()) return
      dangChay = true
      raf = requestAnimationFrame(ve)
    }

    const dung = () => {
      dangChay = false
      if (raf) {
        cancelAnimationFrame(raf)
        raf = 0
      }
    }

    const khiDiChuot = (e: MouseEvent) => {
      const r = cv.getBoundingClientRect()
      if (
        e.clientX >= r.left - BAN_KINH_CHUOT &&
        e.clientX <= r.right + BAN_KINH_CHUOT &&
        e.clientY >= r.top - BAN_KINH_CHUOT &&
        e.clientY <= r.bottom + BAN_KINH_CHUOT
      ) {
        chuot.x = e.clientX - r.left
        chuot.y = e.clientY - r.top
      } else {
        chuot.x = -9999
        chuot.y = -9999
      }
    }

    const khiRoiChuot = () => {
      chuot.x = -9999
      chuot.y = -9999
    }

    const khiAnHienTab = () => {
      if (document.hidden || !dangHieuUng()) dung()
      else batDau()
    }

    capNhatCo()
    batDau()

    const ro = new ResizeObserver(capNhatCo)
    ro.observe(cv)
    window.addEventListener('mousemove', khiDiChuot, { passive: true })
    window.addEventListener('mouseout', khiRoiChuot, { passive: true })
    window.addEventListener('blur', khiRoiChuot)
    document.addEventListener('visibilitychange', khiAnHienTab)

    return () => {
      dung()
      ro.disconnect()
      window.removeEventListener('mousemove', khiDiChuot)
      window.removeEventListener('mouseout', khiRoiChuot)
      window.removeEventListener('blur', khiRoiChuot)
      document.removeEventListener('visibilitychange', khiAnHienTab)
    }
  }, [])

  return <canvas ref={canvasRef} className="nen-hat" aria-hidden="true" />
}
