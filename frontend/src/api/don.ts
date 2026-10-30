import { goi, guiJson, query } from './goi'
import type { DanhSach } from './xe'

// shortcut: kiểu viết tay, thay bằng kiểu sinh từ OpenAPI (kien-truc.md KT-06) khi nhóm chọn công cụ sinh
export type Don = {
  id: number
  ma_don: string
  khach_hang_id: number
  ten_khach: string
  mo_ta: string | null
  kg: string
  m3: string
  so_kien: number
  tinh_lay: string
  dia_chi_lay: string
  lay_tu: string | null
  lay_den: string | null
  tinh_giao: string
  dia_chi_giao: string
  nguoi_nhan: string
  han_giao: string
  cuoc_tinh: number
  trang_thai: string
  tao_luc: string
}

export type DonVao = {
  khach_hang_id: number
  mo_ta: string | null
  kg: string
  m3: string
  so_kien: number
  nut_lay_id: number
  dia_chi_lay: string
  nguoi_lien_he_lay: string | null
  sdt_lay: string
  lay_tu: string | null
  lay_den: string | null
  nut_giao_id: number
  dia_chi_giao: string
  nguoi_nhan: string
  sdt_nhan: string
  han_giao: string
}

export type BaoGia = {
  kl_quy_doi: string
  kl_tinh_cuoc: string
  don_gia_kg: number
  cuoc_toi_thieu: number
  cuoc: number
}

export function danhSachDon(loc: {
  tim?: string
  trang_thai?: string
  trang?: number
  so_dong?: number
}) {
  return goi<DanhSach<Don>>(`/api/don?${query(loc)}`)
}
export const tinhCuoc = (vao: {
  nut_lay_id: number
  nut_giao_id: number
  kg: string
  m3: string
}) => guiJson<BaoGia>('/api/don/tinh-cuoc', 'POST', vao)
export const taoDon = (vao: DonVao) => guiJson<Don>('/api/don', 'POST', vao)
