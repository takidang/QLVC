import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import { doiMatKhau, LoiApi, type NguoiDung } from '../api/auth'
import { DauDanhMuc } from './danh-muc'

// Trang Tài khoản (mọi vai trò): thông tin chỉ đọc lấy từ NguoiDung đang có và form đổi mật khẩu UC-35.
export default function TaiKhoan({ nd, tenVaiTro }: { nd: NguoiDung; tenVaiTro: string }) {
  return (
    <section className="noi-dung cd-trang">
      {nd.vai_tro === 'TAI_XE' && (
        <Link to="/tai-xe/chuyen" className="ct-ve">
          ← Chuyến của tôi
        </Link>
      )}
      <DauDanhMuc tieuDe="Tài khoản" phu="Thông tin tài khoản và đổi mật khẩu đăng nhập." />

      <div className="cd-cot">
        <section className="kinh cd-khoi" aria-labelledby="tk-thong-tin">
          <h2 id="tk-thong-tin">Thông tin cá nhân</h2>
          <dl className="tk-tt">
            <div>
              <dt>Họ tên</dt>
              <dd>{nd.ho_ten}</dd>
            </div>
            <div>
              <dt>Vai trò</dt>
              <dd>{tenVaiTro}</dd>
            </div>
          </dl>
        </section>

        <section className="kinh cd-khoi" aria-labelledby="tk-doi-mk">
          <h2 id="tk-doi-mk">Đổi mật khẩu</h2>
          <p className="ghi-chu">Mật khẩu mới từ 8 đến 200 ký tự, khác mật khẩu hiện tại.</p>
          <DoiMatKhau />
        </section>
      </div>
    </section>
  )
}

// UC-35: mật khẩu hiện tại + mật khẩu mới (8–200 ký tự) + nhập lại. Xong thì báo bằng toast, phiên vẫn dùng tiếp
function DoiMatKhau() {
  const [cu, setCu] = useState('')
  const [moi, setMoi] = useState('')
  const [lai, setLai] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (moi.length < 8) return setLoi('Mật khẩu mới cần ít nhất 8 ký tự')
    if (moi.length > 200) return setLoi('Mật khẩu mới tối đa 200 ký tự')
    if (moi !== lai) return setLoi('Hai lần nhập mật khẩu mới chưa khớp')
    setLoi('')
    setDangGui(true)
    try {
      await doiMatKhau(cu, moi)
      toast.success('Đã đổi mật khẩu')
      setCu('')
      setMoi('')
      setLai('')
    } catch (err) {
      setLoi(
        err instanceof LoiApi && err.status === 429
          ? 'Nhập sai mật khẩu hiện tại quá nhiều lần, tài khoản tạm khóa 15 phút'
          : err instanceof LoiApi && err.status === 422
            ? err.message
            : err instanceof LoiApi && err.status === 400
              ? 'Mật khẩu mới cần 8–200 ký tự'
              : 'Không đổi được mật khẩu, vui lòng thử lại',
      )
    } finally {
      setDangGui(false)
    }
  }

  return (
    <form className="tk-mk" onSubmit={gui} noValidate>
      <label>
        Mật khẩu hiện tại
        <input
          type="password"
          autoComplete="current-password"
          value={cu}
          onChange={(e) => setCu(e.target.value)}
          required
        />
      </label>
      <label>
        Mật khẩu mới
        <input
          type="password"
          autoComplete="new-password"
          value={moi}
          onChange={(e) => setMoi(e.target.value)}
          minLength={8}
          maxLength={200}
          required
        />
      </label>
      <label>
        Nhập lại mật khẩu mới
        <input
          type="password"
          autoComplete="new-password"
          value={lai}
          onChange={(e) => setLai(e.target.value)}
          required
        />
      </label>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      <div className="tk-mk-nut">
        <button disabled={dangGui || !cu || !moi || !lai}>
          {dangGui ? 'Đang lưu…' : 'Đổi mật khẩu'}
        </button>
      </div>
    </form>
  )
}
