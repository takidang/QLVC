import { useEffect, useRef, useState, type CSSProperties, type FormEvent } from 'react'
import { dangNhap, LoiApi, type NguoiDung } from '../api/auth'
import { Link } from 'react-router-dom'
import { dangHieuUng, NEN } from '../nen'
import NenHat from '../NenHat'
import { LogoTK, TenThuongHieu } from '../LogoTK'

const CAU_GIOI_THIEU =
  'Lập chuyến, theo dõi từng điểm dừng, giao hàng bằng quét mã và quyết toán theo chuyến.'

export default function DangNhap({ onXong }: { onXong: (nd: NguoiDung) => void }) {
  const [ten, setTen] = useState('')
  const [matKhau, setMatKhau] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)
  const oMatKhau = useRef<HTMLInputElement>(null)
  const [soKyTu, setSoKyTu] = useState(() => (dangHieuUng() ? 0 : CAU_GIOI_THIEU.length))
  const [tro, setTro] = useState<'an' | 'go' | 'nhay'>(() => (dangHieuUng() ? 'go' : 'an'))

  useEffect(() => {
    if (!dangHieuUng()) return
    let i = 0
    let hNhay: ReturnType<typeof setTimeout> | undefined

    const ketThucGo = () => {
      clearInterval(hGo)
      if (hNhay) clearTimeout(hNhay)
      setSoKyTu(CAU_GIOI_THIEU.length)
      setTro('an')
    }

    const hGo = setInterval(() => {
      if (document.hidden || !dangHieuUng()) {
        ketThucGo()
        return
      }
      i += 1
      if (i >= CAU_GIOI_THIEU.length) {
        clearInterval(hGo)
        setSoKyTu(CAU_GIOI_THIEU.length)
        setTro('nhay')
        // Con trỏ nháy đúng 2 lần (2 × 450 ms) rồi ẩn hẳn
        hNhay = setTimeout(() => setTro('an'), 900)
      } else {
        setSoKyTu(i)
      }
    }, 35)

    const khiAnTab = () => {
      if (document.hidden || !dangHieuUng()) ketThucGo()
    }
    document.addEventListener('visibilitychange', khiAnTab)

    return () => {
      clearInterval(hGo)
      if (hNhay) clearTimeout(hNhay)
      document.removeEventListener('visibilitychange', khiAnTab)
    }
  }, [])

  async function gui(e: FormEvent) {
    e.preventDefault()
    // Tự kiểm thay bong bóng của trình duyệt (theo ngôn ngữ trình duyệt, Edge tiếng Anh hiện tiếng Anh)
    if (!ten.trim() || !matKhau) return setLoi('Vui lòng nhập đủ tên đăng nhập và mật khẩu')
    setLoi('')
    setDangGui(true)
    try {
      onXong(await dangNhap(ten.trim(), matKhau))
    } catch (err) {
      // Máy chủ đã trả câu tiếng Việt (sai thông tin, bị khóa, khóa tạm); 400 là thiếu trường
      setLoi(
        err instanceof LoiApi && err.status !== 400
          ? err.message
          : 'Vui lòng nhập đủ tên đăng nhập và mật khẩu',
      )
      // Nút bị khóa lúc gửi làm mất focus; đưa về ô mật khẩu để gõ lại ngay
      oMatKhau.current?.focus()
    } finally {
      setDangGui(false)
    }
  }

  return (
    <main className="dang-nhap">
      <div className="dn-khung">
        <form onSubmit={gui} noValidate>
          <div className="dn-giua">
            {/* Logo và tên thương hiệu ở đầu khối form (Pixel: thanh tiêu đề cửa sổ) (bản thường / Pixel do CSS chọn theo phong cách) */}
            <div className="dn-thuong-hieu">
              <LogoTK co={44} />
              <TenThuongHieu />
            </div>
            <h1>Đăng nhập</h1>
            <label>
              Tên đăng nhập
              <span className="dn-o">
                <input
                  value={ten}
                  onChange={(e) => setTen(e.target.value)}
                  autoComplete="username"
                  required
                />
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 20.5c0-3.6 3.6-5.5 8-5.5s8 1.9 8 5.5" />
                </svg>
              </span>
            </label>
            <label>
              Mật khẩu
              <span className="dn-o">
                <input
                  ref={oMatKhau}
                  type="password"
                  value={matKhau}
                  onChange={(e) => setMatKhau(e.target.value)}
                  autoComplete="current-password"
                  required
                />
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <rect x="5" y="10.5" width="14" height="9.5" rx="2" />
                  <path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5" />
                </svg>
              </span>
            </label>
            {loi && (
              <p role="alert" className="loi">
                {loi}
              </p>
            )}
            <button disabled={dangGui}>
              {dangGui ? 'Đang đăng nhập…' : 'Đăng nhập'}
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
            {/* Lối vào cho khách: đặt ngay dưới nút Đăng nhập cho khách dễ thấy, không cần đăng nhập */}
            <Link to="/tra-cuu" className="dn-tra-cuu">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="11" cy="11" r="6.5" />
                <path d="m16 16 4.5 4.5" />
              </svg>
              <span>
                <b>Khách hàng? Tra cứu đơn hàng</b>
                <small>Không cần đăng nhập: nhập mã đơn và 4 số cuối điện thoại.</small>
              </span>
              <i aria-hidden="true">→</i>
            </Link>
          </div>
        </form>

        <section className="dn-hinh" style={{ '--anh': `url(${NEN.anh})` } as CSSProperties}>
          <NenHat />
          <p aria-label={CAU_GIOI_THIEU}>
            <span aria-hidden="true">
              {CAU_GIOI_THIEU.slice(0, soKyTu)}
              {tro !== 'an' && <i className={tro === 'nhay' ? 'dn-con-tro nhay' : 'dn-con-tro'} />}
            </span>
          </p>
        </section>
      </div>
    </main>
  )
}
