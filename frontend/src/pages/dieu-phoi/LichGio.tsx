import { useLayoutEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Chuyen } from '../../api/chuyen'

const GIO = 3_600_000
const gio = (ms: number | string) =>
  new Date(ms).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
const LOP: Record<string, string> = {
  LAP: 'lap',
  DA_CHOT: 'chot',
  DANG_CHAY: 'chay',
  HOAN_THANH: 'xong',
  DA_QUYET_TOAN: 'xong',
  HUY: 'huy',
}
// Nhãn ngắn cho thanh hẹp: bỏ điểm đầu (thường là kho chung "TP.HCM"), chỉ giữ điểm cuối của tuyến
const TACH = /\s+[–—→-]\s+/
const tenNgan = (ten: string) => {
  const phan = ten.split(TACH)
  return phan.length > 1 ? `→ ${phan[phan.length - 1]}` : ten
}

// Lịch xe theo giờ: mỗi xe một hàng, mỗi chuyến một thanh từ giờ đi tới giờ kết thúc dự kiến.
// `ds` đã xếp theo giờ đi; `ten` là tên trạng thái để ghi vào chú thích khi rê chuột.
export default function LichGio({ ds, ten }: { ds: Chuyen[]; ten: Record<string, string> }) {
  const dau = Math.floor(Math.min(...ds.map((c) => Date.parse(c.khoi_hanh_du_kien))) / GIO) * GIO
  const cuoi = Math.ceil(Math.max(...ds.map((c) => Date.parse(c.ket_thuc_du_kien))) / GIO) * GIO
  const soGio = (cuoi - dau) / GIO
  const buoc = soGio > 12 ? 2 : 1 // khoảng dài thì kẻ vạch 2 giờ một
  const soVach = Math.ceil(soGio / buoc)
  const pt = (ms: number) => `${((ms - dau) / (cuoi - dau)) * 100}%`
  const xe = [...new Set(ds.map((c) => c.bien_so))]
  const [nay] = useState(Date.now) // lấy một lần lúc mở, không đổi giữa các lần vẽ lại
  const khung = useRef<HTMLElement>(null)

  // Thanh nào không đủ chỗ cho tên tuyến đầy đủ thì đổi sang nhãn ngắn (data-ngan); đo lại khi khung đổi cỡ.
  // Bề rộng thanh vẫn theo giờ, chỉ đổi chữ bên trong.
  useLayoutEffect(() => {
    const el = khung.current
    if (!el) return
    const doLai = () =>
      el.querySelectorAll<HTMLElement>('.lg-thanh').forEach((a) => {
        delete a.dataset.ngan
        if (a.scrollWidth > a.clientWidth + 1) a.dataset.ngan = ''
      })
    doLai()
    const ro = new ResizeObserver(doLai)
    ro.observe(el)
    return () => ro.disconnect()
  }, [ds])

  return (
    <section className="kinh lich-gio" ref={khung}>
      <h2>Lịch xe theo giờ</h2>
      <div className="lg-hang lg-dau" aria-hidden="true">
        <span />
        <div className="lg-duong">
          {Array.from({ length: soVach }, (_, i) => dau + i * buoc * GIO).map((v) => (
            <small key={v} style={{ left: pt(v) }}>
              {gio(v)}
            </small>
          ))}
        </div>
      </div>
      {xe.map((b) => (
        <div className="lg-hang" key={b}>
          <span className="bien">{b}</span>
          <div className="lg-duong" style={{ backgroundSize: `${(buoc / soGio) * 100}% 100%` }}>
            {nay > dau && nay < cuoi && <i className="lg-nay" style={{ left: pt(nay) }} />}
            {ds
              .filter((c) => c.bien_so === b)
              .map((c) => {
                const di = Date.parse(c.khoi_hanh_du_kien)
                const den = Date.parse(c.ket_thuc_du_kien)
                return (
                  <Link
                    key={c.id}
                    to={String(c.id)}
                    className={`lg-thanh ${LOP[c.trang_thai] ?? 'lap'}${c.trang_thai === 'DANG_CHAY' && c.theo_doi?.co.includes('TRE') ? ' tre' : ''}`}
                    style={{ left: pt(di), width: `${((den - di) / (cuoi - dau)) * 100}%` }}
                    title={`${c.ma_chuyen} · ${c.ten_tuyen} · ${gio(di)} → ${gio(den)} · ${c.ten_tai_xe} · ${ten[c.trang_thai] ?? c.trang_thai}`}
                  >
                    <span className="lg-ten">{c.ten_tuyen}</span>
                    <span className="lg-ten-ngan">{tenNgan(c.ten_tuyen)}</span>
                  </Link>
                )
              })}
          </div>
        </div>
      ))}
    </section>
  )
}
