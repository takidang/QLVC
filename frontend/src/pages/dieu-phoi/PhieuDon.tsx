import QRCode from 'qrcode'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { Don } from '../../api/don'
import { goi, LoiApi } from '../../api/goi'
import { DangTaiPixel } from '../../HieuUngPixel'
import { phongCachDaLuu } from '../../nen'

type DonPhieu = Don & { sdt_lay: string; sdt_nhan: string }
const lucVN = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })

// Phiếu gửi hàng (UC-08, làm cùng UC-19-AC14): QR chỉ chứa mã đơn để tài xế quét; in bằng Ctrl+P (Tài chốt 04/11)
export default function PhieuDon() {
  const { id } = useParams()
  const [d, setD] = useState<DonPhieu | null>(null)
  const [qr, setQr] = useState('')
  const [loi, setLoi] = useState('')

  useEffect(() => {
    goi<DonPhieu>(`/api/don/${id}`)
      .then(async (don) => {
        setD(don)
        setQr(await QRCode.toDataURL(don.ma_don, { margin: 1, width: 240 }))
      })
      .catch((e) => setLoi(e instanceof LoiApi ? e.message : 'Không tải được đơn'))
  }, [id])

  return (
    <section className="noi-dung phieu">
      <div className="vd-cong-cu khong-in">
        <Link to="../.." relative="path">
          ← Đơn hàng
        </Link>
        {d && <button onClick={() => window.print()}>In phiếu</button>}
      </div>
      {loi && (
        <p role="alert" className="loi">
          {loi}
        </p>
      )}
      {!d &&
        !loi &&
        (phongCachDaLuu() === 'pixel' ? (
          /* Hiệu ứng Pixel: màn tải kiểu Pixel thay chữ Đang tải… */
          <DangTaiPixel kieu="trang" />
        ) : (
          <p className="ghi-chu">Đang tải…</p>
        ))}
      {d && (
        <article className="van-don" aria-label={`Phiếu gửi hàng ${d.ma_don}`}>
          <header className="vd-dau">
            <span>TAKI Logistics</span>
            <span>Phiếu gửi hàng</span>
          </header>
          <div className="vd-ma">
            <div>
              <small>Mã đơn</small>
              <b>{d.ma_don}</b>
              <small>Khách: {d.ten_khach}</small>
            </div>
            {qr && <img src={qr} alt={`Mã QR đơn ${d.ma_don}`} width={132} height={132} />}
          </div>
          <div className="vd-den">
            <small>Giao đến</small>
            <b>{d.tinh_giao}</b>
          </div>
          <div className="vd-hai">
            <section>
              <small>Lấy hàng · {d.tinh_lay}</small>
              <p>{d.dia_chi_lay}</p>
              <p>SĐT {d.sdt_lay}</p>
              {d.lay_tu && d.lay_den && (
                <p>
                  Khung lấy {lucVN(d.lay_tu)} – {lucVN(d.lay_den)}
                </p>
              )}
            </section>
            <section>
              <small>Người nhận</small>
              <p>
                <strong>{d.nguoi_nhan}</strong>
              </p>
              <p>{d.dia_chi_giao}</p>
              <p>SĐT {d.sdt_nhan}</p>
            </section>
          </div>
          <dl className="vd-hang">
            <div>
              <dt>Số kiện</dt>
              <dd>{d.so_kien}</dd>
            </div>
            <div>
              <dt>Khối lượng</dt>
              <dd>{Number(d.kg).toLocaleString('vi-VN')} kg</dd>
            </div>
            <div>
              <dt>Thể tích</dt>
              <dd>{Number(d.m3).toLocaleString('vi-VN')} m³</dd>
            </div>
          </dl>
          <footer className="vd-chan">
            <span>
              Hạn giao <strong>{lucVN(d.han_giao)}</strong>
            </span>
            {d.mo_ta && <span>{d.mo_ta}</span>}
          </footer>
        </article>
      )}
    </section>
  )
}
