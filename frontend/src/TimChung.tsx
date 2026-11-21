import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import type { VaiTro } from './api/auth'
import { timChung, type KetQuaTim } from './api/tim'

// Ô tìm chung trên thanh đầu (UC-36): mã chuyến, mã đơn, biển số, tài xế, khách hàng.
// Gọi API khi đủ 2 ký tự, chờ 250 ms sau khi ngừng gõ; Esc hoặc bấm ra ngoài để đóng.
// Bấm một kết quả là tới màn của vai trò đang đăng nhập (vai trò không có màn đó thì dẫn về màn gần nhất).
const ngayGio = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  })

export default function TimChung({ vaiTro }: { vaiTro: VaiTro }) {
  const [q, setQ] = useState('')
  const [kq, setKq] = useState<KetQuaTim | null>(null)
  const [mo, setMo] = useState(false)
  const [dangTim, setDangTim] = useState(false)
  const khung = useRef<HTMLDivElement>(null)
  const tu = q.trim()

  useEffect(() => {
    if (tu.length < 2) return
    const dk = new AbortController()
    const h = setTimeout(() => {
      setDangTim(true)
      timChung(tu, dk.signal)
        .then((r) => setKq(r))
        .catch(() => !dk.signal.aborted && setKq(null))
        .finally(() => !dk.signal.aborted && setDangTim(false))
    }, 250)
    return () => {
      clearTimeout(h)
      dk.abort()
    }
  }, [tu])

  // Đường dẫn theo vai trò
  const dp = vaiTro === 'DIEU_PHOI' || vaiTro === 'QUAN_LY'
  const den = {
    chuyen: (id: number) =>
      dp
        ? `/dieu-phoi/chuyen/${id}`
        : vaiTro === 'TAI_XE'
          ? `/tai-xe/chuyen/${id}`
          : '/ke-toan/quyet-toan',
    don: (id: number) => (dp ? `/dieu-phoi/don/${id}/phieu` : '/ke-toan/cong-no'),
    xe: () => '/dieu-phoi/xe',
    tai_xe: () => '/dieu-phoi/tai-xe',
    khach_hang: () => (dp ? '/dieu-phoi/khach-hang' : '/ke-toan/cong-no'),
  }
  const dong = () => {
    setMo(false)
    setQ('')
    setKq(null)
  }

  const nhom =
    kq && tu.length >= 2
      ? [
          {
            ten: 'Chuyến',
            tong: kq.chuyen.tong,
            ds: kq.chuyen.ds.map((x) => ({
              key: `c${x.id}`,
              to: den.chuyen(x.id),
              chinh: x.ma_chuyen,
              phu: `${x.bien_so} · ${x.ten_tai_xe} · ${ngayGio(x.khoi_hanh_du_kien)}`,
            })),
          },
          {
            ten: 'Đơn hàng',
            tong: kq.don.tong,
            ds: kq.don.ds.map((x) => ({
              key: `d${x.id}`,
              to: den.don(x.id),
              chinh: x.ma_don,
              phu: `${x.ten_khach} · ${x.tinh_lay} → ${x.tinh_giao}`,
            })),
          },
          {
            ten: 'Xe',
            tong: kq.xe.tong,
            ds: kq.xe.ds.map((x) => ({
              key: `x${x.id}`,
              to: den.xe(),
              chinh: x.bien_so,
              phu: x.trang_thai === 'HOAT_DONG' ? 'Hoạt động' : 'Ngừng',
            })),
          },
          {
            ten: 'Tài xế',
            tong: kq.tai_xe.tong,
            ds: kq.tai_xe.ds.map((x) => ({
              key: `t${x.id}`,
              to: den.tai_xe(),
              chinh: x.ho_ten,
              phu: x.trang_thai === 'HOAT_DONG' ? 'Hoạt động' : 'Ngừng',
            })),
          },
          {
            ten: 'Khách hàng',
            tong: kq.khach_hang.tong,
            ds: kq.khach_hang.ds.map((x) => ({
              key: `k${x.id}`,
              to: den.khach_hang(),
              chinh: x.ten,
              phu: x.sdt,
            })),
          },
        ].filter((n) => n.tong > 0)
      : []

  return (
    <div
      ref={khung}
      className="tim-chung"
      onBlur={(e) => {
        if (!khung.current?.contains(e.relatedTarget)) setMo(false)
      }}
      onKeyDown={(e) => e.key === 'Escape' && dong()}
    >
      <label className="tim-o">
        <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="6.5" />
          <path d="M16 16l4.5 4.5" />
        </svg>
        <input
          type="search"
          value={q}
          placeholder="Tìm mã chuyến, mã đơn, biển số…"
          aria-label="Tìm chung"
          onChange={(e) => {
            setQ(e.target.value)
            setMo(true)
          }}
          onFocus={() => setMo(true)}
        />
      </label>
      {mo && tu.length >= 2 && (
        <div className="tim-hop" role="region" aria-label="Kết quả tìm" aria-live="polite">
          {dangTim && !kq && <p>Đang tìm…</p>}
          {kq && nhom.length === 0 && <p>Không tìm thấy “{tu}”.</p>}
          {nhom.map((n) => (
            <section key={n.ten}>
              <h3>
                {n.ten} <em>{n.tong > n.ds.length ? `${n.ds.length} / ${n.tong}` : n.tong}</em>
              </h3>
              {n.ds.map((x) => (
                <Link key={x.key} to={x.to} onClick={dong}>
                  <strong>{x.chinh}</strong>
                  <small>{x.phu}</small>
                </Link>
              ))}
            </section>
          ))}
          {nhom.some((n) => n.tong > n.ds.length) && (
            <p className="tim-them">Chỉ hiện 5 kết quả đầu mỗi nhóm, gõ thêm để thu hẹp.</p>
          )}
        </div>
      )}
    </div>
  )
}
