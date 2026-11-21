import { goi, guiJson } from './goi'

// UC-23 tạm ứng (Kế toán ghi, Quản lý xem) – api.md 2.6
export type HinhThuc = 'TIEN_MAT' | 'CHUYEN_KHOAN'
export const TEN_HINH_THUC: Record<HinhThuc, string> = {
  TIEN_MAT: 'Tiền mặt',
  CHUYEN_KHOAN: 'Chuyển khoản',
}
export type TamUng = {
  id: number
  chuyen_id: number
  ma_chuyen: string
  tai_xe_id: number
  ten_tai_xe: string
  so_tien: number
  hinh_thuc: HinhThuc
  trang_thai: 'HIEU_LUC' | 'DA_THU_HOI'
  tao_luc: string
}
export type TamUngChuyen = {
  chuyen_id: number
  ma_chuyen: string
  trang_thai_chuyen: string
  dinh_muc: number
  tong_hieu_luc: number
  con_duoc_cap: number
  khoan: TamUng[]
}

export const tamUngChuyen = (chuyen_id: number) =>
  goi<TamUngChuyen>(`/api/chuyen/${chuyen_id}/tam-ung`)
export const capTamUng = (chuyen_id: number, so_tien: number, hinh_thuc: HinhThuc) =>
  guiJson<TamUng>(`/api/chuyen/${chuyen_id}/tam-ung`, 'POST', { so_tien, hinh_thuc })
export const suaTamUng = (id: number, so_tien: number, hinh_thuc: HinhThuc, ly_do: string) =>
  guiJson<TamUng>(`/api/tam-ung/${id}`, 'PATCH', { so_tien, hinh_thuc, ly_do })
export const thuHoiTamUng = (id: number) =>
  guiJson<TamUng>(`/api/tam-ung/${id}/thu-hoi`, 'POST', {})
