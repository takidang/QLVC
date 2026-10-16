import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { dangXuat, toi, type NguoiDung, type VaiTro } from './api/auth'
import DangNhap from './pages/DangNhap'

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

// Chỉ để điều hướng; quyền thật do máy chủ kiểm (BR-57). Quản lý vào được trang Điều phối.
const duocVao = (nd: NguoiDung, trang: VaiTro) =>
  nd.vai_tro === trang || (trang === 'DIEU_PHOI' && nd.vai_tro === 'QUAN_LY')

export default function App() {
  const [nd, setNd] = useState<NguoiDung | null | undefined>(undefined) // undefined = đang kiểm phiên

  useEffect(() => {
    toi()
      .then(setNd)
      .catch(() => setNd(null))
  }, [])

  if (nd === undefined) return <p className="dang-tai">Đang tải…</p>

  async function thoat() {
    await dangXuat()
    setNd(null)
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
        {(Object.keys(TRANG_CHU) as VaiTro[]).map((trang) => (
          <Route
            key={trang}
            path={TRANG_CHU[trang]}
            element={
              !nd ? (
                <Navigate to="/dang-nhap" replace />
              ) : !duocVao(nd, trang) ? (
                <Navigate to={TRANG_CHU[nd.vai_tro]} replace />
              ) : (
                <main className="trang">
                  <header>
                    <span>
                      {nd.ho_ten} · {TEN_VAI_TRO[nd.vai_tro]}
                    </span>
                    <button onClick={thoat}>Đăng xuất</button>
                  </header>
                  {/* Trang tạm của UC-01; nội dung thật làm ở các UC sau */}
                  <h1>Trang {TEN_VAI_TRO[trang]}</h1>
                </main>
              )
            }
          />
        ))}
        <Route
          path="*"
          element={<Navigate to={nd ? TRANG_CHU[nd.vai_tro] : '/dang-nhap'} replace />}
        />
      </Routes>
    </BrowserRouter>
  )
}
