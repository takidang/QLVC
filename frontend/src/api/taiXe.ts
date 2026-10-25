import { goi, guiJson } from './goi'
import type { DanhSach } from './xe'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type TrangThaiTaiXe = 'HOAT_DONG' | 'NGUNG'
export type HangGplx = 'B' | 'C1' | 'C'
export type TaiXe = {
  id: number
  ten_dang_nhap: string
  ho_ten: string
  so_gplx: string
  hang_gplx: HangGplx
  han_gplx: string // YYYY-MM-DD
  sdt: string
  trang_thai: TrangThaiTaiXe
}
// Thêm tài xế tạo luôn tài khoản đăng nhập vai trò TAI_XE (UC-04)
export type TaiXeVao = Omit<TaiXe, 'id' | 'trang_thai'> & { mat_khau: string }
// Không sửa tên đăng nhập, mật khẩu ở đây (UC-02)
export type TaiXeSua = Partial<Omit<TaiXe, 'id' | 'ten_dang_nhap'>>

export function danhSachTaiXe(loc: {
  tim?: string
  trang_thai?: string
  trang?: number
  so_dong?: number
}) {
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(loc)) if (v !== undefined && v !== '') q.set(k, String(v))
  return goi<DanhSach<TaiXe>>(`/api/tai-xe?${q}`)
}

export const themTaiXe = (vao: TaiXeVao) => guiJson<TaiXe>('/api/tai-xe', 'POST', vao)
export const suaTaiXe = (id: number, vao: TaiXeSua) =>
  guiJson<TaiXe>(`/api/tai-xe/${id}`, 'PATCH', vao)
