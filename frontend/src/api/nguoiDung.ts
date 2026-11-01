import type { VaiTro } from './auth'
import { goi, guiJson, query } from './goi'
import type { DanhSach } from './xe'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type TrangThaiNguoiDung = 'HOAT_DONG' | 'NGUNG'
export type TaiKhoan = {
  id: number
  ten_dang_nhap: string
  ho_ten: string
  vai_tro: VaiTro
  trang_thai: TrangThaiNguoiDung
  khoa_den: string | null // khóa tạm do sai mật khẩu (NFR-SEC-05)
}
// Tài khoản tài xế tạo ở UC-04
export type VaiTroTao = Exclude<VaiTro, 'TAI_XE'>
export type TaiKhoanVao = {
  ten_dang_nhap: string
  ho_ten: string
  mat_khau: string
  vai_tro: VaiTroTao
}
export type TaiKhoanSua = Partial<{
  ten_dang_nhap: string
  ho_ten: string
  vai_tro: VaiTroTao
  trang_thai: TrangThaiNguoiDung
}>

export function danhSachNguoiDung(loc: {
  tim?: string
  vai_tro?: string
  trang_thai?: string
  trang?: number
  so_dong?: number
}) {
  return goi<DanhSach<TaiKhoan>>(`/api/nguoi-dung?${query(loc)}`)
}

export const themNguoiDung = (vao: TaiKhoanVao) => guiJson<TaiKhoan>('/api/nguoi-dung', 'POST', vao)
export const suaNguoiDung = (id: number, vao: TaiKhoanSua) =>
  guiJson<TaiKhoan>(`/api/nguoi-dung/${id}`, 'PATCH', vao)
export const datLaiMatKhau = (id: number, mat_khau: string) =>
  guiJson<void>(`/api/nguoi-dung/${id}/mat-khau`, 'PUT', { mat_khau })
