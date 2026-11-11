import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { LoiApi } from '../../api/goi'
import { Ic, Nhan } from '../../nhan'
import {
  TEN_TRANG_THAI,
  chuyenCuaToi,
  ngayGio,
  type ChuyenCuaToi as Chuyen,
  type NhomChuyen,
} from '../../api/toi'

const SO_DONG = 20
// Dòng ngày trên tiêu đề, tính một lần lúc tải trang
const homNay = new Date().toLocaleDateString('vi-VN', {
  weekday: 'long',
  day: '2-digit',
  month: '2-digit',
})
// UC-17: chuyến của tài xế trên điện thoại (thẻ thay bảng để không cuộn ngang ở 360 px)
export default function ChuyenCuaToi() {
  const [nhom, setNhom] = useState<NhomChuyen>('can_lam')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: Chuyen[]; tong: number } | null>(null)
  const [loi, setLoi] = useState('')

  useEffect(() => {
    let bo = false // đổi thẻ nhanh: kết quả cũ về muộn thì bỏ
    chuyenCuaToi({ nhom, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoi('')
      })
      .catch((e) => {
        if (!bo) setLoi(e instanceof LoiApi ? e.message : 'Không tải được chuyến của bạn')
      })
    return () => {
      bo = true
    }
  }, [nhom, trang])

  const soTrang = Math.max(1, Math.ceil((ds?.tong ?? 0) / SO_DONG))
  return (
    <section className="noi-dung dien-thoai">
      <p className="dt-ngay">{homNay}</p>
      <h1>Chuyến của tôi</h1>
      <div className="the-chon" role="tablist">
        {(['can_lam', 'da_xong'] as NhomChuyen[]).map((n) => (
          <button
            key={n}
            role="tab"
            aria-selected={nhom === n}
            className={nhom === n ? undefined : 'phu'}
            onClick={() => {
              if (n === nhom) return // bấm lại thẻ đang chọn: không tải lại, không xóa danh sách
              setNhom(n)
              setTrang(1)
              setDs(null)
            }}
          >
            {n === 'can_lam' ? 'Cần làm' : 'Đã xong'}
          </button>
        ))}
      </div>

      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      {ds === null && !loi && <p className="ghi-chu">Đang tải…</p>}
      {ds?.du_lieu.length === 0 && (
        <p className="trong">
          {nhom === 'can_lam' ? 'Chưa có chuyến nào được giao' : 'Chưa có chuyến đã xong'}
        </p>
      )}

      {/* Chuyến đang chạy nổi lên thành khối đậm, nút mở to cho ngón tay; chuyến khác là dòng gọn */}
      {ds?.du_lieu
        .filter((c) => c.trang_thai === 'DANG_CHAY')
        .map((c) => (
          <section key={c.id} className="the-chinh">
            <div className="dong">
              <span className="ma">{c.ma_chuyen}</span>
              <Nhan loai={c.trang_thai}>{TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}</Nhan>
            </div>
            <div>
              <h2>{c.ten_tuyen}</h2>
              <div className="mo-chu">
                <span className="bien">{c.bien_so}</span>
                {ngayGio(c.khoi_hanh_du_kien)} → {ngayGio(c.ket_thuc_du_kien)}
              </div>
              <div className="mo-chu">{c.so_don} đơn</div>
            </div>
            <Link to={String(c.id)} className="nut-to">
              Mở lịch trình, quét mã
              <Ic ten="phai" />
            </Link>
          </section>
        ))}

      <ul className="ds-the">
        {ds?.du_lieu
          .filter((c) => c.trang_thai !== 'DANG_CHAY')
          .map((c) => (
            <li key={c.id}>
              <Link to={String(c.id)} className="the hang-dt">
                <span className="gio">
                  <b>{ngayGio(c.khoi_hanh_du_kien).split(' ')[0]}</b>
                  <small>{ngayGio(c.khoi_hanh_du_kien).split(' ')[1]}</small>
                </span>
                <span>
                  <span className="tuyen">{c.ten_tuyen}</span>
                  <small>
                    {c.ma_chuyen} · {c.bien_so} · {c.so_don} đơn
                  </small>
                </span>
                <Nhan loai={c.trang_thai}>{TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}</Nhan>
              </Link>
            </li>
          ))}
      </ul>

      {soTrang > 1 && (
        <div className="phan-trang">
          <button className="phu" disabled={trang <= 1} onClick={() => setTrang(trang - 1)}>
            Trước
          </button>
          <span>
            {trang}/{soTrang}
          </span>
          <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
            Sau
          </button>
        </div>
      )}
    </section>
  )
}
