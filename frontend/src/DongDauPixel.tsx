import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { createPortal } from 'react-dom'
import { dangHieuUngPixel, phongCachDaLuu } from './nen'

type LoaiDau = 'luu' | 'huy'

type GhiNhoBam = {
  id: number
  hop: Element
  loai: LoaiDau
  x: number
  y: number
  luc: number
}

type DauHien = {
  id: number
  loai: LoaiDau
  x: number
  y: number
  ngayGio: string
}

const HAN_NHO_MS = 2000
const THOI_GIAN_DAU_MS = 920
// Kiểm chữ nút trước để nút chính dạng Xóa / Ngừng / Hủy / Xác nhận hủy vẫn đóng dấu đỏ "ĐÃ HỦY"
const MAU_CHU_HUY = /^(?:huy|thoi|xoa|ngung|tu choi|go|xac nhan (?:huy|xoa|ngung|tu choi|go))\b/

// Bỏ dấu tiếng Việt và gom khoảng trắng để so khớp chữ nút không phân biệt hoa thường/dấu
function chuanHoaChu(chu: string): string {
  return chu
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'd')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim()
}

// Phân loại nút trong .hop-thoai. Chỉ đóng dấu khi việc có tác động vào dữ liệu:
// - nút phụ / nút type="button" (Hủy, Thôi, Đóng…: chỉ thoát hộp, không gọi API): KHÔNG đóng dấu (null)
// - nút chính chữ Xóa / Ngừng / Hủy đơn / Xác nhận hủy…: dấu đỏ "ĐÃ HỦY" (có thay đổi dữ liệu)
// - nút chính còn lại (Lưu, Xác nhận…): dấu xanh "ĐÃ LƯU"
function phanLoaiNut(nut: HTMLButtonElement): LoaiDau | null {
  if (nut.classList.contains('phu') || nut.type === 'button') return null
  const chu = chuanHoaChu(nut.textContent ?? '')
  return MAU_CHU_HUY.test(chu) ? 'huy' : 'luu'
}

// Ngày giờ ngắn dd/mm HH:mm cho dòng nhỏ dưới dấu "ĐÃ LƯU"
function ngayGioNgan(d: Date): string {
  const hai = (n: number) => String(n).padStart(2, '0')
  const ngay = `${hai(d.getDate())}/${hai(d.getMonth() + 1)}`
  const gio = `${hai(d.getHours())}:${hai(d.getMinutes())}`
  return `${ngay} · ${gio}`
}

// Tâm hộp thoại lúc bấm, giữ trong khung nhìn để con dấu không bị cắt mép
function tamHopThoai(hop: Element): { x: number; y: number } {
  const r = hop.getBoundingClientRect()
  const leX = Math.min(110, window.innerWidth / 2)
  const leY = Math.min(60, window.innerHeight / 2)
  const x = Math.round(Math.min(Math.max(r.left + r.width / 2, leX), window.innerWidth - leX))
  const y = Math.round(Math.min(Math.max(r.top + r.height / 2, leY), window.innerHeight - leY))
  return { x, y }
}

// Hiệu ứng Pixel: con dấu đóng xuống khi hộp thoại .hop-thoai đóng SAU một thao tác thay đổi dữ liệu
// (Lưu = xanh teal, Xóa/Ngừng/Hủy đơn = đỏ). Bấm Hủy/Thôi/Đóng chỉ thoát hộp thì không đóng dấu.
export function DongDauPixel() {
  const bat = phongCachDaLuu() === 'pixel' && dangHieuUngPixel()
  const [dau, setDau] = useState<DauHien | null>(null)
  const ghiNhoRef = useRef<GhiNhoBam | null>(null)
  const henQuenRef = useRef<number | undefined>(undefined)
  const demIdRef = useRef(0)

  // Tự gỡ con dấu sau ~900 ms kể từ lúc hiện
  useEffect(() => {
    if (!dau) return
    const t = window.setTimeout(() => setDau(null), THOI_GIAN_DAU_MS)
    return () => window.clearTimeout(t)
  }, [dau])

  useEffect(() => {
    if (!bat) return

    const xoaGhiNho = () => {
      ghiNhoRef.current = null
      if (henQuenRef.current !== undefined) {
        window.clearTimeout(henQuenRef.current)
        henQuenRef.current = undefined
      }
    }

    const ghiNhan = (hop: Element, loai: LoaiDau) => {
      const { x, y } = tamHopThoai(hop)
      demIdRef.current += 1
      const id = demIdRef.current
      ghiNhoRef.current = { id, hop, loai, x, y, luc: Date.now() }
      if (henQuenRef.current !== undefined) window.clearTimeout(henQuenRef.current)
      henQuenRef.current = window.setTimeout(() => {
        if (ghiNhoRef.current?.id === id) ghiNhoRef.current = null
        henQuenRef.current = undefined
      }, HAN_NHO_MS)
    }

    // Lắng nghe pha capture để kịp ghi hình chữ nhật của .hop-thoai trước khi React gỡ nó
    const khiBam = (e: MouseEvent) => {
      if (phongCachDaLuu() !== 'pixel' || !dangHieuUngPixel()) return
      const mucTieu = e.target
      if (!(mucTieu instanceof Element)) return
      const hop = mucTieu.closest('.hop-thoai')
      if (!hop) {
        // Bấm ra ngoài hộp thoại (vd. nền mờ .nen-mo hoặc menu): quên cú bấm cũ tránh đóng dấu nhầm
        xoaGhiNho()
        return
      }
      const nut = mucTieu.closest('button')
      if (!nut || !hop.contains(nut) || nut.disabled) return
      if (nut.classList.contains('px-note-nut')) return
      const loai = phanLoaiNut(nut)
      // Thoát hộp không lưu gì: quên cú bấm cũ để hộp đóng đi không bị gán nhầm dấu
      if (!loai) return xoaGhiNho()
      ghiNhan(hop, loai)
    }

    // Bắt thêm sự kiện submit khi người dùng nhấn Enter trong form hộp thoại
    const khiGuiForm = (e: SubmitEvent) => {
      if (phongCachDaLuu() !== 'pixel' || !dangHieuUngPixel()) return
      const mucTieu = e.target
      if (!(mucTieu instanceof HTMLFormElement) || !mucTieu.classList.contains('hop-thoai')) return
      const nutGui =
        e.submitter instanceof HTMLButtonElement
          ? e.submitter
          : mucTieu.querySelector<HTMLButtonElement>('button[type="submit"], button:not([type])')
      const loai = nutGui ? phanLoaiNut(nutGui) : 'luu'
      if (!loai) return xoaGhiNho()
      ghiNhan(mucTieu, loai)
    }

    // Chỉ đóng dấu khi .hop-thoai thật sự bị gỡ khỏi DOM trong vòng 2 giây sau cú bấm
    const quanSat = new MutationObserver((ds) => {
      const ghiNho = ghiNhoRef.current
      if (!ghiNho) return
      if (Date.now() - ghiNho.luc > HAN_NHO_MS) {
        xoaGhiNho()
        return
      }
      let coGo = false
      for (let i = 0; i < ds.length; i++) {
        if (ds[i].removedNodes.length > 0) {
          coGo = true
          break
        }
      }
      if (!coGo || ghiNho.hop.isConnected) return
      xoaGhiNho()
      if (phongCachDaLuu() !== 'pixel' || !dangHieuUngPixel()) return
      demIdRef.current += 1
      setDau({
        id: demIdRef.current,
        loai: ghiNho.loai,
        x: ghiNho.x,
        y: ghiNho.y,
        ngayGio: ngayGioNgan(new Date()),
      })
    })

    document.addEventListener('click', khiBam, true)
    document.addEventListener('submit', khiGuiForm, true)
    quanSat.observe(document.body, { childList: true, subtree: true })

    return () => {
      document.removeEventListener('click', khiBam, true)
      document.removeEventListener('submit', khiGuiForm, true)
      quanSat.disconnect()
      xoaGhiNho()
    }
  }, [bat])

  if (!bat || !dau) return null

  const viTri = {
    '--px-dd-x': `${dau.x}px`,
    '--px-dd-y': `${dau.y}px`,
  } as CSSProperties

  return createPortal(
    <div className="px-dd-lop" style={viTri} aria-hidden="true">
      <div key={dau.id} className={dau.loai === 'luu' ? 'px-dd-dau luu' : 'px-dd-dau huy'}>
        <b>{dau.loai === 'luu' ? 'ĐÃ LƯU' : 'ĐÃ HỦY'}</b>
        {dau.loai === 'luu' && <small>{dau.ngayGio}</small>}
      </div>
    </div>,
    document.body,
  )
}

export default DongDauPixel
