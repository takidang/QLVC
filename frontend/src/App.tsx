import { useEffect, useState, type ReactNode } from 'react'
import {
  BrowserRouter,
  Navigate,
  NavLink,
  Outlet,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom'
import { dangXuat, toi, type NguoiDung, type VaiTro } from './api/auth'
import { Ic } from './nhan'
import { KhungThongBao } from './thongBao'
import ChuongThongBao from './ChuongThongBao'
import MenuTaiKhoan from './MenuTaiKhoan'
import TimChung from './TimChung'
import DangNhap from './pages/DangNhap'
import BangGiaDanhSach from './pages/quan-ly/BangGiaDanhSach'
import CauHinh from './pages/quan-ly/CauHinh'
import NguoiDungDanhSach from './pages/quan-ly/NguoiDungDanhSach'
import ChuyenChiTiet from './pages/dieu-phoi/ChuyenChiTiet'
import ChuyenDanhSach from './pages/dieu-phoi/ChuyenDanhSach'
import DonDanhSach from './pages/dieu-phoi/DonDanhSach'
import KhachHangDanhSach from './pages/dieu-phoi/KhachHangDanhSach'
import NutDanhSach from './pages/dieu-phoi/NutDanhSach'
import PhieuDon from './pages/dieu-phoi/PhieuDon'
import TuyenDanhSach from './pages/dieu-phoi/TuyenDanhSach'
import TaiXeDanhSach from './pages/dieu-phoi/TaiXeDanhSach'
import XeDanhSach from './pages/dieu-phoi/XeDanhSach'
import ChiPhiCoDinh from './pages/ke-toan/ChiPhiCoDinh'
import CongNo from './pages/ke-toan/CongNo'
import QuyetToan from './pages/ke-toan/QuyetToan'
import TamUng from './pages/ke-toan/TamUng'
import ChuyenCuaToi from './pages/tai-xe/ChuyenCuaToi'
import ChuyenCuaToiChiTiet from './pages/tai-xe/ChuyenCuaToiChiTiet'
import TongQuan from './pages/TongQuan'
import TraCuu from './pages/TraCuu'

const TRANG_CHU: Record<VaiTro, string> = {
  QUAN_LY: '/quan-ly',
  DIEU_PHOI: '/dieu-phoi',
  TAI_XE: '/tai-xe',
  KE_TOAN: '/ke-toan',
}
const TEN_VAI_TRO: Record<VaiTro, string> = {
  QUAN_LY: 'Quản lý',
  DIEU_PHOI: 'Điều phối viên',
  TAI_XE: 'Tài xế',
  KE_TOAN: 'Kế toán',
}

// Trang con của từng vai trò. Thêm UC mới: thêm một dòng ở đây (docs/mau-use-case.md).
// `an`: không hiện trên menu; `nhom`: gộp vào mục xổ xuống "Danh mục" cho thanh menu gọn
const TRANG_CON: Partial<
  Record<
    VaiTro,
    { duong_dan: string; ten: string; trang: ReactNode; an?: boolean; nhom?: boolean }[]
  >
> = {
  DIEU_PHOI: [
    { duong_dan: 'chuyen', ten: 'Chuyến', trang: <ChuyenDanhSach /> },
    { duong_dan: 'chuyen/:id', ten: 'Chi tiết chuyến', trang: <ChuyenChiTiet />, an: true },
    { duong_dan: 'don', ten: 'Đơn hàng', trang: <DonDanhSach /> },
    { duong_dan: 'don/:id/phieu', ten: 'Phiếu đơn', trang: <PhieuDon />, an: true },
    { duong_dan: 'xe', ten: 'Xe', trang: <XeDanhSach /> },
    { duong_dan: 'tai-xe', ten: 'Tài xế', trang: <TaiXeDanhSach /> },
    { duong_dan: 'khach-hang', ten: 'Khách hàng', trang: <KhachHangDanhSach /> },
    { duong_dan: 'nut', ten: 'Nút', trang: <NutDanhSach /> },
    { duong_dan: 'tuyen', ten: 'Tuyến', trang: <TuyenDanhSach /> },
  ],
  KE_TOAN: [
    { duong_dan: 'tong-quan', ten: 'Tổng quan', trang: <TongQuan ketToan /> },
    { duong_dan: 'chi-phi-xe', ten: 'Chi phí cố định xe', trang: <ChiPhiCoDinh /> },
    { duong_dan: 'cong-no', ten: 'Công nợ', trang: <CongNo /> },
    { duong_dan: 'quyet-toan', ten: 'Quyết toán', trang: <QuyetToan /> },
    { duong_dan: 'tam-ung', ten: 'Tạm ứng', trang: <TamUng /> },
  ],
  QUAN_LY: [
    { duong_dan: 'tong-quan', ten: 'Tổng quan', trang: <TongQuan /> },
    { duong_dan: 'nguoi-dung', ten: 'Người dùng', trang: <NguoiDungDanhSach />, nhom: true },
    { duong_dan: 'bang-gia', ten: 'Bảng giá', trang: <BangGiaDanhSach />, nhom: true },
    { duong_dan: 'cau-hinh', ten: 'Cấu hình', trang: <CauHinh />, nhom: true },
    // Quản lý chỉ xem tiền (nghiep-vu.md mục 8): ẩn nút ghi; quyền thật do máy chủ kiểm
    { duong_dan: 'cong-no', ten: 'Công nợ', trang: <CongNo chiXem /> },
    { duong_dan: 'quyet-toan', ten: 'Quyết toán', trang: <QuyetToan chiXem /> },
  ],
  TAI_XE: [
    { duong_dan: 'chuyen', ten: 'Chuyến của tôi', trang: <ChuyenCuaToi /> },
    { duong_dan: 'chuyen/:id', ten: 'Lịch trình chuyến', trang: <ChuyenCuaToiChiTiet />, an: true },
  ],
}

// Vào trang của vai trò thì mở thẳng trang con này thay trang chào
// (tài xế vào thẳng chuyến của mình, UC-17; điều phối vào bảng chuyến hôm nay; quản lý, kế toán vào Tổng quan)
const TRANG_DAU: Partial<Record<VaiTro, string>> = {
  TAI_XE: 'chuyen',
  DIEU_PHOI: 'chuyen',
  QUAN_LY: 'tong-quan',
  KE_TOAN: 'tong-quan',
}

// Chỉ để điều hướng; quyền thật do máy chủ kiểm (BR-57). Quản lý vào được trang Điều phối.
const duocVao = (nd: NguoiDung, trang: VaiTro) =>
  nd.vai_tro === trang || (trang === 'DIEU_PHOI' && nd.vai_tro === 'QUAN_LY')

// Menu của người dùng: trang của vai trò mình, Quản lý thấy thêm trang Điều phối
const DANH_MUC_DP = ['xe', 'tai-xe', 'nut', 'tuyen']
const menu = (nd: NguoiDung) =>
  (Object.keys(TRANG_CHU) as VaiTro[])
    .filter((vt) => duocVao(nd, vt))
    .flatMap((vt) =>
      (TRANG_CON[vt] ?? [])
        .filter((t) => !t.an)
        .map((t) => ({
          ...t,
          den: `${TRANG_CHU[vt]}/${t.duong_dan}`,
          // Quản lý có thêm Tổng quan, Công nợ, Quyết toán: danh mục của Điều phối gộp vào "Danh mục"
          // cho thanh đầu một hàng; Điều phối vẫn thấy thẳng (Tài góp ý 12/11)
          nhom: t.nhom || (nd.vai_tro === 'QUAN_LY' && DANH_MUC_DP.includes(t.duong_dan)),
        })),
    )

// Khung trang sau đăng nhập: tên hệ thống, menu viên thuốc (mục phụ gộp vào "Danh mục"), người dùng
function KhungTrang({
  nd,
  loiThoat,
  onThoat,
}: {
  nd: NguoiDung
  loiThoat: string
  onThoat: () => void
}) {
  const { pathname } = useLocation()
  const muc = menu(nd)
  const danhMuc = muc.filter((m) => m.nhom)
  return (
    <main className="trang">
      <header>
        <span className="thuong-hieu">Quản lý vận tải</span>
        {/* Chỉ một mục (tài xế) thì không cần menu: tiêu đề trang đã nói đủ */}
        <nav className="vien-thuoc" aria-label="Chức năng" hidden={muc.length < 2}>
          {muc
            .filter((m) => !m.nhom)
            .map((m) => (
              <NavLink key={m.den} to={m.den}>
                {m.ten}
              </NavLink>
            ))}
          {danhMuc.length > 0 && (
            <details
              className={danhMuc.some((m) => pathname.startsWith(m.den)) ? 'on' : undefined}
              // Bấm ra ngoài hoặc Tab ra khỏi thì đóng
              onBlur={(e) => {
                if (!e.currentTarget.contains(e.relatedTarget)) e.currentTarget.open = false
              }}
            >
              <summary>
                Danh mục
                <Ic ten="xuong" />
              </summary>
              <div>
                {danhMuc.map((m) => (
                  <NavLink
                    key={m.den}
                    to={m.den}
                    onClick={(e) => e.currentTarget.closest('details')!.removeAttribute('open')}
                  >
                    {m.ten}
                  </NavLink>
                ))}
              </div>
            </details>
          )}
        </nav>
        <div className="ben-phai">
          <TimChung vaiTro={nd.vai_tro} />
          <span className="ten">
            {nd.ho_ten} · {TEN_VAI_TRO[nd.vai_tro]}
          </span>
          <ChuongThongBao nguoiDungId={nd.id} vaiTro={nd.vai_tro} />
          <MenuTaiKhoan nd={nd} tenVaiTro={TEN_VAI_TRO[nd.vai_tro]} onThoat={onThoat} />
        </div>
      </header>
      {loiThoat && (
        <p role="alert" className="loi trang-loi">
          {loiThoat}
        </p>
      )}
      <Outlet />
    </main>
  )
}

export default function App() {
  const [nd, setNd] = useState<NguoiDung | null | undefined>(undefined) // undefined = đang kiểm phiên
  const [loiThoat, setLoiThoat] = useState('')

  useEffect(() => {
    toi()
      .then(setNd)
      .catch(() => setNd(null))
  }, [])

  if (nd === undefined) return <p className="dang-tai">Đang tải…</p>

  async function thoat() {
    setLoiThoat('')
    try {
      await dangXuat()
      setNd(null)
    } catch {
      // Cookie chưa bị xóa: báo rõ để người dùng máy chung không tưởng đã thoát
      setLoiThoat('Không đăng xuất được, kiểm tra mạng rồi thử lại')
    }
  }

  return (
    <BrowserRouter>
      <KhungThongBao />
      <Routes>
        {/* UC-28: trang công khai cho khách, không cần đăng nhập */}
        <Route path="/tra-cuu" element={<TraCuu />} />
        <Route
          path="/dang-nhap"
          element={
            nd ? <Navigate to={TRANG_CHU[nd.vai_tro]} replace /> : <DangNhap onXong={setNd} />
          }
        />
        {(Object.keys(TRANG_CHU) as VaiTro[]).map((vt) => (
          <Route
            key={vt}
            path={TRANG_CHU[vt]}
            element={
              !nd ? (
                <Navigate to="/dang-nhap" replace />
              ) : !duocVao(nd, vt) ? (
                <Navigate to={TRANG_CHU[nd.vai_tro]} replace />
              ) : (
                <KhungTrang nd={nd} loiThoat={loiThoat} onThoat={thoat} />
              )
            }
          >
            <Route
              index
              element={
                TRANG_DAU[vt] ? (
                  <Navigate to={TRANG_DAU[vt]} replace />
                ) : (
                  <section className="noi-dung">
                    <h1>Trang {TEN_VAI_TRO[vt]}</h1>
                    <p className="ghi-chu">Chọn chức năng trên thanh menu.</p>
                  </section>
                )
              }
            />
            {(TRANG_CON[vt] ?? []).map((t) => (
              <Route key={t.duong_dan} path={t.duong_dan} element={t.trang} />
            ))}
          </Route>
        ))}
        <Route
          path="*"
          element={<Navigate to={nd ? TRANG_CHU[nd.vai_tro] : '/dang-nhap'} replace />}
        />
      </Routes>
    </BrowserRouter>
  )
}
