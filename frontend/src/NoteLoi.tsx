import { useEffect, useId, useRef, useState } from 'react'

export type KieuNoteLoi = 'ghim' | 'nho'

type Props = {
  noiDung: string
  kieu?: KieuNoteLoi
}

// Đinh ghim pixel (lưới 12×12 nét sắc, màu lấy từ biến CSS Nostalgos)
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

// Tờ note báo lỗi ở phong cách Pixel:
// - 'ghim': hiện nguyên tờ note có đinh ghim ở khoảng trống bên cạnh khối lỗi
// - 'nho': hiện mẩu note đỏ nhỏ có dấu "!", rê chuột hoặc bấm/Enter thì bung tờ note đầy đủ
export function NoteLoi({ noiDung, kieu = 'ghim' }: Props) {
  const [bamMo, setBamMo] = useState(false)
  const [reChuot, setReChuot] = useState(false)
  const bocRef = useRef<HTMLDivElement>(null)
  const nutRef = useRef<HTMLButtonElement>(null)
  const idNote = useId()
  const mo = bamMo || reChuot

  // Bấm ra ngoài hoặc nhấn Esc thì thu gọn tờ note (chỉ lắng nghe khi đang mở)
  useEffect(() => {
    if (kieu !== 'nho' || !mo) return

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
  }, [kieu, mo])

  if (!noiDung) return null

  if (kieu === 'ghim') {
    return (
      <div role="alert" className="px-note px-note-ghim">
        <span className="px-note-dinh" aria-hidden="true">
          <DinhGhimPixel />
        </span>
        <span className="px-note-tieu-de">LỖI</span>
        <p className="px-note-chu">{noiDung}</p>
      </div>
    )
  }

  function bamNut() {
    if (bamMo) {
      setBamMo(false)
      setReChuot(false)
    } else {
      setBamMo(true)
    }
  }

  return (
    <div
      ref={bocRef}
      className="px-note-boc"
      onMouseEnter={() => setReChuot(true)}
      onMouseLeave={() => setReChuot(false)}
    >
      <button
        ref={nutRef}
        type="button"
        className="px-note-nut"
        aria-label="Xem chi tiết lỗi"
        aria-expanded={mo}
        aria-describedby={idNote}
        onClick={bamNut}
      >
        <span className="px-note-cham" aria-hidden="true">
          !
        </span>
      </button>
      <div
        id={idNote}
        role="alert"
        className={mo ? 'px-note px-note-pop mo' : 'px-note px-note-pop an'}
      >
        <span className="px-note-dinh" aria-hidden="true">
          <DinhGhimPixel />
        </span>
        <span className="px-note-tieu-de">LỖI</span>
        <p className="px-note-chu">{noiDung}</p>
      </div>
    </div>
  )
}

export default NoteLoi
