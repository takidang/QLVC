import { goi, guiJson, query } from './goi'

// UC-25 công nợ (Kế toán ghi, Quản lý xem) – api.md 2.6
export type PhaiThu = {
  id: number
  don_hang_id: number
  ma_don: string
  khach_hang_id: number
  ten_khach: string
  ngay_giao: string | null
  so_tien: number
  trang_thai_tt: 'CHUA_THU' | 'DA_THU'
  phieu_thu_id: number | null
  ngay_thu: string | null
}
export type DanhSachPhaiThu = { du_lieu: PhaiThu[]; tong: number; tong_tien: number }
export type NoTheoKhach = {
  khach_hang_id: number
  ten_khach: string
  so_khoan: number
  tong_no: number
}
export type PhieuThu = {
  phieu_thu_id: number
  khach_hang_id: number
  tong_tien: number
  ngay: string
  so_khoan: number
}

export const noTheoKhach = () => goi<NoTheoKhach[]>('/api/phai-thu/theo-khach')
export const danhSachPhaiThu = (loc: {
  trang_thai_tt?: string
  khach_hang_id?: number
  trang?: number
  so_dong?: number
}) => goi<DanhSachPhaiThu>(`/api/phai-thu?${query(loc)}`)
export const danhDauDaThu = (phai_thu_ids: number[], ngay: string) =>
  guiJson<PhieuThu>('/api/phai-thu/da-thu', 'POST', { phai_thu_ids, ngay })
