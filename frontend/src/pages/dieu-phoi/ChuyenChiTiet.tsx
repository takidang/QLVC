import { lazy, Suspense, useEffect, useState, type ReactNode } from 'react'
import { Link, useLocation, useNavigate, useOutletContext, useParams } from 'react-router-dom'
import type { NguoiDung } from '../../api/auth'
import {
  chiTietChuyen,
  danhSachChuyen,
  chotChuyen,
  donPhuHop,
  duDoanTre,
  ghepDon,
  goDon,
  huyChuyen,
  moChotChuyen,
  phanCong,
  TEN_CO,
  taiXeKhaDungChuyen,
  xeKhaDungChuyen,
  type Chuyen as ChuyenNgan,
  type ChuyenChiTiet as Chuyen,
  type DuDoanTre,
  type MucNguyCoTre,
  type NguonDuDoanTre,
  type TaiXeKhaDung,
  type ViPhamGhep,
  type XacNhanChot,
  type XeKhaDung,
  type YeuToDuDoanTre,
} from '../../api/chuyen'
import { ChonKhaDung, type KhaDung } from './ChuyenDanhSach'
import { TEN_TRANG_THAI_DON, type Don } from '../../api/don'
import { kemMaBr, LoiApi } from '../../api/goi'
import { BangDinhNiemPhongPixel, DangTaiPixel } from '../../HieuUngPixel'
import { dangHieuUngPixel, phongCachDaLuu } from '../../nen'
import { Nhan } from '../../nhan'
import { NoteCanhBao } from '../../NoteCanhBao'
import { CanhBaoTheoDoi, DongThoiGian, KhoiSuCo, KhoiTien } from './TheoDoiChuyen'
import XepHang from './XepHang'
import KhoiXe from './KhoiXe'
import { xemTaiXe, type TaiXe } from '../../api/taiXe'
import { xemTuyen } from '../../api/tuyen'
import { xemXe, type Xe } from '../../api/xe'

// Bản đồ (leaflet + css) tải riêng khi mở chi tiết chuyến, không kéo theo vào màn đăng nhập
const BanDoChuyen = lazy(() => import('./BanDoChuyen'))

const TEN_KET_QUA: Record<string, string> = {
  LAY: 'đã lấy',
  KHONG_LAY: 'không lấy được',
  GIAO: 'đã giao',
  GIAO_THAT_BAI: 'giao không được',
}
// Nhãn đơn dùng hình của nhãn chuyến (giống màn Đơn hàng)
const NHAN_DON: Record<string, string> = {
  CHO_GHEP: 'LAP',
  DA_GHEP: 'DA_CHOT',
  DA_LAY: 'DANG_CHAY',
  DA_GIAO: 'HOAN_THANH',
  THAT_BAI: 'THAT_BAI',
  TRA_HANG: 'HUY',
  HUY: 'HUY',
}

const dong = (n: number) => n.toLocaleString('vi-VN')
const so = (s: string) => Number(s).toLocaleString('vi-VN')
const gio = (iso: string) =>
  new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
const lucVN = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
const TEN_TRANG_THAI: Record<string, string> = {
  LAP: 'Đang lập',
  DA_CHOT: 'Đã chốt',
  DANG_CHAY: 'Đang chạy',
  HOAN_THANH: 'Hoàn thành',
  DA_QUYET_TOAN: 'Đã quyết toán',
  HUY: 'Hủy',
}
// Trễ so ETA kế hoạch: âm là đến sớm
const phut = (n: number) => (n >= 60 ? `${Math.floor(n / 60)} giờ ${n % 60}′` : `${n}′`)
const tre = (n: number) => (n > 0 ? `Trễ ${phut(n)}` : n < 0 ? `Sớm ${phut(-n)}` : 'Đúng giờ')
const XAC_NHAN: Record<string, keyof XacNhanChot> = {
  'BR-23': 'xac_nhan_chay_rong',
  'BR-52': 'xac_nhan_lai_am',
}
const TEN_MUC_TRE: Record<MucNguyCoTre, string> = {
  THAP: 'Thấp',
  TRUNG_BINH: 'Trung bình',
  CAO: 'Cao',
}
const MUC_TRE_DS: { ma: MucNguyCoTre; ten: string; lop: string }[] = [
  { ma: 'THAP', ten: 'Thấp', lop: 'nc-thap' },
  { ma: 'TRUNG_BINH', ten: 'Trung bình', lop: 'nc-tb' },
  { ma: 'CAO', ten: 'Cao', lop: 'nc-cao' },
]
const TEN_THU = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật']
function giaTriYeuTo(y: YeuToDuDoanTre): string {
  if (y.gia_tri == null || Number.isNaN(y.gia_tri)) return ''
  switch (y.ma) {
    case 'km':
      return `${y.gia_tri.toLocaleString('vi-VN', { maximumFractionDigits: 1 })} km`
    case 'thoi_gian_gio':
      return `${y.gia_tri.toLocaleString('vi-VN', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} giờ`
    case 'gio_khoi_hanh':
      return `${Math.round(y.gia_tri)} giờ`
    case 'thu_trong_tuan':
      return TEN_THU[Math.round(y.gia_tri)] ?? String(y.gia_tri)
    default:
      return y.gia_tri.toLocaleString('vi-VN')
  }
}
function tomTatNguon(nguon?: NguonDuDoanTre | null): string {
  if (!nguon) return ''
  const phan: string[] = []
  if (nguon.dataset) phan.push(`Nguồn: ${nguon.dataset}`)
  if (nguon.so_mau != null) phan.push(`${nguon.so_mau.toLocaleString('vi-VN')} mẫu`)
  if (nguon.auc != null) phan.push(`AUC ${nguon.auc.toLocaleString('vi-VN')}`)
  return phan.join(' · ')
}

// Chi tiết chuyến (giao diện v2, màn 03): đầu trang, số liệu, lịch trình dọc + bản đồ, tiền, dòng thời gian.
// Chi tiết chuyến, thẻ Hàng (UC-13): tải, lịch trình, ghép và gỡ đơn; chốt / mở chốt (UC-15); hủy (UC-16)
export default function ChuyenChiTiet() {
  const id = Number(useParams().id)
  const [c, setC] = useState<Chuyen | null>(null)
  const [phuHop, setPhuHop] = useState<Don[]>([])
  const [chonGhep, setChonGhep] = useState<number[]>([])
  const [chonGo, setChonGo] = useState<number[]>([])
  const [loi, setLoi] = useState('')
  const [lyDoHuy, setLyDoHuy] = useState<string | null>(null) // null: chưa mở ô nhập lý do
  const [viPham, setViPham] = useState<ViPhamGhep[]>([])
  const [dangGui, setDangGui] = useState(false)
  const [lanTai, setLanTai] = useState(0)
  // Hiệu ứng Pixel: cờ hiện băng dính niêm phong kéo ngang thẻ chuyến sau khi chốt thành công (≤ 1,4 s)
  const [niemPhong, setNiemPhong] = useState(0)

  // Sang chuyến khác (bấm cột trái) thì trang không dựng lại: giữ danh sách bên trái, chỉ bỏ trạng thái của chuyến cũ
  const [idTruoc, setIdTruoc] = useState(id)
  if (idTruoc !== id) {
    setIdTruoc(id)
    setPhuHop([])
    setChonGhep([])
    setChonGo([])
    setLoi('')
    setLyDoHuy(null)
    setViPham([])
  }

  useEffect(() => {
    if (niemPhong === 0) return
    const t = window.setTimeout(() => setNiemPhong(0), 1400)
    return () => window.clearTimeout(t)
  }, [niemPhong])
  const dieuHuong = useNavigate()
  const { pathname } = useLocation()
  const nd = useOutletContext<NguoiDung | undefined>()
  const [cungNgay, setCungNgay] = useState<ChuyenNgan[]>([])
  const [xe, setXe] = useState<Xe | null>(null)
  const [taiXe, setTaiXe] = useState<TaiXe | null>(null)
  const [km, setKm] = useState<number | null>(null)
  const [duDoan, setDuDoan] = useState<{ id: number; duLieu: DuDoanTre } | null>(null)

  useEffect(() => {
    let bo = false
    chiTietChuyen(id)
      .then((r) => {
        if (bo) return
        setC(r)
        if (r.trang_thai === 'LAP')
          donPhuHop(id)
            .then((d) => !bo && setPhuHop(d))
            .catch(() => !bo && setLoi('Không tải được danh sách đơn chờ ghép'))
      })
      .catch((e) => !bo && setLoi(e instanceof LoiApi ? e.message : 'Không tải được chuyến'))
    return () => {
      bo = true
    }
  }, [id, lanTai])

  // Dữ liệu phụ cho bố cục: các chuyến cùng ngày (cột trái), xe, tài xế, km tuyến. Hỏng thì bỏ qua phần đó
  const ngayChuyen = c ? new Date(c.khoi_hanh_du_kien).toLocaleDateString('sv-SE') : ''
  const xeId = c?.xe_id
  const taiXeId = c?.tai_xe_id
  const tuyenId = c?.tuyen_id
  useEffect(() => {
    if (!ngayChuyen) return
    danhSachChuyen({ ngay: ngayChuyen, so_dong: 100 })
      .then((r) =>
        setCungNgay(
          [...r.du_lieu].sort(
            (a, b) => Date.parse(a.khoi_hanh_du_kien) - Date.parse(b.khoi_hanh_du_kien),
          ),
        ),
      )
      .catch(() => setCungNgay([]))
  }, [ngayChuyen, lanTai])
  useEffect(() => {
    if (xeId)
      xemXe(xeId)
        .then(setXe)
        .catch(() => setXe(null))
  }, [xeId])
  useEffect(() => {
    if (taiXeId)
      xemTaiXe(taiXeId)
        .then(setTaiXe)
        .catch(() => setTaiXe(null))
  }, [taiXeId])
  useEffect(() => {
    if (tuyenId)
      xemTuyen(tuyenId)
        .then((t) => setKm(t.tong_km))
        .catch(() => setKm(null))
  }, [tuyenId])

  // UC-30: chỉ gọi dự đoán nguy cơ trễ khi Điều phối / Quản lý xem chuyến chưa hủy; lỗi hoặc không có gợi ý thì im lặng (KT-08)
  const duocXemDuDoan = nd?.vai_tro === 'DIEU_PHOI' || nd?.vai_tro === 'QUAN_LY'
  const chuyenId = c?.id
  const biHuy = c?.trang_thai === 'HUY'
  useEffect(() => {
    if (!duocXemDuDoan || !chuyenId || biHuy) return
    let bo = false
    duDoanTre(chuyenId)
      .then(
        (r) =>
          !bo &&
          setDuDoan(
            r.co_du_doan && r.xac_suat != null && r.muc ? { id: chuyenId, duLieu: r } : null,
          ),
      )
      .catch(() => !bo && setDuDoan(null))
    return () => {
      bo = true
    }
  }, [duocXemDuDoan, chuyenId, biHuy])

  // Chốt: thiếu xác nhận chạy rỗng (BR-23) hoặc lãi âm (BR-52) thì hỏi, đồng ý thì gửi lại kèm cờ
  async function chot(): Promise<Chuyen> {
    const xn: XacNhanChot = {}
    for (;;) {
      try {
        return await chotChuyen(id, xn)
      } catch (e) {
        const co = e instanceof LoiApi && e.status === 422 && XAC_NHAN[e.ma]
        if (!co || !window.confirm(`${e instanceof Error ? e.message : ''}. Vẫn chốt chuyến?`))
          throw e
        xn[co] = true
      }
    }
  }

  // `ids`: ghép / gỡ một đơn từ khối Xếp hàng lên xe; bỏ trống thì dùng các ô đã tích trong bảng
  async function lam(viec: 'ghep' | 'go' | 'chot' | 'mo-chot' | 'huy', ids?: number[]) {
    setLoi('')
    setViPham([])
    setDangGui(true)
    try {
      const goi = {
        ghep: () => ghepDon(id, ids ?? chonGhep),
        go: () => goDon(id, ids ?? chonGo),
        chot,
        'mo-chot': () => moChotChuyen(id),
        huy: () => huyChuyen(id, lyDoHuy ?? ''),
      }
      const moi = await goi[viec]()
      setC(moi)
      // Hiệu ứng Pixel: băng dính niêm phong kéo ngang thẻ chuyến sau khi API chốt chuyến thành công
      if (viec === 'chot' && dangHieuUngPixel()) setNiemPhong((n) => n + 1)
      setLyDoHuy(null)
      setChonGhep([])
      setChonGo([])
      setLanTai((n) => n + 1) // tải lại đơn chờ ghép ở effect; lỗi tải lại không bị báo nhầm là lưu hỏng
    } catch (e) {
      // Người dùng bấm Hủy ở hộp xác nhận: không báo lỗi
      if (e instanceof LoiApi && e.status === 422 && XAC_NHAN[e.ma]) return
      if (e instanceof LoiApi && e.status === 422 && e.chiTiet.length) {
        setLoi(e.message)
        setViPham(e.chiTiet as ViPhamGhep[])
      } else {
        setLoi(e instanceof LoiApi ? e.message : 'Không lưu được, vui lòng thử lại')
        // 409: đơn vừa bị người khác ghép, hoặc chuyến đã đổi trạng thái → tải lại
        if (e instanceof LoiApi && e.status === 409) {
          setChonGhep([])
          setChonGo([])
          setLanTai((n) => n + 1)
        }
      }
    } finally {
      setDangGui(false)
    }
  }

  if (!c)
    return (
      <section className="noi-dung">
        <Link to="..">← Danh sách chuyến</Link>
        {loi ? (
          <p role="alert" className="loi">
            {loi}
          </p>
        ) : phongCachDaLuu() === 'pixel' ? (
          /* Hiệu ứng Pixel: màn tải kiểu Pixel thay chữ Đang tải… */
          <DangTaiPixel kieu="trang" />
        ) : (
          <p className="ghi-chu">Đang tải…</p>
        )}
      </section>
    )

  const dangLap = c.trang_thai === 'LAP'
  const maDon = new Map([...c.don, ...phuHop].map((d) => [d.id, d.ma_don]))
  const doi = (ds: number[], dat: (v: number[]) => void, x: number) =>
    dat(ds.includes(x) ? ds.filter((y) => y !== x) : [...ds, x])
  const daChay = !!c.tien && c.trang_thai !== 'LAP' && c.trang_thai !== 'DA_CHOT'
  // Điểm đang tới: điểm đầu tiên chưa có kết quả khi chuyến đang chạy
  const dangToi =
    c.trang_thai === 'DANG_CHAY' ? c.lich_trinh.find((d) => !d.ket_qua)?.thu_tu : undefined

  // Cột trái: các chuyến cùng ngày; bấm để chuyển chuyến, không phải quay lại danh sách
  const sangChuyen = (x: number) => dieuHuong(pathname.replace(/\/\d+$/, `/${x}`))
  const viTri = cungNgay.find((x) => x.id === c.id)?.theo_doi?.vi_tri

  return (
    <section className="noi-dung chi-tiet ct2">
      <Link to=".." className="ct-ve">
        ← Danh sách chuyến
      </Link>
      <div className="ct2-luoi">
        <aside className="kinh ct2-ds" aria-label="Chuyến cùng ngày">
          <h2>
            Chuyến ngày {lucVN(c.khoi_hanh_du_kien).split(' ')[1] ?? ''} <em>{cungNgay.length}</em>
          </h2>
          <ul>
            {cungNgay.map((x) => {
              const [di, den] = x.ten_tuyen.split(' – ')
              return (
                <li key={x.id}>
                  <button
                    type="button"
                    aria-current={x.id === c.id ? 'page' : undefined}
                    onClick={() => x.id !== c.id && sangChuyen(x.id)}
                  >
                    <span className="ct2-ds-dau">
                      <strong>{x.ma_chuyen}</strong>
                      <Nhan loai={x.trang_thai}>
                        {TEN_TRANG_THAI[x.trang_thai] ?? x.trang_thai}
                      </Nhan>
                    </span>
                    <span className="ct2-ds-tuyen">
                      <span>{di}</span>
                      <span>{den ?? ''}</span>
                    </span>
                    {x.theo_doi?.diem && x.theo_doi.diem.length > 0 && (
                      <span className="doan" aria-hidden="true">
                        {x.theo_doi.diem.map((d, k) => (
                          <i
                            key={k}
                            className={
                              d === 'XONG'
                                ? 'x'
                                : d === 'THAT_BAI'
                                  ? 'f'
                                  : d === 'DANG_TOI'
                                    ? 'c'
                                    : undefined
                            }
                          />
                        ))}
                      </span>
                    )}
                    <small>
                      {gio(x.khoi_hanh_du_kien)} → {gio(x.ket_thuc_du_kien)} · {x.bien_so}
                    </small>
                  </button>
                </li>
              )
            })}
          </ul>
        </aside>

        <div className="ct2-chinh">
          {/* Đầu chi tiết gọn một dòng: tên, mã, nhãn, số chính; hành động bên phải */}
          {/* Khối đầu có viền như ảnh mẫu 01: tên, mã, nhãn, số liệu, nút; cảnh báo và form hủy nằm trong khối */}
          <section className="kinh ct2-dau-khung">
            {/* Hiệu ứng Pixel: băng dính niêm phong kéo ngang thẻ chuyến sau khi chốt thành công */}
            {niemPhong > 0 && dangHieuUngPixel() && <BangDinhNiemPhongPixel key={niemPhong} />}
            <div className="ct-dau ct2-dau">
              <div>
                <h1>{c.ten_tuyen}</h1>
                <div className="ct-nhan">
                  <span className="ma">
                    {c.ma_chuyen} · {c.ma_tuyen}
                  </span>
                  <Nhan loai={c.trang_thai}>{TEN_TRANG_THAI[c.trang_thai] ?? c.trang_thai}</Nhan>
                  {c.co?.map((x) => (
                    <Nhan
                      key={x}
                      loai={x}
                      title={x === 'CHONG_LICH' ? c.chong?.join(', ') : undefined}
                    >
                      {TEN_CO[x] ?? x}
                    </Nhan>
                  ))}
                </div>
                <ul className="ct2-so">
                  <li>
                    {so(c.tai_trong.da_dung_kg)} / {dong(c.tai_trong.toi_da_kg)} kg
                  </li>
                  <li>{c.lich_trinh.length} điểm dừng</li>
                  {km !== null && <li>{dong(km)} km</li>}
                  <li>Khởi hành {lucVN(c.khoi_hanh_du_kien)}</li>
                  <li className={c.ket_thuc_dang_chay ? 'ct-tre' : undefined}>
                    {c.ket_thuc_dang_chay ? 'Dự kiến xong (đang trễ) ' : 'Kết thúc dự kiến '}
                    {lucVN(c.ket_thuc_dang_chay ?? c.ket_thuc_du_kien)}
                  </li>
                  {dangLap && c.canh_bao_lai_am && (
                    <li className="ct-tre">Lãi dự kiến âm, phải xác nhận khi chốt</li>
                  )}
                  {c.chay_rong && <li>Chạy rỗng (đã xác nhận)</li>}
                </ul>
              </div>
              <div className="ct-hanh-dong">
                {dangLap && lyDoHuy === null && (
                  <button disabled={dangGui} onClick={() => lam('chot')}>
                    Chốt chuyến
                  </button>
                )}
                {c.trang_thai === 'DA_CHOT' && lyDoHuy === null && (
                  <button className="phu" disabled={dangGui} onClick={() => lam('mo-chot')}>
                    Mở chốt
                  </button>
                )}
                {(dangLap || c.trang_thai === 'DA_CHOT') && lyDoHuy === null && (
                  <button className="phu" disabled={dangGui} onClick={() => setLyDoHuy('')}>
                    Hủy chuyến
                  </button>
                )}
              </div>
            </div>
            {duocXemDuDoan && !biHuy && duDoan?.id === c.id && (
              <KhoiDuDoanTre key={c.id} d={duDoan.duLieu} />
            )}
            {lyDoHuy !== null && (
              <form
                className="thanh-cong-cu canh-bao"
                onSubmit={(e) => {
                  e.preventDefault()
                  lam('huy')
                }}
              >
                <label>
                  Lý do hủy
                  <input
                    required
                    autoFocus
                    maxLength={300}
                    value={lyDoHuy}
                    onChange={(e) => setLyDoHuy(e.target.value)}
                  />
                </label>
                <button disabled={dangGui || !lyDoHuy.trim()}>Xác nhận hủy</button>
                <button
                  type="button"
                  className="phu"
                  disabled={dangGui}
                  onClick={() => setLyDoHuy(null)}
                >
                  Thôi
                </button>
              </form>
            )}
            <CanhBaoTheoDoi c={c} onDoi={setC} />
            {loi && (
              <NoteCanhBao
                tieuDe={viPham.length > 0 ? 'Vi phạm quy tắc' : 'Cảnh báo chuyến'}
                soMuc={viPham.length > 0 ? viPham.length : undefined}
              >
                <div role="alert" className="canh-bao">
                  <strong className="loi">{loi}</strong>
                  {viPham.length > 0 && (
                    <table>
                      <thead>
                        <tr>
                          <th>Đơn</th>
                          <th>Quy tắc</th>
                          <th>Nội dung</th>
                        </tr>
                      </thead>
                      <tbody>
                        {viPham.map((v, i) => (
                          <tr key={i}>
                            <td className="bien-so">
                              {v.don_id ? (maDon.get(v.don_id) ?? v.don_id) : 'Cả chuyến'}
                            </td>
                            <td>{v.ma}</td>
                            <td>{kemMaBr(v.thong_diep, v.ma)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </NoteCanhBao>
            )}
            {dangLap && (
              <DoiXeTaiXe
                c={c}
                onLuu={(r) => {
                  setC(r)
                  setLanTai((n) => n + 1)
                }}
              />
            )}
          </section>

          {/* Hàng 1: bản đồ lớn và lịch trình dọc */}
          <div className="ct2-hang ct2-hang-ban-do">
            <div className="ct2-ban-do">
              {/* Hiệu ứng Pixel: màn tải kiểu Pixel thay chữ Đang tải bản đồ… */}
              <Suspense
                fallback={
                  phongCachDaLuu() === 'pixel' ? (
                    <DangTaiPixel kieu="trang" nhan="Đang tải bản đồ…" />
                  ) : (
                    <p className="ghi-chu">Đang tải bản đồ…</p>
                  )
                }
              >
                <BanDoChuyen
                  lichTrinh={c.lich_trinh}
                  viTri={c.trang_thai === 'DANG_CHAY' ? viTri : null}
                />
              </Suspense>
            </div>
            {/* Lịch trình dạng dòng thời gian dọc: mỗi điểm dừng một dòng */}
            <section className="kinh ct-khoi">
              <h2>
                Lịch trình
                <em>
                  {c.lich_trinh.filter((d) => d.ket_qua).length} / {c.lich_trinh.length} điểm
                </em>
              </h2>
              {c.lich_trinh.length === 0 ? (
                <p className="ghi-chu">Chưa có đơn – chuyến đang tính như chạy rỗng</p>
              ) : (
                <ol className="lt">
                  {c.lich_trinh.map((d) => {
                    const hong = d.ket_qua === 'KHONG_LAY' || d.ket_qua === 'GIAO_THAT_BAI'
                    const lop = hong
                      ? 'hong'
                      : d.ket_qua === 'BO'
                        ? 'bo'
                        : d.ket_qua
                          ? 'xong'
                          : d.thu_tu === dangToi
                            ? 'toi'
                            : undefined
                    return (
                      <li key={d.thu_tu} className={lop}>
                        <i aria-hidden="true" />
                        <div>
                          <strong>{d.nut}</strong>
                          <small>
                            {d.viec === 'LAY' ? 'Lấy' : 'Giao'} · {d.ma_don}
                            {d.ket_qua === 'BO'
                              ? ' · bỏ (không lấy được)'
                              : d.ket_qua && ` · ${TEN_KET_QUA[d.ket_qua] ?? d.ket_qua}`}
                            {d.thu_tu === dangToi && ' · đang tới'}
                          </small>
                        </div>
                        <div className="lt-gio">
                          <span>{gio(d.eta)}</span>
                          {daChay && d.thuc_te && <small>quét {gio(d.thuc_te)}</small>}
                          {daChay && d.tre_phut != null && (
                            <small className={d.tre_phut > 15 ? 'ct-tre' : undefined}>
                              {tre(d.tre_phut)}
                            </small>
                          )}
                        </div>
                      </li>
                    )
                  })}
                </ol>
              )}
            </section>
          </div>

          <XepHang
            c={c}
            phuHop={phuHop}
            dangLap={dangLap}
            dangGui={dangGui}
            onGhep={(x) => lam('ghep', [x])}
            onGo={(x) => lam('go', [x])}
          />

          {/* Hàng 3: xe & tài xế, tiền */}
          <div className="ct2-hang">
            <KhoiXe xe={xe} taiXe={taiXe} />
            <KhoiTien c={c} />
          </div>
          <div className="ct2-hang">
            <DongThoiGian c={c} />
            <KhoiSuCo c={c} onDoi={() => setLanTai((n) => n + 1)} />
          </div>

          <BangDon
            tieu_de={`${['HOAN_THANH', 'DA_QUYET_TOAN', 'HUY'].includes(c.trang_thai) ? 'Đơn của chuyến' : 'Đơn đang ghép'} (${c.don.length})`}
            ds={c.don}
            hienTrangThai
            chon={dangLap ? chonGo : undefined}
            onChon={(x) => doi(chonGo, setChonGo, x)}
            nut={
              dangLap && (
                <button
                  className="phu"
                  disabled={dangGui || chonGo.length === 0}
                  onClick={() => lam('go')}
                >
                  Gỡ {chonGo.length || ''} đơn đã chọn
                </button>
              )
            }
          />
        </div>
      </div>
    </section>
  )
}

// UC-30: khối gợi ý nguy cơ trễ gần phần thời gian dự kiến; chỉ gợi ý, không đổi ETA hay chặn thao tác
function KhoiDuDoanTre({ d }: { d: DuDoanTre }) {
  const [moGiaiThich, setMoGiaiThich] = useState(false)
  if (!d.co_du_doan || d.xac_suat == null || !d.muc) return null
  // Không hiện %: dữ liệu train có tỷ lệ trễ nền 82%, nên "Thấp · 72%" dễ hiểu lầm (góp ý Kiệt #63)
  const yeuTo = d.yeu_to ?? []
  const nguon = tomTatNguon(d.nguon)
  return (
    <div className="ct-du-doan" title={nguon || undefined}>
      <div className="ct-du-doan-dau">
        <span className="ct-du-doan-tieu-de">Dự đoán trễ (AI)</span>
        <Nhan loai={`NGUY_CO_${d.muc}`}>Nguy cơ trễ: {TEN_MUC_TRE[d.muc]}</Nhan>
        <button
          type="button"
          className="phu ct-du-doan-nut"
          aria-expanded={moGiaiThich}
          onClick={() => setMoGiaiThich((v) => !v)}
        >
          Cách tính
        </button>
      </div>
      <div
        className="ct-du-doan-thang"
        role="img"
        aria-label={`Mức nguy cơ trễ: ${TEN_MUC_TRE[d.muc]}`}
      >
        {MUC_TRE_DS.map((m) => {
          const chon = d.muc === m.ma
          return (
            <div key={m.ma} className={`ct-du-doan-bac${chon ? ` chon ${m.lop}` : ''}`}>
              <span className="ct-du-doan-o" aria-hidden="true" />
              <span className="ct-du-doan-ten">{m.ten}</span>
            </div>
          )
        })}
      </div>
      {yeuTo.length > 0 && (
        <ul className="ct-du-doan-yt" aria-label="Các yếu tố ảnh hưởng">
          {yeuTo.map((y) => {
            const gt = giaTriYeuTo(y)
            return (
              <li key={y.ma || y.ten}>
                {y.ten}
                {gt ? ` ${gt}` : ''} –{' '}
                {y.huong === 'TANG' ? 'làm tăng nguy cơ' : 'làm giảm nguy cơ'}
              </li>
            )
          })}
        </ul>
      )}
      <small className="ct-du-doan-ghi-chu">
        Gợi ý từ mô hình thử nghiệm, không thay đổi ETA
        {nguon && <> · {nguon}</>}
      </small>
      {moGiaiThich && (
        <div className="ct-du-doan-giai-thich">
          <p>
            Mô hình hồi quy logistic học từ{' '}
            {d.nguon?.so_mau != null
              ? `${d.nguon.so_mau.toLocaleString('vi-VN')} chuyến xe tải thật`
              : 'các chuyến xe tải thật'}{' '}
            (dataset Kaggle, Ấn Độ), dùng 4 yếu tố: quãng đường, thời gian dự kiến, giờ khởi hành và
            thứ trong tuần
            {d.nguon?.auc != null && <> (độ chính xác AUC {d.nguon.auc.toLocaleString('vi-VN')})</>}
            .
          </p>
          {/* shortcut: số trung bình ghi cứng theo mo_hinh_tre.json hiện tại; train lại thì sửa câu này */}
          <p>
            "Làm tăng / làm giảm nguy cơ" là so với một chuyến trung bình trong dữ liệu học: khoảng
            249 km, dự kiến 15 giờ, khởi hành khoảng 15 giờ 30, giữa tuần. Ví dụ đường ngắn hơn 249
            km thì ít rủi ro hơn; thời gian dự kiến dài (dư giờ) cũng làm giảm nguy cơ; đi muộn
            trong ngày hoặc đầu tuần làm tăng nguy cơ.
          </p>
          <p>
            Mức nguy cơ theo khả năng trễ: Thấp dưới 75%, Trung bình 75–90%, Cao từ 90%. Dữ liệu học
            có 82% chuyến bị trễ nên phần lớn chuyến ở mức Trung bình.
          </p>
          <p>
            Đây chỉ là gợi ý tham khảo, không đổi giờ dự kiến của chuyến và sẽ học lại khi hệ thống
            có dữ liệu chạy thật.
          </p>
        </div>
      )}
    </div>
  )
}

function BangDon({
  tieu_de,
  ds,
  chon,
  onChon,
  nut,
  hienTrangThai = false,
}: {
  tieu_de: string
  ds: Don[]
  chon?: number[]
  onChon: (id: number) => void
  nut: ReactNode
  hienTrangThai?: boolean
}) {
  const soCot = 7 + (chon ? 1 : 0) + (hienTrangThai ? 1 : 0)
  return (
    <section className="kinh bang-khung ct-don">
      <div className="cong-cu">
        <h2>{tieu_de}</h2>
        {nut}
      </div>
      <table>
        <thead>
          <tr>
            {chon && <th />}
            <th>Mã đơn</th>
            <th>Khách</th>
            <th>Lấy → giao</th>
            <th className="so">Hàng</th>
            <th>Khung lấy</th>
            <th>Hạn giao</th>
            <th className="so">Cước (đ)</th>
            {hienTrangThai && <th>Trạng thái</th>}
          </tr>
        </thead>
        <tbody>
          {ds.map((d) => (
            <tr key={d.id}>
              {chon && (
                <td>
                  <input
                    type="checkbox"
                    aria-label={`Chọn ${d.ma_don}`}
                    checked={chon.includes(d.id)}
                    onChange={() => onChon(d.id)}
                  />
                </td>
              )}
              <td className="bien-so">{d.ma_don}</td>
              <td>{d.ten_khach}</td>
              <td>
                {d.tinh_lay} → {d.tinh_giao}
              </td>
              <td className="so">
                {so(d.kg)} kg, {so(d.m3)} m³
              </td>
              <td>{d.lay_tu && d.lay_den ? `${gio(d.lay_tu)}–${gio(d.lay_den)}` : 'Cả ngày'}</td>
              <td>{lucVN(d.han_giao)}</td>
              <td className="so">{dong(d.cuoc_tinh)}</td>
              {hienTrangThai && (
                <td>
                  <Nhan loai={NHAN_DON[d.trang_thai] ?? 'LAP'}>
                    {TEN_TRANG_THAI_DON[d.trang_thai] ?? d.trang_thai}
                  </Nhan>
                </td>
              )}
            </tr>
          ))}
          {ds.length === 0 && (
            <tr>
              <td colSpan={soCot} className="trong">
                Không có đơn
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  )
}

// UC-12: đổi xe và/hoặc tài xế khi chuyến LAP; cái bị loại hiện kèm lý do (BR-11…19, tải theo đơn đang ghép)
function DoiXeTaiXe({ c, onLuu }: { c: Chuyen; onLuu: (c: Chuyen) => void }) {
  const [mo, setMo] = useState(false)
  const [xeId, setXeId] = useState(String(c.xe_id))
  const [taiXeId, setTaiXeId] = useState(String(c.tai_xe_id))
  const [xe, setXe] = useState<KhaDung<XeKhaDung>>()
  const [taiXe, setTaiXe] = useState<KhaDung<TaiXeKhaDung>>()
  const [loi, setLoi] = useState<string[]>([])
  // Ghép / gỡ đơn khi khung đang mở làm đổi tải cần chở (BR-01): tải lại danh sách khả dụng
  const donGhep = c.don.map((d) => d.id).join(',')

  useEffect(() => {
    if (!mo) return
    let bo = false
    xeKhaDungChuyen(c.id)
      .then((ds) => {
        if (bo) return
        setXe({ khoa: '', ds, loi: '' })
        // xe đang chọn không còn dùng được (vd. vừa ghép thêm đơn, quá tải BR-01): bỏ chọn
        setXeId((v) => (ds.some((x) => String(x.id) === v && x.kha_dung) ? v : ''))
      })
      .catch(
        (e) => !bo && setXe({ khoa: '', ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [mo, c.id, donGhep])
  useEffect(() => {
    if (!mo) return
    let bo = false
    taiXeKhaDungChuyen(c.id, xeId ? Number(xeId) : undefined)
      .then((ds) => {
        if (bo) return
        setTaiXe({ khoa: xeId, ds, loi: '' })
        setTaiXeId((v) => (ds.some((t) => String(t.id) === v && t.kha_dung) ? v : ''))
      })
      .catch(
        (e) =>
          !bo && setTaiXe({ khoa: xeId, ds: [], loi: e instanceof LoiApi ? e.message : 'Lỗi' }),
      )
    return () => {
      bo = true
    }
  }, [mo, c.id, xeId, donGhep])

  async function luu() {
    setLoi([])
    try {
      onLuu(await phanCong(c.id, Number(xeId), Number(taiXeId)))
      setMo(false)
    } catch (e) {
      setLoi(
        e instanceof LoiApi && e.chiTiet.length
          ? (e.chiTiet as { ma: string; thong_diep: string }[]).map((v) =>
              kemMaBr(v.thong_diep, v.ma),
            )
          : [e instanceof LoiApi ? e.message : 'Không lưu được, vui lòng thử lại'],
      )
    }
  }

  if (!mo)
    return (
      <p>
        <button className="phu" onClick={() => setMo(true)}>
          Đổi xe / tài xế
        </button>
      </p>
    )
  return (
    <div className="canh-bao">
      <div className="hai-cot">
        <ChonKhaDung
          nhan="Xe"
          kq={xe}
          gia_tri={xeId}
          onChon={setXeId}
          ten={(x) => `${x.bien_so} (${x.tai_trong_kg.toLocaleString('vi-VN')} kg)`}
        />
        <ChonKhaDung
          nhan="Tài xế"
          kq={taiXe?.khoa === xeId ? taiXe : undefined}
          gia_tri={taiXeId}
          onChon={setTaiXeId}
          ten={(t) => `${t.ho_ten} (hạng ${t.hang_gplx})`}
        />
      </div>
      {loi.length > 0 && (
        <ul role="alert" className="loi">
          {loi.map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      )}
      <div className="nut">
        <button type="button" className="phu" onClick={() => setMo(false)}>
          Hủy
        </button>
        <button onClick={luu} disabled={!xeId || !taiXeId}>
          Lưu xe / tài xế
        </button>
      </div>
    </div>
  )
}
