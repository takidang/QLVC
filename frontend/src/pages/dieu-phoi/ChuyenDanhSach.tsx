import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import {
  danhSachChuyen,
  lapChuyen,
  taiXeKhaDung,
  xeKhaDung,
  type Chuyen,
  type LyDo,
  type TaiXeKhaDung,
  type XeKhaDung,
} from '../../api/chuyen'
import { kemMaBr, LoiApi, loiTheoTruong } from '../../api/goi'
import { danhSachTuyen, type Tuyen } from '../../api/tuyen'

const SO_DONG = 20
const lucVN = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
// Ô datetime-local không có múi giờ; nhà xe ở Việt Nam nên gắn +07:00 (API bắt buộc có múi giờ)
const coMuiGio = (v: string) => `${v}:00+07:00`
const TEN_TRANG_THAI: Record<string, string> = {
  LAP: 'Đang lập',
  DA_CHOT: 'Đã chốt',
  DANG_CHAY: 'Đang chạy',
  HOAN_THANH: 'Hoàn thành',
  DA_QUYET_TOAN: 'Đã quyết toán',
  HUY: 'Hủy',
}
// Mỗi vi phạm hiện kèm mã quy tắc (NFR-USA-02)
const cauLoi = (ly_do: LyDo[]) => ly_do.map((v) => kemMaBr(v.thong_diep, v.ma))

export default function ChuyenDanhSach() {
  const [ngay, setNgay] = useState('')
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: Chuyen[]; tong: number }>({ du_lieu: [], tong: 0 })
  const [loiTai, setLoiTai] = useState('')
  const [moForm, setMoForm] = useState(false)
  const [vuaLap, setVuaLap] = useState<Chuyen | null>(null)
  const [lanTai, setLanTai] = useState(0)

  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ
    danhSachChuyen({ ngay, trang_thai: trangThai, trang, so_dong: SO_DONG })
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (!bo) setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách chuyến')
      })
    return () => {
      bo = true
    }
  }, [ngay, trangThai, trang, lanTai])

  const soTrang = Math.max(1, Math.ceil(ds.tong / SO_DONG))
  return (
    <section className="noi-dung">
      <div className="thanh-cong-cu">
        <h1>Chuyến</h1>
        <input
          type="date"
          aria-label="Ngày khởi hành"
          value={ngay}
          onChange={(e) => {
            setNgay(e.target.value)
            setTrang(1)
          }}
        />
        <select
          aria-label="Lọc trạng thái"
          value={trangThai}
          onChange={(e) => {
            setTrangThai(e.target.value)
            setTrang(1)
          }}
        >
          <option value="">Mọi trạng thái</option>
          {Object.entries(TEN_TRANG_THAI).map(([ma, ten]) => (
            <option key={ma} value={ma}>
              {ten}
            </option>
          ))}
        </select>
        <button onClick={() => setMoForm(true)}>Lập chuyến</button>
      </div>
      {vuaLap && (
        <p className="thanh-cong">
          Đã lập chuyến <strong>{vuaLap.ma_chuyen}</strong> ({vuaLap.ma_tuyen}, {vuaLap.bien_so},{' '}
          {vuaLap.ten_tai_xe}).
        </p>
      )}
      {loiTai && (
        <p role="alert" className="loi">
          {loiTai}
        </p>
      )}

      <table>
        <thead>
          <tr>
            <th>Mã chuyến</th>
            <th>Tuyến</th>
            <th>Xe</th>
            <th>Tài xế</th>
            <th>Khởi hành</th>
            <th>Kết thúc dự kiến</th>
            <th>Trạng thái</th>
          </tr>
        </thead>
        <tbody>
          {ds.du_lieu.map((c) => (
            <tr key={c.id}>
              <td className="bien-so">
                <Link to={String(c.id)}>{c.ma_chuyen}</Link>
              </td>
              <td>
                {c.ma_tuyen} – {c.ten_tuyen}
              </td>
              <td className="bien-so">{c.bien_so}</td>
              <td>{c.ten_tai_xe}</td>
              <td>{lucVN(c.khoi_hanh_du_kien)}</td>
              <td>{lucVN(c.ket_thuc_du_kien)}</td>
              <td>{TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}</td>
            </tr>
          ))}
          {ds.du_lieu.length === 0 && (
            <tr>
              <td colSpan={7} className="trong">
                Chưa có chuyến nào phù hợp
              </td>
            </tr>
          )}
        </tbody>
      </table>
      <div className="phan-trang">
        <button className="phu" disabled={trang <= 1} onClick={() => setTrang(trang - 1)}>
          Trước
        </button>
        <span>
          Trang {trang}/{soTrang} · {ds.tong} chuyến
        </span>
        <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
          Sau
        </button>
      </div>

      {moForm && (
        <FormLapChuyen
          onDong={() => setMoForm(false)}
          onLuu={(c) => {
            setMoForm(false)
            setVuaLap(c)
            setLanTai((n) => n + 1)
          }}
        />
      )}
    </section>
  )
}

export type KhaDung<T> = { khoa: string; ds: T[]; loi: string }

function FormLapChuyen({ onDong, onLuu }: { onDong: () => void; onLuu: (c: Chuyen) => void }) {
  const [dsTuyen, setDsTuyen] = useState<Tuyen[]>([])
  const [tuyenId, setTuyenId] = useState('')
  const [khoiHanh, setKhoiHanh] = useState('')
  const [xeId, setXeId] = useState('')
  const [taiXeId, setTaiXeId] = useState('')
  // Danh sách khả dụng gắn với đúng tuyến + giờ (+ xe) đã hỏi; đổi lựa chọn thì không hiện kết quả cũ
  const [xe, setXe] = useState<KhaDung<XeKhaDung>>()
  const [taiXe, setTaiXe] = useState<KhaDung<TaiXeKhaDung>>()
  const [loiTruong, setLoiTruong] = useState<Record<string, string>>({})
  const [loiChung, setLoiChung] = useState<string[]>([])
  const [dangGui, setDangGui] = useState(false)

  useEffect(() => {
    // shortcut: tối đa 100 tuyến đang hoạt động, đủ cho nhà xe nhỏ
    danhSachTuyen({ trang_thai: 'HOAT_DONG', so_dong: 100 })
      .then((r) => setDsTuyen(r.du_lieu))
      .catch(() => setLoiChung(['Không tải được danh sách tuyến']))
  }, [])

  const duDeHoi = !!tuyenId && !!khoiHanh
  const khoaXe = `${tuyenId}|${khoiHanh}`
  const khoaTaiXe = `${khoaXe}|${xeId}`
  useEffect(() => {
    if (!duDeHoi) return
    let bo = false
    xeKhaDung(Number(tuyenId), coMuiGio(khoiHanh))
      .then((ds) => !bo && setXe({ khoa: khoaXe, ds, loi: '' }))
      .catch(
        (e) => !bo && setXe({ khoa: khoaXe, ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [duDeHoi, khoaXe, tuyenId, khoiHanh])
  useEffect(() => {
    if (!duDeHoi) return
    let bo = false
    // Đã chọn xe thì lọc thêm hạng GPLX theo xe (BR-14)
    taiXeKhaDung(Number(tuyenId), coMuiGio(khoiHanh), xeId ? Number(xeId) : undefined)
      .then((ds) => !bo && setTaiXe({ khoa: khoaTaiXe, ds, loi: '' }))
      .catch(
        (e) =>
          !bo &&
          setTaiXe({ khoa: khoaTaiXe, ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [duDeHoi, khoaTaiXe, tuyenId, khoiHanh, xeId])
  const dsXe = duDeHoi && xe?.khoa === khoaXe ? xe : undefined
  const dsTaiXe = duDeHoi && taiXe?.khoa === khoaTaiXe ? taiXe : undefined

  async function gui(e: FormEvent) {
    e.preventDefault()
    setLoiTruong({})
    setLoiChung([])
    setDangGui(true)
    try {
      onLuu(
        await lapChuyen({
          tuyen_id: Number(tuyenId),
          khoi_hanh_du_kien: coMuiGio(khoiHanh),
          xe_id: Number(xeId),
          tai_xe_id: Number(taiXeId),
        }),
      )
    } catch (err) {
      const theoTruong = loiTheoTruong(err)
      setLoiTruong(theoTruong)
      if (err instanceof LoiApi && err.chiTiet.length && Object.keys(theoTruong).length === 0)
        setLoiChung(cauLoi(err.chiTiet as LyDo[]))
      else if (Object.keys(theoTruong).length === 0)
        setLoiChung([err instanceof LoiApi ? err.message : 'Không lưu được, vui lòng thử lại'])
    } finally {
      setDangGui(false)
    }
  }

  return (
    <div className="nen-mo" onClick={onDong}>
      <form className="hop-thoai rong" onSubmit={gui} onClick={(e) => e.stopPropagation()}>
        <h2>Lập chuyến</h2>
        <div className="hai-cot">
          <label>
            Tuyến
            <select
              value={tuyenId}
              onChange={(e) => {
                setTuyenId(e.target.value)
                setXeId('')
                setTaiXeId('')
              }}
              required
            >
              <option value="">– Chọn tuyến –</option>
              {dsTuyen.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.ma} – {t.ten} ({Math.floor(t.tong_phut / 60)} giờ {t.tong_phut % 60} phút)
                </option>
              ))}
            </select>
          </label>
          <label>
            Giờ khởi hành
            <input
              type="datetime-local"
              value={khoiHanh}
              onChange={(e) => {
                setKhoiHanh(e.target.value)
                setXeId('')
                setTaiXeId('')
              }}
              aria-invalid={!!loiTruong.khoi_hanh_du_kien}
              required
            />
            {loiTruong.khoi_hanh_du_kien && (
              <span className="loi">{loiTruong.khoi_hanh_du_kien}</span>
            )}
          </label>
        </div>

        {!duDeHoi ? (
          <p className="ghi-chu">Chọn tuyến và giờ khởi hành để xem xe, tài xế dùng được.</p>
        ) : (
          <div className="hai-cot">
            <ChonKhaDung
              nhan="Xe"
              kq={dsXe}
              gia_tri={xeId}
              onChon={(v) => {
                setXeId(v)
                setTaiXeId('')
              }}
              ten={(x) => `${x.bien_so} (${x.tai_trong_kg.toLocaleString('vi-VN')} kg)`}
            />
            <ChonKhaDung
              nhan="Tài xế"
              kq={dsTaiXe}
              gia_tri={taiXeId}
              onChon={setTaiXeId}
              ten={(t) => `${t.ho_ten} (hạng ${t.hang_gplx})`}
            />
          </div>
        )}

        {loiChung.length > 0 && (
          <ul role="alert" className="loi">
            {loiChung.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        )}
        <div className="nut">
          <button type="button" className="phu" onClick={onDong}>
            Hủy
          </button>
          <button disabled={dangGui || !xeId || !taiXeId}>
            {dangGui ? 'Đang lưu…' : 'Lập chuyến'}
          </button>
        </div>
      </form>
    </div>
  )
}

// Ô chọn xe / tài xế: cái bị loại không chọn được, lý do loại hiện bên dưới (UC-11 luồng chính bước 2)
export function ChonKhaDung<T extends { id: number; kha_dung: boolean; ly_do: LyDo[] }>({
  nhan,
  kq,
  gia_tri,
  onChon,
  ten,
}: {
  nhan: string
  kq: KhaDung<T> | undefined
  gia_tri: string
  onChon: (v: string) => void
  ten: (x: T) => string
}) {
  const biLoai = kq?.ds.filter((x) => !x.kha_dung) ?? []
  return (
    <div>
      <label>
        {nhan}
        <select value={gia_tri} onChange={(e) => onChon(e.target.value)} required disabled={!kq}>
          <option value="">{kq ? `– Chọn ${nhan.toLowerCase()} –` : 'Đang tải…'}</option>
          {kq?.ds.map((x) => (
            <option key={x.id} value={x.id} disabled={!x.kha_dung}>
              {ten(x)}
              {!x.kha_dung && ' – không dùng được'}
            </option>
          ))}
        </select>
      </label>
      {kq?.loi && <p className="loi">{kq.loi}</p>}
      {biLoai.length > 0 && (
        <ul className="ghi-chu">
          {biLoai.map((x) => (
            <li key={x.id}>
              <strong>{ten(x)}:</strong> {cauLoi(x.ly_do).join('; ')}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
