import { useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { LoiApi } from '../../api/goi'
import { Nhan } from '../../nhan'
import {
  TEN_TRANG_THAI,
  chuyenCuaToiChiTiet,
  ghiKm,
  khoangGio,
  ngayGio,
  thongBaoQuet,
  type ChuyenCuaToiChiTiet as ChiTiet,
  type KetQuaQuet,
} from '../../api/toi'
import { nenAnh } from '../../nenAnh'
import { ChiPhi } from './ChiPhi'
import { SuCoChuyen } from './SuCo'
import { GiaoHang } from './GiaoHang'
import { KhongLay, QuetLay } from './QuetLay'

const gio = (iso: string) =>
  new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
// Nhãn theo việc của điểm: điểm Lấy của đơn đã giao vẫn là "Đã lấy", không phải "Đã giao"
const NHAN_DIEM: Record<'LAY' | 'GIAO', Record<string, string>> = {
  LAY: { DA_GHEP: 'Chờ lấy', DA_LAY: 'Đã lấy', DA_GIAO: 'Đã lấy', TRA_HANG: 'Đã lấy' },
  GIAO: { DA_GHEP: 'Chưa lấy hàng', DA_LAY: 'Chờ giao', DA_GIAO: 'Đã giao', TRA_HANG: 'Trả hàng' },
}
// Đơn thất bại: điểm Lấy là "Đã lấy" nếu chuyến này đã quét lấy (thất bại khi giao), không thì "Thất bại"
const nhanDiem = (viec: 'LAY' | 'GIAO', tt: string, daLay: boolean) =>
  NHAN_DIEM[viec][tt] ??
  (tt === 'THAT_BAI' ? (viec === 'LAY' && daLay ? 'Đã lấy' : 'Thất bại') : tt)
// Nhãn tính là điểm đã xong (chấm đặc trên dòng thời gian)
const XONG = ['Đã lấy', 'Đã giao', 'Trả hàng']

// UC-17: lịch trình cho tài xế – từng điểm dừng, đơn, địa chỉ, gọi điện. Không có cước (quyết định số 3)
// UC-18: chuyến chờ chạy có ô Bắt đầu, chuyến đang chạy có ô Kết thúc (km + ảnh đồng hồ)
// UC-19: chuyến đang chạy có khối Lấy hàng (quét QR / gõ mã); điểm lấy chưa lấy có nút Không lấy được
// UC-20: điểm giao của đơn đã lấy có Giao hàng (quét xác nhận, ảnh, tên, chữ ký) và Giao không được
export default function ChuyenCuaToiChiTiet() {
  const { id } = useParams()
  const [c, setC] = useState<ChiTiet | null>(null)
  const [loi, setLoi] = useState('')
  const [quet, setQuet] = useState<KetQuaQuet | null>(null)
  const tb = quet && c ? thongBaoQuet(quet, c) : null

  // Quét xong: giữ câu báo, tải lại lịch trình để trạng thái điểm đổi ngay
  const xongQuet = (kq: KetQuaQuet) => {
    setQuet(kq)
    chuyenCuaToiChiTiet(Number(id))
      .then(setC)
      .catch(() => setLoi('Đã ghi nhận nhưng không tải lại được lịch trình, kéo xuống để tải lại'))
  }

  useEffect(() => {
    chuyenCuaToiChiTiet(Number(id))
      .then(setC)
      .catch((e) => setLoi(e instanceof LoiApi ? e.message : 'Không tải được chuyến'))
  }, [id])

  // Trạng thái từng điểm cho dòng thời gian: xong / thất bại / đang tới (điểm đầu chưa xong khi đang chạy)
  const nhan = (p: ChiTiet['lich_trinh'][number]) => nhanDiem(p.viec, p.trang_thai_don, p.da_lay)
  const xongDiem = (p: ChiTiet['lich_trinh'][number]) => XONG.includes(nhan(p))
  const keTiep =
    c?.trang_thai === 'DANG_CHAY'
      ? c.lich_trinh.find((p) => !xongDiem(p) && nhan(p) !== 'Thất bại')
      : undefined
  const soXong = c ? c.lich_trinh.filter(xongDiem).length : 0
  // Còn điểm lấy chưa quét thì mới cần khối Lấy hàng (quét lấy); lấy hết rồi thì giao ở từng điểm
  const conLay = !!c?.lich_trinh.some((p) => p.viec === 'LAY' && p.trang_thai_don === 'DA_GHEP')
  const idDiem = (p: ChiTiet['lich_trinh'][number]) => `diem-${p.viec}-${p.don_id}`
  // Cuộn tới một khối; máy bật giảm chuyển động thì nhảy thẳng
  const toi = (id: string) =>
    document.getElementById(id)?.scrollIntoView({
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start',
    })

  return (
    <section className="noi-dung dien-thoai">
      <Link to=".." relative="path" className="ct-ve">
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
          {/* Khối chính: đậm khi đang chạy (điểm kế tiếp + tiến độ), nhạt khi chờ chạy / đã xong */}
          <section className={c.trang_thai === 'DANG_CHAY' ? 'the-chinh' : 'the-chinh nhat'}>
            <div className="dong">
              <span className="ma">{c.ma_chuyen}</span>
              <Nhan loai={c.trang_thai}>{TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}</Nhan>
            </div>
            <div>
              <h1>{c.ten_tuyen}</h1>
              <div className="mo-chu">
                <span className="bien">{c.bien_so}</span>
                {khoangGio(c.khoi_hanh_du_kien, c.ket_thuc_du_kien)}
              </div>
              <div className="mo-chu">
                {c.so_don} đơn
                {c.luong_tai_xe_chot !== null &&
                  ` · Lương chuyến ${c.luong_tai_xe_chot.toLocaleString('vi-VN')} đ`}
              </div>
            </div>
            {c.lich_trinh.length > 0 && (
              <div>
                <div className="doan" aria-hidden="true">
                  {c.lich_trinh.map((p) => (
                    <i
                      key={`${p.viec}-${p.don_id}`}
                      className={
                        xongDiem(p)
                          ? 'x'
                          : nhan(p) === 'Thất bại'
                            ? 'f'
                            : p === keTiep
                              ? 'c'
                              : undefined
                      }
                    />
                  ))}
                </div>
                <div className="mo-chu">
                  Xong {soXong} / {c.lich_trinh.length} điểm
                </div>
              </div>
            )}
            {keTiep && (
              <div className="ke">
                <div className="luc">
                  <span>Điểm kế tiếp · {keTiep.viec === 'LAY' ? 'Lấy hàng' : 'Giao hàng'}</span>
                  <span>dự kiến {gio(keTiep.eta)}</span>
                </div>
                <strong>{keTiep.nut}</strong>
                <p>
                  {keTiep.dia_chi} · {keTiep.so_kien} kiện · {keTiep.ma_don}
                </p>
                <div className="ke-nut">
                  <button type="button" className="nut-to" onClick={() => toi(idDiem(keTiep))}>
                    {keTiep.viec === 'LAY' ? 'Tới điểm lấy' : 'Tới điểm, giao hàng'}
                  </button>
                  <a className="nut-vien" href={`tel:${keTiep.sdt}`}>
                    Gọi {keTiep.nguoi_lien_he ?? keTiep.sdt}
                  </a>
                  <button type="button" className="nut-vien" onClick={() => toi('khoi-su-co')}>
                    Gặp sự cố trên đường
                  </button>
                </div>
              </div>
            )}
          </section>

          {tb && (
            <div role="status">
              <p className="thanh-cong">{tb.xong}</p>
              {tb.canhBao.map((x) => (
                <p key={x} className="canh-bao">
                  {x}
                </p>
              ))}
            </div>
          )}
          {c.trang_thai === 'DANG_CHAY' && conLay && <QuetLay onXong={xongQuet} />}

          {c.trang_thai === 'DA_CHOT' && <FormKm key={c.trang_thai} c={c} onXong={setC} />}

          <h2>Lịch trình</h2>
          {c.lich_trinh.length === 0 && <p className="trong">Chuyến chạy rỗng – không có đơn</p>}
          <ol className="lt lt-dt">
            {c.lich_trinh.map((p) => (
              <li
                key={`${p.viec}-${p.don_id}`}
                id={idDiem(p)}
                className={
                  xongDiem(p)
                    ? 'xong'
                    : nhan(p) === 'Thất bại'
                      ? 'hong'
                      : p === keTiep
                        ? 'toi'
                        : undefined
                }
              >
                <i aria-hidden="true" />
                <div className="the">
                  <div className="the-dau">
                    <strong>
                      {gio(p.eta)} · {p.viec === 'LAY' ? 'Lấy' : 'Giao'} tại {p.nut}
                    </strong>
                    <span className="nhan xam">{nhan(p)}</span>
                  </div>
                  <div>
                    <span className="bien-so">{p.ma_don}</span> · {p.ten_khach}
                    {p.mo_ta && ` · ${p.mo_ta}`}
                  </div>
                  <div className="ghi-chu">
                    {Number(p.kg).toLocaleString('vi-VN')} kg ·{' '}
                    {Number(p.m3).toLocaleString('vi-VN')} m³ · {p.so_kien} kiện
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
                  {c.trang_thai === 'DANG_CHAY' &&
                    p.viec === 'LAY' &&
                    p.trang_thai_don === 'DA_GHEP' && (
                      <KhongLay maDon={p.ma_don} onXong={xongQuet} />
                    )}
                  {c.trang_thai === 'DANG_CHAY' &&
                    p.viec === 'GIAO' &&
                    p.trang_thai_don === 'DA_LAY' && (
                      <div className="giao-nut">
                        <GiaoHang maDon={p.ma_don} onXong={xongQuet} />
                        <KhongLay maDon={p.ma_don} viec="GIAO" onXong={xongQuet} />
                      </div>
                    )}
                </div>
              </li>
            ))}
          </ol>

          {/* Kết thúc nằm sau lịch trình: còn điểm chưa xong thì không đứng chắn ở đầu trang */}
          {c.trang_thai === 'DANG_CHAY' && <FormKm key={c.trang_thai} c={c} onXong={setC} />}

          {['DANG_CHAY', 'HOAN_THANH', 'DA_QUYET_TOAN'].includes(c.trang_thai) && (
            <ChiPhi chuyenId={c.id} ghiDuoc={c.trang_thai !== 'DA_QUYET_TOAN'} />
          )}
          {['DANG_CHAY', 'HOAN_THANH', 'DA_QUYET_TOAN'].includes(c.trang_thai) && (
            <div id="khoi-su-co" className="neo">
              <SuCoChuyen chuyenId={c.id} baoDuoc={c.trang_thai === 'DANG_CHAY'} />
            </div>
          )}
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
