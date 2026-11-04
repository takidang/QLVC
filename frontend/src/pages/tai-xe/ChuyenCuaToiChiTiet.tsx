import { useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { LoiApi } from '../../api/goi'
import {
  TEN_TRANG_THAI,
  chuyenCuaToiChiTiet,
  ghiKm,
  ngayGio,
  type ChuyenCuaToiChiTiet as ChiTiet,
} from '../../api/toi'
import { nenAnh } from '../../nenAnh'

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
// UC-18: chuyến chờ chạy có ô Bắt đầu, chuyến đang chạy có ô Kết thúc (km + ảnh đồng hồ)
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

          {(c.trang_thai === 'DA_CHOT' || c.trang_thai === 'DANG_CHAY') && (
            <FormKm key={c.trang_thai} c={c} onXong={setC} />
          )}

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

// Lỗi nghiệp vụ có danh sách (BR-11…15 giấy tờ, BR-28 đơn còn lại): hiện từng dòng kèm mã BR
const dongLoi = (e: unknown): string[] => {
  if (!(e instanceof LoiApi)) return ['Không gửi được, kiểm tra mạng rồi thử lại']
  const ds = (e.chiTiet as { ma?: string; thong_diep?: string }[]).filter((x) => x.thong_diep)
  return ds.length ? [e.message, ...ds.map((x) => `${x.thong_diep} (${x.ma})`)] : [e.message]
}

function FormKm({ c, onXong }: { c: ChiTiet; onXong: (c: ChiTiet) => void }) {
  const batDau = c.trang_thai === 'DA_CHOT'
  const [km, setKm] = useState('')
  const [anh, setAnh] = useState<File | null>(null)
  const [loi, setLoi] = useState<string[]>([])
  const [dangGui, setDangGui] = useState(false)

  async function gui(e: FormEvent) {
    e.preventDefault()
    if (!anh) return setLoi(['Chụp ảnh đồng hồ km trước khi gửi'])
    setLoi([])
    setDangGui(true)
    try {
      onXong(await ghiKm(c.id, batDau ? 'bat-dau' : 'ket-thuc', Number(km), await nenAnh(anh)))
    } catch (err) {
      setLoi(err instanceof Error && !(err instanceof LoiApi) ? [err.message] : dongLoi(err))
    } finally {
      setDangGui(false)
    }
  }

  return (
    <form className="the form-km" onSubmit={gui}>
      <strong>{batDau ? 'Bắt đầu chuyến' : 'Kết thúc chuyến'}</strong>
      <label>
        Km đồng hồ {batDau ? 'lúc xuất phát' : 'lúc về'}
        <input
          type="number"
          inputMode="numeric"
          min={0}
          required
          value={km}
          onChange={(e) => setKm(e.target.value)}
        />
      </label>
      <label>
        Ảnh đồng hồ km
        <input
          type="file"
          accept="image/jpeg,image/png"
          capture="environment"
          required
          onChange={(e) => setAnh(e.target.files?.[0] ?? null)}
        />
      </label>
      {loi.length > 0 && (
        <ul role="alert" className="loi">
          {loi.map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      )}
      <button disabled={dangGui}>{dangGui ? 'Đang gửi…' : batDau ? 'Bắt đầu' : 'Kết thúc'}</button>
    </form>
  )
}
