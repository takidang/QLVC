import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { chuTat, urlAnhDaiDien, type NguoiDung } from './api/auth'

// Menu tài khoản (bấm vòng ảnh đại diện / chữ tắt): họ tên + vai trò, Tài khoản, Cài đặt,
// Cấu hình hệ thống (chỉ Quản lý), tách riêng nút Đăng xuất ở cuối.
export default function MenuTaiKhoan({
  nd,
  tenVaiTro,
  phienBanAnh,
  onThoat,
}: {
  nd: NguoiDung
  tenVaiTro: string
  phienBanAnh: number
  onThoat: () => void
}) {
  // Lưu phiên bản ảnh bị lỗi tải; khi phienBanAnh tăng sau lần đổi ảnh mới sẽ tự thử tải lại
  const [loiAnhV, setLoiAnhV] = useState<number | null>(null)
  // Đóng khi bấm/Tab ra ngoài menu hoặc nhấn Esc
  const hop = useRef<HTMLDetailsElement>(null)
  const dong = () => {
    if (hop.current) hop.current.open = false
  }
  useEffect(() => {
    const ngoai = (e: Event) => {
      if (hop.current?.open && !hop.current.contains(e.target as Node)) hop.current.open = false
    }
    const phim = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && hop.current?.open) hop.current.open = false
    }
    document.addEventListener('pointerdown', ngoai)
    document.addEventListener('focusin', ngoai)
    document.addEventListener('keydown', phim)
    return () => {
      document.removeEventListener('pointerdown', ngoai)
      document.removeEventListener('focusin', ngoai)
      document.removeEventListener('keydown', phim)
    }
  }, [])
  const tat = chuTat(nd.ho_ten)
  const hienAnh = nd.co_anh_dai_dien && loiAnhV !== phienBanAnh
  return (
    <details className="menu-tk" ref={hop}>
      <summary className="tron" aria-label={`Tài khoản ${nd.ho_ten}`}>
        {hienAnh ? (
          <img src={urlAnhDaiDien(phienBanAnh)} alt="" onError={() => setLoiAnhV(phienBanAnh)} />
        ) : (
          tat
        )}
      </summary>
      <div className="menu-tk-hop">
        <div className="menu-tk-dau">
          <strong>{nd.ho_ten}</strong>
          <small>{tenVaiTro}</small>
        </div>
        <nav className="menu-tk-ds" aria-label="Menu tài khoản">
          <Link to="/tai-khoan" onClick={dong}>
            Tài khoản
          </Link>
          <Link to="/cai-dat" onClick={dong}>
            Cài đặt
          </Link>
          {nd.vai_tro === 'QUAN_LY' && (
            <Link to="/quan-ly/cau-hinh" onClick={dong}>
              Cấu hình hệ thống
            </Link>
          )}
        </nav>
        <div className="menu-tk-cuoi">
          <button
            type="button"
            className="phu"
            onClick={() => {
              dong()
              onThoat()
            }}
          >
            Đăng xuất
          </button>
        </div>
      </div>
    </details>
  )
}
