import { goi, query } from './goi'

// UC-26: lãi lỗ (chỉ chuyến đã quyết toán); UC-34: hiệu suất xe theo tháng (api.md 2.6)
export type DongLaiLo = {
  so_chuyen: number
  doanh_thu: number
  tong_chi: number
  luong_tai_xe: number
  lai_chuyen: number
  chi_phi_co_dinh: number
  lai: number
}
export type LaiLo<T> = {
  theo: 'thang' | 'xe' | 'chuyen'
  tu: string
  den: string
  du_lieu: T[]
  tong: DongLaiLo
  so_chuyen_cho_quyet_toan: number
  thieu_chi_phi_co_dinh: { xe_id: number; bien_so: string; thang: string }[]
}
export const laiLoThang = (tu: string, den: string) =>
  goi<LaiLo<DongLaiLo & { thang: string }>>(
    `/api/bao-cao/lai-lo?${query({ theo: 'thang', tu, den })}`,
  )
export const laiLoXe = (thang: string) =>
  goi<LaiLo<DongLaiLo & { xe_id: number; bien_so: string }>>(
    `/api/bao-cao/lai-lo?${query({ theo: 'xe', tu: thang, den: thang })}`,
  )

export type HieuSuatXe = {
  xe_id: number
  bien_so: string
  so_chuyen: number
  so_chuyen_rong: number
  lap_day_tb: number | null
  km: number
  dau_thuc_te_lit: number
  dau_tham_khao_lit: number | null
  chenh_lech_lit: number | null
  so_chuyen_chua_quyet_toan: number
}
export const hieuSuatXe = (thang: string) =>
  goi<{ thang: string; du_lieu: HieuSuatXe[]; tong: Omit<HieuSuatXe, 'xe_id' | 'bien_so'> }>(
    `/api/bao-cao/hieu-suat-xe?${query({ thang })}`,
  )
