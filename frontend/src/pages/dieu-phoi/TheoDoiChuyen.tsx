import { useState, type FormEvent } from 'react'
import { dongSuCo, ketThucSuCo, type ChuyenChiTiet } from '../../api/chuyen'
import { kemMaBr, LoiApi } from '../../api/goi'
import { Nhan } from '../../nhan'

const dong = (n: number) => `${n.toLocaleString('vi-VN')} đ`
const lucVN = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })

// UC-32: cảnh báo chồng lịch (BR-73), kết thúc do sự cố (BR-68), tiền, sự cố, dòng thời gian.
// Chỉ có khi trang tải bằng GET chi tiết (có `tien`); kết quả ghép / gỡ / chốt không kèm phần này.
// Mỗi phần là một khối riêng để màn chi tiết đặt vào đúng chỗ của bố cục.

export function CanhBaoTheoDoi({
  c,
  onDoi,
}: {
  c: ChuyenChiTiet
  onDoi: (c: ChuyenChiTiet) => void
}) {
  if (!c.tien) return null
  return (
    <>
      {(c.chong?.length ?? 0) > 0 && c.ket_thuc_dang_chay && (
        <p role="alert" className="loi">
          Đang trễ: dự kiến xong {lucVN(c.ket_thuc_dang_chay)}, chồng lên chuyến kế tiếp của xe /
          tài xế: {c.chong!.join(', ')} (BR-73). Hệ thống không tự đổi lịch.
        </p>
      )}
      {c.ket_thuc_bat_thuong && <p className="canh-bao">Kết thúc do sự cố: {c.ly_do_ket_thuc}</p>}
      {c.trang_thai === 'DANG_CHAY' && <KetThucSuCo c={c} onDoi={onDoi} />}
    </>
  )
}

// Khối tiền: doanh thu, định mức, lương, lãi dự kiến, tạm ứng (số đã chốt khi chuyến đã chốt)
export function KhoiTien({ c }: { c: ChuyenChiTiet }) {
  if (!c.tien) return null
  return (
    <section className="kinh ct-khoi">
      <h2>Tiền</h2>
      <dl className="ct-tien">
        <dt>Doanh thu dự kiến</dt>
        <dd>{dong(c.tien.doanh_thu)}</dd>
        <dt>Định mức chi phí</dt>
        <dd>− {dong(c.tien.dinh_muc)}</dd>
        <dt>Lương tài xế</dt>
        <dd>− {dong(c.tien.luong)}</dd>
        <dt className="ct-lai">Lãi dự kiến</dt>
        <dd className={c.canh_bao_lai_am ? 'ct-lai het-han' : 'ct-lai'}>{dong(c.lai_du_kien)}</dd>
        <dt>Tạm ứng còn hiệu lực</dt>
        <dd>{dong(c.tien.tam_ung_hieu_luc)}</dd>
        {c.km_bat_dau != null && (
          <>
            <dt>Km đồng hồ</dt>
            <dd>
              {c.km_bat_dau.toLocaleString('vi-VN')}
              {c.km_ket_thuc != null && ` → ${c.km_ket_thuc.toLocaleString('vi-VN')}`}
            </dd>
          </>
        )}
      </dl>
    </section>
  )
}

export function KhoiSuCo({ c, onDoi }: { c: ChuyenChiTiet; onDoi: () => void }) {
  if (!c.tien || !c.su_co?.length) return null
  return (
    <section className="kinh ct-khoi">
      <h2>Sự cố</h2>
      <ul className="ds-the">
        {c.su_co.map((s) => (
          <li key={s.id} className="the">
            <div className="the-dau">
              <strong>
                {s.loai} · {lucVN(s.luc)}
              </strong>
              <Nhan loai={s.trang_thai === 'MO' ? 'SU_CO' : 'HOAN_THANH'}>
                {s.trang_thai === 'MO' ? 'Đang mở' : 'Đã đóng'}
              </Nhan>
            </div>
            {s.ghi_chu && <div>{s.ghi_chu}</div>}
            {s.cach_xu_ly && <div className="ghi-chu">Cách xử lý: {s.cach_xu_ly}</div>}
            {s.trang_thai === 'MO' && <DongSuCo id={s.id} onXong={onDoi} />}
          </li>
        ))}
      </ul>
    </section>
  )
}

// Dòng thời gian: mới nhất trên cùng, giờ bên trái
export function DongThoiGian({ c }: { c: ChuyenChiTiet }) {
  if (!c.tien) return null
  const ds = [...(c.dong_thoi_gian ?? [])].reverse()
  return (
    <section className="kinh ct-khoi">
      <h2>Dòng thời gian</h2>
      <ol className="dtg">
        {ds.map((s, i) => (
          <li key={i}>
            <time>{lucVN(s.luc)}</time>
            <span>
              {s.noi_dung}
              {s.nguoi && <small>{s.nguoi}</small>}
            </span>
          </li>
        ))}
        {ds.length === 0 && <li className="ghi-chu">Chưa có sự kiện</li>}
      </ol>
    </section>
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
