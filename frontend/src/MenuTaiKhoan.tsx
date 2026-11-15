import { useEffect, useRef, useState, type FormEvent } from 'react'
import { toast } from 'sonner'
import { doiMatKhau, LoiApi, type NguoiDung } from './api/auth'
import { CHE_DO, apCheDo, cheDoDaLuu } from './nen'

// Menu tài khoản (bấm vòng tên tắt): thông tin người dùng, chọn giao diện sáng / tối,
// đổi mật khẩu (UC-35), đăng xuất.
export default function MenuTaiKhoan({
  nd,
  tenVaiTro,
  onThoat,
}: {
  nd: NguoiDung
  tenVaiTro: string
  onThoat: () => void
}) {
  const [cheDo, setCheDo] = useState(cheDoDaLuu)
  // Đóng khi bấm hoặc Tab ra ngoài menu (không dựa vào blur: nút bị khóa lúc gửi làm mất focus)
  const hop = useRef<HTMLDetailsElement>(null)
  useEffect(() => {
    const ngoai = (e: Event) => {
      if (hop.current?.open && !hop.current.contains(e.target as Node)) hop.current.open = false
    }
    document.addEventListener('pointerdown', ngoai)
    document.addEventListener('focusin', ngoai)
    return () => {
      document.removeEventListener('pointerdown', ngoai)
      document.removeEventListener('focusin', ngoai)
    }
  }, [])
  const chon = (ma: string) => {
    apCheDo(ma)
    setCheDo(ma)
  }
  const tat = nd.ho_ten
    .split(' ')
    .slice(-2)
    .map((x) => x[0])
    .join('')
    .toUpperCase()
  return (
    <details className="menu-tk" ref={hop}>
      <summary className="tron" aria-label={`Tài khoản ${nd.ho_ten}`}>
        {tat}
      </summary>
      <div className="menu-tk-hop">
        <div className="menu-tk-dau">
          <strong>{nd.ho_ten}</strong>
          <small>{tenVaiTro}</small>
        </div>
        <div className="menu-tk-che-do" role="group" aria-label="Giao diện">
          <small>Giao diện</small>
          <div className="vien-thuoc">
            {CHE_DO.map((c) => (
              <button
                key={c.ma || 'may'}
                type="button"
                aria-pressed={cheDo === c.ma}
                onClick={() => chon(c.ma)}
              >
                {c.ten}
              </button>
            ))}
          </div>
        </div>
        <DoiMatKhau />
        <button className="phu" onClick={onThoat}>
          Đăng xuất
        </button>
      </div>
    </details>
  )
}

// UC-35: mật khẩu hiện tại + mật khẩu mới (8–200 ký tự) + nhập lại. Xong thì báo bằng toast, phiên vẫn dùng tiếp
function DoiMatKhau() {
  const [mo, setMo] = useState(false)
  const [cu, setCu] = useState('')
  const [moi, setMoi] = useState('')
  const [lai, setLai] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (moi.length < 8) return setLoi('Mật khẩu mới cần ít nhất 8 ký tự')
    if (moi !== lai) return setLoi('Hai lần nhập mật khẩu mới chưa khớp')
    setLoi('')
    setDangGui(true)
    try {
      await doiMatKhau(cu, moi)
      toast.success('Đã đổi mật khẩu')
      setMo(false)
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

  if (!mo)
    return (
      <button type="button" className="phu" onClick={() => setMo(true)}>
        Đổi mật khẩu
      </button>
    )
  return (
    <form className="menu-tk-mk" onSubmit={gui} noValidate>
      <label>
        Mật khẩu hiện tại
        <input
          type="password"
          autoComplete="current-password"
          value={cu}
          onChange={(e) => setCu(e.target.value)}
          autoFocus
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
      <div className="nut">
        <button type="button" className="phu" disabled={dangGui} onClick={() => setMo(false)}>
          Thôi
        </button>
        <button disabled={dangGui || !cu || !moi || !lai}>
          {dangGui ? 'Đang lưu…' : 'Đổi mật khẩu'}
        </button>
      </div>
    </form>
  )
}
