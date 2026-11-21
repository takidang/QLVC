import { goi, guiJson } from './goi'
import type { HinhThuc } from './tamUng'

// UC-24 quyết toán (Kế toán ghi, Quản lý xem) – api.md 2.6, 3.3
export type XuLy = 'TAI_XE_DA_NOP' | 'CONG_TY_DA_TRA' | 'KHONG_CHENH'
export const TEN_XU_LY: Record<XuLy, string> = {
  TAI_XE_DA_NOP: 'Tài xế đã nộp lại',
  CONG_TY_DA_TRA: 'Công ty đã trả thêm',
  KHONG_CHENH: 'Không chênh lệch',
}
export type KhoanChiQt = {
  id: number
  loai: 'DAU' | 'CAU_DUONG' | 'BOC_XEP' | 'PHAT_SINH'
  so_tien_khai: number
  so_tien_duyet: number | null
  so_lit: string | null
  ghi_chu: string
  trang_thai: 'CHO_DUYET' | 'DA_DUYET' | 'TU_CHOI'
  anh: number[]
  tao_luc: string
}
type DonQt = { id: number; ma_don: string; ten_khach: string; cuoc: number }
export type BangQuyetToan = {
  chuyen_id: number
  ma_chuyen: string
  trang_thai: string
  bien_so: string
  ten_tai_xe: string
  ten_tuyen: string
  ket_thuc_bat_thuong: boolean
  ly_do_ket_thuc: string | null
  don_giao: DonQt[]
  don_that_bai: DonQt[]
  doanh_thu: number
  chi_theo_loai: {
    loai: KhoanChiQt['loai']
    dinh_muc: number
    thuc_te: number
    chenh_lech: number
  }[]
  dinh_muc: number
  tong_chi: number
  km: number | null
  dau_tham_khao_lit: string | null
  dau_thuc_te_lit: string
  khoan: KhoanChiQt[]
  so_cho_duyet: number
  luong_chot: number
  luong_tai_xe: number
  can_luong_tay: boolean
  ly_do_luong_tay: string | null
  tong_tam_ung_hieu_luc: number
  chenh_lech_tam_ung: number
  xu_ly_goi_y: XuLy
  lai: number
  lai_du_kien: number
  ly_do_lech: { mo_ta: string; so_tien: number }[]
  xu_ly_chenh_lech: XuLy | null
  hinh_thuc: HinhThuc | null
  luc_xu_ly: string | null
  luc_quyet_toan: string | null
}
export type QuyetToanVao = {
  xu_ly_chenh_lech: XuLy
  hinh_thuc?: HinhThuc
  luc_xu_ly?: string
  luong_tay?: number
  ly_do_luong_tay?: string
}

export const bangQuyetToan = (chuyen_id: number) =>
  goi<BangQuyetToan>(`/api/chuyen/${chuyen_id}/quyet-toan`)
export const quyetToan = (chuyen_id: number, vao: QuyetToanVao) =>
  guiJson<unknown>(`/api/chuyen/${chuyen_id}/quyet-toan`, 'POST', vao)
export const duyetChi = (id: number, so_tien_duyet: number, ly_do?: string) =>
  guiJson<KhoanChiQt>(`/api/chi-phi/${id}/duyet`, 'POST', { so_tien_duyet, ly_do: ly_do || null })
export const tuChoiChi = (id: number, ly_do: string) =>
  guiJson<KhoanChiQt>(`/api/chi-phi/${id}/tu-choi`, 'POST', { ly_do })
// Link ảnh có hạn 5 phút (NFR-SEC-04): lấy ngay lúc bấm xem
export const linkAnh = (tep_id: number) => goi<{ url: string }>(`/api/tep/${tep_id}/link`)
