import type { Chuyen } from './chuyen'
import { goi, query } from './goi'
import type { DanhSach } from './xe'

// Trang tài xế (UC-17). shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06)
export type NhomChuyen = 'can_lam' | 'da_xong'
export type ChuyenCuaToi = Chuyen & { so_don: number }
export type DiemCuaToi = {
  thu_tu: number
  nut: string
  viec: 'LAY' | 'GIAO'
  eta: string
  don_id: number
  ma_don: string
  ten_khach: string
  mo_ta: string | null
  kg: string
  m3: string
  so_kien: number
  trang_thai_don: string
  dia_chi: string
  nguoi_lien_he: string | null
  sdt: string
  lay_tu: string | null
  lay_den: string | null
  han_giao: string
}
export type ChuyenCuaToiChiTiet = ChuyenCuaToi & {
  luong_tai_xe_chot: number | null
  lich_trinh: DiemCuaToi[]
}

export const chuyenCuaToi = (loc: { nhom: NhomChuyen; trang?: number; so_dong?: number }) =>
  goi<DanhSach<ChuyenCuaToi>>(`/api/toi/chuyen?${query(loc)}`)
export const chuyenCuaToiChiTiet = (id: number) => goi<ChuyenCuaToiChiTiet>(`/api/toi/chuyen/${id}`)

export const TEN_TRANG_THAI: Record<string, string> = {
  DA_CHOT: 'Chờ chạy',
  DANG_CHAY: 'Đang chạy',
  HOAN_THANH: 'Hoàn thành',
  DA_QUYET_TOAN: 'Đã quyết toán',
}
export const ngayGio = (iso: string) =>
  new Date(iso).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  })
