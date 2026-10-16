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
      <form onSubmit={gui}>
        <h1>QLVC – Đăng nhập</h1>
        <label>
          Tên đăng nhập
          <input
            value={ten}
            onChange={(e) => setTen(e.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label>
          Mật khẩu
          <input
            type="password"
            value={matKhau}
            onChange={(e) => setMatKhau(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {loi && (
          <p role="alert" className="loi">
            {loi}
          </p>
        )}
        <button disabled={dangGui}>{dangGui ? 'Đang đăng nhập…' : 'Đăng nhập'}</button>
      </form>
    </main>
  )
}
