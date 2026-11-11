import { lazy, Suspense, useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  danhSachChuyen,
  phutDoc,
  TEN_CO,
  lapChuyen,
  taiXeKhaDung,
  xeKhaDung,
  type Chuyen,
  type LyDo,
  type TaiXeKhaDung,
  type XeKhaDung,
} from '../../api/chuyen'
import { canhBao } from '../../api/canhBao'
import { donCanXuLy } from '../../api/don'
import { kemMaBr, LoiApi, loiTheoTruong } from '../../api/goi'
import { TEN_LOAI_SU_CO, type LoaiSuCo } from '../../api/suCo'
import { danhSachTuyen, type Tuyen } from '../../api/tuyen'
import { Ic, Nhan } from '../../nhan'
import LichGio from './LichGio'

// Bản đồ (leaflet + css) tải riêng, chỉ khi ngày đang xem có chuyến
const BanDoNgay = lazy(() => import('./BanDoNgay'))

const SO_DONG = 20
const homNay = () => new Date().toLocaleDateString('sv-SE')
const gio = (iso: string) =>
  new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
const ngayThang = (iso: string) => new Date(iso).toLocaleDateString('en-GB').slice(0, 5) // dd/mm
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
// Đoạn của thanh điểm dừng theo trạng thái điểm (UC-32, PR #41)
const DOAN: Record<string, string | undefined> = {
  XONG: 'x',
  THAT_BAI: 'f',
  DANG_TOI: 'c',
  CHUA: undefined,
}
// Cờ đưa lên khung "Cần chú ý" (Chưa quyết toán là việc của kế toán, không phải việc gấp của điều phối)
const CO_CHU_Y = ['TRE', 'SU_CO', 'THAT_BAI', 'CHONG_LICH']
// Việc khác của hôm nay trên khung "Cần chú ý": lấy từ bảng cảnh báo UC-27 (GET /api/canh-bao)
// và đơn thất bại chờ xử lý (UC-22). Chuyến trễ / chồng lịch của ngày đang xem đã có ở danh sách chuyến
type Viec = { den: string; nang: boolean; chinh: string; phu: string; ma?: string }
const ngayVN = (ymd: string) => ymd.slice(0, 10).split('-').reverse().join('/')
const TEN_GIAY: Record<string, string> = {
  DANG_KIEM: 'đăng kiểm',
  BAO_HIEM: 'bảo hiểm',
  GPLX: 'GPLX',
}
async function viecHomNay(): Promise<Viec[]> {
  // Mỗi nguồn hỏng riêng thì bỏ qua nguồn đó, không làm mất cả khung
  const [cb, don] = await Promise.all([canhBao().catch(() => null), donCanXuLy().catch(() => [])])
  const ds = (n: number, ma: string[]) => ma.slice(0, 3).join(', ') + (n > 3 ? '…' : '')
  const quaHan = cb?.don_sap_qua_han.filter((d) => d.qua_han) ?? []
  const sapHan = cb?.don_sap_qua_han.filter((d) => !d.qua_han) ?? []
  return [
    ...(cb?.su_co_mo ?? []).map((x) => ({
      ma: x.ma_chuyen,
      den: String(x.chuyen_id),
      nang: true,
      chinh: `${x.ma_chuyen} · Sự cố ${TEN_LOAI_SU_CO[x.loai as LoaiSuCo]?.toLowerCase() ?? x.loai}`,
      phu: `${x.bien_so}, ${x.ten_tai_xe}${x.ghi_chu ? ` · ${x.ghi_chu}` : ''}`,
    })),
    // Chuyến trễ: chuyến đã có trong danh sách ngày đang xem bị lọc bỏ lúc vẽ (trường `ma`)
    ...(cb?.chuyen_tre ?? []).map((x) => ({
      ma: x.ma_chuyen,
      den: String(x.chuyen_id),
      nang: x.chong.length > 0,
      chinh: `${x.ma_chuyen} · ${x.tre_phut ? `Trễ ${phutDoc(x.tre_phut)}` : 'Chồng lịch'}`,
      phu: `${x.bien_so}, ${x.ten_tai_xe}${x.chong.length ? ` · trùng ${x.chong.join(', ')}` : ''}`,
    })),
    ...(don.length
      ? [
          {
            den: '../don',
            nang: true,
            chinh: `${don.length} đơn thất bại chờ xử lý`,
            phu: ds(
              don.length,
              don.map((d) => d.ma_don),
            ),
          },
        ]
      : []),
    ...(quaHan.length
      ? [
          {
            den: '../don',
            nang: true,
            chinh: `${quaHan.length} đơn chờ ghép đã quá hạn giao`,
            phu: ds(
              quaHan.length,
              quaHan.map((d) => d.ma_don),
            ),
          },
        ]
      : []),
    ...(sapHan.length
      ? [
          {
            den: '../don',
            nang: false,
            chinh: `${sapHan.length} đơn chờ ghép sắp tới hạn giao`,
            phu: `Còn dưới ${cb!.cau_hinh.gio_cho_ghep} giờ · ${ds(
              sapHan.length,
              sapHan.map((d) => d.ma_don),
            )}`,
          },
        ]
      : []),
    ...(cb?.thieu_gps.length
      ? [
          {
            den: '../chuyen',
            nang: false,
            chinh: `${cb.thieu_gps.length} lượt quét thiếu GPS`,
            phu: 'Tài xế quét khi điện thoại chưa bật định vị (BR-43)',
          },
        ]
      : []),
    ...(cb?.giay_to ?? []).map((g) => ({
      den: g.doi_tuong === 'XE' ? '../xe' : '../tai-xe',
      nang: g.het_han,
      chinh: `${g.ten} · ${TEN_GIAY[g.loai] ?? g.loai} ${g.het_han ? 'đã hết hạn' : 'sắp hết hạn'}`,
      phu: `Hạn ${ngayVN(g.han)}${g.het_han ? '' : ` · còn ${g.con_ngay} ngày`}`,
    })),
  ]
}
// Mỗi vi phạm hiện kèm mã quy tắc (NFR-USA-02)
const cauLoi = (ly_do: LyDo[]) => ly_do.map((v) => kemMaBr(v.thong_diep, v.ma))
// Vạch của một chuyến trên dải đầu trang: xong đặc, đang chạy xanh, trễ cam, hủy rỗng
const lopVach = (c: Chuyen) =>
  c.trang_thai === 'HUY'
    ? 'h'
    : c.trang_thai === 'DANG_CHAY' && c.theo_doi?.co.includes('TRE')
      ? 't'
      : c.trang_thai === 'DANG_CHAY'
        ? 'c'
        : c.trang_thai === 'HOAN_THANH' || c.trang_thai === 'DA_QUYET_TOAN'
          ? 'x'
          : undefined

export default function ChuyenDanhSach() {
  const dieuHuong = useNavigate()
  const [ngay, setNgay] = useState(homNay) // '' = mọi ngày
  const [trangThai, setTrangThai] = useState('')
  const [trang, setTrang] = useState(1)
  const [ds, setDs] = useState<{ du_lieu: Chuyen[]; tong: number } | null>(null) // null = đang tải
  const [loiTai, setLoiTai] = useState('')
  const [moForm, setMoForm] = useState(false)
  const [vuaLap, setVuaLap] = useState<Chuyen | null>(null)
  const [lanTai, setLanTai] = useState(0)
  const [tim, setTim] = useState('')
  const [tuKhoa, setTuKhoa] = useState('') // giá trị ô tìm sau khi ngừng gõ 300 ms
  useEffect(() => {
    const h = setTimeout(() => {
      setTuKhoa(tim.trim())
      setTrang(1)
    }, 300)
    return () => clearTimeout(h)
  }, [tim])
  const [viec, setViec] = useState<Viec[]>([])
  useEffect(() => {
    viecHomNay().then(setViec)
  }, [])

  // Xem theo ngày: lấy cả ngày một lượt để đếm theo trạng thái, lọc trạng thái tại chỗ.
  // shortcut: tối đa 100 chuyến một ngày, đủ cho nhà xe nhỏ. Mọi ngày: máy chủ lọc và phân trang như cũ.
  const locMayChu = ngay ? '' : trangThai
  const trangMayChu = ngay ? 1 : trang
  useEffect(() => {
    let bo = false // yêu cầu cũ về muộn thì bỏ
    danhSachChuyen(
      ngay
        ? { ngay, tu_khoa: tuKhoa, so_dong: 100 }
        : { trang_thai: locMayChu, tu_khoa: tuKhoa, trang: trangMayChu, so_dong: SO_DONG },
    )
      .then((r) => {
        if (bo) return
        setDs(r)
        setLoiTai('')
      })
      .catch((e) => {
        if (bo) return
        setDs({ du_lieu: [], tong: 0 })
        setLoiTai(e instanceof LoiApi ? e.message : 'Không tải được danh sách chuyến')
      })
    return () => {
      bo = true
    }
  }, [ngay, locMayChu, trangMayChu, tuKhoa, lanTai])

  const chonNgay = (v: string) => {
    setNgay(v)
    setTrang(1)
    setDs(null)
  }
  // Cả ngày, xếp theo giờ đi (máy chủ trả mới nhất trước)
  const caNgay = ngay
    ? [...(ds?.du_lieu ?? [])].sort(
        (a, b) => Date.parse(a.khoi_hanh_du_kien) - Date.parse(b.khoi_hanh_du_kien),
      )
    : []
  const dem = (...tt: string[]) => caNgay.filter((c) => tt.includes(c.trang_thai)).length
  const dong = ngay
    ? caNgay.filter((c) => !trangThai || c.trang_thai === trangThai)
    : (ds?.du_lieu ?? [])
  const canChuY = caNgay.filter((c) => c.theo_doi?.co.some((x) => CO_CHU_Y.includes(x)))
  const viecKhac =
    ngay === homNay() ? viec.filter((v) => !v.ma || !caNgay.some((c) => c.ma_chuyen === v.ma)) : []
  const soViec = canChuY.length + viecKhac.length
  const soTrang = Math.max(1, Math.ceil((ds?.tong ?? 0) / SO_DONG))
  const soCot = ngay ? 7 : 5

  return (
    <section className="noi-dung">
      <div className="mo-dau">
        <div>
          <h1>
            {!ngay
              ? 'Tất cả chuyến'
              : ngay === homNay()
                ? 'Chuyến hôm nay'
                : `Chuyến ngày ${ngayThang(`${ngay}T00:00`)}`}
          </h1>
          <p className="ngay">
            {ngay
              ? new Date(`${ngay}T00:00`).toLocaleDateString('vi-VN', { dateStyle: 'full' })
              : 'Mọi ngày khởi hành, mới nhất trước'}
          </p>
          {caNgay.length > 0 && (
            <div className="vach" role="img" aria-label={`${caNgay.length} chuyến theo giờ đi`}>
              {caNgay.map((c) => (
                <i
                  key={c.id}
                  className={lopVach(c)}
                  title={`${gio(c.khoi_hanh_du_kien)} · ${c.ma_chuyen} · ${TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}`}
                />
              ))}
            </div>
          )}
          <div className="so-lieu">
            {caNgay.length > 0 && (
              <>
                <div>
                  <b>{caNgay.length}</b>
                  <span>chuyến</span>
                </div>
                <div>
                  <b>{dem('DANG_CHAY')}</b>
                  <span>đang chạy</span>
                </div>
                <div>
                  <b>{dem('LAP', 'DA_CHOT')}</b>
                  <span>chưa xuất phát</span>
                </div>
                <div>
                  <b>{dem('HOAN_THANH', 'DA_QUYET_TOAN')}</b>
                  <span>đã xong</span>
                </div>
              </>
            )}
            <button onClick={() => setMoForm(true)}>
              <Ic ten="cong" />
              Lập chuyến
            </button>
          </div>
        </div>
        {ngay && (
          <aside className="kinh chu-y">
            <h2>Cần chú ý {soViec > 0 && <em>{soViec} việc</em>}</h2>
            {canChuY.map((c) => {
              const co = c.theo_doi!.co.filter((x) => CO_CHU_Y.includes(x))
              const nang = co.some((x) => x !== 'TRE')
              return (
                <Link key={c.id} to={String(c.id)} className={nang ? 'do' : undefined}>
                  <Ic ten={nang ? 'canh-bao' : 'dong-ho'} />
                  <span>
                    <strong>
                      {c.ma_chuyen} ·{' '}
                      {co
                        .map((x) =>
                          x === 'TRE' && (c.theo_doi!.tre_phut ?? 0) > 0
                            ? `Trễ ${phutDoc(c.theo_doi!.tre_phut!)}`
                            : (TEN_CO[x] ?? x),
                        )
                        .join(', ')}
                    </strong>
                    <small>
                      {c.ten_tuyen} ·{' '}
                      {co.includes('CHONG_LICH')
                        ? `trùng ${c.theo_doi!.chong.join(', ')}`
                        : `${c.bien_so}, ${c.ten_tai_xe}`}
                    </small>
                  </span>
                  <Ic ten="phai" />
                </Link>
              )
            })}
            {viecKhac.map((v) => (
              <Link key={v.chinh} to={v.den} className={v.nang ? 'do' : undefined}>
                <Ic ten={v.nang ? 'canh-bao' : 'dong-ho'} />
                <span>
                  <strong>{v.chinh}</strong>
                  <small>{v.phu}</small>
                </span>
                <Ic ten="phai" />
              </Link>
            ))}
            {soViec === 0 && <p>{ds ? 'Không có việc nào cần chú ý.' : 'Đang tải…'}</p>}
          </aside>
        )}
      </div>
      {caNgay.length > 0 && (
        <div className="hai-khoi">
          <LichGio ds={caNgay} ten={TEN_TRANG_THAI} />
          <Suspense
            fallback={<section className="kinh ban-do-ngay ghi-chu">Đang tải bản đồ…</section>}
          >
            <BanDoNgay ds={caNgay} ten={TEN_TRANG_THAI} />
          </Suspense>
        </div>
      )}
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

      <div className="kinh bang-khung">
        <div className="cong-cu">
          <div className="vien-thuoc" role="group" aria-label="Lọc trạng thái">
            {[['', 'Tất cả'], ...Object.entries(TEN_TRANG_THAI)].map(([ma, ten]) => (
              <button
                key={ma}
                aria-pressed={trangThai === ma}
                onClick={() => {
                  setTrangThai(ma)
                  setTrang(1)
                }}
              >
                {ten}
                {ngay && ds && <em>{ma ? dem(ma) : caNgay.length}</em>}
              </button>
            ))}
          </div>
          <div className="loc-ngay">
            <input
              type="search"
              className="o-tim"
              aria-label="Tìm chuyến"
              placeholder="Tìm mã chuyến, biển số, tài xế"
              value={tim}
              onChange={(e) => setTim(e.target.value)}
            />
            <input
              type="date"
              aria-label="Ngày khởi hành"
              value={ngay}
              onChange={(e) => chonNgay(e.target.value)}
            />
            {ngay !== homNay() && (
              <button className="phu" onClick={() => chonNgay(homNay())}>
                Hôm nay
              </button>
            )}
            {ngay && (
              <button className="phu" onClick={() => chonNgay('')}>
                Mọi ngày
              </button>
            )}
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Giờ đi</th>
              <th>Tuyến</th>
              <th>Xe · Tài xế</th>
              {ngay && <th>Điểm dừng</th>}
              {ngay && <th>Độ đầy</th>}
              <th>Trạng thái</th>
              <th>
                <span className="an-chu">Mở chuyến</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {dong.map((c) => {
              const td = c.theo_doi
              const day = td ? Math.round(Number(td.ty_le_lap_day) * 100) : 0
              const denKhacNgay = ngayThang(c.ket_thuc_du_kien) !== ngayThang(c.khoi_hanh_du_kien)
              return (
                <tr
                  key={c.id}
                  className={c.trang_thai === 'HUY' ? 'hang mo' : 'hang'}
                  onClick={() => dieuHuong(String(c.id))}
                >
                  <td className="gio">
                    <b>{gio(c.khoi_hanh_du_kien)}</b>
                    <small className={td?.co.includes('TRE') ? 'tre' : undefined}>
                      {!ngay && `${ngayThang(c.khoi_hanh_du_kien)} `}→ {gio(c.ket_thuc_du_kien)}
                      {denKhacNgay && ` (${ngayThang(c.ket_thuc_du_kien)})`}
                    </small>
                  </td>
                  <td>
                    <div className="tuyen">{c.ten_tuyen}</div>
                    <span className="ma">
                      <Link to={String(c.id)} onClick={(e) => e.stopPropagation()}>
                        {c.ma_chuyen}
                      </Link>{' '}
                      · {c.ma_tuyen}
                    </span>
                  </td>
                  <td>
                    <span className="bien">{c.bien_so}</span>
                    <small>{c.ten_tai_xe}</small>
                  </td>
                  {ngay && (
                    <td>
                      {td && (
                        <div className="tien-do">
                          <div className="doan">
                            {td.diem
                              ? td.diem.map((d, i) => <i key={i} className={DOAN[d]} />)
                              : Array.from({ length: td.tong }, (_, i) => (
                                  <i key={i} className={i < td.xong ? 'x' : undefined} />
                                ))}
                          </div>
                          <small>
                            {td.xong} / {td.tong} điểm
                            {(td.diem?.filter((d) => d === 'THAT_BAI').length ?? 0) > 0 && (
                              <b> · {td.diem!.filter((d) => d === 'THAT_BAI').length} thất bại</b>
                            )}
                          </small>
                        </div>
                      )}
                    </td>
                  )}
                  {ngay && (
                    <td>
                      {td && (
                        <div className={day > 95 ? 'day cao' : 'day'}>
                          <span>
                            <i style={{ width: `${Math.min(day, 100)}%` }} />
                          </span>
                          {day}%
                        </div>
                      )}
                    </td>
                  )}
                  <td>
                    <div className="tt">
                      <Nhan loai={c.trang_thai}>
                        {TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}
                      </Nhan>
                      {td?.co.map((x) => (
                        <Nhan
                          key={x}
                          loai={x}
                          title={x === 'CHONG_LICH' ? td.chong.join(', ') : undefined}
                        >
                          {x === 'TRE' && (td.tre_phut ?? 0) > 0
                            ? `Trễ ${phutDoc(td.tre_phut!)}`
                            : (TEN_CO[x] ?? x)}
                        </Nhan>
                      ))}
                    </div>
                  </td>
                  <td className="mui">
                    <Ic ten="phai" />
                  </td>
                </tr>
              )
            })}
            {dong.length === 0 && (
              <tr>
                <td colSpan={soCot} className="trong">
                  {!ds
                    ? 'Đang tải…'
                    : ngay && !trangThai && !loiTai
                      ? 'Chưa có chuyến nào khởi hành ngày này. Bấm “Mọi ngày” để xem các ngày khác.'
                      : 'Chưa có chuyến nào phù hợp'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {ngay ? (
        (ds?.tong ?? 0) > caNgay.length && (
          <p className="ghi-chu">
            Đang hiện {caNgay.length} / {ds!.tong} chuyến của ngày này.
          </p>
        )
      ) : (
        <div className="phan-trang">
          <button className="phu" disabled={trang <= 1} onClick={() => setTrang(trang - 1)}>
            Trước
          </button>
          <span>
            Trang {trang}/{soTrang} · {ds?.tong ?? 0} chuyến
          </span>
          <button className="phu" disabled={trang >= soTrang} onClick={() => setTrang(trang + 1)}>
            Sau
          </button>
        </div>
      )}

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
