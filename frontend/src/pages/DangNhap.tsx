import { useEffect, useRef, useState, type CSSProperties, type FormEvent } from 'react'
import { dangNhap, LoiApi, type NguoiDung } from '../api/auth'
import { Link } from 'react-router-dom'
import { dangHieuUng, NEN } from '../nen'
import NenHat from '../NenHat'

const CAU_PHU = 'Hệ thống quản lý vận tải'
const CAU_GIOI_THIEU =
  'Lập chuyến, theo dõi từng điểm dừng, giao hàng bằng quét mã và quyết toán theo chuyến.'

// Tách từng ký tự inline-block; 4 chữ cái cuối ("n", "t", "ả", "i") nổi lên lệch nhịp (-0.12em…-0.3em) khi tải trang
const NHO_CUOI: Record<number, { nho: string; tre: string }> = {
  [CAU_PHU.length - 5]: { nho: '-0.12em', tre: '0ms' },
  [CAU_PHU.length - 3]: { nho: '-0.18em', tre: '55ms' },
  [CAU_PHU.length - 2]: { nho: '-0.24em', tre: '110ms' },
  [CAU_PHU.length - 1]: { nho: '-0.3em', tre: '165ms' },
}
const KY_TU_PHU = [...CAU_PHU].map((ch, i) => ({ ch, i, nho: NHO_CUOI[i] }))

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
            <h1>Đăng nhập</h1>
            <p className="dn-phu" aria-label={CAU_PHU}>
              <span aria-hidden="true">
                {KY_TU_PHU.map(({ ch, i, nho }) => (
                  <span
                    key={i}
                    className={nho ? 'dn-kt dn-kt-cuoi' : 'dn-kt'}
                    style={
                      nho ? ({ '--nho': nho.nho, '--tre': nho.tre } as CSSProperties) : undefined
                    }
                  >
                    {ch}
                  </span>
                ))}
              </span>
            </p>
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
          </div>

          <p className="dn-chan">
            Khách hàng? <Link to="/tra-cuu">Tra cứu đơn hàng</Link>
          </p>
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
