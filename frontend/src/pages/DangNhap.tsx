import { useState, type FormEvent } from 'react'
import { dangNhap, LoiApi, type NguoiDung } from '../api/auth'

export default function DangNhap({ onXong }: { onXong: (nd: NguoiDung) => void }) {
  const [ten, setTen] = useState('')
  const [matKhau, setMatKhau] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
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
    } finally {
      setDangGui(false)
    }
  }

  return (
    <main className="dang-nhap">
      <div className="dn-khung">
        <section className="dn-hinh">
          <p>
            Lập chuyến, theo dõi từng điểm dừng, giao hàng bằng quét mã và quyết toán theo chuyến.
          </p>
        </section>

        <form onSubmit={gui}>
          <div className="dn-logo">
            <svg viewBox="0 0 26 26" aria-hidden="true">
              <path d="M4 20C9 20 8 6 13 6s4 14 9 14" />
              <circle cx="4" cy="20" r="1.8" />
              <circle className="dang-toi" cx="22" cy="20" r="1.8" />
            </svg>
            QLVC
          </div>

          <div className="dn-giua">
            <h1>Đăng nhập</h1>
            <p className="dn-phu">Hệ thống quản lý vận tải</p>
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

          <p className="dn-chan">Đồ án chuyên ngành · Nhóm 8</p>
        </form>
      </div>
    </main>
  )
}
