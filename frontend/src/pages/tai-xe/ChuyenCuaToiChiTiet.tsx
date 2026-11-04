import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { LoiApi } from '../../api/goi'
import {
  TEN_TRANG_THAI,
  chuyenCuaToiChiTiet,
  ngayGio,
  type ChuyenCuaToiChiTiet as ChiTiet,
} from '../../api/toi'

const gio = (iso: string) =>
  new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
const TEN_TRANG_THAI_DON: Record<string, string> = {
  DA_GHEP: 'Chờ lấy',
  DA_LAY: 'Đã lấy',
  DA_GIAO: 'Đã giao',
  THAT_BAI: 'Thất bại',
  TRA_HANG: 'Trả hàng',
}

// UC-17: lịch trình cho tài xế – từng điểm dừng, đơn, địa chỉ, gọi điện. Không có cước (quyết định số 3)
export default function ChuyenCuaToiChiTiet() {
  const { id } = useParams()
  const [c, setC] = useState<ChiTiet | null>(null)
  const [loi, setLoi] = useState('')

  useEffect(() => {
    chuyenCuaToiChiTiet(Number(id))
      .then(setC)
      .catch((e) => setLoi(e instanceof LoiApi ? e.message : 'Không tải được chuyến'))
  }, [id])

  return (
    <section className="noi-dung dien-thoai">
      <Link to=".." relative="path">
        ← Chuyến của tôi
      </Link>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      {!c && !loi && <p className="ghi-chu">Đang tải…</p>}
      {c && (
        <>
          <div className="the-dau">
            <h1>{c.ma_chuyen}</h1>
            <span className={c.trang_thai === 'DANG_CHAY' ? 'nhan' : 'nhan xam'}>
              {TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}
            </span>
          </div>
          <p>
            {c.ma_tuyen} – {c.ten_tuyen}
            <br />
            Xe <span className="bien-so">{c.bien_so}</span> · {ngayGio(c.khoi_hanh_du_kien)} →{' '}
            {ngayGio(c.ket_thuc_du_kien)}
            <br />
            {c.so_don} đơn
            {c.luong_tai_xe_chot !== null &&
              ` · Lương chuyến ${c.luong_tai_xe_chot.toLocaleString('vi-VN')} đ`}
          </p>

          <h2>Lịch trình</h2>
          {c.lich_trinh.length === 0 && <p className="trong">Chuyến chạy rỗng – không có đơn</p>}
          <ol className="ds-the">
            {c.lich_trinh.map((p) => (
              <li key={`${p.viec}-${p.don_id}`} className="the">
                <div className="the-dau">
                  <strong>
                    {p.thu_tu}. {gio(p.eta)} · {p.viec === 'LAY' ? 'Lấy' : 'Giao'} tại {p.nut}
                  </strong>
                  <span className="nhan xam">
                    {TEN_TRANG_THAI_DON[p.trang_thai_don] ?? p.trang_thai_don}
                  </span>
                </div>
                <div>
                  <span className="bien-so">{p.ma_don}</span> · {p.ten_khach}
                  {p.mo_ta && ` · ${p.mo_ta}`}
                </div>
                <div className="ghi-chu">
                  {Number(p.kg).toLocaleString('vi-VN')} kg · {Number(p.m3).toLocaleString('vi-VN')}{' '}
                  m³ · {p.so_kien} kiện
                </div>
                <div>{p.dia_chi}</div>
                <div>
                  {p.nguoi_lien_he && `${p.nguoi_lien_he} · `}
                  <a href={`tel:${p.sdt}`}>{p.sdt}</a>
                </div>
                <div className="ghi-chu">
                  {p.viec === 'GIAO'
                    ? `Hạn giao ${ngayGio(p.han_giao)}`
                    : p.lay_tu && p.lay_den
                      ? `Khung lấy ${gio(p.lay_tu)}–${gio(p.lay_den)}`
                      : 'Lấy cả ngày'}
                </div>
              </li>
            ))}
          </ol>
        </>
      )}
    </section>
  )
}
