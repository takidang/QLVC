import { useState, type FormEvent } from 'react'
import { dongSuCo, ketThucSuCo, TEN_CO, type ChuyenChiTiet } from '../../api/chuyen'
import { kemMaBr, LoiApi } from '../../api/goi'

const dong = (n: number) => `${n.toLocaleString('vi-VN')} đ`
const lucVN = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })

// UC-32: cờ, cảnh báo chồng lịch (BR-73), tiền, sự cố, dòng thời gian, kết thúc do sự cố (BR-68).
// Chỉ có khi trang tải bằng GET chi tiết; kết quả ghép / gỡ / chốt không kèm phần này
export default function TheoDoiChuyen({
  c,
  onDoi,
}: {
  c: ChuyenChiTiet
  onDoi: (c: ChuyenChiTiet | null) => void
}) {
  if (!c.tien) return null
  return (
    <>
      {(c.co?.length ?? 0) > 0 && (
        <p>
          {c.co!.map((x) => (
            <span key={x} className="nhan do">
              {TEN_CO[x] ?? x}
            </span>
          ))}
        </p>
      )}
      {(c.chong?.length ?? 0) > 0 && c.ket_thuc_dang_chay && (
        <p role="alert" className="loi">
          Đang trễ: dự kiến xong {lucVN(c.ket_thuc_dang_chay)}, chồng lên chuyến kế tiếp của xe /
          tài xế: {c.chong!.join(', ')} (BR-73). Hệ thống không tự đổi lịch.
        </p>
      )}
      {c.ket_thuc_bat_thuong && <p className="canh-bao">Kết thúc do sự cố: {c.ly_do_ket_thuc}</p>}
      {c.trang_thai === 'DANG_CHAY' && <KetThucSuCo c={c} onDoi={onDoi} />}

      <h2>Tiền</h2>
      <p>
        Doanh thu dự kiến <strong>{dong(c.tien.doanh_thu)}</strong> · Định mức chi phí{' '}
        <strong>{dong(c.tien.dinh_muc)}</strong> · Lương tài xế{' '}
        <strong>{dong(c.tien.luong)}</strong> · Tạm ứng còn hiệu lực{' '}
        <strong>{dong(c.tien.tam_ung_hieu_luc)}</strong>
        {c.km_bat_dau !== null && ` · Km ${c.km_bat_dau?.toLocaleString('vi-VN')}`}
        {c.km_ket_thuc != null && ` → ${c.km_ket_thuc.toLocaleString('vi-VN')}`}
      </p>

      {(c.su_co?.length ?? 0) > 0 && (
        <>
          <h2>Sự cố</h2>
          <ul className="ds-the">
            {c.su_co!.map((s) => (
              <li key={s.id} className="the">
                <div className="the-dau">
                  <strong>
                    {s.loai} · {lucVN(s.luc)}
                  </strong>
                  <span className={s.trang_thai === 'MO' ? 'nhan do' : 'nhan xam'}>
                    {s.trang_thai === 'MO' ? 'Đang mở' : 'Đã đóng'}
                  </span>
                </div>
                {s.ghi_chu && <div>{s.ghi_chu}</div>}
                {s.cach_xu_ly && <div className="ghi-chu">Cách xử lý: {s.cach_xu_ly}</div>}
                {s.trang_thai === 'MO' && <DongSuCo id={s.id} onXong={() => onDoi(null)} />}
              </li>
            ))}
          </ul>
        </>
      )}

      <h2>Dòng thời gian</h2>
      <ol className="ghi-chu">
        {(c.dong_thoi_gian ?? []).map((s, i) => (
          <li key={i}>
            {lucVN(s.luc)} · {s.noi_dung}
            {s.nguoi && ` · ${s.nguoi}`}
          </li>
        ))}
      </ol>
    </>
  )
}

function DongSuCo({ id, onXong }: { id: number; onXong: () => void }) {
  const [cach, setCach] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)
  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoi('')
    setDangGui(true)
    try {
      await dongSuCo(id, cach.trim())
      onXong()
    } catch (err) {
      setLoi(err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại')
    } finally {
      setDangGui(false)
    }
  }
  return (
    <form className="thanh-cong-cu" onSubmit={gui}>
      <input
        aria-label="Cách xử lý"
        placeholder="Cách xử lý"
        maxLength={500}
        value={cach}
        onChange={(e) => setCach(e.target.value)}
      />
      <button disabled={dangGui || !cach.trim()}>Đóng sự cố</button>
      {loi && <span className="loi">{loi}</span>}
    </form>
  )
}

function KetThucSuCo({ c, onDoi }: { c: ChuyenChiTiet; onDoi: (c: ChuyenChiTiet) => void }) {
  const [mo, setMo] = useState(false)
  const [lyDo, setLyDo] = useState('')
  const [km, setKm] = useState('')
  const [loi, setLoi] = useState('')
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    const con = c.don.filter((d) => d.trang_thai === 'DA_GHEP' || d.trang_thai === 'DA_LAY').length
    if (
      !window.confirm(
        `Kết thúc chuyến ${c.ma_chuyen} do sự cố? ${con} đơn chưa giao sẽ thành Thất bại.`,
      )
    )
      return
    setLoi('')
    setDangGui(true)
    try {
      onDoi(await ketThucSuCo(c.id, lyDo.trim(), km ? Number(km) : null))
    } catch (err) {
      setLoi(
        err instanceof LoiApi ? kemMaBr(err.message, err.ma) : 'Không lưu được, vui lòng thử lại',
      )
    } finally {
      setDangGui(false)
    }
  }

  if (!mo)
    return (
      <p>
        <button className="phu" onClick={() => setMo(true)}>
          Kết thúc do sự cố
        </button>
      </p>
    )
  return (
    <form className="canh-bao" onSubmit={gui}>
      <strong>Kết thúc chuyến do sự cố (BR-68)</strong>
      <label>
        Lý do
        <input value={lyDo} maxLength={300} required onChange={(e) => setLyDo(e.target.value)} />
      </label>
      <label>
        Km cuối (nếu biết)
        <input type="number" min={0} value={km} onChange={(e) => setKm(e.target.value)} />
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
        <button disabled={dangGui || !lyDo.trim()}>
          {dangGui ? 'Đang lưu…' : 'Kết thúc chuyến'}
        </button>
      </div>
    </form>
  )
}
