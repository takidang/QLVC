import { useEffect, useState, type ReactNode } from 'react'
import { BrowserRouter, Navigate, NavLink, Outlet, Route, Routes } from 'react-router-dom'
import { dangXuat, toi, type NguoiDung, type VaiTro } from './api/auth'
import DangNhap from './pages/DangNhap'
import BangGiaDanhSach from './pages/quan-ly/BangGiaDanhSach'
import CauHinh from './pages/quan-ly/CauHinh'
import DonDanhSach from './pages/dieu-phoi/DonDanhSach'
import KhachHangDanhSach from './pages/dieu-phoi/KhachHangDanhSach'
import NutDanhSach from './pages/dieu-phoi/NutDanhSach'
import TuyenDanhSach from './pages/dieu-phoi/TuyenDanhSach'
import TaiXeDanhSach from './pages/dieu-phoi/TaiXeDanhSach'
import XeDanhSach from './pages/dieu-phoi/XeDanhSach'
import ChiPhiCoDinh from './pages/ke-toan/ChiPhiCoDinh'

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

// Trang con của từng vai trò. Thêm UC mới: thêm một dòng ở đây (docs/mau-use-case.md)
const TRANG_CON: Partial<Record<VaiTro, { duong_dan: string; ten: string; trang: ReactNode }[]>> = {
  DIEU_PHOI: [
    { duong_dan: 'don', ten: 'Đơn hàng', trang: <DonDanhSach /> },
    { duong_dan: 'xe', ten: 'Xe', trang: <XeDanhSach /> },
    { duong_dan: 'tai-xe', ten: 'Tài xế', trang: <TaiXeDanhSach /> },
    { duong_dan: 'khach-hang', ten: 'Khách hàng', trang: <KhachHangDanhSach /> },
    { duong_dan: 'nut', ten: 'Nút', trang: <NutDanhSach /> },
    { duong_dan: 'tuyen', ten: 'Tuyến', trang: <TuyenDanhSach /> },
  ],
  KE_TOAN: [{ duong_dan: 'chi-phi-xe', ten: 'Chi phí cố định xe', trang: <ChiPhiCoDinh /> }],
  QUAN_LY: [
    { duong_dan: 'bang-gia', ten: 'Bảng giá', trang: <BangGiaDanhSach /> },
    { duong_dan: 'cau-hinh', ten: 'Cấu hình', trang: <CauHinh /> },
  ],
}

// Chỉ để điều hướng; quyền thật do máy chủ kiểm (BR-57). Quản lý vào được trang Điều phối.
const duocVao = (nd: NguoiDung, trang: VaiTro) =>
  nd.vai_tro === trang || (trang === 'DIEU_PHOI' && nd.vai_tro === 'QUAN_LY')

// Menu của người dùng: trang của vai trò mình, Quản lý thấy thêm trang Điều phối
const menu = (nd: NguoiDung) =>
  (Object.keys(TRANG_CHU) as VaiTro[])
    .filter((vt) => duocVao(nd, vt))
    .flatMap((vt) =>
      (TRANG_CON[vt] ?? []).map((t) => ({ ...t, den: `${TRANG_CHU[vt]}/${t.duong_dan}` })),
    )

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
      <Routes>
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
                <main className="trang">
                  <header>
                    <nav>
                      {menu(nd).map((m) => (
                        <NavLink key={m.den} to={m.den}>
                          {m.ten}
                        </NavLink>
                      ))}
                    </nav>
                    <span>
                      {nd.ho_ten} · {TEN_VAI_TRO[nd.vai_tro]}
                    </span>
                    <button onClick={thoat}>Đăng xuất</button>
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
          >
            <Route
              index
              element={
                <section className="noi-dung">
                  <h1>Trang {TEN_VAI_TRO[vt]}</h1>
                  <p className="ghi-chu">Chọn chức năng trên thanh menu.</p>
                </section>
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
