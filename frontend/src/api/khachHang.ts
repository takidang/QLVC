import { goi, guiJson, query } from './goi'
import type { DanhSach } from './xe'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type KhachHang = {
  id: number
  ten: string
  sdt: string
  dia_chi: string | null
  ma_so_thue: string | null
  trang_thai: 'HOAT_DONG' | 'NGUNG'
}
export type KhachHangVao = Omit<KhachHang, 'id' | 'trang_thai'>

export function danhSachKhachHang(loc: {
  tim?: string
  trang_thai?: string
  trang?: number
  so_dong?: number
}) {
  return goi<DanhSach<KhachHang>>(`/api/khach-hang?${query(loc)}`)
}

export const themKhachHang = (vao: KhachHangVao) =>
  guiJson<KhachHang>('/api/khach-hang', 'POST', vao)
export const suaKhachHang = (
  id: number,
  vao: Partial<KhachHangVao> & { trang_thai?: KhachHang['trang_thai'] },
) => guiJson<KhachHang>(`/api/khach-hang/${id}`, 'PATCH', vao)
