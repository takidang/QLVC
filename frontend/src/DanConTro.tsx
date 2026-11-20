import { useEffect, useRef, useState } from 'react'
import { dangHieuUng } from './nen'

const T_VE = 1180
const T_TONG = 1480

type ConTro = {
  ten: string
  mau: string
  vao: (vw: number, vh: number) => [number, number]
  ra: (vw: number, vh: number) => [number, number]
}

const BA_CON_TRO: readonly ConTro[] = [
  {
    ten: 'Điều phối',
    mau: 'var(--chay)',
    vao: () => [-48, 120],
    ra: (_, vh) => [-60, vh * 0.45],
  },
  {
    ten: 'Kế toán',
    mau: 'var(--cam)',
    vao: (vw) => [vw + 48, 110],
    ra: (vw, vh) => [vw + 60, vh * 0.4],
  },
  {
    ten: 'Tài xế',
    mau: 'var(--muc)',
    vao: (vw) => [vw * 0.52, -48],
    ra: (vw, vh) => [vw * 0.58, vh + 60],
  },
]

type MucTieu = {
  el: HTMLElement
  left: number
  top: number
  width: number
  height: number
  daMo: boolean
}

const diCong = (
  p0: [number, number],
  p2: [number, number],
  doCong: number,
  t: number,
): [number, number] => {
  const mx = (p0[0] + p2[0]) * 0.5
  const my = (p0[1] + p2[1]) * 0.5 - doCong
  const u = 1 - t
  return [
    u * u * p0[0] + 2 * u * t * mx + t * t * p2[0],
    u * u * p0[1] + 2 * u * t * my + t * t * p2[1],
  ]
}

const muot = (t: number) => 1 - Math.pow(1 - Math.min(Math.max(t, 0), 1), 3)

// Đàn con trỏ dựng trang (v4): chạy mỗi lần mở trang có gắn component (Tổng quan, Chuyến; Tài chốt 20/11), ≤ 1,6 s.
// 3 con trỏ SVG kèm nhãn Điều phối / Kế toán / Tài xế bay vào theo đường cong, kéo khung nét đứt kèm badge W × H
// trên 1–2 khối .kinh đầu tiên đang thấy rồi hiện khối thật; bấm / phím / cuộn bất kỳ lúc nào bỏ qua ngay.
export default function DanConTro() {
  const [xong, setXong] = useState(() => !dangHieuUng())
  const lopPhuRef = useRef<HTMLDivElement>(null)
  const troRefs = useRef<(HTMLDivElement | null)[]>([])
  const khungRefs = useRef<(HTMLDivElement | null)[]>([])
  const nhanRefs = useRef<(HTMLSpanElement | null)[]>([])

  useEffect(() => {
    const lopPhu = lopPhuRef.current
    if (!lopPhu || !dangHieuUng()) return

    const vw = window.innerWidth
    const vh = window.innerHeight
    const dsKhoi = Array.from(
      document.querySelectorAll<HTMLElement>('.trang .kinh, .noi-dung .kinh'),
    )
      .filter((el) => {
        const r = el.getBoundingClientRect()
        return r.width >= 50 && r.height >= 32 && r.top < vh - 16 && r.bottom > 16
      })
      .slice(0, 6)

    if (dsKhoi.length === 0) return

    const mucTieu: MucTieu[] = dsKhoi.map((el) => {
      const r = el.getBoundingClientRect()
      el.dataset.danTro = 'cho'
      return {
        el,
        left: r.left,
        top: r.top,
        width: r.width,
        height: r.height,
        daMo: false,
      }
    })

    // Chia mỗi con trỏ 1–2 khối .kinh đầu tiên đang thấy trên màn
    const nhom: MucTieu[][] = [[], [], []]
    mucTieu.forEach((m, idx) => {
      nhom[idx % 3].push(m)
    })
    for (let i = 0; i < 3; i++) {
      if (nhom[i].length === 0) nhom[i].push(mucTieu[i % mucTieu.length])
    }

    lopPhu.style.display = 'block'
    let raf = 0
    let daKetThuc = false
    const t0 = performance.now()

    const moKhoi = (m: MucTieu) => {
      if (m.daMo) return
      m.daMo = true
      m.el.dataset.danTro = 'hien'
    }

    // xongThat: chạy hết hoặc người dùng bỏ qua → gỡ lớp phủ khỏi DOM.
    // Unmount giữa chừng (đổi trang, StrictMode chạy effect hai lần ở dev) thì chỉ dọn, không setState.
    const donDep = (xongThat = true) => {
      if (daKetThuc) return
      daKetThuc = true
      if (raf) {
        cancelAnimationFrame(raf)
        raf = 0
      }
      for (const m of mucTieu) {
        delete m.el.dataset.danTro
      }
      window.removeEventListener('pointerdown', boQua, true)
      window.removeEventListener('keydown', boQua, true)
      window.removeEventListener('wheel', boQua, true)
      window.removeEventListener('scroll', boQua, true)
      document.removeEventListener('visibilitychange', khiAnTab)
      if (xongThat) setXong(true)
      else lopPhu.style.display = 'none'
    }

    function boQua() {
      donDep()
    }

    function khiAnTab() {
      if (document.hidden || !dangHieuUng()) donDep()
    }

    const buoc = (now: number) => {
      if (daKetThuc) return
      if (!dangHieuUng() || document.hidden) {
        donDep()
        return
      }
      const dt = now - t0
      if (dt >= T_TONG) {
        donDep()
        return
      }

      for (let i = 0; i < 3; i++) {
        const troEl = troRefs.current[i]
        const khungEl = khungRefs.current[i]
        const nhanEl = nhanRefs.current[i]
        if (!troEl || !khungEl || !nhanEl) continue

        const ds = nhom[i]
        const diemVao = BA_CON_TRO[i].vao(vw, vh)
        const diemRa = BA_CON_TRO[i].ra(vw, vh)
        const treConTro = i * 45
        const tHieuDung = Math.max(0, dt - treConTro)
        const tVeConTro = T_VE - treConTro

        if (tHieuDung < tVeConTro) {
          const doDaiMuc = tVeConTro / ds.length
          const chiSo = Math.min(ds.length - 1, Math.floor(tHieuDung / doDaiMuc))
          for (let j = 0; j < chiSo; j++) moKhoi(ds[j])

          const m = ds[chiSo]
          const pMuc = (tHieuDung - chiSo * doDaiMuc) / doDaiMuc
          const diemBatDau: [number, number] =
            chiSo === 0
              ? diemVao
              : [ds[chiSo - 1].left + ds[chiSo - 1].width, ds[chiSo - 1].top + ds[chiSo - 1].height]
          const gocTrenTrai: [number, number] = [m.left, m.top]
          const gocDuoiPhai: [number, number] = [m.left + m.width, m.top + m.height]

          if (pMuc < 0.38) {
            // Bay theo đường cong tới góc trên trái của khối
            const pBay = muot(pMuc / 0.38)
            const [cx, cy] = diCong(diemBatDau, gocTrenTrai, 54, pBay)
            troEl.style.opacity = '1'
            troEl.style.transform = `translate3d(${cx.toFixed(1)}px, ${cy.toFixed(1)}px, 0)`
            khungEl.style.opacity = '0'
          } else {
            // Kéo khung nét đứt từ góc trên trái tới góc dưới phải
            const pKeo = muot((pMuc - 0.38) / 0.62)
            const [cx, cy] = diCong(gocTrenTrai, gocDuoiPhai, 18, pKeo)
            const rw = Math.max(8, Math.round(m.width * pKeo))
            const rh = Math.max(8, Math.round(m.height * pKeo))
            troEl.style.opacity = '1'
            troEl.style.transform = `translate3d(${cx.toFixed(1)}px, ${cy.toFixed(1)}px, 0)`
            khungEl.style.opacity = '1'
            khungEl.style.transform = `translate3d(${m.left.toFixed(1)}px, ${m.top.toFixed(1)}px, 0)`
            khungEl.style.width = `${rw}px`
            khungEl.style.height = `${rh}px`
            nhanEl.textContent = `${rw} × ${rh}`
            if (pKeo >= 0.96) moKhoi(m)
          }
        } else {
          // Đã dựng xong các khối của con trỏ này -> hiện hết khối và bay ra ngoài mép
          for (const m of ds) moKhoi(m)
          khungEl.style.opacity = '0'
          const cuoi = ds[ds.length - 1]
          const tuDiem: [number, number] = [cuoi.left + cuoi.width, cuoi.top + cuoi.height]
          const pRa = muot((tHieuDung - tVeConTro) / (T_TONG - T_VE))
          const [cx, cy] = diCong(tuDiem, diemRa, -48, pRa)
          troEl.style.opacity = String(Math.max(0, 1 - pRa * 0.9))
          troEl.style.transform = `translate3d(${cx.toFixed(1)}px, ${cy.toFixed(1)}px, 0)`
        }
      }

      raf = requestAnimationFrame(buoc)
    }

    raf = requestAnimationFrame(buoc)
    window.addEventListener('pointerdown', boQua, { capture: true, passive: true })
    window.addEventListener('keydown', boQua, { capture: true })
    window.addEventListener('wheel', boQua, { capture: true, passive: true })
    window.addEventListener('scroll', boQua, { capture: true, passive: true })
    document.addEventListener('visibilitychange', khiAnTab)

    return () => donDep(false)
  }, [])

  if (xong) return null

  return (
    <div ref={lopPhuRef} className="dan-con-tro" aria-hidden="true" style={{ display: 'none' }}>
      {BA_CON_TRO.map((c, i) => (
        <div key={c.ten}>
          <div
            ref={(el) => {
              khungRefs.current[i] = el
            }}
            className="dct-khung"
            style={{ ['--mau-tro' as string]: c.mau, opacity: 0 }}
          >
            <span
              ref={(el) => {
                nhanRefs.current[i] = el
              }}
              className="dct-kt"
            />
          </div>
          <div
            ref={(el) => {
              troRefs.current[i] = el
            }}
            className="dct-tro"
            style={{ ['--mau-tro' as string]: c.mau, opacity: 0 }}
          >
            <svg viewBox="0 0 20 20" width="18" height="18">
              <path d="M3 2.5L16.5 9.2L10.2 11.1L7.8 17.2L3 2.5Z" />
            </svg>
            <span className="dct-nhan">{c.ten}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
