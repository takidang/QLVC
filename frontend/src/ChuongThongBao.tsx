import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { canhBao, type CanhBao } from './api/canhBao'
import { Ic } from './nhan'

// Chuông thông báo của Điều phối / Quản lý: số việc từ bảng cảnh báo UC-27 (GET /api/canh-bao),
// mở ra là tóm tắt theo nhóm, bấm để tới màn tương ứng. Tải lại khi đổi trang và mỗi 2 phút.
// Thay bằng GET /api/thong-bao (UC-37) khi backend có.
export default function ChuongThongBao({ goc }: { goc: string }) {
  const { pathname } = useLocation()
  const [cb, setCb] = useState<CanhBao | null>(null)
  useEffect(() => {
    let bo = false
    const tai = () =>
      canhBao()
        .then((r) => !bo && setCb(r))
        .catch(() => !bo && setCb(null))
    tai()
    const h = setInterval(tai, 120_000)
    return () => {
      bo = true
      clearInterval(h)
    }
  }, [pathname])

  const nhom = cb
    ? [
        { so: cb.su_co_mo.length, chu: 'sự cố đang mở', den: `${goc}/chuyen`, nang: true },
        {
          so: cb.chuyen_tre.length,
          chu: 'chuyến trễ / chồng lịch',
          den: `${goc}/chuyen`,
          nang: true,
        },
        {
          so: cb.don_sap_qua_han.filter((d) => d.qua_han).length,
          chu: 'đơn chờ ghép đã quá hạn giao',
          den: `${goc}/don`,
          nang: true,
        },
        {
          so: cb.don_sap_qua_han.filter((d) => !d.qua_han).length,
          chu: 'đơn chờ ghép sắp tới hạn',
          den: `${goc}/don`,
          nang: false,
        },
        {
          so: cb.giay_to.length,
          chu: 'giấy tờ xe / GPLX sắp hết hạn',
          den: `${goc}/xe`,
          nang: false,
        },
        { so: cb.thieu_gps.length, chu: 'lượt quét thiếu GPS', den: `${goc}/chuyen`, nang: false },
      ].filter((x) => x.so > 0)
    : []
  const tong = cb?.so_viec ?? 0

  return (
    <details
      className="chuong"
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) e.currentTarget.open = false
      }}
    >
      <summary aria-label={tong ? `Thông báo: ${tong} việc cần chú ý` : 'Thông báo'}>
        <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15zM10 20.5a2 2 0 0 0 4 0" />
        </svg>
        {tong > 0 && <em>{tong > 99 ? '99+' : tong}</em>}
      </summary>
      <div className="chuong-hop">
        <strong>Cần chú ý</strong>
        {nhom.map((x) => (
          <Link
            key={x.chu}
            to={x.den}
            className={x.nang ? 'do' : undefined}
            onClick={(e) => e.currentTarget.closest('details')?.removeAttribute('open')}
          >
            <b>{x.so}</b>
            <span>{x.chu}</span>
            <Ic ten="phai" />
          </Link>
        ))}
        {cb && nhom.length === 0 && <p>Không có việc nào cần chú ý.</p>}
        {!cb && <p>Không tải được thông báo.</p>}
      </div>
    </details>
  )
}
