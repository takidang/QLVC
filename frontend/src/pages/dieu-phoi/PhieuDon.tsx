import QRCode from 'qrcode'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { Don } from '../../api/don'
import { goi, LoiApi } from '../../api/goi'

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
      <div className="thanh-cong-cu khong-in">
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
      {!d && !loi && <p className="ghi-chu">Đang tải…</p>}
      {d && (
        <article className="the phieu-noi-dung">
          <div className="phieu-dau">
            <div>
              <h1>Phiếu gửi hàng</h1>
              <p className="phieu-ma">{d.ma_don}</p>
              <p>
                Khách: <strong>{d.ten_khach}</strong>
              </p>
            </div>
            {qr && <img src={qr} alt={`Mã QR đơn ${d.ma_don}`} width={160} height={160} />}
          </div>
          <dl className="hai-cot">
            <div>
              <dt>Lấy hàng</dt>
              <dd>
                {d.dia_chi_lay}, {d.tinh_lay}
                <br />
                SĐT {d.sdt_lay}
                {d.lay_tu && d.lay_den && (
                  <>
                    <br />
                    Khung lấy {lucVN(d.lay_tu)} – {lucVN(d.lay_den)}
                  </>
                )}
              </dd>
            </div>
            <div>
              <dt>Giao hàng</dt>
              <dd>
                {d.dia_chi_giao}, {d.tinh_giao}
                <br />
                {d.nguoi_nhan} · SĐT {d.sdt_nhan}
                <br />
                Hạn giao {lucVN(d.han_giao)}
              </dd>
            </div>
          </dl>
          <p>
            {d.mo_ta && `${d.mo_ta} · `}
            <strong>{d.so_kien} kiện</strong> · {Number(d.kg).toLocaleString('vi-VN')} kg ·{' '}
            {Number(d.m3).toLocaleString('vi-VN')} m³
          </p>
        </article>
      )}
    </section>
  )
}
