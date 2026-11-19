import { useEffect, useState, type ReactNode } from 'react'
import { BrowserRouter, Link, Navigate, NavLink, Outlet, Route, Routes } from 'react-router-dom'
import { dangXuat, toi, type NguoiDung, type VaiTro } from './api/auth'
import { Ic, type TenIc } from './nhan'
import { KhungThongBao } from './thongBao'
import ChuongThongBao from './ChuongThongBao'
import MenuTaiKhoan from './MenuTaiKhoan'
import TimChung from './TimChung'
import CaiDat from './pages/CaiDat'
import DangNhap from './pages/DangNhap'
import TaiKhoan from './pages/TaiKhoan'
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
// `an`: không hiện trên menu; `nhom`: tên nhóm trên cột menu (bỏ trống là đứng đầu, không tên nhóm)
const TRANG_CON: Partial<
  Record<
    VaiTro,
    { duong_dan: string; ten: string; trang: ReactNode; an?: boolean; nhom?: string }[]
  >
> = {
  DIEU_PHOI: [
    { duong_dan: 'chuyen', ten: 'Chuyến', trang: <ChuyenDanhSach />, nhom: 'Vận hành' },
    { duong_dan: 'chuyen/:id', ten: 'Chi tiết chuyến', trang: <ChuyenChiTiet />, an: true },
    { duong_dan: 'don', ten: 'Đơn hàng', trang: <DonDanhSach />, nhom: 'Vận hành' },
    { duong_dan: 'don/:id/phieu', ten: 'Phiếu đơn', trang: <PhieuDon />, an: true },
    { duong_dan: 'xe', ten: 'Xe', trang: <XeDanhSach />, nhom: 'Danh mục' },
    { duong_dan: 'tai-xe', ten: 'Tài xế', trang: <TaiXeDanhSach />, nhom: 'Danh mục' },
    { duong_dan: 'khach-hang', ten: 'Khách hàng', trang: <KhachHangDanhSach />, nhom: 'Vận hành' },
    { duong_dan: 'nut', ten: 'Nút', trang: <NutDanhSach />, nhom: 'Danh mục' },
    { duong_dan: 'tuyen', ten: 'Tuyến', trang: <TuyenDanhSach />, nhom: 'Danh mục' },
  ],
  KE_TOAN: [
    { duong_dan: 'tong-quan', ten: 'Tổng quan', trang: <TongQuan ketToan /> },
    {
      duong_dan: 'chi-phi-xe',
      ten: 'Chi phí cố định xe',
      trang: <ChiPhiCoDinh />,
      nhom: 'Tài chính',
    },
    { duong_dan: 'cong-no', ten: 'Công nợ', trang: <CongNo />, nhom: 'Tài chính' },
    { duong_dan: 'quyet-toan', ten: 'Quyết toán', trang: <QuyetToan />, nhom: 'Tài chính' },
    { duong_dan: 'tam-ung', ten: 'Tạm ứng', trang: <TamUng />, nhom: 'Tài chính' },
  ],
  QUAN_LY: [
    { duong_dan: 'tong-quan', ten: 'Tổng quan', trang: <TongQuan /> },
    { duong_dan: 'nguoi-dung', ten: 'Người dùng', trang: <NguoiDungDanhSach />, nhom: 'Quản trị' },
    { duong_dan: 'bang-gia', ten: 'Bảng giá', trang: <BangGiaDanhSach />, nhom: 'Quản trị' },
    { duong_dan: 'cau-hinh', ten: 'Cấu hình', trang: <CauHinh />, nhom: 'Quản trị' },
    // Quản lý chỉ xem tiền (nghiep-vu.md mục 8): ẩn nút ghi; quyền thật do máy chủ kiểm
    { duong_dan: 'cong-no', ten: 'Công nợ', trang: <CongNo chiXem />, nhom: 'Tài chính' },
    { duong_dan: 'quyet-toan', ten: 'Quyết toán', trang: <QuyetToan chiXem />, nhom: 'Tài chính' },
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
const menu = (nd: NguoiDung) =>
  (Object.keys(TRANG_CHU) as VaiTro[])
    .filter((vt) => duocVao(nd, vt))
    .flatMap((vt) =>
      (TRANG_CON[vt] ?? [])
        .filter((t) => !t.an)
        .map((t) => ({ ...t, den: `${TRANG_CHU[vt]}/${t.duong_dan}` })),
    )
// Thứ tự nhóm trên cột menu
const NHOM = ['', 'Vận hành', 'Danh mục', 'Tài chính', 'Quản trị']

const Hieu = ({ den }: { den: string }) => (
  <Link to={den} className="hieu">
    <i aria-hidden="true">
      <Ic ten="chuyen" />
    </i>
    Quản lý vận tải
  </Link>
)

// Khung trang sau đăng nhập (v3): cột menu trái theo nhóm, thanh trên có tìm chung, chuông, tài khoản.
// Chỉ một mục (tài xế) thì không có cột menu: tiêu đề trang đã nói đủ. Màn hẹp: cột menu thành thanh đáy.
function KhungTrang({
  nd,
  phienBanAnh,
  loiThoat,
  onThoat,
}: {
  nd: NguoiDung
  phienBanAnh: number
  loiThoat: string
  onThoat: () => void
}) {
  const muc = menu(nd)
  const coMenu = muc.length > 1
  return (
    <div className={coMenu ? 'khung' : 'khung mot'}>
      {coMenu && (
        <aside className="canh">
          <Hieu den={TRANG_CHU[nd.vai_tro]} />
          <nav aria-label="Chức năng">
            {NHOM.map((nhom) => {
              const ds = muc.filter((m) => (m.nhom ?? '') === nhom)
              if (ds.length === 0) return null
              return (
                <div key={nhom} role="group" aria-label={nhom || undefined}>
                  {nhom && <h2>{nhom}</h2>}
                  {ds.map((m) => (
                    <NavLink key={m.den} to={m.den}>
                      <Ic ten={m.duong_dan as TenIc} />
                      {m.ten}
                    </NavLink>
                  ))}
                </div>
              )
            })}
          </nav>
          <p className="canh-chan">Đồ án chuyên ngành · Nhóm 8</p>
        </aside>
      )}
      <div className="than">
        <header className="dau">
          <Hieu den={TRANG_CHU[nd.vai_tro]} />
          <TimChung vaiTro={nd.vai_tro} />
          <div className="ben-phai">
            <span className="ten">
              <b>{nd.ho_ten}</b>
              {TEN_VAI_TRO[nd.vai_tro]}
            </span>
            <ChuongThongBao nguoiDungId={nd.id} vaiTro={nd.vai_tro} />
            <MenuTaiKhoan
              nd={nd}
              tenVaiTro={TEN_VAI_TRO[nd.vai_tro]}
              phienBanAnh={phienBanAnh}
              onThoat={onThoat}
            />
          </div>
        </header>
        <main className="trang">
          {loiThoat && (
            <p role="alert" className="loi trang-loi">
              {loiThoat}
            </p>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default function App() {
  const [nd, setNd] = useState<NguoiDung | null | undefined>(undefined) // undefined = đang kiểm phiên
  const [phienBanAnh, setPhienBanAnh] = useState(0) // tăng khi đổi/xóa ảnh hoặc đăng nhập lại để tránh dính cache
  const [loiThoat, setLoiThoat] = useState('')

  useEffect(() => {
    toi()
      .then(setNd)
      .catch(() => setNd(null))
  }, [])

  if (nd === undefined) return <p className="dang-tai">Đang tải…</p>

  function capNhatAnh(coAnh: boolean) {
    setNd((cu) => (cu ? { ...cu, co_anh_dai_dien: coAnh } : cu))
    setPhienBanAnh((v) => v + 1)
  }

  async function thoat() {
    setLoiThoat('')
    try {
      await dangXuat()
      setNd(null)
      setPhienBanAnh((v) => v + 1)
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
            nd ? (
              <Navigate to={TRANG_CHU[nd.vai_tro]} replace />
            ) : (
              <DangNhap
                onXong={(moi) => {
                  setNd(moi)
                  setPhienBanAnh((v) => v + 1)
                }}
              />
            )
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
                <KhungTrang nd={nd} phienBanAnh={phienBanAnh} loiThoat={loiThoat} onThoat={thoat} />
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
        {/* Trang chung cho mọi vai trò đã đăng nhập (không hiện trên thanh menu bên trái) */}
        <Route
          element={
            !nd ? (
              <Navigate to="/dang-nhap" replace />
            ) : (
              <KhungTrang nd={nd} phienBanAnh={phienBanAnh} loiThoat={loiThoat} onThoat={thoat} />
            )
          }
        >
          <Route
            path="/tai-khoan"
            element={
              nd && (
                <TaiKhoan
                  nd={nd}
                  tenVaiTro={TEN_VAI_TRO[nd.vai_tro]}
                  phienBanAnh={phienBanAnh}
                  onDoiAnh={capNhatAnh}
                />
              )
            }
          />
          <Route path="/cai-dat" element={nd && <CaiDat vaiTro={nd.vai_tro} />} />
        </Route>
        <Route
          path="*"
          element={<Navigate to={nd ? TRANG_CHU[nd.vai_tro] : '/dang-nhap'} replace />}
        />
      </Routes>
    </BrowserRouter>
  )
}
