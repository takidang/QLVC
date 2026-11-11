import { useState } from 'react'
import type { NguoiDung } from './api/auth'
import { BO_MAU, apMau, mauDaLuu } from './nen'

// Menu tài khoản (bấm vòng tên tắt): thông tin người dùng, chọn bộ màu giao diện, đăng xuất.
// Đổi mật khẩu thêm vào đây khi backend có UC-35.
export default function MenuTaiKhoan({
  nd,
  tenVaiTro,
  onThoat,
}: {
  nd: NguoiDung
  tenVaiTro: string
  onThoat: () => void
}) {
  const [mau, setMau] = useState(mauDaLuu)
  const chon = (ma: string) => {
    apMau(ma)
    setMau(ma)
  }
  const tat = nd.ho_ten
    .split(' ')
    .slice(-2)
    .map((x) => x[0])
    .join('')
    .toUpperCase()
  return (
    <details
      className="menu-tk"
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) e.currentTarget.open = false
      }}
    >
      <summary className="tron" aria-label={`Tài khoản ${nd.ho_ten}`}>
        {tat}
      </summary>
      <div className="menu-tk-hop">
        <div className="menu-tk-dau">
          <strong>{nd.ho_ten}</strong>
          <small>{tenVaiTro}</small>
        </div>
        <div className="menu-tk-mau" role="group" aria-label="Bộ màu giao diện">
          <small>Bộ màu giao diện</small>
          {[{ ma: '', ten: 'Ngẫu nhiên theo ảnh', nen: '', nhan: '' }, ...BO_MAU].map(
            (b) => (
              <button
                key={b.ma || 'ngau-nhien'}
                type="button"
                aria-pressed={mau === b.ma}
                onClick={() => chon(b.ma)}
              >
                <i
                  className={b.ma ? 'o-mau' : 'o-mau ngau-nhien'}
                  aria-hidden="true"
                  style={
                    b.ma
                      ? { background: `linear-gradient(135deg, ${b.nen} 50%, ${b.nhan} 50%)` }
                      : undefined
                  }
                />
                {b.ten}
              </button>
            ),
          )}
        </div>
        <button className="phu" onClick={onThoat}>
          Đăng xuất
        </button>
      </div>
    </details>
  )
}
