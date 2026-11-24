import { useEffect, useId, useRef, useState, type ReactNode } from 'react'
import { phongCachDaLuu } from './nen'

type Props = {
  tieuDe: string
  soMuc?: number
  children: ReactNode
}

// Đinh ghim pixel (lưới 12×12 nét sắc, dùng lại lớp màu từ NoteLoi)
function DinhGhimPixel() {
  return (
    <svg
      className="px-note-ghim-ic"
      viewBox="0 0 12 12"
      width={14}
      height={14}
      shapeRendering="crispEdges"
      aria-hidden="true"
    >
      <rect x={3} y={0} width={6} height={1} className="px-note-ghim-vien" />
      <rect x={2} y={1} width={8} height={4} className="px-note-ghim-vien" />
      <rect x={3} y={1} width={6} height={3} className="px-note-ghim-dau" />
      <rect x={4} y={1} width={2} height={1} className="px-note-ghim-sang" />
      <rect x={4} y={5} width={4} height={2} className="px-note-ghim-vien" />
      <rect x={5} y={5} width={2} height={2} className="px-note-ghim-dau" />
      <rect x={5} y={7} width={2} height={4} className="px-note-ghim-vien" />
      <rect x={4} y={10} width={4} height={1} className="px-note-ghim-bong" />
    </svg>
  )
}

// Khối cảnh báo / lưu ý dạng "tờ note ghim" ở phong cách Pixel:
// ngoài Pixel trả thẳng children như cũ; ở Pixel hiện mẩu note vàng bơ ghim vào,
// rê chuột hoặc bấm/Enter thì bung trang giấy pixel chứa nội dung bên trong
export function NoteCanhBao({ tieuDe, soMuc, children }: Props) {
  const [bamMo, setBamMo] = useState(false)
  const [reChuot, setReChuot] = useState(false)
  const bocRef = useRef<HTMLDivElement>(null)
  const nutRef = useRef<HTMLButtonElement>(null)
  const idNote = useId()
  const laPixel = phongCachDaLuu() === 'pixel'
  const mo = bamMo || reChuot

  // Bấm ra ngoài hoặc nhấn Esc thì thu gọn tờ giấy (chỉ lắng nghe khi đang mở ở Pixel)
  useEffect(() => {
    if (!laPixel || !mo) return

    const khiBamNgoai = (e: PointerEvent) => {
      if (bocRef.current && e.target instanceof Node && !bocRef.current.contains(e.target)) {
        setBamMo(false)
        setReChuot(false)
      }
    }

    const khiNhanPhim = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setBamMo(false)
        setReChuot(false)
        if (bocRef.current?.contains(document.activeElement)) {
          nutRef.current?.focus()
        }
      }
    }

    document.addEventListener('pointerdown', khiBamNgoai)
    document.addEventListener('keydown', khiNhanPhim)
    return () => {
      document.removeEventListener('pointerdown', khiBamNgoai)
      document.removeEventListener('keydown', khiNhanPhim)
    }
  }, [laPixel, mo])

  if (!laPixel) return <>{children}</>

  const nhan = soMuc !== undefined ? `${tieuDe} · ${soMuc}` : tieuDe

  function bamNut() {
    if (bamMo) {
      setBamMo(false)
      setReChuot(false)
    } else {
      setBamMo(true)
    }
  }

  return (
    <div className="px-cb-neo">
      <div
        ref={bocRef}
        className="px-cb-boc"
        onMouseEnter={() => setReChuot(true)}
        onMouseLeave={() => setReChuot(false)}
      >
        <button
          ref={nutRef}
          type="button"
          className="px-cb-nut"
          aria-expanded={mo}
          aria-describedby={idNote}
          onClick={bamNut}
        >
          <span className="px-note-dinh" aria-hidden="true">
            <DinhGhimPixel />
          </span>
          <span className="px-cb-cham" aria-hidden="true">
            !
          </span>
          <span className="px-cb-nhan">{nhan}</span>
          <span className="px-cb-mui" aria-hidden="true">
            {mo ? '▲' : '▼'}
          </span>
        </button>
        <div
          id={idNote}
          className={mo ? 'px-note px-note-pop px-cb-pop mo' : 'px-note px-note-pop px-cb-pop an'}
          onFocus={() => setBamMo(true)}
        >
          <span className="px-note-dinh" aria-hidden="true">
            <DinhGhimPixel />
          </span>
          <div className="px-cb-pop-dau">
            <span className="px-note-tieu-de">{nhan}</span>
            <button
              type="button"
              className="px-cb-dong"
              tabIndex={mo ? 0 : -1}
              aria-label="Đóng"
              onClick={() => {
                setBamMo(false)
                setReChuot(false)
                nutRef.current?.focus()
              }}
            >
              ×
            </button>
          </div>
          <div className="px-cb-pop-than">{children}</div>
        </div>
      </div>
    </div>
  )
}

export default NoteCanhBao
